# -*- coding: utf-8 -*-

"""
/***************************************************************************
 QGIS Viewshed Analysis
                                 A QGIS plugin
 
                              -------------------
        begin                : 2017-03-10
        copyright            : (C) 2017 by Zoran Čučković
        email                : contact@zoran-cuckovic.from.hr
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

from os import path 

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingException,
                       
                       QgsProcessingAlgorithm,

                       QgsFeatureSink,
                       
                       QgsProcessingParameterFeatureSource,
                        QgsProcessingParameterFeatureSink,
                                               
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterNumber,
                      QgsProcessingParameterField,
                       QgsProcessingParameterFile )

        
from .modules import Points as pts
from .modules import Raster as rst


class ViewshedPoints(QgsProcessingAlgorithm):

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OBSERVER_POINTS = 'OBSERVER_POINTS'
    DEM = 'DEM'

    OUTPUT = 'OUTPUT'

    OBSERVER_ID = 'OBSERVER_ID'

    RADIUS = 'RADIUS'
    RADIUS_FIELD = 'RADIUS_FIELD'
    RADIUS_IN_FIELD = 'RADIUS_IN_FIELD'
    
    OBS_HEIGHT = 'OBS_HEIGHT'
    OBS_HEIGHT_FIELD = 'OBS_HEIGHT_FIELD'

    TARGET_HEIGHT = 'TARGET_HEIGHT'
    TARGET_HEIGHT_FIELD = 'TARGET_HEIGHT_FIELD'
    
    AZIM_1_FIELD = 'AZIM_1_FIELD'
    AZIM_2_FIELD = 'AZIM_2_FIELD'
    
    ANGLE_UP_FIELD = 'ANGLE_UP_FIELD'
    ANGLE_DOWN_FIELD = 'ANGLE_DOWN_FIELD'
    
   # MOVE_TOP = 'MOVE_TOP'

    #OUTPUT_DIR = 'OUTPUT_DIR'

    

#    def help(self):
#        return False, 'http://zoran-cuckovic.github.io/senscape/help/points'
        
    
    def initAlgorithm(self, config):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

 
        self.addParameter(
            QgsProcessingParameterFeatureSource(
  
            self.OBSERVER_POINTS,
            self.tr('Observer location(s)'),
            [QgsProcessing.TypeVectorPoint]))
        
        self.addParameter(QgsProcessingParameterRasterLayer
                          (self.DEM,
            self.tr('Digital elevation model ')))
       
        self.addParameter(QgsProcessingParameterField(
            self.OBSERVER_ID,
            self.tr('Observer ids (leave unchanged to use feature ids)'),
            parentLayerParameterName = self.OBSERVER_POINTS,
            optional=True))
##
        self.addParameter( 	QgsProcessingParameterNumber(
            self.RADIUS,
            self.tr("Radius of analysis, meters"),
            QgsProcessingParameterNumber.Integer,
            defaultValue= 5000))
  
        self.addParameter(QgsProcessingParameterField(
            self.RADIUS_FIELD,
            self.tr('Field value for analysis radius'),
            parentLayerParameterName = self.OBSERVER_POINTS,
            optional=True))
        

        self.addParameter(QgsProcessingParameterNumber(
            self.OBS_HEIGHT,
            self.tr('Observer height, meters'),
            QgsProcessingParameterNumber.Double,
            defaultValue= 1.6))
        
        self.addParameter(QgsProcessingParameterField(
            self.OBS_HEIGHT_FIELD,
            self.tr('Field value for observer height'),
            parentLayerParameterName =self.OBSERVER_POINTS,
            optional=True))

        self.addParameter(QgsProcessingParameterNumber(
            self.TARGET_HEIGHT,
            self.tr('Target height, meters'),
            QgsProcessingParameterNumber.Double,
            defaultValue= 0.0))

        self.addParameter(QgsProcessingParameterField(
            self.TARGET_HEIGHT_FIELD,
            self.tr('Field value for target height, meters'),
            parentLayerParameterName =self.OBSERVER_POINTS,
            optional=True))
        
        self.addParameter(QgsProcessingParameterField(
            self.RADIUS_IN_FIELD,
            self.tr('Inner radius'),
            parentLayerParameterName = self.OBSERVER_POINTS,
            optional=True))
        
        self.addParameter(QgsProcessingParameterField(
            self.AZIM_1_FIELD,
            self.tr('Azimuth mask - start'),
            parentLayerParameterName = self.OBSERVER_POINTS,
            optional=True))
         
        self.addParameter(QgsProcessingParameterField(
            self.AZIM_2_FIELD,
            self.tr('Azimuth mask - end'),
            parentLayerParameterName = self.OBSERVER_POINTS,
            optional=True))
        
        self.addParameter(QgsProcessingParameterField(
            self.ANGLE_UP_FIELD,
            self.tr('Upper angle mask'),
            parentLayerParameterName = self.OBSERVER_POINTS,
            optional=True))
         
        self.addParameter(QgsProcessingParameterField(
            self.ANGLE_DOWN_FIELD,
            self.tr('Lower angle mask'),
            parentLayerParameterName = self.OBSERVER_POINTS,
            optional=True))
     
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')) )

    def shortHelpString(self):
        
        curr_dir = path.dirname(path.realpath(__file__))

        h = (f"""
            This is the first step for the visibility analysis. The result will be written as a geopackage file with standardised field names and reprojected to match the elevation model used (if needed).

            <h3>Parameters</h3>

            <ul>
                <li> <em>Observer IDs</em>: viewpoints can be assigned individual names or id numbers, stored in the associated table. Otherwise, internal ids will be used (sequential numbers).</li>
                <li> <em>Observer height</em>: in meters.</li>
                <li> <em>Target height</em>: height value to be added to all terrain areas checked for visibility from the observer point.</li>
                <li> <em>Radius of analysis</em>: maximum distance for visibility testing, in meters.</li>
            </ul>

            For other parameters, see <a href="http://www.zoran-cuckovic.from.hr/QGIS-visibility-analysis/help_qgis3.html">help online</a>
            
            If you find this tool useful, consider to :
                 
             <a href='https://ko-fi.com/D1D41HYSW' target='_blank'><img height='30' style='border:0px;height:36px;' src='{curr_dir}/kofi2.webp' /></a>
            
			<font size = "+3"> <b>&#9774;</b></font size>This GIS tool is intended for <b>peaceful use !
			""") 

        return h

    def processAlgorithm(self, parameters, context, feedback):

        # The first thing to do is retrieve the values of the parameters
        # entered by the user
        raster = self.parameterAsRasterLayer(parameters,self.DEM, context)
        Points_layer = self.parameterAsSource(parameters, self.OBSERVER_POINTS, context)

       
        observer_id = self.parameterAsString(parameters, self.OBSERVER_ID, context)
        
        observer_height = self.parameterAsDouble(parameters,self.OBS_HEIGHT, context)
        observer_height_field =  self.parameterAsString(parameters,self.OBS_HEIGHT_FIELD,context)
        
        radius = self.parameterAsDouble(parameters, self.RADIUS, context)
        radius_field = self.parameterAsString(parameters, self.RADIUS_FIELD, context)
        
        target= self.parameterAsDouble(parameters,self.TARGET_HEIGHT, context)
        target_field= self.parameterAsString(parameters,self.TARGET_HEIGHT_FIELD, context)
    
        radius_in = self.parameterAsString(parameters,self.RADIUS_IN_FIELD, context)
        azim1 = self.parameterAsString(parameters,self.AZIM_1_FIELD, context)
        azim2= self.parameterAsString(parameters,self.AZIM_2_FIELD, context)
        angle_down = self.parameterAsString(parameters,self.ANGLE_DOWN_FIELD , context)
        angle_up = self.parameterAsString(parameters,self.ANGLE_UP_FIELD, context)
    
        
    #    move = self.parameterAsRasterLayer(parameters,self.MOVE_TOP, context).source()

        
       # output_dir = self.getParameterValue(self.OUTPUT_DIR) 
        
        # convert meters to layer distance units
        # [this can be confusing when the module is used in a script,
        #  and it's 3.0 function ]
        #coef = QgsUnitTypes.fromUnitToUnitFactor(Qgis.DistanceMeters, dem.crs().mapUnits())
		
        #searchRadius = searchRadius * coef
    
        
        if raster.crs().mapUnits() != 0 :
            err= " \n ****** \n ERROR! \n Raster data has to be projected in a metric system!"
            feedback.reportError(err, fatalError = True)
            raise QgsProcessingException(err)

        if  round(abs(raster.rasterUnitsPerPixelX()), 2) !=  round(abs(raster.rasterUnitsPerPixelY()),2):
            
            err= (" \n ****** \n ERROR! \n Raster pixels are irregular in shape " +
                  "(probably due to incorrect projection)!")
            feedback.reportError(err, fatalError = True)
            raise QgsProcessingException(err)
      
        points = pts.Points(Points_layer,
                            crs = Points_layer.sourceCrs(),
                            project_crs = raster.crs()) 

        points.clean_parameters( observer_height, radius,
                           z_targ = target ,
                           field_ID = observer_id,
                           field_zobs = observer_height_field,
                           field_ztarg= target_field,
                           field_radius= radius_field, 
                           field_radius_in=radius_in,
                        field_azim_1 = azim1,
                        field_azim_2 = azim2,
                        field_angle_down = angle_down,
                        field_angle_up = angle_up)
                           #folder = output_dir)
        
##        if success != 0 :
##            raise QgsProcessingException(
##                self.invalidSinkError(parameters, self.OUTPUT))
        
           # "Duplicate IDs!", str(success))

        if not len(points.pt):
            err= " \n ****** \n ERROR! \n No points were found, possibly a projection error!"
            feedback.reportError(err, fatalError = True)
            raise QgsProcessingException(err)

                
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                context,
                            points.field_defs(), 
                            Points_layer.wkbType(),
                            raster.crs()) # attention ! REPROJECTED    

        for f in points.return_points():
            sink.addFeature(f, QgsFeatureSink.FastInsert)
        
        


        #self.outputs[0].description = path.basename(Output)[:-4]
        
        return {self.OUTPUT: dest_id}


        
    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'createviewpoints'
    
    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr("Create viewpoints")
    
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
        return 'Create viewpoints'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        #return ViewshedPoints() NORMALLY
        return type(self)()
