# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Senscape
                                 A QGIS plugin
 
                              -------------------
        begin                : 2017-03-10
        copyright            : (C) 2017 by Zoran Čučković
        email                : some
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

__author__ = 'Zoran Čučković'
__date__ = '2018-03-18'
__copyright__ = '(C) 2018 by Zoran Čučković'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsWkbTypes,
                       QgsFields, QgsField, QgsPoint, QgsFeature,QgsGeometry,

                       QgsProcessing,QgsProcessingException,
                       
                       QgsProcessingAlgorithm,

                       QgsFeatureSink,
                       
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                                               
                       QgsProcessingParameterRasterLayer,

                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterEnum )

        
from .modules import Points as pts
from .modules import Raster as rst

# from processing.tools import dataobjects


from .modules import visibility as ws
from .modules import Points as pts
from .modules import Raster as rst


class Intervisibility(QgsProcessingAlgorithm):

    DEM = 'DEM'
    
    OBSERVER_POINTS = 'OBSERVER_POINTS'
    TARGET_POINTS = 'TARGET_POINTS'

    WRITE_NEGATIVE= 'WRITE_NEGATIVE'
    
    USE_CURVATURE = 'USE_CURVATURE'
    REFRACTION = 'REFRACTION'

    OUTPUT = 'OUTPUT'


    PRECISIONS = ['Coarse', 'Normal']
    PRECISION = 'PRECISION'


    def helpUrl(self):
        return  'zoran-cuckovic.github.io/QGIS-visibility-analysis/help_qgis3.html'
            

    def initAlgorithm(self, config):
        
        self.addParameter(QgsProcessingParameterFeatureSource(self.OBSERVER_POINTS,
                                                              self.tr('Observer points'),
                                                              [QgsProcessing.TypeVectorPoint]))

        self.addParameter(QgsProcessingParameterFeatureSource(self.TARGET_POINTS,
                                                              self.tr('Target points'),
                                                              [QgsProcessing.TypeVectorPoint]))

        self.addParameter(QgsProcessingParameterRasterLayer
                          (self.DEM,
            self.tr('Digital elevation model ')))

        self.addParameter(QgsProcessingParameterBoolean(
            self.WRITE_NEGATIVE,
            self.tr('Save negative links'),
            False))
        
        self.addParameter(QgsProcessingParameterBoolean(
            self.USE_CURVATURE,
            self.tr('Take in account Earth curvature'),
            False))
        self.addParameter(QgsProcessingParameterNumber(
            self.REFRACTION,
            self.tr('Atmoshpheric refraction'),
            1, 0.13, False, 0.0, 1.0))
        
##        
##        self.addParameter(QgsProcessingParameterEnum (
##            self.PRECISION,
##            self.tr('Algorithm precision'),
##            self.PRECISIONS,
##            defaultValue=1))

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')) )



    def processAlgorithm(self, parameters, context, feedback):

        
        
        raster = self.parameterAsRasterLayer(parameters,self.DEM, context)
        observers = self.parameterAsSource(parameters,self.OBSERVER_POINTS,context)
        targets = self.parameterAsSource(parameters,self.TARGET_POINTS,context)
        write_negative = self.parameterAsBool(parameters,self.WRITE_NEGATIVE,context)
        
        useEarthCurvature = self.parameterAsBool(parameters,self.USE_CURVATURE,context)
        refraction = self.parameterAsDouble(parameters,self.REFRACTION,context)
        precision = 1#self.parameterAsInt(parameters,self.PRECISION,context)
   


    # ----- convert meters to layer distance units ------
##        coef = QgsUnitTypes.fromUnitToUnitFactor(Qgis.DistanceMeters, dem.crs().mapUnits())
##
##
##        searchRadius = searchRadius * coef
##
        
        dem = rst.Raster(raster.source())
       
        o= pts.Points(observers)       
        t= pts.Points(targets)

        required=["observ_hgt", "radius"]

        miss1 = o.test_fields (required)
        miss2 = t.test_fields (required)
        
        if miss1 or miss2:

            msg = ("\n ********** \n MISSING FIELDS! \n" +
                "\n Missing in observer points: " + ", ".join(miss1) +
                "\n Missing in target points: " + ", ".join(miss2))
               
            raise QgsProcessingException(msg)
                 
        o.take(dem.extent, dem.pix)
        t.take(dem.extent, dem.pix)

        if o.count == 0 or t.count == 0:

            msg = ("\n ********** \n ERROR! \n"
                "\n No view points/target points in the chosen area!")
            
            raise QgsProcessingException(msg)
           
        fds = [("Source", QVariant.String, 'string',255),
               ("Target", QVariant.String, 'string',255),
               ("TargetSize", QVariant.Double, 'double',10,3)]

        qfields = QgsFields()
        for f in fds : qfields.append(QgsField(*f))
        
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                            qfields,
                            QgsWkbTypes.LineString,
                            o.crs)

        
        feedback.setProgressText("*1* Constructing the network")
        o.network(t, skip_same_id = (observers==targets)) #do this after .take which takes points within raster extents

        t = None
       
        dem.set_master_window(o.max_radius,
                            curvature =useEarthCurvature,
                            refraction = refraction )
        
        cnt = 0

        feedback.setProgressText("*2* Testing visibility")   
        for key, ob in o.pt.items():

            ws.intervisibility(ob, dem, interpolate = precision)

            p1 = QgsPoint(float(ob["x_geog"]), float(ob["y_geog"] ))

            for key, tg in ob["targets"].items():
                
                h = tg["depth"]           
                
                if not write_negative:
                    if h<0: continue
               
                p2 = QgsPoint(float(tg["x_geog"]), float(tg["y_geog"] ))

                feat = QgsFeature()
                feat.setGeometry(QgsGeometry.fromPolyline([p1, p2]))

                feat.setFields(qfields)
                feat['Source'] = ob["id"]
                feat['Target'] = tg["id"]
                feat['TargetSize'] = float(h) #.                
           
                sink.addFeature(feat, QgsFeatureSink.FastInsert) 
     
            cnt +=1
            feedback.setProgress(int((cnt/o.count) *100))

        feedback.setProgressText("*3* Drawing the network")

        return {self.OUTPUT: dest_id}
       
        
    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Intervisibility'
    
    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr("Intervisibility network")
    
    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Analysis'
    
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        #return ViewshedPoints() NORMALLY
        return type(self)()
        
