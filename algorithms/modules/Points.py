from PyQt4.QtCore import *
from qgis.core import *
import ogr, gdal
import numpy as np

import doViewshed
# this is circular import !! cannot do import dem_chunk



class Points:


    # tu sve radnje!!!
    #assembly etc
    def __init__(self):
        self.pt={}
        self.crs = None
        self.max_radius = 0
        self.pix = 0
        

    def point_dict (self, shapefile, bounding_box, pix_size, z_obs,radius ,
                    z_targ=None, 
                spatial_index=None, field_ID = None,
                field_zobs = None, field_ztarg=None, field_radius=None):
    #layer = qgis layer,  bounding_box = QgsRectangle,   field_id= string)



        x_min = bounding_box.xMinimum() 
        y_max = bounding_box.yMaximum()
        

        pix= pix_size
        self.pix=pix

        radius_float = radius/pix
        self.max_radius = radius_float

        
        layer = QgsVectorLayer(shapefile, 'o', 'ogr')

        self.crs=layer.crs()

        # returns 0-? for indexes or -1 if doesn't exist
        if bool( layer.fieldNameIndex ("ID") + 1):
            ID_field = "ID"
        else: ID_field = None


        if not spatial_index: #for intersect, not very helpful ...?
            s_index = QgsSpatialIndex()
            for f in layer.getFeatures():  s_index.insertFeature(f)
            
        else: s_index = spatial_index

        
        feature_ids = s_index.intersects(bounding_box)

                  
        for fid in feature_ids:

            # next = to get feature
            # could be slow, but not critical... !?
            feat = layer.getFeatures(QgsFeatureRequest().setFilterFid(fid)).next()           

            geom = feat.geometry()
            t = geom.asPoint()
            
            id1 = feat[ID_field] if ID_field else feat.id() 

            x_geog, y_geog = t[0], t[1]

            z,zt,r = z_obs, z_targ, radius_float
           
            x = int((x_geog - x_min) / pix) # not float !
            y = int((y_max - y_geog) / pix) #reversed !
           
           
            #addition for possible field values. Defaults are always loaded above
            if field_zobs :
                try : z = float(feat[field_zobs])
                except: pass

            if field_ztarg:
                try : zt = float(feat[field_target])
                except: pass

            if field_radius:
                try :
                    r = float(feat[field_radius]) / pix
                    if r > self.max_radius : self.max_radius = r
                except: pass
            

            self.pt[id1]={"x_pix" : x, "y_pix":y,
                      "z":z , "z_targ":zt, "radius_float" : r,
                      "x_geog" :x_geog, "y_geog": y_geog}              
     

    
       # self.max_radius = max(x, key=lambda i: x[i])



    def search_top_z (self, search_radius, raster_path):
        """
        Find the highest point in a perimeter around each observer point.
        Probably a better option is to make a separate loop/function for all points
        before making viewsheds...
        
        TO BE REMOVED TO A SEPARATE SCRIPT : this is not a good practice (we do not know the
        position of observer points !)
        """
        gdal_raster = gdal.Open(raster_path)


##        raster_y_size = gdal_raster.RasterYSize
##        raster_x_size = gdal_raster.RasterXSize

        pix = gdal_raster.GetGeoTransform()[1]
    #raster_y_min = raster_y_max - raster_y_size * pix
    #raster_x_max = raster_x_min + raster_x_size * pix

        for key in self.pt:
                     
            pt_x, pt_y = self.pt[key]["x_pix"], self.pt[key]["y_pix"]

            #chunks are padded to be square (for viewsheds)
            # so initialise borders to some impossible value ... should work ?

            dem, cropping = doViewshed.dem_chunk(pt_x, pt_y, search_radius,
                                                  gdal_raster, square = False)

            off_x, off_y = cropping[0:2]
            #we are interested only in offsets from the beginning
            #local_x = search_radius - local_off_x
            #local_y = search_radius - local_off_y

            m = np.argmax(dem); iy, ix=np.unravel_index(m, dem.shape)

            x2 , y2 = ix + off_x, iy + off_y

            self.pt[key]["x_pix"]= x2
            self.pt[key]["y_pix"]= y2

            # only nedded for intervisibility !!
            
            self.pt[key]["x_geog"] += (x2 - pt_x)  * pix
            self.pt[key]["y_geog"] += (y2 - pt_y)  * pix

    """
                
            # we cannot know the position of the observer! if it is not in the center ...
            z_top = None
            
            for j in xrange(0, y_size): 
                for i in xrange(0, x_size):
                    try: k = dt [j, i] # it may be an empty cell or whatever...
                    except: continue
                    
                    if k > z_top: x_top,y_top,z_top = i,j,k

            if x_off1: x_top = pt_x + (x_top - search_top)
            if y_off1: y_top = pt_y + (y_top - search_top)



            #todo                 
            x_geog += (x2 - x)  * pix
            y_geog += (y2 - y) * pix
    """

    
    """ could be done much faster with numpy ..."""
    def point_network (self ,target_points, radius):

        radius_float = radius / self.pix

        radius_pix= int(radius_float)
        
        d= radius_float **2

        for pt1 in self.pt: 

          
            x = self.pt[pt1]["x_pix"]
            y = self.pt[pt1]["y_pix"]
            max_x = x + radius_pix; min_x = x - radius_pix
            max_y = y + radius_pix; min_y = y - radius_pix
            #does not need cropping if target points match raster extent


            # cheap distance check 
            #   if mx_dist [y2_local,x2_local] > radius: continue
            #local coords :in intervisibilty

                
##                if z_target_field: #this is a clumsy addition so that each point might have it's own height
##                    try: tg_offset = float(feat2[z_target_field])
##                    except: pass
            
            for pt2 in target_points.pt:
                x2 = target_points.pt[pt2]["x_pix"]
                y2 = target_points.pt[pt2]["y_pix"]

                #skipping 1
                if x2==x and y2==y : continue
                
                if min_x <= x2 <= max_x and min_y <= y2 <= max_y:
                    if  (x-x2)**2 + (y-y2)**2 <= d:
                        try: self.pt[pt1]["targets"].append(pt2)
                        except: self.pt[pt1]["targets"]=[pt2]
        

