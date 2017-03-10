# -*- coding: utf-8 -*-

"""
/***************************************************************************
 TestProcessing
                                 A QGIS plugin
 Some descr
                              -------------------
        begin                : 2017-03-10
        copyright            : (C) 2017 by some
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

__author__ = 'some'
__date__ = '2017-03-10'
__copyright__ = '(C) 2017 by some'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from PyQt4.QtCore import QSettings
from qgis.core import QgsVectorFileWriter

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import (ParameterRaster,
                                        ParameterVector,
                                        ParameterBoolean,
                                        ParameterString,
                                        ParameterSelection )
from processing.core.outputs import  OutputRaster ###OutputVector
from processing.tools import dataobjects, vector


class ViewshedBinary(GeoAlgorithm):
    """This is an example algorithm that takes a vector layer and
    creates a new one just with just those features of the input
    layer that are selected.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the GeoAlgorithm class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT_POINTS = 'INPUT_POINTS'
    INPUT_DEM = 'INPUT_RASTER'

    OUTPUT_RASTER = 'OUTPUT_RASTER'

    RADIUS = 'RADIUS'
    OBS_HEIGHT = 'OBS_HEIGHT'
    
    def defineCharacteristics(self):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # The name that the user will see in the toolbox
        self.name = 'Binary viewshed'

        # The branch of the toolbox under which the algorithm will appear
        self.group = 'Visibility'

        # We add the input vector layer. It can have any kind of geometry
        # It is a mandatory (not optional) one, hence the False argument
        self.addParameter(ParameterVector(self.INPUT_POINTS,
            self.tr('Observation points'), [ParameterVector.VECTOR_TYPE_ANY], False))
			
		
        self.addParameter(ParameterRaster(self.INPUT_DEM,
            self.tr('Elevation model (DEM)'),  False))

        self.addParameter(ParameterString(self.RADIUS,
                                          self.tr("Radius of analysis"),
                                                    '5000', False)) 

        self.addParameter(ParameterString(self.OBS_HEIGHT,
                                          self.tr("Observer height"),
                                                    '1.6', False))

        self.addOutput(OutputRaster(self.OUTPUT_RASTER,
                                    self.tr('Output layer')))


        
# optional param
#        self.addParameter(ParameterString(self.RADIUS,
#                                          self.tr("SOME MOCK PARAMETER"),
#                                                    '', optional=True)) 
        # We add a vector layer as output
      ##    NEW ?
##                self.addParameter(ParameterSelection(self.RTYPE,
##                                             self.tr('Output raster type'),
##                self.TYPE, 5))

    def processAlgorithm(self, progress):
        
	
	# is it better to import here or on top ?
        import gdal
        from qgis.core import QgsRectangle
        import numpy as np
        
        from .modules import doViewshed as ws
        from .modules import Points as pts
        from .modules import Raster as rst

        # The first thing to do is retrieve the values of the parameters
        # entered by the user
        Raster_path = self.getParameterValue(self.INPUT_DEM)
        Points_path = self.getParameterValue(self.INPUT_POINTS)
        
        Output = self.getOutputValue(self.OUTPUT_RASTER)


        observer_height = float(self.getParameterValue(self.OBS_HEIGHT))
        radius = float(self.getParameterValue(self.RADIUS))

        
        
                        
        dem = rst.Raster(Raster_path)
                        # crs=  layer.crs().toWkt() #I do not have layer object ??
                        # write_mode = 'cumulative', if cumulative
        
        
        points = pts.Points(Points_path, dem.extent, dem.pix, observer_height, radius) # and all other stuff ....

        if points.count >1: mode='cumulative'
        else: mode = None

    

        output_options=["Binary", mode]
        
	#will assign the result to dem class (?)	
        result =  ws.Viewshed (points, dem, 
                              output_options,
                              Target_points=None,
                              curvature=0, refraction=0, algorithm = 1)

        

        if mode == "cumulative":
            """

            
            Perhaps there could be problems when registered crs
            is not matching the one chosen in QGIS ??
            In 'Raster' class : self.crs = crs if crs else gdal_raster.GetProjection()
            so to override on can do Dem_raster.crs = ....
            """
            dem.write_raster(Output, result)
        else:
            dem.write_raster(Output, result, sliced = True)

        """
        Is this a good practice? dem object has been modified in ws.Viewshed routine.
        But there is no sense in putting viewshed algorithm in Raster class,
        it is also used for vectors (intervisibility). And it's a lot of code .. 

        """

        # write output
        #driver = gdal.GetDriverByName( 'GTiff' )
          
        #c = driver.CreateCopy(Output, r , 0) #WHAT IS 0 ? : "strict or not" default =1

        #c.GetRasterBand(1).WriteArray(matrix_final)

        #c = None
