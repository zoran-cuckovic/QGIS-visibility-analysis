# -*- coding: utf-8 -*-

"""
/***************************************************************************
ViewshedAnalysis
A QGIS plugin
begin : 2013-05-22
copyright : (C) 2013 by Zoran Čučković
email : /
***************************************************************************/

/***************************************************************************
* *
* This program is free software; you can redistribute it and/or modify *
* it under the terms of the GNU General Public License as published by *
* the Free Software Foundation version 2 of the License, or *
* any later version. *
* *
***************************************************************************/
"""

from os import path

from PyQt5.QtCore import QCoreApplication

from qgis.core import (QgsProcessing,
                       
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,

                       #individual files
                       QgsProcessingOutputRasterLayer,

                       
                      QgsProcessingParameterBoolean,
                      QgsProcessingParameterNumber,
                      QgsProcessingParameterField,
                       QgsProcessingParameterEnum ,
                      QgsProcessingParameterFile,

                      QgsProcessingException,

                       QgsMessageLog)

from processing.core.ProcessingConfig import ProcessingConfig

from .modules import visibility as ws
from .modules import Points as pts
from .modules import Raster as rst

import numpy as np
import time

class ViewshedRaster(QgsProcessingAlgorithm):

    DEM = 'DEM'
    OBSERVER_POINTS = 'OBSERVER_POINTS'
    
    USE_CURVATURE = 'USE_CURVATURE'
    REFRACTION = 'REFRACTION'
    PRECISION = 'PRECISION'
    ANALYSIS_TYPE = 'ANALYSIS_TYPE'
    OPERATOR = 'OPERATOR'
    OUTPUT = 'OUTPUT'
   

    PRECISIONS = ['Coarse','Normal', 'Fine']

   
    TYPES = ['Binary viewshed', 'Depth below horizon','Horizon' ]
#              'Horizon - intermediate', 'Projected horizon']

  
    OPERATORS = [ 'Addition', "Minimum", "Maximum"]

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config):

        self.addParameter(QgsProcessingParameterEnum(
            self.ANALYSIS_TYPE,
            self.tr('Analysis type'),
            self.TYPES, defaultValue=0))

        self.addParameter(
            QgsProcessingParameterFeatureSource(
  
            self.OBSERVER_POINTS,
            self.tr('Observer location(s)'),
            [QgsProcessing.TypeVectorPoint]))

        self.addParameter(QgsProcessingParameterRasterLayer
                          (self.DEM,
            self.tr('Digital elevation model ')))


        self.addParameter(QgsProcessingParameterBoolean(
            self.USE_CURVATURE,
            self.tr('Take in account Earth curvature'),
            False))
        self.addParameter(QgsProcessingParameterNumber(
            self.REFRACTION,
            self.tr('Atmospheric refraction'),
            QgsProcessingParameterNumber.Double,
            defaultValue = 0.13, minValue= 0, maxValue= 1))
        
        
##        self.addParameter(QgsProcessingParameterEnum (
##            self.PRECISION,
##            self.tr('Algorithm precision'),
##            self.PRECISIONS,
##            defaultValue=1))

        self.addParameter(QgsProcessingParameterEnum (
            self.OPERATOR,
            self.tr('Combining multiple outputs'),
            self.OPERATORS,
            defaultValue=0))

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
            self.tr("Output file")))

    def shortHelpString(self):
        
        curr_dir = path.dirname(path.realpath(__file__))
        h = (f"""
            Produces a visibility map where each observer point on a terrain model. The output can be:
            <ul>
                <li> Binary viewshed: visible/not visible (1/0).</li>
                <li> Depth below horizon: height that each location should attain in order to become visible.</li>
                <li> Horizon: outer edges of a viewshed. </li>
            </ul>

            Terrain model used should be in the same projection system as viewpoints file (preferably the one used in "Create viewpoints" routine).
            
            When multiple observer points are used, individual viewsheds will be combined according to the Combinig multiple ouptuts option.
          
            <h3>Parameters</h3>

            <ul>
                <li> <em>Observer locations</em>: viewpoints created by the "Create viewpoints" routine.</li>
                <li> <em>Digital elevation model</em>: DEM in the same projection system as viewpoints file.</li>
            </ul>

            For more see <a href="http://zoran-cuckovic.github.io/QGIS-visibility-analysis/help_qgis3.html">help online</a>.
            
            If you find this tool useful, consider to :
                 
             <a href='https://ko-fi.com/D1D41HYSW' target='_blank'><img height='30' style='border:0px;height:36px;' src='{curr_dir}/kofi2.webp' /></a>
            
			 <b>This GIS tool is intended for peaceful use !</b>
			<img height='80' style='border:0px;height:36px;' src='{curr_dir}/ukraine.png'/>
			
			""") 

        return h            

    #---------- not working ---------------- 
    def helpUrl(self):
        return 'https://landscapearchaeology.org/QGIS-visibility-analysis/'
    # for local file : QUrl.fromLocalFile(os.path.join(helpPath, '{}.html'.format(self.grass7Name))).toString()
        

    def processAlgorithm(self, parameters, context, feedback):


        raster = self.parameterAsRasterLayer(parameters,self.DEM, context)
        observers = self.parameterAsSource(parameters,self.OBSERVER_POINTS,context)

        
        useEarthCurvature = self.parameterAsBool(parameters,self.USE_CURVATURE,context)
        refraction = self.parameterAsDouble(parameters,self.REFRACTION,context)
        precision = 1#self.parameterAsInt(parameters,self.PRECISION,context)
        analysis_type = self.parameterAsInt(parameters,self.ANALYSIS_TYPE, context)
        operator = self.parameterAsInt(parameters,self.OPERATOR,context) +1       

        output_path = self.parameterAsOutputLayer(parameters,self.OUTPUT,context)
 

        #getTempFilenameInTempFolder(
            #self.name + '.' + self.getDefaultFileExtension(alg)

            
        # output_dir = self.getOutputValue(self.OUTPUT_DIR)

        # convert meters to layer distance units
        # [this can be confusing when the module is used in a script,
        #  and it's 3.0 function ]
        #coef = QgsUnitTypes.fromUnitToUnitFactor(Qgis.DistanceMeters, dem.crs().mapUnits())
		
        #searchRadius = searchRadius * coef

