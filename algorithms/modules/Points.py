# -*- coding: utf-8 -*-

#from PyQt5.QtCore import QCoreApplication
from qgis.PyQt.QtCore import *

import processing

from qgis.core import *

from os import path

try:
    from osgeo import gdal
except ImportError:
    import gdal 

import numpy as np

from . import Raster as rst



"""

TODO: find highest pt

TODO : calculating coordinates in pixels ==> to Raster class !!

"""

FIELDS = {"id" : ["ID", 255,0],
          "z": ["observ_hgt", 10,4],
          "z_targ":["target_hgt", 10, 4],
          "radius":["radius", 10, 2],
          "radius_in":["radius_in", 10, 2],
          "path":["file", 255,0],
          "azim_1":["azim_1", 8, 5],
          "azim_2":["azim_2", 8, 5],
          "angle_down":["angle_down", 8, 5],
          "angle_up": ["angle_up", 8, 5]}


            
class Points:
    """
    Points class is creating a clean shapefile with analysis parameteres in
    the associated table. It is also taking care of geometries (filtering
    points outside raster, searching for neighbours in a specified radius etc.)
    """
    
    def __init__(self, layer, crs=None, project_crs=None):
    #layer = qgis layer,  bounding_box = QgsRectangle,   field_id= string)
        self.pt={}

        # this is not a good apporach! not working with txt files...
        #self.layer = QgsVectorLayer(shapefile, 'o', 'ogr')

        self.layer = layer #this is a  QgsProcessingFeatureSource object

        self.crs = crs if crs else self.layer.sourceCrs()

        self.project_crs = project_crs if project_crs != crs else None

        #make a test first !
        self.missing = []

        self.max_radius=0
        #provider = self.layer.dataProvider()
 
        
        self.count = 0 # only the take routine can determine the number of used points

        
    """
    check the existence of param. fields  

    """
    def test_fields(self, field_list):
        
        l=[]
        f_in = self.layer.fields()
        
        for e in field_list:
            try: f_in.field(e)
            except:  l.append(e)
        return l   
        
##        for defs in iter(FIELDS.items()): 
##            f = defs[0]
            

    def field_defs (self):
            
        qfields = QgsFields()
       
        
        for f in FIELDS:
        
            if f not in list(self.pt.values())[0]: continue
            
            name, length, decimals = FIELDS[f]
            if name in ["ID", "file"]: 
                #windows has 250 character limit for filenames...
                qfields.append ( QgsField(name, QVariant.String, 'string',255))
            else:
                
                qfields.append (QgsField(name, QVariant.Double,
                                        'double', length,decimals))

        return qfields
    
    """
    Take care of parameters and reproject if necessary.
    Same points can be used with different rasters, so do not crop.
    """
    # multiple parameters (numeric + field name) 
    # enable to set a default in case there is a problem, eg z = float(None)
    def clean_parameters(self, z_obs, radius ,
                        z_targ=0,
                        field_ID = None,
                        field_zobs = None,
                        field_ztarg=None,
                        field_radius=None,
                        field_radius_in=None,
                        folder = None,
                        field_azim_1 = None,
                        field_azim_2= None,
                        field_angle_down = None,
                        field_angle_up = None):
       
        errors=[]

        if self.project_crs:

            transf = QgsCoordinateTransform(self.crs, self.project_crs, QgsProject.instance())   

        

        for feat in self.layer.getFeatures():
            
            geom = feat.geometry()

            # try geom.transform(crsTransform)
            t = geom.asPoint()

            if self.project_crs:
                try: t = transf.transform(t)
                except: continue #in case of wrong coords etc.. 
                
            x_geog, y_geog= t

            #z,zt,r = z_obs, z_targ, radius
            
            
            key  = feat.id()

            try: id1 = feat[field_ID]
            except: id1 = key
                
            #addition for possible field values.
            #override with fixed parameters in case of problem 
            
            try : z = float(feat[field_zobs])
            except: z=z_obs

            try : r = float(feat[field_radius]) 
            except: r=radius
                
            # obligatory prarameters        
            self.pt[key]={"id":id1, "z":z ,  "radius" : r,
                          "x_geog":x_geog, "y_geog" : y_geog }
        
            # optional
            if z_targ or field_ztarg:
                try : self.pt[key]["z_targ"] = float(feat[field_ztarg])
                except: self.pt[key]["z_targ"]=z_targ

            if folder:
                self.pt[key]["path"] = path.join(folder, str(id1) + ".tif")

            if field_radius_in:
                try: self.pt[key]["radius_in"] = float(feat[field_radius_in])
                except: self.pt[key]["radius_in"] = 0
            
            if  field_azim_1 and field_azim_2:
                
                a1, a2 = 0, 360 #default values
                
                try : 
                    t1, t2 =  float(feat[field_azim_1]), float(feat[field_azim_2])
                    
                    if 0 <= t1 <= 360 and 0 <= t2 <= 360: a1, a2 = t1, t2 
                    else: errors.append("Azimuth angle out of range, point " + str(id1))  
                    
                except: errors.append("Data error for azimuth, point " + str(id1))        
                
 
                self.pt[key]["azim_1"], self.pt[key]["azim_2"] =a1, a2


            if  field_angle_down and field_angle_up:
                
                a1, a2 = -90, 90 #default values

                try : 
                    t1, t2 = float(feat[field_angle_down]), float(feat[field_angle_up])
                    
                    if not -90 <= t1 <= 90 or not -90 <= t2 <= 90:
                        errors.append("Angular mask out of range, point " + str(id1))   
                    elif t1 > t2 : 
                        errors.append("Angles not compatible" + str(t1) + " and" + str(t2) + "Point:" + str(id1))
                    else: a1, a2 = t1, t2 
                                
                except: errors.append("Data error for angular mask, point " + str(id1))   
                
                #perhaps the reversed angles could be useful, e.g. an obstacle  ?
                
                self.pt[key]["angle_down"], self.pt[key]["angle_up"] = a1, a2


            #else: errors.append(["duplicate ID:",id1])
       #TODO : testing for duplicates --> network etc ...
                
        
         
       # self.max_radius = max(x, key=lambda i: x[i])

        if errors:
            txt = "ERRORS in observer point parameters :\n."
            for l in errors: txt += "\n" + l

            QgsMessageLog.logMessage( txt, "Viewshed info")
    
    def move_top(self,  raster_path, search_radius):
        """
            Find the highest point in a perimeter around each observer point.
            Note that it always moves the point to the center of the highest pixel
        
            This is duplicating functions from take_points (selection inside a frame)!
            to reorganise !! (should be independent function, could be useful elsewhere...)
            
        """
  
        r = rst.Raster(raster_path)
        pix = r.pix; half_pix = pix/2

        raster_x_min, raster_y_min, raster_x_max,raster_y_max = r.extent
                
        radius_pix = int(search_radius/pix)

        win_size = radius_pix * 2 + 1

        r.set_master_window(radius_pix, background_value=r.min)
        
        
    #raster_y_min = raster_y_max - raster_y_size * pix
    #raster_x_max = raster_x_min + raster_x_size * pix

        for key in self.pt:
           
