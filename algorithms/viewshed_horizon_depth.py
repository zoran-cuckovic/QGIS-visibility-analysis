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

from PyQt5.QtCore import QCoreApplication

from plugins.processing.gui import MessageBarProgress

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


class HorizonDepth(QgsProcessingAlgorithm):

    DEM = 'DEM'
    OBSERVER_POINTS = 'OBSERVER_POINTS'
    
    USE_CURVATURE = 'USE_CURVATURE'
    REFRACTION = 'REFRACTION'
    PRECISION = 'PRECISION'
    OPERATOR = 'OPERATOR'
    OUTPUT = 'OUTPUT'
   

    PRECISIONS = ['Coarse','Normal', 'Fine']

    # not used yet
    OPERATORS = [ "Addition", "Minimum","Maximum"]

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config):

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
            self.tr('Atmoshpheric refraction'),
            1, 0.13, False, 0.0, 1.0))
        
        
##        self.addParameter(QgsProcessingParameterEnum (
##            self.PRECISION,
##            self.tr('Algorithm precision'),
##            self.PRECISIONS,
##            defaultValue=1))

        self.addParameter(QgsProcessingParameterEnum (
            self.OPERATOR,
            self.tr('Combining multiple outputs'),
            self.OPERATORS,
            defaultValue=1))

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
            self.tr("Output file")))


    def shortHelpString(self):

        h = ("""
             Calculate the depth at which lay invisible portions of a terrain, considerning theoretical horizon.

            <h3>Parameters</h3>

            <ul>
                <li> <em>Observer locations</em>: viewpoints created by the "Create viewpoints" routine.</li>
                <li> <em>Digital elevation model</em>: DEM in the same projection system as viepoints file (preferably the one used in "Create viewpoints" routine).</li>
                <li> <em>Combining multiple outputs</em>: filter for minimum or maximum values when combining multiple visibility models.</li>
            </ul>

            For more see <a href="http://www.zoran-cuckovic.from.hr/QGIS-visibility-analysis/help_qgis3.html">help online</a>.
        
            """)

        return h

    #---------- not working ---------------- 
    def helpUrl(self):
        return 'https://zoran-cuckovic.github.io/QGIS-visibility-analysis/help_qgis3.html'
    # for local file : QUrl.fromLocalFile(os.path.join(helpPath, '{}.html'.format(self.grass7Name))).toString()
        

    def processAlgorithm(self, parameters, context, feedback):


        raster = self.parameterAsRasterLayer(parameters,self.DEM, context)
        observers = self.parameterAsSource(parameters,self.OBSERVER_POINTS,context)

        
        useEarthCurvature = self.parameterAsBool(parameters,self.USE_CURVATURE,context)
        refraction = self.parameterAsDouble(parameters,self.REFRACTION,context)
        precision = 1#self.parameterAsInt(parameters,self.PRECISION,context)
        analysis_type = 1
        operator = self.parameterAsInt(parameters,self.OPERATOR,context) + 1       

        output_path = self.parameterAsOutputLayer(parameters,self.OUTPUT,context)
 

        raster_path= raster.source()
        dem = rst.Raster(raster_path, output=output_path)
                     
        points = pts.Points(observers)
       
        fields =["observ_hgt", "radius"]
        miss = points.test_fields(fields)
        
        if miss:
            err= " \n ****** \n ERROR! \n Missing fields: \n" + "\n".join(miss)
            feedback.reportError(err, fatalError = True)
            raise QgsProcessingException(err)

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

        #has to be assigned before write_outpur routine because the
        #operator variable determines raster background value [opaque ...]
        dem.set_buffer(operator, live_memory = live_memory)
            
        # prepare the output raster
        if not live_memory:
            dem.write_output(output_path) #, fill = np.nan) [not needed]


        pt = points.pt #this is a dict of obs. points


        start = time.clock(); report=[]

        
        #for speed and convenience, use maximum sized window for all analyses
        #this is not clear! should set using entire size, not radius !!
        dem.set_master_window(points.max_radius,
                            size_factor = precision ,
                            background_value=np.nan,
                            pad = precision>0,
                            curvature =useEarthCurvature,
                            refraction = refraction )
        

        cnt = 0
       
        for id1 in pt :

            

            if feedback.isCanceled():  break

               
            matrix_vis = ws.viewshed_raster (analysis_type, pt[id1], dem,
                                          interpolate = precision > 0)

            # the algorithm is giving angular difference
            matrix_vis *= - dem.mx_dist 
            matrix_vis[dem.radius_pix, dem.radius_pix ]=0
        

            # must set mask before writing the result!             
            dem.set_mask( pt[id1]["radius"])

            r = dem.add_to_buffer (matrix_vis, report = True)
            
            report.append([pt[id1]["id"],*r])


            cnt += 1

            feedback.setProgress(int((cnt/points.count) *100))
                
       
        if live_memory: dem.write_output(output_path)
        
        dem = None


        txt = ("\n Analysis time: " + str(
                            round( (time.clock() - start
                                    ) / 60, 2)) + " minutes."
              " \n.      RESULTS \n Point_ID, non-visible pixels, total pixels" )
        
        for l in report:
            txt = txt + "\n" + ' , '.join(str(x) for x in l)

        
        QgsMessageLog.logMessage( txt, "Viewshed info")
          
        results = {}
        
        for output in self.outputDefinitions():
            outputName = output.name()
                
            if outputName in parameters :
                results[outputName] = parameters[outputName]

    
        return results

    
    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """

        return 'horizon_depth'
    
    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Depth below horizon')
    
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
