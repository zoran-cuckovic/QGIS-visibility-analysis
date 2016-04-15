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

def error_matrix(radius):
    
    mx_index= numpy.zeros((radius + radius/2, radius +radius/2, 4))
    #number of lines (smaller than radius because y is on the circle!)

    min_err = {}
        
    lst8=[[0, radius]] #add horizontal line first
	
    f = 1 - radius
    ddf_x = 1
    ddf_y = -2 * radius
    x = 0
    y = radius
    
    while x < y:
        if f >= 0:
            y -= 1
            ddf_y += 2
            f += ddf_y
            
        x += 1
        ddf_x += 2
        f += ddf_x
        
		#circle_rim
        lst8.append([x,y])
        lst8.append([x,y-1]) #IMPORTANT FOR GOOD COVERAGE
  
    j=0
    for k in lst8: #fill lines from center to the rim
        
        x_f, y_f = radius,radius #=x0,y0
        #dy = x; dx = y 
        dy,dx=k #SWAPPED x and y! MESSY
        #x and y = delta x and y but y is steep!
        #fist line is min y then it ascends till 45°
       
        D=0
        for i in xrange (0, dx ):        
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

            mx_index[j,i,2]=e
  
            try:
                err_old = min_err[yx][0] 
                if err < err_old: min_err[yx]=[err,j,i]
            except:
                min_err[yx]=[err,j,i]
   
        j+=1
             
        
    #check minimum errors
    for key in min_err:
        ix=min_err[key][1:3]
        er = min_err[key][0]         
        mx_index[ix[0], ix[1]][3]= 1

    return mx_index #[numpy.all(mx_index != 0, axis = 0)]#skip zero lines
    
   




def Viewshed (Obs_points_layer, Raster_layer, z_obs, z_target, radius, output,
              output_options,
              Target_layer=0, search_top_obs=0, search_top_target=0,
              z_obs_field=0, z_target_field=0,
              curvature=0, refraction=0):


        
    def search_top_z (pt_x, pt_y, search_top): #shoud be a separate loop for all points ?

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

    mx_vis = numpy.zeros ((full_window_size, full_window_size)) 

    temp_x= ((numpy.arange(full_window_size) - radius_pix) * pix) **2
    temp_y= ((numpy.arange(full_window_size) - radius_pix) * pix) **2

    mx_dist = numpy.sqrt(temp_x[:,None] + temp_y[None,:])

    if curvature:
        mx_curv = (temp_x[:,None] + temp_y[None,:]) / Diameter 
    

    if output_options[1] == "cumulative":
        matrix_final = numpy.zeros ( (gdal_raster.RasterYSize, gdal_raster.RasterXSize) )
    else:   mx_vis[:] = numpy.nan # set to nan so that it's nicer on screen ...
    
        
    #index matrix
    t= error_matrix(radius_pix)

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

    mx_x_rev = numpy.subtract ( t[:,:,1], (t[:,:,1]-x0) *2 , dtype=int )
    mx_y_rev = numpy.subtract ( t[:,:,0], (t[:,:,0]- y0) *2, dtype = int)
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
            x,y,z_UNUSED = search_top_z (x, y, search_top_obs)
            
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
                    x2,y2,z2 = search_top_z (x2,y2, search_top_target)
                    x2_geog, y2_geog= raster_x_min  + x2 * pix + pix/2 , raster_y_max - y2 *pix - pix/2

                x2 = radius_pix + (x2 - x); y2 = radius_pix + (y2 - y)

                if x2==x and y2==y : continue #skip same pixels!
                
                #this eliminates distance calculation for each point (delta x + delta y < radius is always OK)
                if x2 + y2 > radius_pix:
                    if round(dist(radius_pix,radius_pix,x2,y2)) > radius_pix :
                        continue

                delta_z=0
                if z_target_field: #this is a clumsy addition so that each point might have it's own height
                    try: delta_z = float(feat2[z_target_field])- z_target
                    except: pass 
                
                targets.append ([x2,y2, delta_z, id2, x2_geog, y2_geog])

      
        # ------------visibility calculation in main point loop ----------------------

        #np.take is  much more efficient than using "fancy" indexing (stack overflow says ...)
        
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

                        interp = data[mx,my] + (data[me, my]-data[mx,my] ) * numpy.absolute(mx_err)                    
                    else: 
                        interp = data[mx,my] + (data[mx, me] -data[mx,my] ) * numpy.absolute(mx_err)
                    
                        
                    test_val = numpy.maximum.accumulate(interp, axis=1)

                    if z_target: interp = mx_target[mx,my] #cheat here - test aginst target mx 
                            #target is non-interpolated !!
             
                    if output_options[0]== "Fast": #skip interpolation
                        #NOT WORKING needs to overide interpolation above, needs one more if-else...
                        v = data[mx,my] == numpy.maximum.accumulate(data[mx,my], axis=1)
