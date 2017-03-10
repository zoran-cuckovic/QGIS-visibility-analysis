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
# TEST: points out of raster, raster rotated, raster rectnagular pixels

from __future__ import division 

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.utils import * #progress bar
import os
from osgeo import osr, gdal, ogr

import time
#_____Testing_____________
from cProfile import Profile

import numpy as np
from math import sqrt, degrees, atan, atan2, tan

from Points import Points
from Raster import Raster



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

    
    if size_factor == 0: size_factor = 1 #0 is for non-interpolated algo...
    radius_large = radius  * size_factor  
                                                
    mx_index= np.zeros((radius_large +1 , radius, 2)).astype(int)
    mx_err = np.zeros((radius_large +1 , radius))
    mx_mask = np.zeros(mx_err.shape).astype(bool)

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
                           
            #reverse x,y for data array!
            yx= (y_f,x_f)
            mx_index[j,i,0:2]=yx
                           
            if D: e=D/dx; err=abs(e)
            else: e, err = 0,0

            mx_err[j,i]=e
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
        mx_mask[ix[0], ix[1]]= 1

    mx_err_dir = np.where(mx_err > 0, 1, -1)
    mx_err_dir[mx_err == 0]=0 #should use some multiple criteria in where... 

    #take the best pixels  
    #cannot simply use indices as pairs [[x,y], [...]]- np thing...
    #cannot use mx : has a lot of duplicate indices

   
    mx_err_index = mx_index [:,:, 0] + mx_err_dir
                                # we do not need negative errors any more
    return mx_index, mx_err_index,np.absolute(mx_err), mx_mask


"""
    Single point viewshed function: works on a number of precalculated matrices: for speed.
    Takes prepared errors and indices of best pixels (with least offset from line of sight)
    Cannot be much simplified (?) - without loosing speed...
    Note that only 1/8 of the entire analysed zone is enough for interpolation etc,
    the rest is filled by flipping arrays.
    
"""
    
def viewshed_raster (option, data,                  
              error_matrix, error_mask, indices, indices_interpolation,                  
              target_matrix=None, algorithm = 1):


    #np.take is  much more efficient than using "fancy" indexing (stack overflow says ...)
    #... but it flattens arrays ! TODO...

    mx_vis = np.ones(data.shape)#ones so that the centre gets True val
   
    mx = indices[: ,:, 1]; my = indices[: ,:, 0]

    me_x, me_y = mx, indices_interpolation #me_x = mx ! 

    for steep in [False, True]: #- initially it's steep 0, 0

        if steep: #swap x and y
            
            me_x, me_y = me_y , me_x 
            mx, my = my,mx 
            

        for quad in [1,2,3,4]:                

            
            if quad == 1  :
                view = data [:]
                view_o = mx_vis[:]
                if target_matrix is not None: view_tg = target_matrix[:]
                
                
            elif quad == 4:
                view_o = mx_vis[ :, ::-1] 
                view = data [ :, ::-1] #y flip
                if target_matrix is not None: view_tg = target_matrix[ :, ::-1] 
                                
            elif quad == 2:
                view = data [ ::-1, :] #x flip
                view_o = mx_vis[ ::-1, :]
                if target_matrix is not None: view_tg = target_matrix[ ::-1, :] 
                         
            else          :
                view = data [::-1 , ::-1]
                view_o = mx_vis[::-1 , ::-1]
                if target_matrix is not None: view_tg = target_matrix[ ::-1, ::-1] 
                  

            interp = view[mx,my]
           

            if algorithm > 0: #do interpolation
                interp += (view[me_x, me_y] - interp) * error_matrix
           
                           
            # do it here so we can subsitute target below!
            test_val = np.maximum.accumulate(interp, axis=1)
            
            
            if target_matrix is not None: 
                # substitute target matrix, but only after test matrix is calculated
                interp = view_tg[mx,my] 

                if algorithm > 0: 
                
                # could be done only on "good pixels", those with minimal error !!
                # use mask on mx, my etc  - test for speed ...
                    interp += (view_tg[me_x, me_y] - interp) * error_matrix
     
            # non-interpolated, normal                  
           # v = data[mx,my] == np.maximum.accumulate(data[mx,my], axis=1)

           
            if option== "Binary":  v = interp >= test_val
            #if it's T/F then False is written as NoData by gdal (i.e. nothing is written)

            elif option == "Invisibility": v = interp - test_val

            elif option == "Angular_size":

                v = np.zeros(interp.shape)#This is INEFFICIENT           
                v[:, 1:] = np.diff(test_val)

                
            elif option == "Horizon": # = true or last horizon

                v = interp >= test_val
                #to avoid confusion because of hidden corners
                #problematic : cannot be un-masked for rectangular output!
                v[view_d >= radius_pix + 2] = False
                                           
                #select last pixel (find max value in a reversed array (last axis!)
                #argmax stops at first occurence
                #indices have to be re-reversed :)
                #gives a flat array of 1 index for each row (axis=1)
                rev_max = radius_pix - np.argmax(v[:, ::-1], axis=1) -1
                               
                v[:] = False

                #radius = row n° for fancy index (should be some nicer way...)

                
                v[ np.arange(radius_pix +1), rev_max.flat ] = True

                v[: , -1] = 0 #artifacts at borders (false horizons)
                #(all matrix edges are marked as horizon - if visibilty zone gets cut off there) 
                

           
                                         
            #mx_vis [mx[mask], my[mask]]= v[mask] #np.absolute(mx_err[mask]) for errors

            view_o [mx[error_mask], my[error_mask]]= v[error_mask] #view of mx_vis, NOT A COPY!

         
    return mx_vis


