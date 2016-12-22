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


from __future__ import division 

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.utils import * #progress bar
import os
from osgeo import osr, gdal, ogr

import time

import numpy
from math import sqrt, degrees, atan, atan2, tan



def dist(x1,y1,x2,y2, estimation=False):
    if not estimation: r=sqrt(pow((x1-x2),2) + pow((y1-y2),2))
    else: # error = cca 1% - NOT USED!
        rt= 1.4142135623730950488016887242097
        r = (abs(x1-x2) * rt + abs(y1-y2) * rt) / 2

    return r


def error_matrix(radius, size_factor=1):

    """
    Create a set of lines of sight which can be reused for all calculations. 
    Each line (departing from the observer point) has its target and a set of pixels it passes through.
    Only 1/8th of full radius is enough : the rest can be copied/mirrored. 
    """

    
    if size_factor == 0: size_factor = 1 #0 is for coarse algo...
    radius_large = radius  * size_factor  #if double else 0  
                                                
    mx_index= numpy.zeros((radius_large +1 , radius, 4))

    min_err = {}

    j=0 #keep 0 line empty

    for m in range (0, radius_large+1 ): # 45 deg line is added (+1) 

        x_f, y_f = radius, radius #x0,y0

        #dy = x; dx = y 
        dy,dx= m, radius_large #SWAPPED x and y! MESSY

        
        #x and y = delta x and y but y is steep!
        #fist line is min y then it ascends till 45°

        D=0
        for i in xrange (0, radius ):   #restrict iteration to actual radius!     
            x_f += 1
            if 2* (D + dy) < dx:
                D += dy # y_f remains
            else:
                y_f += 1
                D += dy - dx
#        # it is not necessary to make a circle, all calculations are in a square matrix (when x / y are not specified, they are 0,0)
                           
            #reverse x,y for data array!
            yx= (y_f,x_f)
            mx_index[j,i,0:2]=yx
                           
            if D: e=D/dx; err=abs(e)
            else: e, err = 0,0

            mx_index[j,i,2]=e
          # keep pixel dictionary to sort out best pixels
            try:
                err_old = min_err[yx][0] 
                if err < err_old: min_err[yx]=[err,j,i]
            except:
                min_err[yx]=[err,j,i]
   
        j+=1
    

    #check-out minimum errors
    for key in min_err:
        ix=min_err[key][1:3]
        er = min_err[key][0]         
        mx_index[ix[0], ix[1]][3]= 1

    return mx_index
    

