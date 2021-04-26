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


import os
#from osgeo import osr, gdal, ogr

import time

import numpy as np
from math import sqrt

from . import Points as pts
from . import Raster as rst

from qgis.core import QgsMessageLog # for testing


BINARY = 0
DEPTH = 1
HORIZON = 2
HORIZON_FULL = 3
ANGLE = 4
INTERVISIBILITY = 5 # not used: separate function!

HORIZON_PROJECTION = 6
ANGULAR_SIZE = 7



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
    1/8th of full radius is enough : the rest can be copied/mirrored. 
    """

    if size_factor == 0: size_factor = 1 #0 is for non-interpolated algo...
    radius_large = radius  * size_factor  
                                                
    mx_index= np.zeros((radius_large +1 , radius, 2)).astype(int)
    mx_err = np.zeros((radius_large +1 , radius))
    mx_mask = np.zeros(mx_err.shape).astype(bool)

    j=0 #keep 0 line empty
    
    for m in range (radius_large+1 ): # 45 deg line is added (+1) 

        x_f, y_f = radius, radius #x0,y0

        #dy = x; dx = y 
        dy,dx= m, radius_large #SWAPPED x and y! MESSY

    
        #x and y = delta x and y but y is steep!
        #first line is min y then it ascends till 45°

        D=0
        for i in range (radius ):   #restrict iteration to actual radius!     
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
#             
        j+=1
        
    # find minimum errors per pixel
    old_pixel, min_value =mx_index[0,0] , 1 # initalise 
    # iterate column-wise !
    for i in range ( radius ): 
        for j in range (radius_large+1): 
            
            index = (j,i)
        
            pixel = mx_index[index]
                
            if np.any(pixel != old_pixel): 
                mx_mask[min_index] = True
                min_value = 1
                
            old_pixel = pixel
            
            v = abs(mx_err[index])
            if v < min_value : 
                min_value, min_index = v, index
        
        
    mx_err_dir = np.where(mx_err > 0, 1, -1)
    mx_err_dir[mx_err == 0]=0 #should use some multiple criteria in where... 
    

    #take the best pixels  
    #cannot simply use indices as pairs [[x,y], [...]]- np thing...
    #cannot use mx : has a lot of duplicate indices

    mx_err_index = mx_index [:,:, 0] + mx_err_dir
                                # we do not need negative errors any more
    return [np.absolute(mx_err),  mx_mask, mx_index, mx_err_index]


"""
    Single point viewshed function: works on a number of precalculated matrices: for speed.
    Takes prepared errors and indices of best pixels (with least offset from line of sight)
    Cannot be much simplified (?) - without loosing speed...
    Note that only 1/8 of the entire analysed zone is enough for interpolation etc,
    the rest is filled by flipping arrays.