# --------------- verification of inputs ------------------

        raster_path= raster.source()
        dem = rst.Raster(raster_path, output=output_path)
        # TODO: ADD MORE TESTS (raster rotated [projections ??], rectnagular pixels [OK?]
                         
        points = pts.Points(observers)
           
        miss = points.test_fields(["observ_hgt", "radius"])
        
        if miss:
            err= " \n ****** \n ERROR! \n Missing fields: \n" + "\n".join(miss)
            feedback.reportError(err, fatalError = True)
            raise QgsProcessingException(err)

        miss_params = points.test_fields(["radius_in", "azim_1", "azim_2"])

        points.take(dem.extent, dem.pix)

        if points.count == 0:
            err= "  \n ******* \n ERROR! \n No viewpoints in the chosen area!"
            feedback.reportError(err, fatalError = True)
            raise QgsProcessingException(err )

        elif points.count == 1:
            operator=0
            live_memory = False

        else:
            live_memory = ( (dem.size[0] * dem.size[1]) / 1000000 <
                           float(ProcessingConfig.getSetting(
                               'MEMORY_BUFFER_SIZE')))
        
        dem.set_buffer(operator, live_memory = live_memory)
            
        # prepare the output raster
        if not live_memory:
            # !! we cannot use compression because of a strange memory bloat 
            # produced by GDAL
            dem.write_output(output_path, compression = False)

        pt = points.pt #this is a dict of obs. points

# --------------------- analysis ----------------------   

        start = time.process_time()
        report = []

        
        #for speed and convenience, use maximum sized window for all analyses
        
        dem.set_master_window(points.max_radius,
                            size_factor = precision ,
                            background_value=0,
                            pad = precision>0,
                            curvature =useEarthCurvature,
                            refraction = refraction )
        


        cnt = 0
       
        for id1 in pt :     

            if feedback.isCanceled():  break
          

            matrix_vis = ws.viewshed_raster (analysis_type, pt[id1], dem,
                                          interpolate = precision > 0)

            # must set the mask before writing the result!
            mask = [pt[id1]["radius"]]

            inner_radius_specified = "radius_in" not in miss_params
            if inner_radius_specified:
                mask += [ pt[id1]["radius_in"] ]

            if  "azim_1" not in miss_params and  "azim_2" not in miss_params:
                if not inner_radius_specified:
                    mask += [ None ]
                mask += [ pt[id1]["azim_1"], pt[id1]["azim_2"] ]
                print (mask)

            dem.set_mask(*mask)

            r = dem.add_to_buffer (matrix_vis, report = True)
            
            
            report.append([pt[id1]["id"],*r])

            cnt += 1

            feedback.setProgress(int((cnt/points.count) *100))
            if feedback.isCanceled(): return {}
                
       
        if live_memory: dem.write_output(output_path)
        
        dem = None

        txt = ("\n Analysis time: " + str(
            round((time.process_time() - start
                                    ) / 60, 2)) + " minutes."
              " \n.      RESULTS \n Point_ID, visible pixels, total pixels" )
        
        for l in report:
            txt = txt + "\n" + ' , '.join(str(x) for x in l)

        # TODO : write to Results viewer !!
        QgsMessageLog.logMessage( txt, "Viewshed info")
          
        results = {}
        
        for output in self.outputDefinitions():
            outputName = output.name()
                
            if outputName in parameters :
                results[outputName] = parameters[outputName]
                results["OUTPUT"] = output_path
    
        return results

    
    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """

        return 'viewshed'
    
    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return 'Viewshed'
    
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