##            x, y = self.pt[key]["x_geog"], self.pt[key]["y_geog"]
##
##            #how to use Qgs functions?
##            # ext = QgsRectangle(*extents)
##            #pt = QgsPoint(x,y)
##            # pt in ext ???
##          
##            if not raster_x_min < x < raster_x_max \
##            or not raster_y_min < y < raster_y_max: continue
##
##
##            # make a function for pixel coords !!!
##            x_pix= int((x - raster_x_min) / pix)
##            y_pix = int((raster_y_max - y) / pix) #reversed !

            x_pix, y_pix = self.pt[key]["pix_coord"]

            r.open_window(x_pix, y_pix, radius_pix)

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

            self.pt[key]["x_geog"] = (ix + x_off) * pix + raster_x_min + half_pix
            self.pt[key]["y_geog"] = raster_y_max - (iy + y_off) * pix  - half_pix

#           
##            if iy != radius_pix or ix != radius_pix:
##        
##                self.pt[key]["x_geog"] += (ix - x_pix)  * pix
##                self.pt[key]["y_geog"] += (iy - y_pix)  * pix
        

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

    
    """ much faster with numpy ...

    if not 0 <= x < raster_x_size or not 0 <= y < raster_y_size : continue
       
       #cropping from the front
    if x <= radius_pix:   x_offset =0
       #cropping from the back
    else:      x_offset = x - radius_pix         
      
    if y <= radius_pix:  y_offset =0
    else:   y_offset = y - radius_pix

    x_offset2 = min(x + radius_pix +1, raster_x_size) #could be enormus radius, so check both ends always
    y_offset2 = min(y + radius_pix + 1, raster_y_size )
    
    window_size_y = y_offset2 - y_offset
    window_size_x = x_offset2 - x_offset

    mx = r.ReadAsArray(x_offset, y_offset, window_size_x, window_size_y).astype(float)
    m = np.argmax(mx)

    iy, ix=np.unravel_index(m, mx.shape)
    
    #0.5 is to move to the center of corresp. pixel
    x2_g = ( ix +0.5 + x_offset) * pix  + raster_x_min 
    
    y2_g = raster_y_max - (y_offset + iy + 0.5) * pix  

    g= QgsGeometry.fromPoint(QgsPoint( x2_g, y2_g))
    
    inputLayer.dataProvider().changeGeometryValues({ pt_id : g })

    """

    
    """
    Assign targets for each observer point. Targets are a class instance
    Used after take which selects good points

    TODO : use spatial indexing ... == use .take ??
    """
    def network (self,targets):

         for pt1 in self.pt:

            id1 = self.pt[pt1]["id"]        
            x,y = self.pt[pt1]["pix_coord"]
            
            r = self.pt[pt1]["radius"] #it's pixelised after take !!

            radius_pix= int(r); r_sq = r**2
            
            max_x, min_x = x + radius_pix, x - radius_pix
            max_y, min_y = y + radius_pix, y - radius_pix
            #does not need cropping if target points match raster extent


            # cheap distance check 
            #   if mx_dist [y2_local,x2_local] > radius: continue
            #local coords :in intervisibilty

                
