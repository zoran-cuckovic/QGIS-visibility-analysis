# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 16:39:35 2020

@author: zcuckovi
"""
from os import path

from PyQt5.QtCore import QCoreApplication

from qgis.core import (QgsProcessing,
                       
                       QgsProcessingAlgorithm,
                       
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,

                       #individual files
                       QgsProcessingOutputRasterLayer,

                       
                      QgsProcessingParameterBoolean,
                      QgsProcessingParameterNumber,
                      
                       QgsProcessingParameterEnum ,
                      
                      QgsProcessingException,

                       QgsMessageLog)


from .modules import visibility as ws
from .modules import Raster as rst


class VisibilityIndex(QgsProcessingAlgorithm):

    DEM = 'DEM'
    OBSERVER_HEIGHT='OBSERVER_HEIGHT'
    
    RADIUS='RADIUS'
    DIRECTION='DIRECTION'
    INTERPOLATE = 'INTERPOLATE'
    SAMPLE = 'SAMPLE'
    
    OUTPUT = 'OUTPUT'

    USE_CURVATURE = 'USE_CURVATURE'
    REFRACTION='REFRACTION'


    SAMPLES = ['8 lines', '16 lines', '32 lines','64 lines']
    DIRECTIONS = ['Incoming views', 'Outgoing views']

    
    def __init__(self):
        super().__init__()

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def initAlgorithm(self, config):

        self.addParameter(QgsProcessingParameterRasterLayer
                          (self.DEM,
            self.tr('Digital elevation model ')))
        
        self.addParameter(QgsProcessingParameterNumber(
            self.RADIUS,self.tr("Radius of analysis, meters"),
            QgsProcessingParameterNumber.Integer, defaultValue= 3000))

        self.addParameter(QgsProcessingParameterNumber(
            self.OBSERVER_HEIGHT,
            self.tr('Observer height, meters'),
            QgsProcessingParameterNumber.Double,
            defaultValue= 1.6))
			

        self.addParameter(QgsProcessingParameterEnum (
            self.SAMPLE,
            self.tr('Sample'),
            self.SAMPLES,
            defaultValue=1))

        self.addParameter(QgsProcessingParameterEnum (
            self.DIRECTION,
            self.tr('Direction'),
            self.DIRECTIONS,
            defaultValue=0))
     
        
        self.addParameter(QgsProcessingParameterBoolean(
            self.INTERPOLATE,
            self.tr('Use height interpolation'), True))


        self.addParameter(QgsProcessingParameterBoolean(
            self.USE_CURVATURE,
            self.tr('Take in account Earth curvature'),
            False))
        self.addParameter(QgsProcessingParameterNumber(
            self.REFRACTION,
            self.tr('Atmoshpheric refraction'),
            QgsProcessingParameterNumber.Double,
            defaultValue = 0.13 , minValue= 0, maxValue= 1))

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
            self.tr("Output file")))
           

    def processAlgorithm(self, parameters, context, feedback):


        input_raster = self.parameterAsRasterLayer(parameters,self.DEM, context)
            
        obs_height = self.parameterAsDouble(parameters,self.OBSERVER_HEIGHT, context)
        
        radius = self.parameterAsDouble(parameters,self.RADIUS,context)
        
       
        interpolate = self.parameterAsBool(parameters, self.INTERPOLATE, context)
        
        sample = self.parameterAsInt(parameters,self.SAMPLE,context)
        # 8, 16, 32, 64 lines
        sample = 2 ** (3 + sample)
      
        direction = self.parameterAsInt(parameters,self.DIRECTION,context)
        
        output_path = self.parameterAsOutputLayer(parameters,self.OUTPUT,context)
        
        curvature = self.parameterAsBool(parameters, self.USE_CURVATURE, context)    
        refraction=self.parameterAsDouble(parameters,self.REFRACTION, context)
        
        
    
        
        # this code is replicated from Create points routine 
        if input_raster.crs().mapUnits() != 0 :
            err= " \n ****** \n ERROR! \n Raster data has to be projected in a metric system!"
            feedback.reportError(err, fatalError = True)
            raise QgsProcessingException(err)

        if  round(abs(input_raster.rasterUnitsPerPixelX()), 2) !=  round(
                abs(input_raster.rasterUnitsPerPixelY()),2):    
            err= (" \n ****** \n ERROR! \n Raster pixels are irregular in shape " +
                  "(probably due to incorrect projection)!")
            feedback.reportError(err, fatalError = True)
            raise QgsProcessingException(err)

        raster = rst.Raster(input_raster.source())
        
        raster.set_master_window(radius,
                                 curvature = curvature,
                                 refraction = refraction)

       
        out = ws.visibility_index(raster,
                                   obs_height,          
                                   sample=sample,
                                   direction = direction,
                                   interpolate = interpolate,
                                   feedback = feedback)

        # this is a hack : to initilise fill value
        # should not be necessary...
        raster.set_buffer()
        
        raster.result = out
        raster.write_output(output_path)
            

        return {self.OUTPUT: output_path}

    def name(self):
        
        return "visibilityindex"

    def displayName(self):
    
        return self.tr("Visibility index")
    
    def groupId(self):
        return 'Analysis'

    def group(self):
        return self.tr(self.groupId())
    
    
    def shortHelpString(self):
        curr_dir = path.dirname(path.realpath(__file__))

        h = (f"""
             Calculate the incoming/outgouing views for all terrain locations.

            <h3>Parameters</h3>

            <ul>
                <li> <em>Digital elevation model</em>: raster image projected in a metric coordinate system.</li>
                <li> <em>Observer height</em>: eye level above ground.</li>
                 <li> <em>Sample</em>: number of lines of sight per point.</li>
                 <li> <em>Direction</em>: map views to locations seen (incoming) or to the observer point (outgoing).</li>
            </ul>

            For more see <a href="http://www.zoran-cuckovic.from.hr/QGIS-visibility-analysis/help_qgis3.html">help online</a>.
        
            If you find this tool useful, consider to :
              
            <a href='https://ko-fi.com/D1D41HYSW' target='_blank'><img height='30' style='border:0px;height:36px;' src='{curr_dir}/kofi2.webp' /></a>
         
            
            This GIS tool is intended for <b>peaceful use !

            """) 

        return h


    def createInstance(self):
        #return VisibilityIndex() NORMALLY
        return type(self)()
