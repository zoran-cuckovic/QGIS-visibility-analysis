# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ViewshedAnalysis
                                 A QGIS plugin
 ------description-------
                              -------------------
        begin                : 2013-05-22
        copyright            : (C) 2013 by Zoran Čučković
        email                : /
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from viewshedanalysisdialog import ViewshedAnalysisDialog

from doViewshed import *
from osgeo import osr, gdal
import os
#import shutil# to copy files
import numpy 


from operator import itemgetter #ovo je za sortiranje liste NE TREBA!!!

from Points import Points

class ViewshedAnalysis:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/viewshedanalysis"
        # initialize locale
        localePath = ""
    ## REMOVED .toString()
        locale = str(QSettings().value("locale/userLocale"))[0:2] #to je za jezik
        
        if QFileInfo(self.plugin_dir).exists():
            localePath = self.plugin_dir + "/i18n/ViewshedAnalysis_" + locale + ".qm"

        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = ViewshedAnalysisDialog()

    def initGui(self):
        # Create action that will start plugin configuration
        # icon in the plugin reloader : from resouces.qrc file (compiled)
        self.action = QAction(
            QIcon(":/plugins/ViewshedAnalysis/icon.png"),
            u"Viewshed analysis", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)
        

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Viewshed Analysis", self.action)

        # Fire refreshing of combo-boxes containing lists of table columns, after a new layer has been selected
        
        QObject.connect(self.dlg.ui.cmbPoints, SIGNAL("currentIndexChanged(int)"),self.load_cmbObsField)# ne radi sa zadanim parametrom (source)
        QObject.connect(self.dlg.ui.cmbPointsTarget, SIGNAL("currentIndexChanged(int)"),self.load_cmbTargetField)# ne radi sa zadanim parametrom (source)


    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Viewshed Analysis", self.action)
        self.iface.removeToolBarIcon(self.action)
        
    #This is just a clumsy workaround for the problem of mulitple arguments in the Qt signal-slot scheme
    def load_cmbObsField(self,cmb_index): self.reload_dependent_combos(cmb_index,'cmbObsField')
    def load_cmbTargetField(self,cmb_index): self.reload_dependent_combos(cmb_index-1,'cmbTargetField')
                                                                           #-1 because the first one is empty...          
                   
    def reload_dependent_combos(self,cmb_index,cmb_name):

        if cmb_name=='cmbObsField':
            cmb_obj=self.dlg.ui.cmbObsField
            l=self.dlg.ui.cmbPoints.itemData(cmb_index)   #(self.dlg.ui.cmbPoints.currentIndex())
        else:
            cmb_obj=self.dlg.ui.cmbTargetField
            l=self.dlg.ui.cmbPoints.itemData(cmb_index)   #(self.dlg.ui.cmbPoints.currentIndex())
       
        cmb_obj.clear()
        cmb_obj.addItem('',0)
        
        ly_name=str(l)
        ly = QgsMapLayerRegistry.instance().mapLayer(ly_name)
        
        #QMessageBox.information(self.iface.mainWindow(), "prvi", str(ly_name))
        if ly is None: return
        
        provider = ly.dataProvider()
        columns = provider.fields() # a dictionary
        j=0
        for fld in columns:
            #QMessageBox.information(self.iface.mainWindow(), "drugi", str(i.name))
            j+=1
            cmb_obj.addItem(str(fld.name()),str(fld.name())) #for QGIS 2.0 we need column names, not index (j)


    def run(self):
 

       
        myLayers = []
        iface = self.iface
        #clear combos        
        self.dlg.ui.cmbRaster.clear();self.dlg.ui.cmbPoints.clear();self.dlg.ui.cmbPointsTarget.clear()
        #add an empty value to optional combo
        self.dlg.ui.cmbPointsTarget.addItem('',0)
        #add layers to combos
        for i in range(len(iface.mapCanvas().layers())):
            myLayer = iface.mapCanvas().layer(i)

            #l_id = myLayer.id() not used   

            l_path =myLayer.dataProvider().dataSourceUri()

            l_name= myLayer.name()
            
            if not myLayer.isValid() :
                l_name ='ERROR ' + l_name 
            
            if myLayer.type() == myLayer.RasterLayer:

                #provjera da li je DEM 1 band .... !!!
                self.dlg.ui.cmbRaster.addItem(l_name,l_path)

            elif myLayer.geometryType() == QGis.Point: 
                self.dlg.ui.cmbPoints.addItem(l_name, l_path)
                self.dlg.ui.cmbPointsTarget.addItem(l_name, l_path)

        #allAttrs = layer.pendingAllAttributesList()
       
                
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()

        l = self.dlg.ui.cmbPoints.itemData(self.dlg.ui.cmbPoints.currentIndex())
        ly_name = str(l)
      #  QMessageBox.information(self.iface.mainWindow(), "drugi", str(ly_name))

        # See if OK was pressed
        
        if result == 1:
            outPath = ViewshedAnalysisDialog.returnOutputFile(self.dlg)
            ly_obs = ViewshedAnalysisDialog.returnPointLayer(self.dlg)
            ly_target = ViewshedAnalysisDialog.returnTargetLayer(self.dlg)
            ly_dem = ViewshedAnalysisDialog.returnRasterLayer(self.dlg)

            z_obs = ViewshedAnalysisDialog.returnObserverHeight(self.dlg) 
            z_obs_field = self.dlg.ui.cmbObsField.itemData(
                self.dlg.ui.cmbObsField.currentIndex())#table columns are indexed 0-n 

            z_target = ViewshedAnalysisDialog.returnTargetHeight(self.dlg) 
            z_target_field =self.dlg.ui.cmbTargetField.itemData(
                self.dlg.ui.cmbTargetField.currentIndex())       
            
            Radius = ViewshedAnalysisDialog.returnRadius(self.dlg)

            Algo = ViewshedAnalysisDialog.returnAlgorithm(self.dlg)

            search_top_obs = ViewshedAnalysisDialog.returnSearchTopObserver(self.dlg)
            search_top_target = ViewshedAnalysisDialog.returnSearchTopTarget(self.dlg)
            
            output_options = ViewshedAnalysisDialog.returnOutputOptions(self.dlg)
                
            curvature=ViewshedAnalysisDialog.returnCurvature(self.dlg)
            
            
            if not output_options [0]:
                QMessageBox.information(self.iface.mainWindow(), "Error!", str("Select an output option")) 
                return 
             #   LOADING CSV
             # uri = "file:///some/path/file.csv?delimiter=%s&crs=epsg:4723&wktField=%s" \
             # % (";", "shape")


           
            
            rst = QgsRasterLayer(ly_dem, 'o', 'gdal')
            ext = rst.extent()
            pix = rst.rasterUnitsPerPixelX()
        
            if pix < 0.01: #this is not the best way to test for WGS !!
                            # eg.   projection= gdal_raster.GetProjection()
                QMessageBox.information(self.iface.mainWindow(), "Error!",
                      """The elevation data seems to be in a latitude/longitude system
                        that cannot be used.""")
                return         
            elif round(pix, 4) != round(rst.rasterUnitsPerPixelY(), 4):
                QMessageBox.information(self.iface.mainWindow(), "Error!", 
                    """Elevation model does not have regular pixels!
                    Was it properly reprojected from a latitude/longitude system ?""") 
                return

            
            
            if curvature: #a list of two values: Diameter of Earth and refraction
                
                # we need ellipsiod for curvature (and crs for output)
               
                raster_crs = rst.crs().toWkt() #messy.. have to parse textual description...
                inx =raster_crs.find("SPHEROID") #(...)spheroid["name",semi_major, minor, etc...]
                inx2 = raster_crs.find(",", inx) +1
                inx3 = raster_crs.find(",", inx2 )
                try:
                    semi_major= float(raster_crs[inx2:inx3])
                    if not 6000000 < semi_major < 7000000 : semi_major=6378137#WGS 84
                except: semi_major=6378137  

                inx4 = raster_crs.find(",", inx3 +1 )
                try:
                    flattening =  float(raster_crs[inx3 +1:inx4-1])
                    if not 296 <flattening < 301 : flattening= 298.257223563#WGS 84
                except: flattening= 298.257223563
                
                semi_minor=  semi_major - semi_major* (1/flattening)
                # a compromise for 45 deg latitude, ArcGis seems to have a fixed earth diameter?
                Diameter = semi_major + semi_minor
                curvature[0]=Diameter #curvatture [1] = refraction, already set

                
            points = Points()
            points.point_dict(ly_obs, ext, pix, z_obs, Radius,
                              z_targ = z_target,
                              
                              field_ID = None, 
                              field_zobs= z_obs_field,
                              field_ztarg = z_target_field,
                              field_radius=None) #None : not used yet !

            if search_top_obs : points.search_top_z(search_top_obs, ly_dem)

         
            

            if output_options [0] == 'Intervisibility':
                if not ly_target:
                    QMessageBox.information(self.iface.mainWindow(), "Error!", str(
                    "Target points are not chosen")) 
                    return
                points_tg = Points()
                # obs height is not used (target = obs )
                points_tg.point_dict(ly_target, ext, pix, z_obs, Radius,
                              z_targ = z_target,
                              field_ID = None, 
                              field_ztarg = z_target_field)
                
             

                points.point_network( points_tg , Radius)#construct network
            
                
                if search_top_target : pass # TODO !!
                
            else: points_tg = None
            
            if output_options[0]=="Translucency": #not implemented !!
                rst_t = QgsRasterLayer(output_options[2], 'o', 'gdal')
                
                if not ext == rst.extent() or not pix == rst_t.rasterUnitsPerPixelX():
                    answer= QMessageBox.question(None, "Data mismatch",
                    """There seems to be a mismatch between elevation data and coverage raster.
                                           Do you want to proceed anyway? """,
                                           QMessageBox.Yes, QMessageBox.No)

                    if answer == QMessageBox.No: return        

                

            out_raster = Viewshed(points, ly_dem,  outPath,
                                  output_options,
                                  points_tg, curvature,
                                  Algo)
            
            for r in out_raster:
                #QMessageBox.information(self.iface.mainWindow(), "debug", str(r))
                lyName = os.path.splitext(os.path.basename(r))
                layer = QgsRasterLayer(r, lyName[0])
                #if error -> it's shapefile, skip rendering...
                if not layer.isValid():
                    layer= QgsVectorLayer(r,lyName[0],"ogr")
                    
                else: 
                    layer.setContrastEnhancement(QgsContrastEnhancement.StretchToMinimumMaximum)
                    
                QgsMapLayerRegistry.instance().addMapLayer(layer)


            