##                if z_target_field: #this is a clumsy addition so that each point might have it's own height
##                    try: tg_offset = float(feat2[z_target_field])
##                    except: pass
            self.pt[pt1]["targets"]={}
            
            for pt2, value in targets.pt.items():

                id2 = targets.pt[pt2]["id"]

                x2, y2 = value["pix_coord"]

                if id1==id2 and x == x2 and y==y2 : continue
                
                if min_x <= x2 <= max_x and min_y <= y2 <= max_y:
                    if  (x-x2)**2 + (y-y2)**2 <= r_sq:
                          # this is inefficient for looping
                          # need to open a window for each edge...
##                        self.edges[id1,id2]={}
                        self.pt[pt1]["targets"][pt2]=value


    """
    Returns a dict of points, prepared for visibilty analysis
    All values are expressed in pixel offsets.

    To make it robust: everything is in try - except blocks,
    use test_fields( ..) to check!

    
    """
    def take (self, extent, pix_size, spatial_index=None):
        
        x_min, y_max = extent[0], extent [3]

        
        bounding_box = QgsRectangle(*extent) #* unpacks an argument list     

        if not spatial_index: #for intersect, not very helpful ...?
            s_index = QgsSpatialIndex()
            for f in self.layer.getFeatures():
                s_index.insertFeature(f)
            
        else: s_index = spatial_index

        ids = s_index.intersects(bounding_box)

        self.count = len(ids)

##        for fid in feature_ids:
##            feat = self.layer.getFeatures(
##                   QgsFeatureRequest().setFilterFid(fid)).next()

        for feat in self.layer.getFeatures(QgsFeatureRequest( ids)):
 
            geom = feat.geometry()
            t = geom.asPoint()
            
            x_geog, y_geog= t

            id1= feat.id()
          

             # !! SHOULD BE PARAMETRIZED - fiels are listed above
            # test_fileds ( FIELDS) and then map ...

            r=feat["radius"] 
            if r > self.max_radius: self.max_radius=r
            
            self.pt[ id1 ]={"id" : feat["ID"],
                            "z" : feat["observ_hgt"],
                            "radius" : r/ pix_size, #we use pixel distances !
                            # not float !
                            "pix_coord" : (int((x_geog - x_min) / pix_size), 
                                           int((y_max - y_geog) / pix_size)), 
                            # geog. coords are only used for writing vectors
                            "x_geog" :x_geog, "y_geog": y_geog}

            
            # optional fields
          
            
            try: self.pt[ id1 ]["z_targ"]  = feat["target_hgt"]
            except : pass

            try: self.pt[ id1 ]["radius_in"]  = feat["radius_in"]/ pix_size
            except : pass
            
            try: self.pt[ id1 ]["file"] = feat["file"]
            except: pass

            try:
                self.pt[ id1 ]["azim_1"] =  feat["azim_1"]
                self.pt[ id1 ]["azim_2"] =  feat["azim_2"]

            except: pass
            
            try:
                self.pt[ id1 ]["angle_down"] =  feat["angle_down"]
                self.pt[ id1 ]["angle_up"] =  feat["angle_up"]

            except: pass
                

        
                        
    def return_points (self, use_pix_coords=False):

        
        # test the existence of values in dict     
       # miss_tg = "z_targ" not in self.pt.values()[0]
        #miss_file= "path" not in self.pt.values()[0]
        

       # crs = self.project_crs if self.project_crs else self.crs

        fields = self.field_defs()


        
        for p in self.pt:

            data =self.pt[p]

            geom = QgsGeometry.fromPointXY(
                QgsPointXY(float(data["x_geog"]),
                         float(data["y_geog"] )) )
           
            # create a new feature          
           
            feat = QgsFeature(fields)
            #  feat.setFields(fields) ...
            feat.setGeometry(geom)
                  
            for f in data:
                try: feat[FIELDS[f][0]] =data[f]
                except: pass
##
##            feat['ID'] = r
##            feat ['observ_hgt']=self.pt[r]["z"]
##            feat ['radius']=self.pt[r]["radius"]
##            if not miss_tg:
##                feat ['target_hgt']=self.pt[r]["z_targ"]
##            if not miss_file:
##                feat ['file']=self.pt[r]["path"]

         
            yield feat

    