def Viewshed (Obs_points_layer, Raster_layer, z_obs, z_target, radius, output,
              output_options,
              Target_layer=0, search_top_obs=0, search_top_target=0,
              z_obs_field=0, z_target_field=0,
              curvature=0, refraction=0, algorithm = 1): 


    """
    Opens a DEM and produces viewsheds from a set of points. Algorithms for raster ouput are all based on a same approach,
    explained at zoran-cuckovic.from.hr (perhaps published one day...). Intervisibility calculation, however,
    is on point to point basis and has its own algorithm. 
    """

    fast = False #non-interpolated algorithm for next version

    def search_top_z (pt_x, pt_y, search_top):
        """
        Find the highest point in a perimeter around each observer point.
        Probably a better option is to make a separate loop/function for all points
        before making viewsheds...
        """
        # global variables for raster size      

        x_off1 = max(0, pt_x - search_top)
        x_off2 = min(pt_x + search_top +1, raster_x_size) #could be enormus radius, theoretically
        
        y_off1 = max(0, pt_y - search_top)
        y_off2 = min(pt_y + search_top +1, raster_y_size )

        y_size = y_off2 - y_off1; x_size = x_off2 - x_off1

        dt = gdal_raster.ReadAsArray( x_off1, y_off1, x_size,y_size)

            
        # we cannot know the position of the observer! if it is not in the center ...
        z_top = None
        
        for j in xrange(0, y_size): 
            for i in xrange(0, x_size):
                try: k = dt [j, i] # it may be an empty cell or whatever...
                except: continue
                
                if k > z_top: x_top,y_top,z_top = i,j,k

        if x_off1: x_top = pt_x + (x_top - search_top)
        if y_off1: y_top = pt_y + (y_top - search_top)

                             
        return x_top, y_top


       
    
    def intervisibility(x, y, x2, y2, target_offset, id_target, 
                            interpolate=True):

        """
        Calculate intervisibilty lines from the observer point (always in the centre of the matrix)
        to target point (x2,y2).
        Has it's proper algorithm in order to avoid inaccuracies of the usual viewshed approach.
        """

        

        d = mx_dist[y2, x2] #do before swapping
        
        dx = abs(x2 - x); dy = abs(y2 - y)
        steep = (dy > dx)
        #direction of movement : plus or minus in the coord. system
        sx = 1 if (x2 - x) > 0 else -1
        sy = 1 if (y2 - y) > 0 else -1
        
        if steep: # if the line is steep: change x and y
            #x,y = y,x they are the same !!
            x2,y2 = y2,x2
            dx,dy = dy,dx
            sx,sy = sy,sx
            
        D = 0
      
        #for interpolation
       # slope = dy / dx *sx *sy #!!
       #the operators for negative quadrants (we do need dx, dy as absolute to verify steepness, to search distances...)

        #begins with the minimum possible angle for the observer pix,
        #thus the first pixel next to observer is always visible!
        visib = True
        angle_block = None
        angle_block2 = angle_block
        angle_hor_max = angle_block
        angle_hor_min = angle_block

        for i in xrange (0, dx):

        # ---- Bresenham's algorithm (understandable variant)
        # http://www.cs.helsinki.fi/group/goa/mallinnus/lines/bresenh.html       
            x += sx
            if 2* (D + dy) < dx:
                D += dy # y remains
            else:
                y += sy
                D += dy - dx
                           
            #unfortunately, numpy allows for negative values...
            # when x or y are too large, the break is on try-except below
            if x < 0 or y < 0 : break

            # --------- unpack coordinates ------------
            if not steep : x_pix,y_pix = x,y
            else: x_pix,y_pix = y,x
                                              
            try: angle = data[y_pix, x_pix]
            except: break

            angle_exact=0#initiate/reset
            
            if D: 
                err= abs(D/dx)  # D can be a very good substitute (2-3% differences)
              
                sD = -1 if D < 0 else 1 #inverse : if the good pixel is above the line then search down
                interpolated = y  + sD * sy

                #if interpolate<0: break

                if not steep: x_pix_interp, y_pix_interp = x, interpolated
                else: x_pix_interp, y_pix_interp = interpolated, x

                try:    angle2= data [y_pix_interp, x_pix_interp]
                except: break

            else:
                err=0
                angle2=angle

            #it is not correct to test non-interpolated against interpolated horizon angle!!
            # ... nor to test max>max and min>min, because of possible interpolation shift!
            #only : min angle > max old_angle (and vice versa...)
            
            if angle < angle_hor_min and angle2 < angle_hor_min: visib= False
            elif angle > angle_hor_max and angle2 > angle_hor_max: visib= True
            else: #optimisation: interpolate only when really needed

                angle_exact = angle + (angle2 - angle) * err
                if not angle_hor_exact: 
                    angle_hor_exact = angle_block + (angle_block2 - angle_block) * block_err
                
                visib=(angle_exact > angle_hor_exact)


            # catch old values 
            if visib :
                angle_block, angle_block2, block_err = angle, angle2, err
                angle_hor_exact = angle_exact #mostly is 0 !

                if angle > angle2:
                    angle_hor_max, angle_hor_min = angle, angle2

                else: angle_hor_max, angle_hor_min = angle2, angle
                    

            # --------------- processing output ----------------
                                       
                         
        if visib : # there is no ambiguity, visible!
            hgt = target_offset
            
        else:
             # repeat to calculate height (even without target
            angle_off =  target_offset/d if target_offset else 0

            angle += angle_off # ERROR (err) IS NOT POSSIBLE !
            # here it is probable..
            if not angle_hor_exact:
                angle_hor_exact = angle_block + (angle_block2 - angle_block) * block_err

            hgt = (angle - angle_hor_exact) * d
            visib=(hgt >0)
                
            if hgt>target_offset: hgt=target_offset
            #in case when the pixel is preceeded by an invisible one and becomes visible only on exact horizon angle,
            # hgt can get augmented by the relative target pixel height 
                
        return [visib,  hgt, d, err ]

    
