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
* the Free Software Foundation; either version 2 of the License, or *
* (at your option) any later version. *
* *
***************************************************************************/
"""

from __future__ import division #... the Python floating point bug...

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import os
from osgeo import osr, gdal, ogr
from array import * 

import time
from operator import itemgetter 
import numpy
from math import sqrt, degrees, atan, atan2, tan

import numbers


def dist(x1,y1,x2,y2, estimation=False):
    if not estimation: r=sqrt(pow((x1-x2),2) + pow((y1-y2),2))
    else: # error = cca 1% - NOT USED!
        rt= 1.4142135623730950488016887242097
        r = (abs(x1-x2) * rt + abs(y1-y2) * rt) / 2

    return r

def bresenham_circle(x0,y0,radius):
    lst=[]
    f = 1 - radius
    ddf_x = 1
    ddf_y = -2 * radius
    x = 0
    y = radius
    lst.append([x0, y0 + radius])
    lst.append([x0, y0 - radius])
    lst.append([x0 + radius, y0])
    lst.append([x0 - radius, y0])

    x_old,y_old=x,y

    while x < y:
        if f >= 0:
            y -= 1
            ddf_y += 2
            f += ddf_y
            
        x += 1
        ddf_x += 2
        f += ddf_x
        
        lst.append([x0 + x, y0 + y])
        lst.append([x0 - x, y0 + y])
        lst.append([x0 + x, y0 - y])
        lst.append([x0 - x, y0 - y])
        lst.append([x0 + y, y0 + x])
        lst.append([x0 - y, y0 + x])
        lst.append([x0 + y, y0 - x])
        lst.append([x0 - y, y0 - x])

        #addition for a thicker line
            #! screen y descends
            #steep
        lst.append([x0 + x, y0 + y-1])
        lst.append([x0 - x, y0 + y-1])
        lst.append([x0 + x, y0 - y+1])
        lst.append([x0 - x, y0 - y+1])
            #flat
        lst.append([x0 + y-1, y0 + x])
        lst.append([x0 - y+1, y0 + x])
        lst.append([x0 + y-1, y0 - x])
        lst.append([x0 - y+1, y0 - x])
   
    return lst


def Viewshed (Obs_points_layer, Raster_layer, z_obs, z_target, radius, output,
              output_options,
              Target_layer=0, search_top_obs=0, search_top_target=0,
              z_obs_field=0, z_target_field=0,
              curvature=0, refraction=0):


    

    # large nested function : using the same variables..
    def visibility(x0, y0, target_list, options,
                   target_offset = False,
                    mask = False, interpolate=True):
                        
        def write2matrix (x,y,error,value):
            if error <  mx_err[y, x]:
                        mx_vis[y, x]= value  
                        mx_err[y, x]= error

        
        

        ary=[]
        mx_vis = numpy.zeros ( (window_size_y , window_size_x)) # cannot be = data: it ovrewrites it!
        mx_err = numpy.ones ( (window_size_y , window_size_x)) # the initial error    
        
        q=0 #test
        l=[] #testiranje
        
        if options == "Horizon":
            Break=False 
            last_x, last_y = x0, y0
            last_err = 0

        for n in target_list:
            #test
            q+=1
            x,y = x0 , y0
            x2, y2= n[0:2]
            if options == "Intervisibility" :# individual settings for each target point
                target_offset, id_target = n[2:4]
                                
            dx = abs(x2 - x0); dy = abs(y2 - y0)
            steep = (dy > dx)
            #direction of movement : plus or minus in the coord. system
            sx = 1 if (x2 - x0) > 0 else -1
            sy = 1 if (y2 - y0) > 0 else -1
            
            if steep: # if the line is steep: change x and y
                x,y = y,x
                x2,y2 = y2,x2
                dx,dy = dy,dx
                sx,sy = sy,sx
                
            D = 0
          
            #for interpolation
           # slope = dy / dx *sx *sy #!! the operators for negative quadrants (we do need dx, dy as absolute to verify steepness, to search distances...)

            #begins with the minimum possible angle for the observer pix,
            #thus the first pixel next to observer is always visible!
            visib = True
            angle_block = None
            angle_block2 = angle_block
            angle_hor_max = angle_block
            angle_hor_min = angle_block

            for i in xrange (0, dx):
    ##                y_dec = slope * (x-x2) + y2
    ##                y = int(round(y_dec)) #it considers rounded as float...
    ##                err = y - y_dec
    ##
    ##                interpolated = y-1 if err > 0 else y+1 #inverse : if the good pixel is above the line then search down
    ##                                                    # we don't need to y+sy because the slope has already been multiplied by sy
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
                        
                else : # ADDITIONAL TARGET HEIGHT: FOR INVISIBLES ONLY!! (otherwise reset horizon...)
                    # - in case of intervisibility restrain to the last pixel only
                    if target_offset and options != "Intervisibility":
                        
##                        QMessageBox.information(None, "podatak:", str(dx))
##                        return
                        angle = mx_target[y_pix, x_pix]          

                        if D: angle2= mx_target[y_pix_interp, x_pix_interp]
                        else: angle2= angle
                            
                        if angle < angle_hor_min and angle2 < angle_hor_min: visib= False
                        elif angle > angle_hor_max and angle2 > angle_hor_max: visib= True
                        else:
                            angle_exact = angle + (angle2 - angle) * err
                            #optimisation: interpolate only when really needed
                            if not angle_hor_exact: 
                                angle_hor_exact = angle_block + (angle_block2 - angle_block) * block_err
                            
                            visib=(angle_exact > angle_hor_exact)
                      
           
                
            # ----------- skip all but the last one if mask is used 
                if mask and i < dx-1: continue
                
                # --------------- processing output ----------------
                              
                if options == 'Horizon': 

                    if not visib:
                        Break = True
                        write2matrix(x_pix, y_pix, err, 0)
                        #overwrite points on the invisible side 

                    else:
                        if Break and i==0:
                            write2matrix(last_x, last_y, last_err, 1)

                        # overwrite spurious points : horizon on smaller error only
                        # DELTES TOO MUCH ?
                        else:
                            write2matrix(x_pix, y_pix, err + 0.0001, 0)
                            #+0.001 to enable to be overwritten with the last_err!
##                    
##                    # ADVANCED VERSION WITH HORIZON DEPTH
##                    dst = mx_dist[y_pix,x_pix] 
##                    if not visib : Break=True
##                    # break-points are all we need --> passing from invisible to visible
##                    #there's a bug if the first pix (next to the observer) is invisible (i.e. non-existant) because it's normally always visible  
##                    else:
##                        
##                        if Break:       
##                            if i==0 or dst - last_dist > hor_min: d=1
##                            else: d=0
##                            #i= 0: we have jumed into an another line (depth is unknown)
##                            write2matrix(last_x, last_y, last_err, d)                      
                        Break = False
                        
                        last_x, last_y = x_pix, y_pix
                        last_err=err
                        #last_dist = dst              
                    #write all pix : to overwrite on smaller error    
                    
                    
                elif options == 'Binary':
                    
                # faster than calling the function!!!
                   if err <  mx_err[y_pix,x_pix]:
                        mx_vis[y_pix,x_pix]= 1 if visib else 0  
                        mx_err[y_pix,x_pix]= err
                # nicer, but slower:
                  #  write2matrix( x_pix,y_pix, err, 1 if visib else 0)
                   
                elif options == 'Invisibility':
                # repetition : into a function... ?
                    if not visib:
                        if not angle_exact: angle_exact = angle + (angle2 - angle) * err
                        if not angle_hor_exact: angle_hor_exact = angle_block + (angle_block2 - angle_block) * block_err
                        angle_diff = angle_exact - angle_hor_exact
                    else: angle_diff=0
                    
                    write2matrix(x_pix,y_pix, err, angle_diff)
                    
            #out of inner loop : it verifies the last pixel only
            if options =='Intervisibility':
                # d = mx_dist[y_pix,x_pix] THIS IS BETTER, but it cant work when the matrix is cropped (point close to border)
                d= dist(x0,y0, x_pix, y_pix) * pix                
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


                ary.append([id_target, x_pix, y_pix, visib,  hgt, d, err ])
                
                #QMessageBox.information(None, "podatak:", str(ary))

        #finishing
        
        # the first pixel has not been registered...
        # when mask is provided the observer is not important!
        if options == 'Binary': mx_vis [y0,x0] = 1 #ary.append([x0,y0, 0, 1])
        elif options == 'Invisibility': mx_vis = mx_vis * mx_dist

        if options =='Intervisibility': return ary 
        else: return mx_vis

#            QMessageBox.information(None, "podatak:", str(window_size_x) +"  " + str( window_size_y))
        
    def search_top_z (pt_x, pt_y, search_top):

        # global variables
        
        x_off1 = max(0, pt_x - search_top)
        x_off2 = min(pt_x+ search_top +1, raster_x_size) #could be enormus radius, theoretically
        
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

# PREFFERED TECHNIQUE : SOME PROBLEMS ....
##        loc=numpy.argmax(dt, axis=1)
 #       QMessageBox.information(None, "podatak:", str(dt))
##        
##        y_top=loc[0]; x_top = loc[1]
##        z_top= dt [y_top, x_top]

        if x_off1: x_top = pt_x + (x_top - search_top)
        if y_off1: y_top = pt_y + (y_top - search_top)

            
        return (x_top,y_top,z_top)
    
# -------------- MAIN ----------------------------

    start = time.clock(); start_etape=start
    test_rpt= "Start: " + str(start)
    
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
        
##        QMessageBox.information(None, "podatak:", str(semi_minor))
##        return
# ------------------------------------------------------------------------------
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

    #progress report
    test_rpt += "\n GDAL functions : " + str (time.clock()- start_etape)
    start_etape=time.clock()

    Obs_layer=QgsMapLayerRegistry.instance().mapLayer(Obs_points_layer)
    if Obs_layer.isValid():
        # returns 0-? for indexes or -1 if doesn't exist
        obs_has_ID = bool( Obs_layer.fieldNameIndex ("ID") + 1)
    else: return # abandon function
  
    if output_options[1] == "cumulative":
        matrix_final = numpy.zeros ( (gdal_raster.RasterYSize, gdal_raster.RasterXSize) )
        

    #initialise target points and create spatial index for speed
    if Target_layer:
        
        Target_layer = QgsMapLayerRegistry.instance().mapLayer(Target_layer)
        if Target_layer.isValid():
            
            targ_has_ID = bool(Target_layer.fieldNameIndex ("ID") + 1)
          
            targ_index = QgsSpatialIndex()
            for f in Target_layer.getFeatures():
                targ_index.insertFeature(f)
                
        else: return # abandon function
    

    # -------- precalculate distance matrix, curvature etc -------------------------------
    radius_pix = int(radius/pix)
    if output_options[0] == 'Intervisibility': #messy : need a larger window than usual..
        radius_pix += 1 + search_top_target #accomodate for all potential targets in a single array
        #account for posssible one pixel shift because points are not in pixel centres 
       
    full_window_size = radius_pix *2 + 1

    
    
    temp_x= ((numpy.arange(full_window_size) - radius_pix) * pix) **2
    temp_y= ((numpy.arange(full_window_size) - radius_pix) * pix) **2

    mx_dist = numpy.sqrt(temp_x[:,None] + temp_y[None,:])

    if curvature:
        mx_curv = (temp_x[:,None] + temp_y[None,:]) / Diameter 
    
    if not Target_layer:
        target_list = bresenham_circle(radius_pix,radius_pix,radius_pix)    

#PAZI AKO JE POLJE U TABELI ZA TARGET HGT!!! DODATI

    #count features
    #ViewshedAnalysisDialog.setProgressBar(self.dlg, vlayer.featureCount()) ???
   
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
        if search_top_obs: x,y,z_UNUSED = search_top_z (x, y, search_top_obs)  
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

        # realign coords
        x -= x_offset; y -= y_offset

        data = gdal_raster.ReadAsArray(x_offset, y_offset, window_size_x, window_size_y).astype(float)# global variable
        distances = mx_dist [y_offset_dist_mx : y_offset_dist_mx +  window_size_y,
                             x_offset_dist_mx : x_offset_dist_mx + window_size_x] #this is supposed to return a 'view', not a copy of the array!
        if z_obs_field:
            try:    z = data [y,x] + float(feat[z_obs_field])
            except: z = data [y,x] +  z_obs 
        else:	    z = data [y,x] + z_obs  
        
        data -= z # level all according to observer
        
        if curvature:
            data  -= (mx_curv[y_offset_dist_mx : y_offset_dist_mx +  window_size_y,
                             x_offset_dist_mx : x_offset_dist_mx + window_size_x]
                        * (1 - refraction)      )
              
        data /= distances
        #data = data / (temp_x[:,None]  + temp_y[None,:]) #This is nice (avoid sqroot) but it doesn't work for angles ??(<1 values, large deco

        
        # ------  create an array of additional angles (parallel existing surface) ----------
        if z_target > 0 and output_options[0]!= "Intervisibility" : #for intervisibilty offsets may differ for each target -> they are calculated individually
            mx_target = data +  z_target / distances

        else: mx_target=None

        #hypot = hypothenouse, where each array is the length of each side of a straight angle (array1 [0,0]= 3, array2 [0,0] = 4 --> hypot=5)
        #numpy.hypot (t_x[:,None] - t_x[x], t_y[None,:]-t_y[y])
        
        
        if Target_layer:
            # maximum posibility (the new observer coordinate is not translated to geographic)
            diameter = radius + search_top_obs*pix + search_top_target*pix 
            areaOfInterest= QgsRectangle (x_geog -diameter , y_geog -diameter, x_geog +diameter, y_geog +diameter)

            # SPATIAL INDEX FOR SPEED
            feature_ids = targ_index.intersects(areaOfInterest)
                   
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

                if search_top_target: #works with data matrix : True!!
                    s = search_top_z (x2,y2, search_top_target)
                    x2,y2,z2 = s

                x2 -= x_offset; y2 -= y_offset

                if x2==x and y2==y : continue #skip same pixels!
                
                #this eliminates distance calculation for each point (delta x + delta y < radius is always OK)
                if (abs(x2-x) + abs (y2-y))> radius_pix:
                    if round(dist(x,y,x2,y2)) > radius_pix : continue

                if z_target_field:
                    try: z_target = float(feat2[z_target_field])
                    except: pass #do nothing, already given above
                
                targets.append ([x2,y2, z_target, id2])
            
                #test_rpt += "\n - point "+ str(z_obs) + " - " + str(z_target) + " calculations + dumping: " + str (time.clock()- start_etape)

        # ------------ main point loop ----------------------
        # last check: redo targets for matrix output when observer point is not in the matrix center  
        elif x_offset == 0 or y_offset == 0 or x_offset2 == raster_x_size or y_offset2 == raster_y_size:
            targets= bresenham_circle(x,y,radius_pix)
        else: targets = target_list # standard circle, will save some time not to do it each time...
        
        matrix_vis = visibility (x, y, targets, output_options[0], 
				z_target, mask = (Target_layer))
        
        if output_options[0] == "Intervisibility": #skip raster stuff
            if matrix_vis : # it'a list actually..
                for n in matrix_vis:
                    n[1] += x_offset #each new point, new offsets...
                    n[2] += y_offset
                    connection_list.append([id1, x + x_offset ,y + y_offset]+ n)
        else:
            # ~~~~~~~~~~~~~~~ Finalizing raster output ~~~~~~~~~~~~~~~~~~~~~~~
            out=str(output + "_" + str(id1))
            
            #OUTPUT is generic: x, y, error, value
  ##          v = sorted(vis, key=itemgetter(0,1,2)) #sort on x,y and error
            
            if output_options[0] in ['Binary','Horizon']: num_format=gdal.GDT_Byte
            else : num_format=gdal.GDT_Float32
     
            if output_options [1] == "cumulative":               
                matrix_final [ y_offset : y_offset + matrix_vis.shape[0] ,
                               x_offset : x_offset + matrix_vis.shape[1] ] += matrix_vis
            else:
                
                file_name = out + "_" + output_options[0]

                success = write_raster (matrix_vis, file_name, gdal_raster.RasterXSize, gdal_raster.RasterYSize,
                                        x_offset, y_offset, gt, projection, num_format)
                if success : out_files.append(success)
                else: QMessageBox.information(None, "Error writing file !", str(file_name + ' cannot be saved'))

                matrix_vis= None
                    
		
    start_etape=time.clock()

    #exiting the main points loop : write cumulative....
    if output_options [1]== "cumulative":
        success = write_raster (matrix_final, output+'_cumulative',gdal_raster.RasterXSize, gdal_raster.RasterYSize,
                                0, 0, gt, projection)
        if success : out_files.append(success)
        else: QMessageBox.information(None, "Error writing file !", str(output + '_cumulative cannot be saved'))

    if output_options[0]=="Intervisibility":
        success = write_intervisibility_line (output, connection_list, Obs_layer.crs())
        if success : out_files.append(success)

        if not success : 1# do something smart ?

    
    matrix_final = None; data = None; connections_list=None; v=None; vis=None
    test_rpt += "\n Total time: " + str (time.clock()- start)
    #QMessageBox.information(None, "Timing report:", str(test_rpt))

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
    
    dst_ds.GetRasterBand(1).WriteArray(matrix,offset_x,offset_y)#offset=0
    #outBand.SetNoDataValue(-99)
    dst_ds=None
    #driver.GDALClose(dst_ds) not working!
    return file_name +'.tiff'

def write_intervisibility_line (file_name, data_list, coordinate_ref_system):

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
    
    half_pix= pix/2 #global variable pix
   
    for r in data_list:
        # create a new feature
        feat = QgsFeature()
        l_start=QgsPoint(raster_x_min  + r[1]*pix + half_pix, raster_y_max - r[2]*pix - half_pix )
        l_end = QgsPoint(raster_x_min  + r[4]*pix + half_pix, raster_y_max - r[5]*pix - half_pix)
         
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