def intervisibility(point, source_dict, targets_dict, interpolation = True):

    """
    Calculate intervisibilty lines from the observer point (always in the centre of the matrix)
    to target point (x2, y2).
    Has it's proper algorithm in order to avoid inaccuracies of the usual viewshed approach.

    Interpolation can be avoided : no major improvement in time (cca 5%)!
    Bresenham's loop: < 5% time
    """

    out=[]

    x_pix = source_dict[point]["x_pix"]
    y_pix = source_dict[point]["y_pix"]
    
    
    
    for tg in source_dict[point]["targets"]:

        
        
        x2_pix = targets_dict[tg]["x_pix"]
        y2_pix = targets_dict[tg]["y_pix"]
        target_offset = targets_dict[tg]["z_targ"]

        #adjust for local raster
        x2 = radius_pix + (x2_pix - x_pix)
        y2 = radius_pix + (y2_pix - y_pix)


        h = data[y2,x2] #data : global
        d= mx_dist[y2,x2]#distances : global
       
        x,y = radius_pix, radius_pix #re-center point!
        
        dx = abs(x2 - x); dy = abs(y2 - y)
        steep = (dy > dx)
        #direction of movement : plus or minus in the coord. system
        sx = 1 if (x2 - x) > 0 else -1
        sy = 1 if (y2 - y) > 0 else -1

        if steep: # if the line is steep: change x and y
            #x,y = y,x they are the same !!
            
            dx,dy = dy,dx
            sx,sy = sy,sx
   
        D = 0
      
        #for interpolation
       # slope = dy / dx *sx *sy #!!
       #the operators for negative quadrants (we do need dx, dy as absolute to verify steepness, to search distances...)

        dx_short = dx-1 # to leave out the last pixel (target)
        
        #store indices 1) los, 2) neighbours, 3) error
        mx_line = np.zeros((dx_short))
        if interpolation:
            mx_neighbours = np.zeros((dx_short))
            mx_err = np.zeros((dx_short))

   
        for i in xrange (0, dx_short): 

        # ---- Bresenham's algorithm (understandable variant)
        # http://www.cs.helsinki.fi/group/goa/mallinnus/lines/bresenh.html       
            x += sx
            if 2* (D + dy) < dx:
                D += dy # y remains
            else:
                y += sy
                D += dy - dx
                           
            #unfortunately, np allows for negative values...
            # when x or y are too large, the break is on try-except below
            
