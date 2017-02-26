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

import numpy
from math import sqrt, degrees, atan, atan2, tan

from Points import Points



def dist(x1,y1,x2,y2, estimation=False):
    if not estimation: r=sqrt(pow((x1-x2),2) + pow((y1-y2),2))
    else: # error = cca 1% - NOT USED!
        rt= 1.4142135623730950488016887242097
        r = (abs(x1-x2) * rt + abs(y1-y2) * rt) / 2

    return r


def dem_chunk (x, y, radius_pix, gdal_open_raster, square = True):

               
        # raster is open gdal raster ! for speed (?)
        
        raster_y_size = gdal_open_raster.RasterYSize
        raster_x_size = gdal_open_raster.RasterXSize
        
        if x <= radius_pix:  #cropping from the front
            x_offset =0
            x_offset_dist_mx = radius_pix - x
        else:               #cropping from the back
            x_offset = x - radius_pix
            x_offset_dist_mx= 0
                            
        x_offset2 = min(x + radius_pix +1, raster_x_size) #could be enormus radius, so check both ends always
            
        if y <= radius_pix:
            y_offset =0
            y_offset_dist_mx = radius_pix - y
        else:
            y_offset = y - radius_pix
            y_offset_dist_mx= 0

        y_offset2 = min(y + radius_pix + 1, raster_y_size )

        window_size_y = y_offset2 - y_offset
        window_size_x = x_offset2 - x_offset

        if square:
            full_size = radius_pix *2 +1
            mx = numpy.zeros((full_size, full_size)) 
        
            mx[ y_offset_dist_mx : y_offset_dist_mx +  window_size_y,
              x_offset_dist_mx : x_offset_dist_mx + window_size_x] = gdal_open_raster.ReadAsArray(
                  x_offset, y_offset, window_size_x, window_size_y).astype(float)
        else:

            mx = gdal_open_raster.ReadAsArray(x_offset, y_offset, window_size_x, window_size_y).astype(float)
        

        return mx, [x_offset, y_offset, x_offset_dist_mx, y_offset_dist_mx,
                    window_size_x, window_size_y]


def error_matrix(radius, size_factor=1):

    """
    Create a set of lines of sight which can be reused for all calculations. 
    Each line (departing from the observer point) has its target and a set of pixels it passes through.
    Only 1/8th of full radius is enough : the rest can be copied/mirrored. 
    """

    
    if size_factor == 0: size_factor = 1 #0 is for non-interpolated algo...
    radius_large = radius  * size_factor  
                                                
    mx_index= numpy.zeros((radius_large +1 , radius, 2)).astype(int)
    mx_err = numpy.zeros((radius_large +1 , radius))
    mx_mask = numpy.zeros(mx_err.shape).astype(bool)

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

    mx_err_dir = numpy.where(mx_err > 0, 1, -1)
    mx_err_dir[mx_err == 0]=0 #should use some multiple criteria in where... 

    #take the best pixels  
    #cannot simply use indices as pairs [[x,y], [...]]- numpy thing...
    #cannot use mx : has a lot of duplicate indices

   
    mx_err_index = mx_index [:,:, 0] + mx_err_dir
                                # we do not need negative errors any more
    return mx_index, mx_err_index,numpy.absolute(mx_err), mx_mask





