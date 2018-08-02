from PyQt5.QtCore import QCoreApplication
from qgis.core import *
import gdal
import numpy as np

from os import path

from . import visibility as ws

#buffer modes
SINGLE = 0
ADD = 1
MIN = 2
MAX = 3
# ------------------------------------------

"""
This class handles input and output of raster data.
It doesn't do any calculations besides combining analysed patches. 
"""

class Raster:

    
    def __init__(self, raster, output=None, crs=None):
	
		
        gdal_raster=gdal.Open(raster)

       
        self.crs = crs if crs else gdal_raster.GetProjection()
        
        self.rst = gdal_raster #for speed, keep open raster ?
                        
        # size is y first, like numpy
        self.size = (gdal_raster.RasterYSize, gdal_raster.RasterXSize)
           
    
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

        raster_y_min = raster_y_max - self.size[0] * self.pix
        raster_x_max = raster_x_min + self.size[1] * self.pix

        
##        xsize = gdalData.RasterXSize 
##        ysize = gdalData.RasterYSize 
        
        self.extent = [raster_x_min, raster_y_min, 
                       raster_x_max, raster_y_max]

        self.min, self.max = gdal_raster.GetRasterBand(1
                            ).GetStatistics(True, True)[:2]

         # Get raster statistics
##        srcband = gdalData.GetRasterBand(1)
##
##
##        raster_max= srcband.GetMaximum()
##        raster_min = srcband.GetMinimum()
##
##        nodata = srcband.GetNoDataValue()
##
##        data_type =  srcband.DataType

        """
        NP2GDAL_CONVERSION = {
          "uint8": 1,
          "int8": 1,
          "uint16": 2,
          "int16": 3,
          "uint32": 4,
          "int32": 5,
          "float32": 6,
          "float64": 7,
          "complex64": 10,
          "complex128": 11,
        }

        """

        self.output = output

        self.mode = SINGLE
        

    def pixel_coords (self, x, y):
        
        x_min = self.extent[0]; y_max = self.extent[3]
        return (int((x - x_min) / self.pix),
                int((y_max - y) / self.pix)) #reversed !
    

     

    """
    This is the largest window, used for all analyses.
    Smaller windows are slices of this one.

    [ theoretically,window should be a subclass,
    but we can have only one window at a time ...]

    Buffer mode: the method for combining results (summing up or otherwise).
    By default, the mode is 0: no summing up
    
    Buffer size (self.result) is the same size as the entire array
    [ should be done in chunks for very large arrays - to implement ...]
    """

    def set_master_window (self, radius,
                           size_factor = 1,
                           curvature=False,
                           refraction =0,
                           background_value=0,
                           pad=False):           
        
        
        self.radius = radius
        radius_pix = int(radius/self.pix)
        self.radius_pix = radius_pix
        
        full_size = radius_pix *2 +1
        self.window = np.zeros((full_size, full_size))
        self.initial_value=background_value
        self.pad= pad
        
        
        self.mx_dist = self.distance_matrix()

        self.error_matrices = ws.error_matrix( radius_pix, size_factor)

        
        if curvature:
            self.curvature =  self.curvature_matrix(refraction)
        else:
            self.curvature = 0


    """
    Create the output file in memory and determine the mode of combining results
    (addition or min/max)

    TODO : deal with large files
    """
    def set_buffer (self, mode):

        if mode > 0 :
            self.result = np.zeros(self.size)

            # for summing up we need zeros,
            # for min/max we need no_data
            if mode > 1: self.result [:] = np.nan

            self.mode = mode   
        

    """
    Name is self-explanatory... Divide with pixel size if needed.
    Diameter is expressed as half of the major axis plus half of the minor:
    this should work best for moderate latitudes.
    """

    """
    Model vertical drop from a plane to spherical surface (of the Earth)
    Note that it has to be multiplied with pixel size to get usable values

    """
    def get_curvature_earth (self):

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

        
    def curvature_matrix(self, refraction=0):
    
        dist_squared = self.distance_matrix(squared=True)
        # all distances are in pixels in doViewshed module !!
        # formula is  squared distance / diam_earth 
        # need to divide all with pixel size (squared !!)
        D = self.get_curvature_earth() / (self.pix **2)
            
        return (dist_squared / D) * (1 - refraction) 

 
    """
    TODO ....
    """
    def set_mask (self, mask):

        if mask.shape == self.window.shape: self.mask = mask
        else : pass

    """
    Return a map of distances from the central pixel.
    Attention: these are pixel distances, not geographical !
    (to convert to geographical distances: multiply with pixel size)
    """
    def distance_matrix (self, squared=False):

        r = self.radius_pix
        window = self.window.shape[0]
        
        temp_x= ((np.arange(window) - r) ) **2
        temp_y= ((np.arange(window) - r) ) **2

        if not squared:
            return np.sqrt(temp_x[:,None] + temp_y[None,:])
        # squared values
        else: return temp_x[:,None] + temp_y[None,:]

    """
    Extract a quadrangular window from the raster file.
    Observer point (x,y) is always in the centre.

    Upon opening a window, all parameters regarding its size and position are
    registered in the Raster class instance - and reused for writing results
 
    """
    def open_window (self, pixel_coord):

        rx = self.radius_pix
        x, y = pixel_coord

        #NONSENSE !!there can be no smaller window than the master window (unless cropped)
        #to place smaller windows inside the master window
        diff_x = self.window.shape[1] - (rx *2 +1)
        diff_y =  self.window.shape[0] - (rx *2 +1)

        if x <= rx:  #cropping from the front
            x_offset =0
            x_offset_dist_mx = (rx - x) + diff_x
        else:               #cropping from the back
            x_offset = x - rx
            x_offset_dist_mx= 0

                           
        x_offset2 = min(x + rx +1, self.size[1]) #could be enormus radius, so check both ends always
        
        if y <= rx:
            y_offset =0
            y_offset_dist_mx = (rx - y) + diff_y
        else:
            y_offset = y - rx
            y_offset_dist_mx= 0

        y_offset2 = min(y + rx + 1, self.size[0] )

        window_size_y = y_offset2 - y_offset
        window_size_x = x_offset2 - x_offset

        self.window_slice = np.s_[y_offset : y_offset + window_size_y,
                                  x_offset : x_offset + window_size_x ]
        
        in_slice_y = (y_offset_dist_mx, y_offset_dist_mx +  window_size_y)
        in_slice_x = (x_offset_dist_mx , x_offset_dist_mx + window_size_x)

        self.inside_window_slice = [in_slice_y, in_slice_x]

        self.gdal_slice = [x_offset, y_offset, window_size_x, window_size_y]

        
        self.window [:]=self.initial_value 
        
        self.window[ slice(*in_slice_y), slice(*in_slice_x)] = \
                         self.rst.ReadAsArray(*self.gdal_slice ).astype(float)

        if isinstance(self.curvature, np.ndarray):
            
            self.window[
                slice(*in_slice_y), slice(*in_slice_x)] -= self.curvature[
                slice(*in_slice_y), slice(*in_slice_x)]
        # there is a problem with interpolation:
        # if the analysis window stretches outside raster borders
        # the last row/column will be interpolated with the fill value
        # the solution is to copy the same values or to catch these vaules (eg. by initialising to np.nan)
        if self.pad:
            if x_offset_dist_mx:
                self.window[:,in_slice_x[0] -1] = self.window[:,in_slice_x[0]]
            # slice[:4] will give indices 0 to 3, so we need -1 to get the last index!
            if x + rx + 1 > self.size[1]:
                self.window[:,in_slice_x[1] ] =  self.window[:,in_slice_x[1] -1 ]

            if y_offset_dist_mx:
                self.window[in_slice_y[0] -1,:] = self.window[in_slice_y[0],:]

            if y + rx + 1 > self.size[0]:
                self.window[in_slice_y[1] , : ] = self.window[in_slice_y[1] -1, : ]
        