# -------------- MAIN ----------------------------

    start = time.clock(); start_etape=start
    test_rpt= "Start: " + str(start)

    #####################################
    # Prepare  progress Bar
    
    iface.messageBar().clearWidgets() #=qgis.utils.iface - imported module
    #set a new message bar
    progressMessageBar = iface.messageBar()

    progress_bar = QProgressBar()

    #get a vector layer
    vlayer = QgsMapLayerRegistry.instance().mapLayer(Obs_points_layer)
    vlayer.selectAll()
    #Count all selected feature
    feature_count = vlayer.selectedFeatureCount() 

    #could be set to 100, making it easy to work with percentage of completion
    progress_bar.setMaximum(feature_count) 
    #pass the progress bar to the message Bar
    progressMessageBar.pushWidget(progress_bar)

    #set a counter to reference the progress, 1 will be given after pre-calculations
    progress = 0

    ###########################"
    #read data, check etc
    out_files=[];rpt=[];connection_list=[]

    RasterPath= str(QgsMapLayerRegistry.instance().mapLayer(Raster_layer).dataProvider().dataSourceUri())
    # TO BE ADDED TO THE DIALOG DIRECTLY (??)
    if curvature:
        # we need ellipsiod for curvature (and crs for output)
        R_layer=QgsMapLayerRegistry.instance().mapLayer(Raster_layer)
        raster_crs = R_layer.crs().toWkt() #messy.. have to parse textual description...
        inx =raster_crs.find("SPHEROID") #(...)spheroid["name",semi_major, minor, etc...]
        inx2 = raster_crs.find(",", inx) +1
        inx3 = raster_crs.find(",", inx2 )
        try:
            semi_major= float(raster_crs[inx2:inx3])
            if not 6000000 < semi_major < 7000000 : semi_major=6378137#WGS 84
        except: semi_major=6378137  

        inx4 = raster_crs.find(",", inx3 +1 )
        try:
            flattening =  float(raster_crs[inx3 +1:inx4-1])
            if not 296 <flattening < 301 : flattening= 298.257223563#WGS 84
        except: flattening= 298.257223563
        
        semi_minor=  semi_major - semi_major* (1/flattening)
        # a compromise for 45 deg latitude, ArcGis seems to have a fixed earth diameter?
        Diameter = semi_major + semi_minor 
        
    gdal_raster=gdal.Open(RasterPath)
    gt=gdal_raster.GetGeoTransform()#daje podatke o rasteru (metadata)
    projection= gdal_raster.GetProjection()
    global pix; pix=gt[1] # there's a bug in Python: globals cannot be avoided by a nested function (??)
    global raster_x_min; raster_x_min = gt[0]
    global raster_y_max; raster_y_max = gt[3] # it's top left y, so maximum!

    raster_y_size = gdal_raster.RasterYSize
    raster_x_size = gdal_raster.RasterXSize

    raster_y_min = raster_y_max - raster_y_size * pix
    raster_x_max = raster_x_min + raster_x_size * pix

    #adfGeoTransform[0] /* top left x */
    #adfGeoTransform[1] /* w-e pixel resolution */
    #adfGeoTransform[2] /* rotation, 0 if image is "north up" */
    #adfGeoTransform[3] /* top left y */
    #adfGeoTransform[4] /* rotation, 0 if image is "north up" */
    #adfGeoTransform[5] /* n-s pixel resolution */

    gtiff = gdal.GetDriverByName('GTiff')#for creting new rasters
    #projection = gdal_raster.GetProjection() #not good ? better to use crs from the project (may override the original)
 #   rb=gdal_raster.GetRasterBand(1)#treba li to?

    #progress report - for testing only
    test_rpt += "\n GDAL functions : " + str (time.clock()- start_etape)
    start_etape=time.clock()

    Obs_layer=QgsMapLayerRegistry.instance().mapLayer(Obs_points_layer)
    if Obs_layer.isValid():
        # returns 0-? for indexes or -1 if doesn't exist
        obs_has_ID = bool( Obs_layer.fieldNameIndex ("ID") + 1)
    else: return # abandon function       

    #initialise target points and create spatial index for speed
    if Target_layer:
        
        Target_layer = QgsMapLayerRegistry.instance().mapLayer(Target_layer)
        if Target_layer.isValid():
            
            targ_has_ID = bool(Target_layer.fieldNameIndex ("ID") + 1)
          
            targ_index = QgsSpatialIndex()
            for f in Target_layer.getFeatures():
                targ_index.insertFeature(f)
                
        else: return # abandon function
    
    ################################################
    # precalculate distance matrix, errors etc 
    radius_pix = int(radius/pix)
       
    full_window_size = radius_pix *2 + 1
    
    mx_vis = numpy.zeros((full_window_size, full_window_size))

    temp_x= ((numpy.arange(full_window_size) - radius_pix) * pix) **2
    temp_y= ((numpy.arange(full_window_size) - radius_pix) * pix) **2

    mx_dist = numpy.sqrt(temp_x[:,None] + temp_y[None,:])
    mask_circ = mx_dist [:] > radius  #it's real (metric) radius
     
    if curvature:
        mx_curv = (temp_x[:,None] + temp_y[None,:]) / Diameter

    
    if output_options[1] == "cumulative":
        matrix_final = numpy.zeros ( (gdal_raster.RasterYSize, gdal_raster.RasterXSize) )
    #else:   mx_vis[:] = numpy.nan # set to nan so that it's nicer on screen ...
    
    ################index matrix
    t= error_matrix(radius_pix, algorithm) 

    mx_err = t[:,:, 2]
    mx_err_dir = numpy.where(mx_err > 0, 1, -1); mx_err_dir[mx_err == 0]=0 #should use some multiple criteria in where... 
    mask = t[: ,: , 3]==1 #lowest error - for transfering data

    #take the best pixels  
    #cannot simply use indices as pairs [[x,y], [...]]- numpy thing...
    #cannot use mx : has a lot of duplicate indices

    # precalculating everything - ugly, but faster
    x0=y0=radius_pix 
    
    mx_x = t[:, : , 1].astype(int)#x and y are swapped - it's a mess...
    mx_y = t[: ,:, 0].astype(int)
    mx_y_err = mx_y + mx_err_dir

    mx_x_rev = numpy.subtract ( mx_x, (mx_x - x0) *2 , dtype=int )
    mx_y_rev = numpy.subtract ( mx_y , (mx_y - y0) *2, dtype = int)
    mx_y_err_rev = mx_y_rev + mx_err_dir *-1 #switch direction of error!

    #steep = x y swap (error is only on y so now it's only on x) 
    mx_x_steep = x0 + (mx_y - y0)
    mx_y_steep = y0 + (mx_x - x0)
    mx_x_err_steep = x0 + (mx_y_err - y0)

    mx_x_rev_steep = x0 + (mx_y_rev - y0)
    mx_y_rev_steep = y0 + (mx_x_rev - x0)
    mx_x_err_rev_steep = x0 + (mx_y_err_rev - y0)

    # ----------------- POINT LOOP -------------------------
    
    for feat in Obs_layer.getFeatures():
        targets=[]

        geom = feat.geometry()
        t = geom.asPoint()
        
        id1 = feat["ID"] if obs_has_ID else feat.id()
        x_geog, y_geog = t[0], t[1]
        
        #check if the point is out of raster extents
        if raster_x_min <= x_geog <= raster_x_max and raster_y_min <= y_geog <= raster_y_max:
            x = int((x_geog - raster_x_min) / pix) # not float !
            y = int((raster_y_max - y_geog) / pix) #reversed !
        else: continue
        
        #move everything..
        if search_top_obs:
            x,y = search_top_z (x, y, search_top_obs)
            
           # find correct coordinates of new points - needed for intervisibilty only...
            if output_options[0]== "Intervisibility":
                x_geog, y_geog= raster_x_min  + x *pix + pix/2 , raster_y_max - y *pix - pix/2
        else: z = 0 #reset !!

        # ----------  extraction of a chunk of data ---------------

        if x <= radius_pix:  #cropping from the front
            x_offset =0
            x_offset_dist_mx = radius_pix - x
        else:               #cropping from the back
            x_offset = x - radius_pix
            x_offset_dist_mx= 0
                            
        x_offset2 = min(x + radius_pix +1, raster_x_size) #could be enormus radius, so check both ends always
            
        if y <= radius_pix:
            y_offset =0
            y_offset_dist_mx= radius_pix - y
        else:
            y_offset = y - radius_pix
            y_offset_dist_mx= 0

        y_offset2 = min(y + radius_pix + 1, raster_y_size )

        window_size_y = y_offset2 - y_offset
        window_size_x = x_offset2 - x_offset

        data = numpy.zeros((full_window_size, full_window_size)) #window is always the same size
        
        data[ y_offset_dist_mx : y_offset_dist_mx +  window_size_y,
              x_offset_dist_mx : x_offset_dist_mx + window_size_x] = gdal_raster.ReadAsArray(
                  x_offset, y_offset, window_size_x, window_size_y).astype(float)# global variable

        if z_obs_field:
            try:    z = data [radius_pix,radius_pix] + float(feat[z_obs_field])
            except: z = data [radius_pix,radius_pix] +  z_obs 
        else:	    z = data [radius_pix,radius_pix] + z_obs  
        
        data -= z # level all according to observer
        
        if curvature: data -= mx_curv * (1 - refraction) # SHOULD BE FIXED !!

        # ------  create an array of additional angles (parallel to existing surface) ----------
        if z_target > 0 :
            mx_target = (data + z_target) / mx_dist 

        else: mx_target=None

        data /= mx_dist #all one line = (data -z - mxcurv) /mx_dist
                
        if Target_layer and output_options[0]== "Intervisibility":
          
            areaOfInterest= QgsRectangle (x_geog -radius , y_geog -radius, x_geog +radius, y_geog +radius)
            # SPATIAL INDEX FOR SPEED
            feature_ids = targ_index.intersects(areaOfInterest)

            visib_list=[] #initialize output list
                   
            for fid in feature_ids: # NEXT TO GET THE FEATURE
                feat2 = Target_layer.getFeatures(QgsFeatureRequest().setFilterFid(fid)).next()
                id2 = feat2["ID"] if targ_has_ID else feat2.id()
                geom2 = feat2.geometry()
                x2_geog, y2_geog = geom2.asPoint()
                
                # they may fall out of the entire raster
                if raster_x_min <= x2_geog <= raster_x_max and raster_y_min <= y2_geog <= raster_y_max:
                    #re-align to relative pixel coords of the data matrix
                    x2 = int((x2_geog - raster_x_min) / pix)  #round vraca float!!
                    y2 = int((raster_y_max - y2_geog) / pix)  #pazi: obratno!!
                else: continue

                if search_top_target: 
                    x2,y2 = search_top_z (x2,y2,search_top_target)
                    # target point search = 1) on local data array, 2) inside the radius of search
                    # normally the search is on entire data array and the perimeter is then designed around the point

                    x2_geog= raster_x_min  + x2  * pix + pix/2
                    y2_geog=   raster_y_max - y2 *pix - pix/2

                #skipping 1
                if x2==x and y2==y : continue

                x2_local = radius_pix + (x2 - x)
                y2_local = radius_pix + (y2 - y)#x and y are also global

                try : #skipping 2
                    if mx_dist [y2_local,x2_local] > radius: continue
                except : continue #out of local raster

                tg_offset = z_target
                if z_target_field: #this is a clumsy addition so that each point might have it's own height
                    try: tg_offset = float(feat2[z_target_field])
                    except: pass
                     
                visib, hgt, d, err =intervisibility (radius_pix, radius_pix, x2_local, y2_local, tg_offset, id2)

                 
                connection_list.append([id1, x_geog ,y_geog, id2, x2_geog, y2_geog,
                                        visib, hgt, d])
          

        # ------------visibility calculation in main point loop ----------------------
        else:
            #np.take is  much more efficient than using "fancy" indexing (stack overflow says ...)

            #there are some problems with shapes (horizon) so we initialize a working array here
            if output_options[0] in ["Horizon", "Horizon_full"] :
                k = algorithm if algorithm else 1
                v= numpy.zeros((radius_pix * k +1, radius_pix))
            

            for steep in [False, True]: #- initially it's steep 0, 0

                for rev_x in [True, False]:
                    mx = mx_x_rev if rev_x else mx_x

                    for rev_y in [True, False]:
                        my = mx_y_rev if rev_y else mx_y       
                        me =mx_y_err_rev if rev_y else  mx_y_err 

                        if  steep:  # swap x and y                     
                            mx = mx_x_rev_steep if rev_x else mx_x_steep                            
                            my= mx_y_rev_steep if rev_y  else mx_y_steep
                            me= mx_x_err_rev_steep if rev_x  else  mx_x_err_steep
                                            
                        if algorithm == 0:
                            interp = data[mx,my]  #skip interpolation
                        else:
                            if steep:
                                interp = data[mx,my] + (data[me, my]-data[mx,my] ) * numpy.absolute(mx_err)                    
                            else: 
                                interp = data[mx,my] + (data[mx, me] -data[mx,my] ) * numpy.absolute(mx_err)

                            
                        test_val = numpy.maximum.accumulate(interp, axis=1)

                        #swap here - test aginst target mx
                        #target has to be interpolated on its own..
                        if z_target:
                            if algorithm == 0 : interp = mx_target[mx,my]
                            else:
                                if steep:
                                    interp = mx_target[mx,my] + (mx_target[me, my]-mx_target[mx,my] ) * numpy.absolute(mx_err)                    
                                else: 
                                    interp = mx_target[mx,my] + (mx_target[mx, me] -mx_target[mx,my] ) * numpy.absolute(mx_err)
                    

                        if output_options[0]== "Binary":
                            #if it's T/F then False is written as NoData by gdal (i.e. nothing is written)
                            v = interp >= test_val 

                        elif output_options[0] in ["Invisibility" ,"Intervisibility"]:
                            v = interp - test_val
                            #Should it be DATA - accum or interpolated - accumul ??

                        elif output_options[0]== "Horizon_full":
                            
                            #diff always returns one place less than full array! 
                            v[:, :-1] = numpy.diff((interp >= test_val).astype(int)) *-1
                           
                                # 1: make = True/False array;
                                # 2: turn to integers because boolean operations give True False only
                                # 3 diff = x(i)- x(i-1) = -1 or 1 for breaks
                                # * -1 so that good breaks become +1, instead of -1
                                
                            v[v == -1]=0 #delete the beginning of  visible areas

                            
                        elif output_options[0]== "Horizon": # = true or last horizon

                            v = interp >= test_val
                            #to avoid confusion because of hidden corners
                            v[ mx_dist[mx,my] >= radius + pix*2]= False
                                                       
                            #select last pixel (find max value in a reversed array (last axis!)
                            #argmax stops at first occurence
                            #indices have to be re-reversed :)
                            #gives a flat array of 1 index for each row (axis=1)
                            rev_max = radius_pix - numpy.argmax(v[:, ::-1], axis=1) -1
                                           
                            v[:]=False


                            #radius = row n° for fancy index (should be some nicer way...)
                            v[ numpy.arange(radius_pix *k +1), rev_max.flat ] = True
                            # k = 1 or algorithm

                            v[: , -1] = 0 #artifacts at borders (false horizons)
                            #(all matrix edges are marked as horizon - if visibilty zone gets cut off there)     

                        #numpy.absolute(mx_err[mask])# for errors                                
                        mx_vis [mx[mask], my[mask]]=v[mask]
                        
            if output_options[0]== "Binary":
                mx_vis [radius_pix,radius_pix]=1         

            elif output_options[0]== "Invisibility":
                
                mx_vis *= mx_dist
                mx_vis[radius_pix,radius_pix]=z_target
                #this is neccesary because the target matrix is not interpolated!
                mx_vis[mx_vis>z_target]=z_target
                               
            matrix_vis = mx_vis
           
            # ~~~~~~~~~~~~~~~ Finalizing raster output ~~~~~~~~~~~~~~~~~~~~~~~
            out=str(output + "_" + str(id1))           

            if output_options [1] == "cumulative":
                matrix_vis [mask_circ] = 0 #loosing a bit of time, but not critical
                
                matrix_final [ y_offset : y_offset + window_size_y,
                               x_offset : x_offset + window_size_x ] += matrix_vis [
                                   y_offset_dist_mx : y_offset_dist_mx +  window_size_y,
                                    x_offset_dist_mx : x_offset_dist_mx + window_size_x] 
    
            else:
               
                matrix_vis[mask_circ]=numpy.nan #mask out corners 

                file_name = out + "_" + output_options[0]

                num_format=gdal.GDT_Float32
                success = write_raster (matrix_vis[y_offset_dist_mx : y_offset_dist_mx +  window_size_y,
                                        x_offset_dist_mx : x_offset_dist_mx + window_size_x],
                                        file_name, gdal_raster.RasterXSize, gdal_raster.RasterYSize,
                                        x_offset, y_offset, gt, projection, num_format)
                if success : out_files.append(success)
                else: QMessageBox.information(None, "Error writing file !", str(file_name + ' cannot be saved'))

                matrix_vis= None
                    
        ######################################
        #Update the progress bar: point loop
        
        progress += 1
        progress_bar.setValue(progress) 	

        start_etape=time.clock()
        
    #####################################
    #exiting the main points loop : write cumulative....
    if output_options [1]== "cumulative":
        success = write_raster (matrix_final, output+'_cumulative',gdal_raster.RasterXSize, gdal_raster.RasterYSize,
                                0, 0, gt, projection)
        if success : out_files.append(success)
        else: QMessageBox.information(None, "Error writing file !", str(output + '_cumulative cannot be saved'))

    if output_options[0]=="Intervisibility":
        success = write_intervisibility_line (output, connection_list, Obs_layer.crs())
        if success : out_files.append(success)

        else : QMessageBox.information(None, "Error writing file !", str(output + '_intervisibility cannot be saved'))

    
    matrix_final = None; data = None; connections_list=None; v=None; vis=None
    test_rpt += "\n Total time: " + str (time.clock()- start)
    #QMessageBox.information(None, "Timing report:", str(test_rpt))
    
    iface.messageBar().clearWidgets()  

    return out_files


