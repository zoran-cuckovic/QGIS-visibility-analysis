from PyQt4.QtCore import *
from qgis.core import *
import gdal
import numpy as np

#import doViewshed
# this is circular import !! cannot do import dem_chunk

'''
This class handles input and output of raster data.
'''

class Raster:

    
    def __init__(self, raster, crs=None, write_mode=None):
	
		
        gdal_raster=gdal.Open(raster)
        
        
        # This is problematic : the idea is that the thing might work even with 
        # rasters not loaded in QGIS. But for those already loaded, it will override gdal crs. 
        # format has to be same (text string) ??
       
        self.crs = crs if crs else gdal_raster.GetProjection()
        
        self.rst = gdal_raster #for speed, keep open raster ?
                        
        self.mode= write_mode
        
        self.size = (gdal_raster.RasterXSize, gdal_raster.RasterYSize)
           
    
        #adfGeoTransform[0] /* top left x */
        #adfGeoTransform[1] /* w-e pixel resolution */
        #adfGeoTransform[2] /* rotation, 0 if image is "north up" */
        #adfGeoTransform[3] /* top left y */
        #adfGeoTransform[4] /* rotation, 0 if image is "north up" */
        #adfGeoTransform[5] /* n-s pixel resolution */

        gt=gdal_raster.GetGeoTransform()
        self.pix = gt[1] 
                
        raster_x_min = gt[0]
        raster_y_max = gt[3] # it's top left y, so maximum!

        raster_y_min = raster_y_max - self.size[1] * self.pix
        raster_x_max = raster_x_min + self.size[0] * self.pix

        
        self.extent = [raster_x_min, raster_y_min, 
                       raster_x_max, raster_y_max]
        


        self.window = None
        # numpy slices to place correctly windows
        self.window_slice = None
        self.in_window_slice = None

        #window  should be a subclass ??
        #but we can have only one window at a time, and it should be as fast as possible
        
        #def __init__(self, "window"):
        
        
        
        #
    def get_diameter_earth (self):

        crs= self.crs		
    
        start = crs.find("SPHEROID") + len("SPHEROID[")
        end = crs.find("]],", start) + 1
        tmp = crs[start:end].split(",")

        try:
                semiMajor = float(tmp[1])
                if not 6000000 < semiMajor < 7000000:
                        semiMajor = 6378137
        except:
                semiMajor = 6378137

        try:
                flattening = float(tmp[2])
                if not 296 < flattening < 301:
                        flattening = 298.257223563
        except:
                flattening = 298.257223563

        semiMinor = semiMajor - semiMajor / flattening
        
        return semiMajor + semiMinor
                
                
    def dem_window (self, x, y, radius_pix, square = True):

    
        if x <= radius_pix:  #cropping from the front
            x_offset =0
            x_offset_dist_mx = radius_pix - x
        else:               #cropping from the back
            x_offset = x - radius_pix
            x_offset_dist_mx= 0
                            
        x_offset2 = min(x + radius_pix +1, self.size[0]) #could be enormus radius, so check both ends always
            
        if y <= radius_pix:
            y_offset =0
            y_offset_dist_mx = radius_pix - y
        else:
            y_offset = y - radius_pix
            y_offset_dist_mx= 0

        y_offset2 = min(y + radius_pix + 1, self.size[1] )

        window_size_y = y_offset2 - y_offset
        window_size_x = x_offset2 - x_offset

        self.window_slice = np.s_[y_offset : y_offset + window_size_y,
                                  x_offset : x_offset + window_size_x ]


        self.inside_window_slice = np.s_[ y_offset_dist_mx : y_offset_dist_mx +  window_size_y,
                                          x_offset_dist_mx : x_offset_dist_mx + window_size_x]

        self.gdal_slice = [x_offset, y_offset, window_size_x, window_size_y]

        if square:
            full_size = radius_pix *2 +1
            self.window = np.zeros((full_size, full_size)) 
        
            self.window[ self.inside_window_slice] = \
                         self.rst.ReadAsArray(*self.gdal_slice ).astype(float)
        else:

            self.window = self.rst.ReadAsArray(x_offset, y_offset, window_size_x, window_size_y).astype(float)
        

##        self.offset = (x_offset, y_offset)
##        self.win_offset= (x_offset_dist_mx, y_offset_dist_mx)
##        self.win_size = (window_size_x, window_size_y)
                

##    def write_result(self, in_array):
##
##        if self.mode == 'cumulative':            
##            
##            (self.result [self.offset[1] :
##                      self.offset[1] + self.win_size[1],
##                      self.offset[0] :
##                      self.offset[0] + self.win_size[0] ]) += (
##                                    in_array [self.win_offset[1] :
##                                       self.win_offset[1] + self.win_size[1],
##                                       self.win_offset[0] :
##                                       self.win_offset[0] + self.win_size[0] ])
##        else: self.result = in_array

    """
    TODO : a trick to work on very large arrays [mode = cumulative_lage]
    e.g. read a window from a gdal raster, sum, write back
       
    """
    def write_raster(self, filePath, numpy_result,
                     sliced=False,
                     fill = np.nan, no_data = np.nan,
                     dataFormat = gdal.GDT_Float32):
        



        
            
        driver = gdal.GetDriverByName('GTiff')
        ds = driver.Create(filePath, self.size[0], self.size[1], 1, dataFormat)
        ds.SetProjection(self.crs)
        ds.SetGeoTransform(self.rst.GetGeoTransform())


        ds.GetRasterBand(1).Fill(fill)
        ds.GetRasterBand(1).SetNoDataValue(no_data)

##        #cumulative : same size as original array
##        if self.mode == 'cumulative':  ds.GetRasterBand(1).WriteArray(self.result)
##
##        else:
        if sliced:
            #for writing it takes only x and y offset (1st 2 values of self.gdal_slice) 
      
            ds.GetRasterBand(1).WriteArray(numpy_result[ self.inside_window_slice ],
                                           *self.gdal_slice[:2] )
            
        else:
            ds.GetRasterBand(1).WriteArray(numpy_result)
            #self.offset[0], self.offset[1])
        

        ds = None

	  

    
        