##                        
                    elif output_options[0]== "Binary":
                        v = interp >= test_val

                    elif output_options[0] in ["Invisibility" ,"Intervisibility"]:
                        v = interp - test_val
                        #Should it be DATA - accum or interpolated - accumul ??

                    elif output_options[0]== "Horizon":
                        #SOLUTION = http://stackoverflow.com/questions/4494404/find-large-number-of-consecutive-values-fulfilling-condition-in-a-numpy-array
                        v = numpy.diff((interp >= test_val).astype(int))
##                            # 1: make = True/False array;
##                            # 2: turn to integers because boolean operations give True False only
##                            # 3 diff = x(i)- x(i-1) = -1 or 1 for breaks
 
                        v[v==1]=0 #delete the beginning of  visible areas                              
                        
                    mx_vis [mx[mask], my[mask]]= v[mask]#mx_err[mask]
                    
        
        if output_options[0]== "Invisibility":
            mx_vis *= mx_dist
            mx_vis[radius_pix,radius_pix]=z_target
            #this is neccesary because the target matrix is not interpolated!
            mx_vis[mx_vis>z_target]=z_target
        elif output_options[0]== "Binary":
            mx_vis [radius_pix,radius_pix]=1
        elif output_options[0]== "Intervisibility":
            #to make it fast : for each pair choose matrix in-between
            #e.g. linspace + stretch or y = m * x[:, np.newaxis] + b (y =m*x +b...)
            for x2,y2,z2,id2,x2_geo, y2_geo in targets:
                
                d=mx_dist[y2,x2]
                z_angle = z2/d if z2 else 0
                vis  = mx_vis[y2,x2]  + z_angle #z2 is only a difference - main target angle is set up as usual
                z_object= z_target+ z2
                
                hgt= vis * d
                if hgt > z_object: hgt = z_object
                      
                visib_list.append([id2, x2_geo, y2_geo, vis>=0,  hgt, d])#, err=0 
                
                
        matrix_vis = mx_vis
       
        if output_options[0] == "Intervisibility": #skip raster stuff
            if visib_list : 
                for n in visib_list:
                    connection_list.append([id1, x_geog ,y_geog]+ n)
        else:
            # ~~~~~~~~~~~~~~~ Finalizing raster output ~~~~~~~~~~~~~~~~~~~~~~~
            out=str(output + "_" + str(id1))
              
            if output_options[0] in ['Binary','Horizon']: num_format=gdal.GDT_Byte
            else : num_format=gdal.GDT_Float32

            if output_options [1] == "cumulative":               
                matrix_final [ y_offset : y_offset + window_size_y,
                               x_offset : x_offset + window_size_x ] += matrix_vis [
                                   y_offset_dist_mx : y_offset_dist_mx +  window_size_y,
                                    x_offset_dist_mx : x_offset_dist_mx + window_size_x]
    
            else:
                
                file_name = out + "_" + output_options[0]

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
        progress_bar.setValue(progress) #(progress / feature_count) * 100 = percentage - losing time :)	

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
   # QMessageBox.information(None, "Timing report:", str(test_rpt))
    
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