"""
    Single point viewshed function: works on a number of precalculated matrices: for speed
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

    mx_vis = numpy.ones(data.shape)#ones so that the centre gets True val

    # centre=error_matrix.shape[1]#= radius, not passed as argument and not required (..?)
   
    mx = indices[: ,:, 1]; my = indices[: ,:, 0]

    me_x, me_y = mx, indices_interpolation

    for steep in [False, True]: #- initially it's steep 0, 0

        if steep: #swap x and y
            # actually, me_x = mx, but unswapped!
            me_x, me_y = me_y , me_x 
            mx, my = my,mx 
            

        for quad in [1,2,3,4]:                

            #cca 700 nanosec per view - not that expensive ...
             
            #otherwise all possible indices can be precalculated
            #= some 12 matrices for x, y & err, which is ugly
            #... or calculate 'on the fly', but this could be expensive

            # TODO 3 * 2D matrix ! (3Ds are slower than 2D (eg. sorting))

            #... or try : flipping only axes x and y, not 4 quads = 3 options(?) 
            # if rev x: flip 1 (over [:] )
            # if rev_y: flip 2 (over second flip) : SPEED?
            
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
            test_val = numpy.maximum.accumulate(interp, axis=1)
            
            
            if target_matrix is not None: 
                # substitute target matrix, but only after test matrix is calculated
                interp = view_tg[mx,my] 

                if algorithm > 0: 
                
                # could be done only on "good pixels", those with minimal error !!
                # use mask on mx, my etc  - test for speed ...
                    interp += (view_tg[me_x, me_y] - interp) * error_matrix
     
            # non-interpolated, normal                  
           # v = data[mx,my] == numpy.maximum.accumulate(data[mx,my], axis=1)

           
            if option== "Binary":  v = interp >= test_val
            #if it's T/F then False is written as NoData by gdal (i.e. nothing is written)

            elif option == "Invisibility": v = interp - test_val

            elif option == "Angular_size":

                v=numpy.zeros(interp.shape)#This is INEFFICIENT           
                v[:, 1:] = numpy.diff(test_val)

                
            elif option == "Horizon": # = true or last horizon

                v = interp >= test_val
                #to avoid confusion because of hidden corners
                #problematic : cannot be un-masked for rectangular output!
                v[view_d >= radius_pix + 2]= False
                                           
                #select last pixel (find max value in a reversed array (last axis!)
                #argmax stops at first occurence
                #indices have to be re-reversed :)
                #gives a flat array of 1 index for each row (axis=1)
                rev_max = radius_pix - numpy.argmax(v[:, ::-1], axis=1) -1
                               
                v[:]=False

                #radius = row n° for fancy index (should be some nicer way...)

                
                v[ numpy.arange(radius_pix +1), rev_max.flat ] = True

                v[: , -1] = 0 #artifacts at borders (false horizons)
                #(all matrix edges are marked as horizon - if visibilty zone gets cut off there) 
                

           
                                         
            #mx_vis [mx[mask], my[mask]]= v[mask] #numpy.absolute(mx_err[mask]) for errors

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
        mx_line = numpy.zeros((dx_short))
        if interpolation:
            mx_neighbours = numpy.zeros((dx_short))
            mx_err = numpy.zeros((dx_short))

   
        for i in xrange (0, dx_short): 

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
            interp = numpy.max( mx_line + (mx_neighbours -  mx_line)
                           *  abs(mx_err / dx))

            height = ( h  - interp )*d

            if height > target_offset: height=target_offset
            #because it represents pixel height! 
                
            out.append( [tg, height >=0, height, d])

        else:
                     
            out.append( [tg, h > numpy.max(mx_line), -9999, d])
            
    return out


def Viewshed (Obs_points, Raster_layer, output,
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

     
    
    ##########################################
    # Prepare  progress Bar (after checking files etc)
    
    iface.messageBar().clearWidgets() #=qgis.utils.iface - imported module
    #set a new message bar
    progressMessageBar = iface.messageBar()

    progress_bar = QProgressBar()

        #pass the progress bar to the message Bar
    progressMessageBar.pushWidget(progress_bar)

   
    
    
    #Obs_layer=QgsMapLayerRegistry.instance().mapLayer(Obs_points_layer)
   
   #Obs_layer = QgsVectorLayer(Obs_points_layer, 'o', 'ogr')


    ###########################"
    #read data, check etc
    out_files=[];rpt=[]

    # RasterPath= str(QgsMapLayerRegistry.instance().mapLayer(Raster_layer).dataProvider().dataSourceUri())

        
    gdal_raster=gdal.Open(Raster_layer)
    gt=gdal_raster.GetGeoTransform()
    projection= gdal_raster.GetProjection()
    pix=gt[1] 
    raster_x_min = gt[0]
    raster_y_max = gt[3] # it's top left y, so maximum!

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




    points = Obs_points.pt

    radius_float = Obs_points.max_radius; radius_pix = int(radius_float)

     #could be set to 100, making it easy to work with percentage of completion
    progress_bar.setMaximum(len(points)) 


    #set a counter to reference the progress, 1 will be given after pre-calculations
    progress = 0
        

    #pre_calculate distance matrix
           
    full_window_size = radius_pix *2 + 1
    
    temp_x= ((numpy.arange(full_window_size) - radius_pix) ) **2
    temp_y= ((numpy.arange(full_window_size) - radius_pix) ) **2

    mx_dist = numpy.sqrt(temp_x[:,None] + temp_y[None,:])
     
    if curvature:
        Diameter, refraction = curvature
        mx_curv = (temp_x[:,None] + temp_y[None,:]) / (Diameter/pix) #distances are in pixels !!
        mx_curv *= 1 - refraction


    #initialize empty list
    #network has to be already made !
    if output_options[0]=="Intervisibility":
        points2 = Target_points.pt
        connection_list=[]
    else:
        #index matrix: not used for intervisibility, raster only
        mx_indices, mx_err_indices, mx_err, mask = error_matrix(radius_pix, algorithm)
        # for speed : precalculate maximum mask - can be shrunk for lesser diameters ...
        mask_circ_max = mx_dist [:] > radius_float 
        if output_options[1] == "cumulative":
            matrix_final = numpy.zeros ( (raster_y_size, raster_x_size) )
        #else:   mx_vis[:] = numpy.nan # set to nan so that it's nicer on screen ...

   

    # ----------------- POINT LOOP -------------------------

    for id1 in points :

         # x,y, EMPTY_z, x_geog, y_geog = points[id1] #unpack all = RETURNS STRINGS ??
        
        x,y= points[id1]["x_pix"],  points[id1]["y_pix"]
        
        #gives full window size by default
        data, cropping = dem_chunk ( x, y, radius_pix, gdal_raster) 
        
        (x_offset, y_offset,
         x_offset_dist_mx, y_offset_dist_mx,
         window_size_x, window_size_y) = cropping 
        
        z= points[id1]["z"]; z_targ= points[id1]["z_targ"]
        z_abs = z + data [radius_pix,radius_pix] 

        if points[id1]["radius_float"] != radius_float:
            mask_circ = mx_dist [:] > points[id1]["radius_float"]         
        # this is to reduce unnecessary numpy query for each point
        # everything else is made on maximum radius !
        else: mask_circ = mask_circ_max

        
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
                            distance_matrix = mx_dist, target_matrix=mx_target,
                                     cover_matrix=mx_cover)

      

            if output_options[0]== "Invisibility":
            # = OPTION ANGLE ZA ALGO : angle diff , angle incidence ???
                
                matrix_vis *= mx_dist 
                # assign target height to the centre (not observer !)
                # = first neigbour that is always visible
                matrix_vis[radius_pix,radius_pix]=matrix_vis[radius_pix,radius_pix+1]
                
                
               
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
        success = write_intervisibility_line (output, connection_list, Obs_points.crs)
        if success : out_files.append(success)

        else : QMessageBox.information(None, "Error writing file !", str(output + '_intervisibility cannot be saved'))

    
    matrix_final = None; data = None; connections_list=None; v=None; vis=None

#TESTING #################
    prof.disable()
    test_rpt += "\n Total time: " + str (time.clock()- start)
    QMessageBox.information(None, "Timing report:", str(test_rpt))

    import pstats, StringIO
    s = StringIO.StringIO()
   
    ps = pstats.Stats(prof, stream=s).sort_stats('cumulative')
    ps.print_stats()
    print s.getvalue()
##########################
    
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