in : point class, raster

    
""" 
def viewshed_raster (option, point, dem, interpolate = True):


    distance_matrix = dem.mx_dist    

    error_matrix, error_mask, indices, indices_interpolation = dem.error_matrices
    
    dem.open_window (point["pix_coord"])
    data = dem.window
    
    z_observer = point["z"]
    
    center = (dem.radius_pix, dem.radius_pix)
    
    z_abs = z_observer + data [center]
        
    # level all according to observer (Earth curvature is dealt with in the Raster class)
    data -= z_abs

    target_matrix= None   
    try :
        if point["z_targ"] >0:
            target_matrix = (data + point["z_targ"]) / distance_matrix
    except: pass
                            

    data /= distance_matrix #all one line = (data -z - mxcurv) /mx_dist
    #NB : there can be some divisions by zero, but these are OK
    #(it wouldn't be ok for [some value] /= data ! )


    #np.take is  much more efficient than using "fancy" indexing 
    #... but it flattens arrays : https://stackoverflow.com/questions/11800075/faster-numpy-fancy-indexing-and-reduction
    

     #if np.ones then the centre gets True val
    if option == BINARY: mx_vis = np.ones(data.shape)
    
    else: mx_vis = np.zeros(data.shape)


    if option == HORIZON_PROJECTION: mx_temp = np.copy(mx_vis)
  
    
    # Horizon is the last visible zone before the edge of the window
    # need to remove the data from corners (if a circular analysis is required !)
    # has to be done here because of varying radius
    if option in [HORIZON, HORIZON_FULL]:
        data [distance_matrix >= point["radius"] + 2] = np.nan #np.min(data)
   
    mx, my = indices[: ,:, 1], indices[: ,:, 0]

    mx_best, my_best = mx[error_mask], my[error_mask] 

    me_x, me_y = mx, indices_interpolation #me_x = mx !

    # flipping ang flopping data so that it fits indices matrix
    # (rather than producing multiple index matrices )
    views = [ np.s_[:], np.s_[ :, ::-1],
              np.s_[ ::-1, :], np.s_[ ::-1, ::-1] ]
       
    #interp = np.zeros(mx.shape) #initialise for speed ?

    for steep in [False, True]: #- initially it's steep 0, 0

        if steep: #swap x and y
            
            me_x, me_y = me_y , me_x 
            mx, my = my,mx
            mx_best, my_best = my_best, mx_best

        
        for view in views:                

            view_d = data[view]
            view_o = mx_vis[view]              
           
            interp = view_d [mx,my]  #np.take(, axis = 1]
            
            if interpolate:
                interp += (view_d[me_x, me_y] - interp) * error_matrix  
                           
            # do it here so we can subsitute targets below!
            test_val = np.maximum.accumulate(interp, axis=1)
            
            
            if isinstance(target_matrix,np.ndarray):

                view_tg = target_matrix[view]
                # substitute target matrix, but only after the test matrix is calculated!
                interp = view_tg[mx,my] 

                if interpolate: 
                
                # could be done only on "good pixels", those with minimal error !!
                # use mask on mx, my etc  - test for speed ...
                    interp += (view_tg[me_x, me_y] - interp) * error_matrix
     
            # non-interpolated, normal                  
           # v = data[mx,my] == np.maximum.accumulate(data[mx,my], axis=1)

            if option == DEPTH: v = interp - test_val
            else: v = interp >= test_val

            if option == HORIZON:
            #select last pixel (find max value in a reversed array (last axis!)
                #argmax stops at the first occurence
                #indices have to be re-reversed :)
                #gives a flat array of 1 index for each row (axis=1)
                
                rev_max = dem.radius_pix - np.argmax(v[:, ::-1], axis=1) -1
                               
                v[:] = False

                #radius = row n° for fancy index (should be some nicer way...               

                v[ np.arange(dem.radius_pix +1), rev_max.flat ] = True


            #np.compress faster than simple boolean mask.. ??
               
            view_o [mx_best, my_best] = v[error_mask] #       np.absolute(error_matrix[error_mask]) # for errors
            
    # delete areas that are outside max/min view angles (on the basis of the DEM).
    # we need to adjust for pixel based values
    # (This is not the most efficient approach, 
    #  np.maximum.accumulate has already sorted angles, but these values are not conserved...)
    try: 
        a1 = np.tan(np.radians(point["angle_up"])) * dem.pix   
        a2 = np.tan(np.radians(point["angle_down"])) * dem.pix
        mx_vis[np.logical_or(data > a1, data < a2)] = 0 
    except : pass
    

    if option == DEPTH:
        mx_vis *= - distance_matrix # - dist to get positive values for depth
        mx_vis[center, center]=0

    elif option == ANGLE:
        # data has already been divided by distances
        mx_vis = np.atan(data) * mx_vis
        mx_vis[center, center]= np.nan #THIS IS BAD : should handle better noData !!

    return mx_vis #np.degrees(np.arctan(data)) 

"""
Calculate intervisibilty lines from the observer point (always in the centre of the matrix)
to target point (x2, y2).
Has it's proper algorithm in order to avoid inaccuracies of the usual viewshed approach.

Option short: exclude the last pixel  
"""
def rasterised_line (x,y, x2, y2,
                     interpolation = True,
                     crop=0):

    
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

    dx_short = dx-crop  
    
    #store indices 1) los, 2) neighbours, 3) error
    mx_line = np.zeros((dx_short, 2), dtype=int)
    
    if interpolation:
        mx_neighbours = np.zeros((dx_short,2), dtype=int)
        mx_err = np.zeros((dx_short))
        msk = np.ones((dx_short),dtype=bool)


    for i in range (0, dx_short): 

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
        
  
        # --------- coordinates not unpacked ! ------------
        
        mx_line[i, :] = [y, x] if not steep else [x, y] 
      
        if interpolation:
 
            if D:
                sD = -1 if D < 0 else 1
                interp = y + sy *sD

                if steep:
                    mx_neighbours[i, :] = x, interp
                else:
                    mx_neighbours[i, :] = interp, x

                mx_err [i]=D 
  
            else:   msk[i]=False

    if interpolation:
        #give zero-error points themselves as neighbours
        # NB. this is not needed because error is 0; the result *= 0,
        # but it's more clear this way, and will eliminate the possibility of stepping out of matrix
        mx_neighbours[~msk, :]= mx_line[~msk, :]
        
        #error is actually D / dx !
        mx_err[msk]/= dx # zero values will give nans on division!
        return mx_line, mx_neighbours, abs(mx_err)
    
    else: return mx_line
            

"""
Calculates intervisibility lines