# OVO NEMA SMISLA : BRISATI !!??
            if x < 0 or y < 0 : break
# '''''''''''''''''''''''''''''''''''''''''
      
            # --------- coordinates not unpacked ! ------------
            
            mx_line[i] = data[y, x] if not steep else data[x, y] 
          
            # for interpolation
            # D is giving the amount and the direction of error
            # because of flipping, we take y+sy, x+sx rather than y +/- 1  
            if steep: mx_neighbours[i]=data[x + sx if D > 0 else x - sx, y]
            else: mx_neighbours[i]=data[y + sy if D>0 else y - sy, x]
            
            mx_err [i]=D
                

        if target_offset: h += target_offset/d # raise h to target top
                
        if interpolation: 
            interp = np.max( mx_line + (mx_neighbours -  mx_line)
                           *  abs(mx_err / dx))

            height = ( h  - interp )*d

            if height > target_offset: height=target_offset
            #because it represents pixel height! 
                
            out.append( [tg, height >=0, height, d])

        else:
                     
            out.append( [tg, h > np.max(mx_line), -9999, d])
            
    return out


def Viewshed (Obs_points, Dem_raster, 
          output_options,
          Target_points=None,
          curvature=0, refraction=0, algorithm = 1): 


    """
    Opens a DEM and produces viewsheds from a set of points. Algorithms for raster ouput are all
    based on a same approach, explained at zoran-cuckovic.com/landscape-analysis/visibility/.
    Intervisibility calculation, however, is on point to point basis and has its own algorithm. 
    """
          

    ##### TESTING #########
    start = time.clock(); start_etape=start
    test_rpt= "Start: " + str(start)


    prof=Profile()

                   
    prof.enable()
    #########################

    
    #Obs_layer=QgsMapLayerRegistry.instance().mapLayer(Obs_points_layer)
   
   #Obs_layer = QgsVectorLayer(Obs_points_layer, 'o', 'ogr')


    ###########################"
    #read data, check etc
    out_files=[];rpt=[]

    # RasterPath= str(QgsMapLayerRegistry.instance().mapLayer(Raster_layer).dataProvider().dataSourceUri())


    points = Obs_points.pt

    # reading radius from points class !
    # this is maximum radius !! in pixel distance 
    radius_float = Obs_points.max_radius
    radius_pix = int(radius_float)
    old_radius = radius_float #for varying radius

    #pre_calculate distance matrix
           
    full_window_size = radius_pix *2 + 1
    
    temp_x= ((np.arange(full_window_size) - radius_pix) ) **2
    temp_y= ((np.arange(full_window_size) - radius_pix) ) **2

    mx_dist = np.sqrt(temp_x[:,None] + temp_y[None,:])


     
    if curvature:
        Diameter = Dem_raster.get_diameter_earth()
        mx_curv = (temp_x[:,None] + temp_y[None,:]) / (
                    Diameter / Raster.pix() ) #distances are in pixels !!
        mx_curv *= 1 - refraction 

    #initialize empty list
    #network has to be already made !
    if output_options[0] == "Intervisibility":
        points2 = Target_points.pt
        connection_list=[]
    else:
        #index matrix: not used for intervisibility, raster only
        mx_indices, mx_err_indices, mx_err, mask = error_matrix(radius_pix, algorithm)


        # TO BE REFINED
        # masking is used to achieve  doughnut shaped output, or to filter azimuths  etc...
        # >> masking function in raster class ?

        # for speed : precalculate maximum mask - can be shrunk for lesser diameters ...
        mask_circ = mx_dist [:] > radius_float

        if output_options [1] == "cumulative" :

            matrix_final = np.zeros( tuple(reversed(Dem_raster.size)) ) # y size fist!
            mask_fill = 0 
        else:
            mask_fill = np.nan
        
  
    # ----------------- POINT LOOP -------------------------

    for id1 in points :

         # x,y, EMPTY_z, x_geog, y_geog = points[id1] #unpack all = RETURNS STRINGS ??
        
        x,y= points[id1]["x_pix"],  points[id1]["y_pix"]
        
        #gives full window size by default
        
        Dem_raster.dem_window (x, y, radius_pix)
        # is this the rigt way to do this?
        # or make a function ??
        #this routine is also asigning offsets of data window - to the Raster class
        data=Dem_raster.window
        
        z= points[id1]["z"]; z_targ= points[id1]["z_targ"]
        z_abs = z + data [radius_pix,radius_pix]

        r= points[id1]["radius_float"]

        if old_radius != r:            # MESSY !!!
            mask_circ = mx_dist [:] > r
            old_radius = r
        # this is to reduce unnecessary np query for each point
        # everything else is made on maximum radius !    
        
        # level all according to observer
        if curvature: data -= mx_curv + z_abs
        else: data -= z_abs   

        data /= mx_dist #all one line = (data -z - mxcurv) /mx_dist

                
        if output_options[0]== "Intervisibility":
            
            #TODO : reading and passing stuff from points dictionary is unnecessary
            # drawing lines could be done from the points class, here only two Ids and results
          
            if not "targets" in points[id1] : continue
            
            x_geog, y_geog= points[id1]["x_geog"] , points[id1]["y_geog"]
                   
            tests = intervisibility ( id1, points, points2, algorithm )

            for t in tests:
                id2, visib, hgt, dist = t
            
           # find correct coordinates of new points - needed for intervisibilty only...
           
                x2_geog, y2_geog=points2[id2]["x_geog"] , points2[id2]["y_geog"]
  
        
              #  z2= points2[id2]["z_targ"]
            
                #append speed : not that critical
                connection_list.append([id1, x_geog ,y_geog, id2, x2_geog, y2_geog,
                                        visib, hgt, dist])
                
        
        else: # VIEWSHED
            
            if z_targ > 0 : mx_target = data + z_targ / mx_dist 
                            # it's ( data + z_target ) / dist,
                            # but / dist is already made above
            else: mx_target=None

            
            matrix_vis = viewshed_raster (output_options[0], data,
                            mx_err,   mask, mx_indices, mx_err_indices,
                             target_matrix=mx_target)

      

            if output_options[0]== "Invisibility":
            # = OPTION ANGLE ZA ALGO : angle diff , angle incidence ???
                
                matrix_vis *= mx_dist 
                # assign target height to the centre (not observer !)
                # = first neigbour that is always visible :) 
                matrix_vis[radius_pix,radius_pix]=matrix_vis[radius_pix,radius_pix+1]
                
            
  

            matrix_vis [mask_circ] = mask_fill


            if output_options [1] == "cumulative":
                #indices (slices) were assigned in the dem_window function
                matrix_final[Dem_raster.window_slice] += \
                        matrix_vis [Dem_raster.inside_window_slice]


              
    
        
    #####################################
##    #exiting the main points loop : write cumulative....
##    if output_options [1]== "cumulative":
##        success = write_raster (matrix_final, output+'_cumulative',gdal_raster.RasterXSize, gdal_raster.RasterYSize,
##                                0, 0, gt, projection)
##        if success : out_files.append(success)
##        else: QMessageBox.information(None, "Error writing file !", str(output + '_cumulative cannot be saved'))
##
##    if output_options[0]=="Intervisibility":
##        success = write_intervisibility_line (output, connection_list, Obs_points.crs)
##        if success : out_files.append(success)
##
##        else : QMessageBox.information(None, "Error writing file !", str(output + '_intervisibility cannot be saved'))

    
    data = None; connections_list=None; 

#TESTING #################
    prof.disable()
    test_rpt += "\n Total time: " + str (time.clock()- start)
    QMessageBox.information(None, "Timing report:", str(test_rpt))

    import pstats, StringIO
    s = StringIO.StringIO()
   
    ps = pstats.Stats(prof, stream=s).sort_stats('cumulative')
    ps.print_stats()
    # print s.getvalue()

    if output_options [1] == "cumulative" : return matrix_final
    else: return matrix_vis



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