#works with global gdal_raster
def write_raster (matrix, file_name,columns_no, rows_no , offset_x, offset_y,
                  geotransform_data, GDAL_projection_data,
                  num_format=gdal.GDT_Float32): #full file path

    driver = gdal.GetDriverByName( 'GTiff' )
    
    dst_ds = driver.Create( file_name+'.tiff', columns_no, rows_no, 1, num_format)
    if not dst_ds: return 0
       
    dst_ds.SetProjection(GDAL_projection_data)
    dst_ds.SetGeoTransform(geotransform_data)
    
    dst_ds.GetRasterBand(1).Fill(numpy.nan)#this is for esthetic purpose chiefly 
    dst_ds.GetRasterBand(1).SetNoDataValue(numpy.nan)# nans are set for all outputs if not cumulative
    
    dst_ds.GetRasterBand(1).WriteArray(matrix,offset_x,offset_y)#offset=0
    
    dst_ds=None
    #driver.GDALClose(dst_ds) not working!
    return file_name +'.tiff'

def write_intervisibility_line (file_name, data_list, coordinate_ref_system, use_pix_coords=False):

    #QMessageBox.information(None, "Timing report:", str(data_list))
    
    fields = QgsFields() #there's a BUG in QGIS here (?), normally : fields = ....
    fields.append(QgsField("Source", QVariant.String ))
    fields.append(QgsField("Target", QVariant.String))