Assigns values to targets inside the passed dictionary (points_class)

"""

def intervisibility (point_class, raster_class, interpolate = False):
  
    
    p=point_class

    try: tgs = p["targets"]
    except: return None

    x,y= p["pix_coord"];  z= p["z"]
    
          
    mx_dist = raster_class.mx_dist

    radius_pix = raster_class.radius_pix
    
        # radius is in pixels !
        #r=  points[id1]["radius"]
        #r_pix= int (r)

     
    raster_class.open_window ((x,y))
    data= raster_class.window
        
    z_abs = z + data [radius_pix,radius_pix]
        
        # level all according to observer
    data -= z_abs
           
    data /= mx_dist


    for id2 in tgs:
            #adjust for local raster (diff x)
        x2, y2 = tgs[id2]["pix_coord"]

        try: z_targ = tgs[id2]["z_targ"]
        except : z_targ = 0

        # special case : zero or one pixel distance
        if x-1 <= x2 <= x+1 and y-1 <= y2 <= y+1:
            tgs[id2]["depth"]=z_targ
            continue
  
        # x2 = (x2 - x) + radius_pix 
        x2 -= x - radius_pix
        y2 -= y - radius_pix

        # bare terrain, without the target !
        angle_targ = data[y2,x2] 

        d = mx_dist[y2,x2]

        if interpolate:
            mx_line, mx_neighbours, mx_err = rasterised_line (
                                    radius_pix, radius_pix, x2, y2,
                                    interpolation= True,
                                    crop = 1)

        else:
            mx_line = rasterised_line (
                                    radius_pix, radius_pix, x2, y2,
                                    interpolation= False,
                                    crop = 1)
                
        l_x, l_y = mx_line[:,1], mx_line[:,0]

        angles = data[l_y,l_x]

        if interpolate:
            n_x, n_y = mx_neighbours[:,1], mx_neighbours[:,0]
            angles +=  (data[n_y, n_x] - angles) * mx_err

        # bare terrain!
        # target pixel is not calculated (crop =1)!
        depth = (angle_targ - np.max(angles)) * d
              
        # correct with target height only for invisible terrain,
        # otherwise it adds to relative pixel height
        
        tgs[id2]["depth"]= z_targ if depth >= 0 else depth + z_targ
    




def visibility_index (raster, obs_height,
                       target_height = 0,
                       sample = 0,
                       direction=0,
                       interpolate = 0,
                       mask = None,
                       feedback = None,
                       option = None):

    """
    Calculate visual exposition/control for all terrain locations (DEM pixels).
    Uses matrix translations, no viewpoints need to be specified. 
    (aka Total viewshed)
    """
    

    # find two matching matrix views
    def slice_crop (flip, point, size, crop_border = False):

        start, sf = (1, 1) if crop_border else (0,0)
        
        a = slice(point , size - sf) 
        b = slice(start, size - point)

        return (b, a ) if flip else (a, b)      
                    

    def interpolate_heights(raster, offset, x_axis = False, difference_only = False):
            """
            We use raster offset where y axis is descending  
            (positive offset = down or right)
            """
                  
            if x_axis:  view_in, view_off = np.s_[: , :-1], np.s_[ : , 1 :]
            else:       view_in, view_off = np.s_[:-1 , :],np.s_[ 1 : , :] 
                        
            if offset < 0: view_in, view_off = view_off, view_in

            diff = raster[view_off] - raster[view_in]
                                    
            if difference_only:  
                #create a copy !!
                #perhaps not smart, but fool-proof ...
                out = np.zeros(raster.shape)
                out[view_in] = diff
            else:
                out = np.copy(raster)
                out[view_in] += diff * abs(offset)

            return out               
                    
    start = time.process_time()
    
    data = raster.open_raster()
 
    ysize, xsize = data.shape
    
    # pixel distances
    radius = raster.radius / raster.pix

    d = int(radius)

    # precalculated distances 
    # must be in pixel distances!    
    mx_dist = raster.mx_dist [d:, d:]

    step = radius / (sample / 8)
    
    # border targets (without one corner pix)    
    # attention! +d is never included - to avoid duplicates on corners
    b = np.arange(-d, d, step)
    #add a dimension for x
    b= np.stack((b, np.zeros(b.size)), axis = -1)
    b[:,1] = d # x targets

    end_offsets = np.vstack(( b,
                b[:, ::-1] * [1, -1],
                b *[-1, -1],
                b[:, ::-1] * [-1, 1] )).astype(int)
  
    
    out = np.zeros(data.shape)
    temp_z1 = np.zeros(data.shape)
    temp_z2 = np.zeros(data.shape)

    mx_norm = np.zeros(data.shape) #not ones !
        
    cnt = 0 #progress tracking

    for p in end_offsets:
         
        y2,x2 = p
               
        flip_x, flip_y, steep = x2 < 0, y2 < 0, abs(y2) > abs(x2)
                        
        temp_z2 [:] = -999999999999
        
        line, neighbours, errors = rasterised_line (0,0, x2, y2,
                                                           interpolation = True)              
        
        if interpolate:
            
            # APPROXIMATION - average error (except for sample 16 - all errs = 0,5)
            # TO TEST :  err = errors.sum() / np.count_nonzero(errors)
            
            err =  1 # offset only ! 
            # positive error : down/right
            interp_down = interpolate_heights(np.copy(data),  err,  steep, difference_only = True )
            interp_up = interpolate_heights(np.copy(data),  - err ,  steep, difference_only= True)
            # true interpolation needs to be hardcoded - can be done for 16 lines (min 2 matrices - max 4),
            # but for 32 we need min 4 - max 8 matrices  
            
            if (flip_x and steep) or (flip_y and not steep):
                interp_up, interp_down = interp_down, interp_up

        """
        Absolute values are used !
        We are only interested in relative shifts, not in actual coords.
        In fact, we can only use 1/8th of targets and then flip axes.
        (... but then the LOS can't be customised...)
    
        """        
        for y,x in np.abs(line): 

            dist = mx_dist [y, x] 
             
            i= max(x,y)-1 #index inside the line
            e= errors[i]      

            if x> xsize or y> ysize or dist > radius : break
       
            # a= slice(sy_a, sx_a); b=slice(sy_b, sx_b) -- not working!
            y_a, y_b = slice_crop (flip_y, y, ysize)
            x_a, x_b = slice_crop (flip_x, x, xsize)
            
            a = np.s_[y_a, x_a]
            b = np.s_[y_b, x_b]
            
            heights = temp_z1[a] # it's a view, reusing the matrix !
            heights[:] = data[a]
            
            old_heights = temp_z2[b] # same
            
            if interpolate and e :
                
                y_i, x_i = np.abs(neighbours[i])
                
                if (y_i- y) + (x_i - x)  > 0 : 
                #   one of the two is always 0 !
                # ! when x or y rises : go down or right
                    heights += interp_down[a] * e 
                else:
                    heights += interp_up[a] * e 
             
            # this is clumsy : curvature is assigned to master window
            # (set before calling this function)
            try: curv = raster.curvature[d + y, d + x]
            except: curv = 0
            
           # a is shifted, b is the origin point    
            heights -= data[b] + ( obs_height + curv )
            
            heights /= dist
            
            visib = heights > old_heights
                   
            old_heights[visib] = heights [visib]
                
            # a = incoming, viewshed             
            # b = outgoing, observer perspective
            view, anti_view = (b, a) if direction else (a, b)
  
            f = (i + 1) * (8/ sample) # i begins with 0...
            """ 
            each step is representative of a vertical column of pixels
            for four lines (sample = 4) we cover step distance times 2, and so on...
            Remark that this is the same as dist * slope * 2
            where slope = np.tan(np.radians(360/sample))
            """
            out[view][visib] += f
            # this can (should) be precalculated ...
            mx_norm[view] += f        
            
            if feedback.isCanceled(): return None
            # line loop

        cnt += 1
        t = time.process_time()
        end = start + ( t - start) * (sample/cnt)
        info = '  \r{0} minutes left'.format(round((end-t)/60, 1)) 
        try:
            feedback.setProgressText(info)
            feedback.setProgress(cnt/sample * 100)
        except: pass    

    try: 
        QgsMessageLog.logMessage(" Finished: " + str( round( (time.clock() - start) / 60, 2)) +
                                 " minutes."  ,   "Viewshed info 2")
    except: pass

    out /= mx_norm

    return out




