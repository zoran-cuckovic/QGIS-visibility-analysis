# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Viewshed Analysis
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


from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing, QgsProcessingException,
                       
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                        QgsProcessingParameterFeatureSink,QgsFeatureSink,
                       
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterNumber,
                  
                       QgsProcessingParameterFile,

                       QgsCoordinateTransform, QgsProject, QgsPoint, QgsPointXY )

import numpy as np 
       
from .modules import Points as pts
from .modules import Raster as rst


class MovePoints(QgsProcessingAlgorithm):

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OBSERVER_POINTS = 'OBSERVER_POINTS'
    INPUT_DEM = 'INPUT_RASTER'
    RADIUS = 'RADIUS'
    OUTPUT_VECTOR = 'OUTPUT_VECTOR'

       

    def help(self):
        return False, None
        
    
    def initAlgorithm(self, config):


        self.addParameter(
            QgsProcessingParameterFeatureSource(
  
            self.OBSERVER_POINTS,
            self.tr('Observer locations'),
            [QgsProcessing.TypeVectorPoint])) 
            
        self.addParameter(QgsProcessingParameterRasterLayer
                          (self.INPUT_DEM,
            self.tr('Digital elevation model')))
       
      
        self.addParameter( 	QgsProcessingParameterNumber(
            self.RADIUS,
            self.tr("Search radius, meters"),
            QgsProcessingParameterNumber.Integer,
            defaultValue= 300))
                
        self.addParameter(QgsProcessingParameterFeatureSink
                          (self.OUTPUT_VECTOR,
                        self.tr('Output points'),
                           type=QgsProcessing.TypeVectorPoint))

    def processAlgorithm(self, parameters, context, feedback):

        points_layer = self.parameterAsSource(parameters, self.OBSERVER_POINTS, context)        
        dem = self.parameterAsRasterLayer(parameters,self.INPUT_DEM, context)
        radius = self.parameterAsDouble(parameters, self.RADIUS, context)
        
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT_VECTOR,
                context,
                points_layer.fields(), 
                points_layer.wkbType(),
                points_layer.sourceCrs()) 
        
        r = rst.Raster(dem.source())
        pix = r.pix; half_pix = pix/2

        raster_x_min, raster_y_min, raster_x_max,raster_y_max = r.extent
                
        r.set_master_window(radius, background_value=r.min)
        win_size, _ = r.window.shape
        mask = r.mx_dist < radius/pix
              
        # this routine does *not* save reprojected coords, unlike create_points 
        # it only adjusts coords for the search within the raster (messy, but more useful...)              
        transf = QgsCoordinateTransform(points_layer.sourceCrs(), dem.crs() , QgsProject.instance()) 
        rev_transf = QgsCoordinateTransform( dem.crs(), points_layer.sourceCrs(), QgsProject.instance()) 

        for feat in points_layer.getFeatures():
        
            geom = feat.geometry()

            # try geom.transform(crsTransform)
            t = geom.asPoint()
            
            try: t = transf.transform(t)
            except:
                err= " \n ****** \n ERROR! \n Cannot reproject points to raster projection ! "
                feedback.reportError(err, fatalError = True)
                raise QgsProcessingException(err)

                              
            
            #raster_y_min = raster_y_max - raster_y_size * pix
            #raster_x_max = raster_x_min + raster_x_size * pix
            
            try: 
                # coords have been reprojected to raster system !
                r.open_window(r.pixel_coords(*t)) #converts to pixel indices
                
                r.window *= mask #eliminate distant corners (circular radius)
                
                
                #chunks are padded to be square (for viewsheds)
                # x, y is always in the centre 
                iy, ix=np.unravel_index( np.argmax(r.window),
                                         r.window.shape )
            
                # unravel is giving offsets inside the window,
                # we need to place it inside the entire raster
                x_off , y_off, win_x, win_y = r.gdal_slice
                # when the point is close to border, take into account window overlap!
                x_off -= win_size - win_x
                y_off -= win_size - win_y

                new_point = QgsPointXY (
                    (ix + x_off) * pix + raster_x_min + half_pix ,
                    raster_y_max - (iy + y_off) * pix  - half_pix )
                # ...crazy : transform needs QgsPointXY, while setGeometry needs QgsPoint !?
                # now go back to the original CRS (shenaningan : QgsPoint / QgsPointXY)
                feat.setGeometry(QgsPoint(rev_transf.transform (new_point)))
                
            except: pass # do not skip features out of bounds
            
            sink.addFeature(feat, QgsFeatureSink.FastInsert)
                
        return {self.OUTPUT_VECTOR: dest_id}


        
    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'movepoints'
    
    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Move points to higher elevation')
    
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
        return 'Helpers'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        
        return type(self)()