## fields.append(QgsField("Source_lbl", QVariant.String, 'string',50))
## fields.append(QgsField("Target_lbl", QVariant.String, 'string',50))
    fields.append(QgsField("Visible", QVariant.String, 'string',5))
    fields.append(QgsField("TargetSize", QVariant.Double, 'double',10,3))
    fields.append(QgsField("Distance", QVariant.Double, 'double',10,2))

    writer = QgsVectorFileWriter( file_name + ".shp", "CP1250", fields,
                                  QGis.WKBLineString, coordinate_ref_system) #, "ESRI Shapefile"
                                            #CP... = encoding
    if writer.hasError() != QgsVectorFileWriter.NoError:
        QMessageBox.information(None, "ERROR!", "Cannot write intervisibilty file (?)")
        return 0
    
    for r in data_list:
        # create a new feature
        feat = QgsFeature()
        if use_pix_coords:
            half_pix= pix/2 #global variable pix
            l_start=QgsPoint(raster_x_min  + r[1]*pix + half_pix, raster_y_max - r[2]*pix - half_pix )
            l_end = QgsPoint(raster_x_min  + r[4]*pix + half_pix, raster_y_max - r[5]*pix - half_pix)
        else:
            l_start=QgsPoint(r[1],r[2]);  l_end = QgsPoint(r[4],r[5])
         
        feat.setGeometry(QgsGeometry.fromPolyline([l_start, l_end]))
        # do not cast ID to string: unicode problem -- angle * distance in pixels -- distance * pixel_size
        #feat.setAttributes([ str(r[0]), str(r[3]), bool(r[6]), float(r[7] * r[8]), ])
        feat.setFields(fields)
        feat['Source'] = r[0]
        feat['Target'] = r[3]
        feat['Visible'] = 'True' if r[6] else 'False'
        feat['TargetSize'] = float(r[7])
        feat['Distance'] = float(r[8])
        
        writer.addFeature(feat)
        del feat

    del writer
    layer = None
    return file_name + ".shp"


