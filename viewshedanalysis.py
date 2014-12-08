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
#from scipy import sparse Nema ga !!
from math import sqrt, degrees, atan2
from operator import itemgetter #ovo je za sortiranje liste NE TREBA!!!


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
 

        #UBACIVANJE RASTERA I TOCAKA (mora biti ovdje ili se barem pozvati odavde)
        myLayers = []
        iface = self.iface
        #clear combos        
        self.dlg.ui.cmbRaster.clear();self.dlg.ui.cmbPoints.clear();self.dlg.ui.cmbPointsTarget.clear()
        #add an empty value to optional combo
        self.dlg.ui.cmbPointsTarget.addItem('',0)
        #add layers to combos
        for i in range(len(iface.mapCanvas().layers())):
            myLayer = iface.mapCanvas().layer(i)
            if myLayer.type() == myLayer.RasterLayer:

                #provjera da li je DEM 1 band .... !!!
                self.dlg.ui.cmbRaster.addItem(myLayer.name(),myLayer.id())

            elif myLayer.geometryType() == QGis.Point: 
                self.dlg.ui.cmbPoints.addItem(myLayer.name(),myLayer.id())
                self.dlg.ui.cmbPointsTarget.addItem(myLayer.name(),myLayer.id())

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

            search_top_obs = ViewshedAnalysisDialog.returnSearchTopObserver(self.dlg)
            search_top_target = ViewshedAnalysisDialog.returnSearchTopTarget(self.dlg)
            
            output_options = ViewshedAnalysisDialog.returnOutputOptions(self.dlg)
                
            curv=ViewshedAnalysisDialog.returnCurvature(self.dlg)
            refraction = curv[1] if curv else 0 
            
            if not output_options [0]:
                QMessageBox.information(self.iface.mainWindow(), "Error!", str("Select an output option")) 
                return 
             #   LOADING CSV
             # uri = "file:///some/path/file.csv?delimiter=%s&crs=epsg:4723&wktField=%s" \
             # % (";", "shape")

            out_raster = Viewshed(ly_obs, ly_dem, z_obs, z_target, Radius,outPath,
                                  output_options,
                                  ly_target, search_top_obs, search_top_target,
                                  z_obs_field, z_target_field, curv, refraction)
            
            for r in out_raster:
                #QMessageBox.information(self.iface.mainWindow(), "debug", str(r))
                lyName = os.path.splitext(os.path.basename(r))
                layer = QgsRasterLayer(r, lyName[0])
                #if error -> it's shapefile, skip rendering...
                if not layer.isValid():
                    layer= QgsVectorLayer(r,lyName[0],"ogr")
                    
                else:
##                    #rlayer.setColorShadingAlgorithm(QgsRasterLayer.UndefinedShader)
##
##                    #from linfinity.com
##                    extentMin, extentMax = layer.computeMinimumMaximumFromLastExtent( band )
##
##                    # For greyscale layers there is only ever one band
##                    band = layer.bandNumber( layer.grayBandName() ) # base 1 counting in gdal
##                    # We don't want to create a lookup table
##                    generateLookupTableFlag = False
##                    # set the layer min value for this band
##                    layer.setMinimumValue( band, extentMin, generateLookupTableFlag )
##                    # set the layer max value for this band
##                    layer.setMaximumValue( band, extentMax, generateLookupTableFlag )
##
##                    # let the layer know that the min max are user defined
##                    layer.setUserDefinedGrayMinimumMaximum( True )
##
##                    # make sure the layer is redrawn
##                    layer.triggerRepaint()

                    #NOT WORKING 
                    
##                    x = QgsRasterTransparency.TransparentSingleValuePixel()
##                    x.pixelValue = 0
##                    x.transparencyPercent = 100
##                    layer.setTransparentSingleValuePixelList( [ x ] )
                    
                    layer.setContrastEnhancement(QgsContrastEnhancement.StretchToMinimumMaximum)

                    #rlayer.setDrawingStyle(QgsRasterLayer.SingleBandPseudoColor)
                    #rlayer.setColorShadingAlgorithm(QgsRasterLayer.PseudoColorShader)
                    #rlayer.setContrastEnhancementAlgorithm(QgsContrastEnhancement.StretchToMinimumMaximum, False)
                    #rlayer.setTransparency(200)
                    #rlayer.setNoDataValue(0.0)
                    
                QgsMapLayerRegistry.instance().addMapLayer(layer)

            
#    adding csv files ... an attempt
##                    url = QUrl.fromLocalFile(r)
##                    url.addQueryItem('delimiter',',')
##                    url.addQueryItem('xField  <-or-> yField','longitude')
##                    url.addQueryItem('crs','epsg:4723')
##                    url.addQueryItem('wktField','WKT')
## -> Problem
##                    #layer_uri=Qstring.fromAscii(url.toEncoded())
##                    layer_uri= str(url)
##                    layer=QgsVectorLayer(r, lyName[0],"delimitedtext")

#                     QMessageBox.information(None, "File created!", str("Please load file manually (as comma delilmited text)."))





            
