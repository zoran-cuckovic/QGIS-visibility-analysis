# -*- coding: utf-8 -*-

"""
/***************************************************************************
 test_processing
                                 A QGIS plugin
 uuu
                              -------------------
        begin                : 2017-02-27
        copyright            : (C) 2017 by hhhh
        email                : na
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

__author__ = 'hhhh'
__date__ = '2017-02-27'
__copyright__ = '(C) 2017 by hhhh'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from PyQt4.QtCore import QSettings
from qgis.core import QgsVectorFileWriter

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import (ParameterRaster,
                                        ParameterVector,
                                        ParameterBoolean,
                                        ParameterString,
                                        ParameterSelection)
from processing.core.outputs import OutputRaster
from processing.tools import dataobjects, vector


class viewshed_binary(GeoAlgorithm):
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
        
## optional param
##        self.addParameter(ParameterString(self.RADIUS,
##                                          self.tr("SOME MOCK PARAMETER"),
##                                                    '', optional=True)) 
        # We add a vector layer as output
        self.addOutput(OutputRaster(self.OUTPUT_RASTER,
            self.tr('Output layer with selected features')))

##    NEW ?
##                self.addParameter(ParameterSelection(self.RTYPE,
##                                             self.tr('Output raster type'),
##                self.TYPE, 5))

    def processAlgorithm(self, progress):
	
	# is it better to import here or on top ?
        import gdal
        from qgis.core import QgsRectangle
        import numpy as np
        
        from ViewshedAnalysis import doViewshed as ws
        from ViewshedAnalysis import Points as pts

        # The first thing to do is retrieve the values of the parameters
        # entered by the user
        Raster_path = self.getParameterValue(self.INPUT_DEM)
        Points_path = self.getParameterValue(self.INPUT_POINTS)
        
        Output = self.getOutputValue(self.OUTPUT_RASTER)

        observer_height = float(self.getParameterValue(self.OBS_HEIGHT))
        radius = float(self.getParameterValue(self.RADIUS))
        
		
	## THIS IS NOT GOOD : this function is the same for different
        ## types of analysis (looping through points) - will be transfered to doViewshed module

        ## same for Earth curvature etc...
        
        
        # 1 open raster and read basic parameters
        r= gdal.Open(Raster_path)

        projection= r.GetProjection() 

        gt= r.GetGeoTransform()

        #pixels must be square !!
        # will not give useful results if pixels are rectangular
        pix = gt[1] 

        raster_x_min = gt[0]
        raster_y_max = gt[3] # it's top left y, so maximum!

        raster_y_size = r.RasterYSize
        raster_x_size = r.RasterXSize

        raster_y_min = raster_y_max - raster_y_size * pix
        raster_x_max = raster_x_min + raster_x_size * pix

        #extent, to filter points
        ext = QgsRectangle(raster_x_min, raster_y_min,  raster_x_max, raster_y_max)

        #output matrix = entire raster
        matrix_final = np.zeros ( (raster_y_size, raster_x_size) )

        # 2  convert points shapefile into a dictionary
        # supplementary keyword arguments can be used :
        # z_targ : target height, 
         # field_ID : name of table filed that holds IDs of points,
         # field_zobs : name of table filed that holds  observer height - for each point
         # field_ztarg : same for target height 
         # field_radius : same for analysis radius
         
        p = pts.Points()
        p.point_dict(Points_path, ext, pix, observer_height, radius)

        points = p.pt

        # 3 create distance and error matrix
        #  >>  an additional matrix needs to be made for  Earth curvature (not implemented here!)

        radius_float = radius/pix
        radius_pix = int(radius_float)

        full_window_size = radius_pix *2 + 1
         
        #  pixel distances for the entire viewshed area
        temp_x= ((np.arange(full_window_size) - radius_pix) ) **2
        temp_y= ((np.arange(full_window_size) - radius_pix) ) **2
        mx_dist = np.sqrt(temp_x[:,None] + temp_y[None,:])

        # mask corners for circular result (othervise the calculation is on a square slice
        mask_circ = mx_dist [:] > radius_float 

        # we draw all lines beforehand (indices), and save their offsets from pixel centres (errors)
        # mask is used to filter the least error instances for each pixel
        indices, error_indices, errors, mask = ws.error_matrix(radius_pix)

        for p_id in points:
                x,y= points[p_id]["x_pix"],  points[p_id]["y_pix"]

                
                #gives full window size by default
                data, cropping = ws.dem_chunk ( x, y, radius_pix, r) 

                #parameters to place correctly the extracted data window
                (x_offset, y_offset,
                         x_offset_dist_mx, y_offset_dist_mx,
                         window_size_x, window_size_y) = cropping
                         
                  # take absolute height immediately
                 #observer is in the center of the matrix (positoin = radius in pixels)
                z_abs =points[p_id]["z"] + data [radius_pix,radius_pix] 

                # caulculate angular height
                data = (data - z_abs) / mx_dist
                
                v = ws.viewshed_raster("Binary", data, errors, mask, indices, error_indices)
                # additional keyword arguments : target_matrix = None (all same as elevation matrix, 
                # but with target height added to the entire raster), algorithm =1 (0 for non interpolated
           # calculation, 1 for normal) 
           
                v [mask_circ] = 0 #make it circular
                
                #clumsy... place correctly the analysed window inside the raster
                matrix_final [ y_offset : y_offset + window_size_y,
                                 x_offset : x_offset + window_size_x ] += v [
                                 y_offset_dist_mx : y_offset_dist_mx +  window_size_y,
                                 x_offset_dist_mx : x_offset_dist_mx + window_size_x] 


        # write output
        driver = gdal.GetDriverByName( 'GTiff' )
          
        c = driver.CreateCopy(Output, r , 0) #WHAT IS 0 ? : "strict or not" default =1

        c.GetRasterBand(1).WriteArray(matrix_final)

        c = None

        