##        self.offset = (x_offset, y_offset)
##        self.win_offset= (x_offset_dist_mx, y_offset_dist_mx)
##        self.win_size = (window_size_x, window_size_y)

    """
    reads entire raster
    """
    def open_raster (self):
        self.raster = self.rst.ReadAsArray().astype(float)
        return self.raster
        
    """
    Insert a numpy matrix to the same place where data has been extracted.
    Data can be added-up, or chosen from highest/lowest values.
    All parameteres are copied from class properties
    because only one window is possible at a time.
    """
    def add_to_buffer(self, in_array):

        y_in = slice(*self.inside_window_slice[0])
        x_in = slice(*self.inside_window_slice[1])

        m = self.result [self.window_slice]
        m_in = in_array [y_in, x_in]
  

        if self.mode == 1: m += m_in
            
        else:
            if self.mode == 2: operator = np.less
            elif self.mode == 3: operator = np.greater
            
            mask = operator( m_in, m)
            #there is a problem to initialise a comparison without knowing min/max values
            # nan will always give False in any comarison
            # so make a trick with isnan()...
            mask[np.isnan(m)]= True

            m[mask]= m_in[mask]
            
            
            #np.where(self.result [self.window_slice] < in_array [self.inside_window_slice],
            #         in_array [self.inside_window_slice], self.result [self.window_slice])      
            

    """
    TODO : a trick to work on very large arrays [mode = cumulative_lage]
    e.g. read a window from a gdal raster, sum, write back

    TODO : tidy up writing directly to raster file (without buffer)
     - data = self.result
     - slices = self.slices
       
    """
    def write_result(self, file_name = None,
                     fill = np.nan, no_data = np.nan,
                     dataFormat = gdal.GDT_Float32):

        

        if not file_name: file_name = self.output

        driver = gdal.GetDriverByName('GTiff')
        ds = driver.Create(file_name, self.size[1], self.size[0], 1, dataFormat)
        ds.SetProjection(self.crs)
        ds.SetGeoTransform(self.rst.GetGeoTransform())

        ds.GetRasterBand(1).Fill(fill)
        ds.GetRasterBand(1).SetNoDataValue(no_data)

##        #cumulative : same size as original array
##        if self.mode == 'cumulative':  ds.GetRasterBand(1).WriteArray(self.result)
##
##        else:
        
        
        if self.mode == 0 :#in place writing

            try:
                y_in = slice(*self.inside_window_slice[0])
                x_in = slice(*self.inside_window_slice[1])
                #for writing gdal takes only x and y offset (1st 2 values of self.gdal_slice) 
                ds.GetRasterBand(1).WriteArray(in_array [ y_in, x_in ],
                                           *self.gdal_slice[:2] )
            except: # for entire raster             
                ds.GetRasterBand(1).WriteArray(self.result )
        #all modes > 0 operate on a copy of the raster
        else:   
            ds.GetRasterBand(1).WriteArray(self.result )

            
       
            
            #self.offset[0], self.offset[1])     

        ds = None

        

	  

    
        

