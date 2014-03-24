# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ViewshedAnalysis
                                 A QGIS plugin
 ------description-------
                              -------------------
        begin                : 2013-05-22
        copyright            : (C) 2013 by Zoran Čučković
        email                : /
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from __future__ import division #... the Python floating point bug...

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *#main
import os
from osgeo import osr, gdal, ogr
from array import * #????

import time 
import csv #ovo je super!
from operator import itemgetter #ovo je za sortiranje liste
import numpy
from math import sqrt, degrees, atan, atan2, tan

import numbers


def dist(x1,y1,x2,y2, estimation=False): 
    if not estimation: r=sqrt(pow((x1-x2),2) + pow((y1-y2),2))
    else: # error = cca 1%  -  NOT USED!
        rt= 1.4142135623730950488016887242097
        r = (abs(x1-x2) * rt + abs(y1-y2) * rt) / 2

    return r

def kut(x, y, center_x, center_y): #van uporabe
    angle = degrees(atan2(y - center_y, x - center_x))
    bearing1 = (angle + 360) % 360 #ovo je matematicki
    bearing2 = (90 - angle) % 360 #ovo je geografski!
    return bearing2


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
            #!! screen y descends
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


#works with global data array 
def visibility(x0, y0, z0_offset, target_list, target_offset=0, options = None, mask = False):
                                  #target_list : [x,y , (target_offset, target_id for intervisibility)]

    
    def target_angle (tg_offset, z_pt, distance):   # the idea is to avoid unnecessary calculation
                                                    # by providing this value only when needed,
                                                    # which makes a messy code ... 
        z_off = z_pt + tg_offset                   
        if z_off == z0: z_off = z0-0.001
        return (z_off-z0)/distance
    
    
    z0= data[y0,x0] + z0_offset  
    i=0
    ary=[]
    window_y = len(data); window_x = len(data[0])
    for n in target_list:
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

        slope = dy / dx  *sx *sy #!! the operators for negative quadrants (we do need dx, dy as absolute to verify steepness, to search distances...)

        #begins with the minimum possible angle for the observer pix,
        #thus the first pixel next to observer is always visible!
        visib = True  
        angle_block = -9999999999999999 
        insert_horizon=False

        for i in range(0, int(dx)): # dx is integter but not so for Python...

        # -------- linear equation (error estimation) --------
            if i == dx-1: #the target pixel is a special case
                x,y = x2,y2
                err=0; interpolated=0
            else:                
                x += sx
                y_dec = slope * (x-x2) + y2 
                y = int(round(y_dec)) #it considers rounded as float...
                err = y-y_dec

                interpolated = y-1 if err > 0 else y+1 #inverse : if the good pixel is above the line then search down
                                                    # we don't need to y+sy because the slope has already been multiplied by sy     
        # --------- unpack coordinates ------------
            if not steep:
                x_pix,y_pix = x,y 
                x_pix_interp, y_pix_interp = x, interpolated 
            else:
                x_pix,y_pix = y,x
                x_pix_interp, y_pix_interp = interpolated, x
                
            # we have to restrain the extents (1 additional for the interpolated value)
            if not window_x-1 > x_pix > 1 or not window_y-1  > y_pix > 1:  break

        # ------------- interpolation ----------------
            z = data[y_pix][x_pix]
            d = dist(x_pix,y_pix,x0,y0)
            
            if err : 
                z2= data [y_pix_interp][x_pix_interp]
                z = z + (z2 - z) * abs(err) #has to be absolute because of coordinate swapping
                
            if z == z0: z = z0-0.001 # BUG : division with zero

        # ------------ core calculation ----------------------
            angle = (z-z0)/d
            if angle <= angle_block: 
                # ------- target height calculation ----------------
                # speeding up: 
                # - evaluate invisible pixels only 
                # - in case of intervisibility restrain to the last pixel only                    
                if target_offset:
                    if options <> "Intervisibility" or (options == "Intervisibility" and i == dx-1): 
                        angle = target_angle(target_offset, z, d)
                visib = (angle > angle_block)
                
            else:
                visib = True
                angle_block = angle
                
        # -----------  skip all but the last one if mask is used ----------------- 
            if mask and i < dx-1: continue
            
        # --------------- processing output ----------------
            if options == 'Horizon':
                if i > 0: #skip first to intialise 'old' variable
                    if old_visib <> visib: #  break-points are all we need 
                        if visib: # passing from invisible  to visible
                            ary.append([last_x, last_y, abs(err), (d - last_dist) * pix ] )
                        else: # passing from visible to invisible : catch the breakpoint
                            last_x, last_y = x_pix, y_pix
                            last_dist = d
                old_visib = visib # catch the old value
                
                # add the -1 code to the "real" horizon (dx-1 = last pixel)
                if i == dx-1 and not visib: ary.append([last_x, last_y, 0, -1] )

            elif options == 'Binary':
                if visib: ary.append([x_pix,y_pix, abs(err), 1])

            elif options == 'Invisibility':
                if not visib: ary.append([x_pix,y_pix, abs(err), (angle - angle_block)* d])
                
        
        #out of inner loop : it registers the last pixel only
        if options =='Intervisibility':            
            if angle == angle_block: #if they are the same and visib=True the previous pixel was visible : target is entirely visible
                if visib: hgt = target_offset 
                else: hgt = 0 #may happen very rarely: angles exactly the same
            else: hgt = (angle - angle_block) * d
                   
            ary.append([id_target, x_pix, y_pix, visib, hgt, d])

    # the first pixel has not been registered...
    # when mask is provided the observer is not important!
    if options == 'Binary' and not mask: ary.append([x0,y0, 0, 1])
            
   # QMessageBox.information(None, "podatak:", str())          
    return ary


        
def Viewshed (Obs_points_layer, Raster_layer, z_obs, z_target, radius, output,
              output_options,
              Target_layer=0, search_top_obs=0, search_top_target=0,
              z_obs_field=0, z_target_field=0): 
    
    def search_top_z (pt_x, pt_y, search_top):
        z_top = data[pt_y,pt_x]
        x_top, y_top = pt_x, pt_y
        for i in range(pt_x - search_top, pt_x + search_top):
            for j in range(pt_y - search_top, pt_y + search_top):
                try: k = data [j, i] # it may fall out of raster
                except: continue
                if k > z_top: x_top,y_top,z_top = i,j,k
        return (x_top,y_top,z_top)
        

    start = time.clock(); start_etape=start
    test_rpt= "Start: " + str(start)
    
    out_files=[];rpt=[];connection_list=[]; intervisibility = False

    RasterPath= str(QgsMapLayerRegistry.instance().mapLayer(Raster_layer).dataProvider().dataSourceUri())
    
    gdal_raster=gdal.Open(RasterPath)
    gt=gdal_raster.GetGeoTransform()#daje podatke o rasteru (metadata)
    global data # set below, after choosing whether to read in chunks
    global pix; pix=gt[1]
    global raster_x_min; raster_x_min = gt[0]
    global raster_y_max ;raster_y_max = gt[3] # it's top left y, so maximum!

    input_raster_columns = gdal_raster.RasterYSize
    input_raster_rows = gdal_raster.RasterXSize

    raster_y_min = raster_y_max - input_raster_columns * pix 
    raster_x_max = raster_x_min + input_raster_rows * pix 

    #adfGeoTransform[0] /* top left x */
    #adfGeoTransform[1] /* w-e pixel resolution */
    #adfGeoTransform[2] /* rotation, 0 if image is "north up" */
    #adfGeoTransform[3] /* top left y */
    #adfGeoTransform[4] /* rotation, 0 if image is "north up" */
    #adfGeoTransform[5] /* n-s pixel resolution */

    radius_pix = int(round(radius/pix))

    gtiff = gdal.GetDriverByName('GTiff')#for creting new rasters
    projection = gdal_raster.GetProjection()
    rb=gdal_raster.GetRasterBand(1)#treba li to? 

    #progress report
    test_rpt += "\n GDAL functions : " + str (time.clock()- start_etape)
    start_etape=time.clock()

    Obs_layer=QgsMapLayerRegistry.instance().mapLayer(Obs_points_layer)
    if Obs_layer.isValid():
        # returns 0-? for indexes or -1 if doesn't exist
        obs_has_ID  = bool( Obs_layer.fieldNameIndex ("ID") + 1)
        read_chunks = True # some heuristic here (if raster size < ____ : False)
    else: return # abandon function
  
    if output_options == ["Binary","cumulative"]: 
        matrix_final = numpy.zeros ( (input_raster_columns, input_raster_rows) ) 
        # THIS IS BAD !!! a better handling of array addition is necessary
        # -> matrix_final[1:5,1:4] = matrix_final[1:5,1:4] + vis_matrix
        # http://stackoverflow.com/questions/9886303/adding-different-sized-shaped-displaced-numpy-matrices
        read_chunks=False  
        

    #initialise target points and create spatial index for speed
    if Target_layer:
        
        Target_layer=QgsMapLayerRegistry.instance().mapLayer(Target_layer)
        if Target_layer.isValid():
            
            targ_has_ID  = bool(Target_layer.fieldNameIndex ("ID") + 1)
            read_chunks = False   # also heuristic if raster size < _____ do it in chunks (too complicated...)

            targ_index = QgsSpatialIndex()
            for f in Target_layer.getFeatures():
                targ_index.insertFeature(f)
                
        else: return # abandon function

    if not read_chunks:
        data = gdal_raster.ReadAsArray()
        x_offset = 0; y_offset = 0

    #count features 
    #ViewshedAnalysisDialog.setProgressBar(self.dlg, vlayer.featureCount()) ???
   

    # -----------------  POINT LOOP  -------------------------
    
    for feat in Obs_layer.getFeatures():
        
        target_list=[]; vis=[]

        geom = feat.geometry()
        t = geom.asPoint()
        
        id1 = feat["ID"] if obs_has_ID else feat.id()       
        x_geog, y_geog = t[0], t[1]
        
        #check if the point is out of raster extents
        if raster_x_min < x_geog < raster_x_max and raster_y_min < y_geog < raster_y_max:   
            x = int((x_geog - raster_x_min) / pix) # not float !
            y = int((raster_y_max - y_geog) / pix) #reversed !
        else:
            QMessageBox.information(None, "podatak:", "tu je")
            continue
       
        #  ---------- addition for extraction of a chunk of data ---------------
       
        if read_chunks:
            window_size = int((radius_pix + search_top_obs + 1) * 2)
            x_offset = max(0, int(x - window_size/2))
            y_offset = max(0, int(y - window_size/2))
            window_size_x = min(input_raster_rows - x_offset, x_offset + window_size)
            window_size_y = min(input_raster_columns - y_offset, y_offset + window_size)
            data = gdal_raster.ReadAsArray(x_offset, y_offset, window_size_x, window_size_y)# global variable
         #  ---------------------------------------------------------------------
        x = x- x_offset; y = y - y_offset

        if search_top_obs:
            s = search_top_z (x, y, search_top_obs)
            x,y,z = s
        else: z= data[y,x]
                
        if z_obs_field: 
            try: z_obs= float(feat[z_obs_field])
            except: pass #"nothing, will conserve main z_obs"

        if Target_layer:
        
            diameter = radius +  search_top_obs + search_top_target # maximum posibility (the new observer coordinate is not translated to geographic)
            areaOfInterest= QgsRectangle (t[0]-diameter , t[1]-diameter, t[0]+diameter, t[1]+diameter)

            # SPATIAL INDEX FOR SPEED
            feature_ids = targ_index.intersects(areaOfInterest)
                   
            for fid in feature_ids:                                                 # NEXT TO GET THE FEATURE
                feat2 = Target_layer.getFeatures(QgsFeatureRequest().setFilterFid(fid)).next()
                id2 = feat2["ID"] if targ_has_ID else feat2.id()
                geom2 = feat2.geometry()
                x_geog, y_geog = geom2.asPoint()

                x2 = int((x_geog - raster_x_min) / pix)- x_offset #round vraca float!!
                y2 = int((raster_y_max - y_geog) / pix)- y_offset #pazi: obratno!!

                if search_top_target:
                    s = search_top_z (x2,y2, search_top_target)
                    x2,y2,z2 = s
                else : z2 = data[y2,x2]
                
                #only after the adaptation to the highest point
                # has been made for both observer and target can we verify distances
                if x2==x and y2==y : continue #skip same pixels!
                
                #this eliminates distance calculation for each point (x+y < radius is always OK)
                if (abs(x2-x) + abs (y2-y))> radius_pix:
                    if round(dist(x,y,x2,y2)) > radius_pix : continue

                if z_target_field:
                    try: z_target = float(feat[z_target_field])
                    except: pass #do nothing, already given above
                
                target_list.append ([x2,y2, z_target, id2])
          
        else:
           
            target_list = bresenham_circle(x,y,radius_pix)#this is the list of target points
            

        # ------------  main point loop ----------------------
        vis = visibility (x, y, z_obs, target_list, z_target, output_options[0], (Target_layer <> 0))
        
        if output_options[0] == "Intervisibility": #skip raster stuff
            if vis :
                for n in vis: connection_list.append([id1, x,y]+ n)
        else:
            #   ~~~~~~~~~~~~~~~  Finalizing raster output  ~~~~~~~~~~~~~~~~~~~~~~~
            out=str(output + "_" + str(id1))
            matrix_vis = numpy.zeros ( (len(data) , len(data[0])) ) # cannot be = data: it ovrewrites it!
            
            #OUTPUT is generic:  x, y, error, value
            v = sorted(vis, key=itemgetter(0,1,2))  #sort on x,y and error
            
            if output_options[0] == 'Binary': num_format=gdal.GDT_Byte
            else : num_format=gdal.GDT_Float32

            for k in v:
                #insert only pixels with lower error (the top ones in the list)        
                if matrix_vis [k[1],k[0]] == 0:
                    matrix_vis [k[1],k[0]] = k[3]
     
            if output_options [1] == "cumulative": 
                matrix_final = matrix_final + matrix_vis
            else:            
                file_name = out + "_" + output_options[0]

                success = write_raster (matrix_vis, file_name, input_raster_rows, input_raster_columns,
                                        x_offset, y_offset, gt, projection, num_format)
                if success : out_files.append(success)
                else: QMessageBox.information(None, "Error writing file !", str(file_name + ' cannot be saved')) 

                matrix_vis= None          
                    
    test_rpt += "\n    - point " + str(id1) + " calculations + dumping: " + str (time.clock()- start_etape)
    start_etape=time.clock()

    #exiting the main points loop : write cumulative....                
    if output_options [1]== "cumulative":
        success = write_raster (matrix_final, output+'_cumulative',input_raster_rows, input_raster_columns,
                                x_offset, y_offset, gt, projection, gdal.GDT_Int32)
        if success : out_files.append(success)
        else: QMessageBox.information(None, "Error writing file !", str(output + '_cumulative cannot be saved'))

    if output_options[0]=="Intervisibility":
        success = write_intervisibility_line (output, connection_list, Obs_layer.crs()) 
        if success : out_files.append(success)

        if not success : 1# do something smart ?

        
    matrix_final = None; data = None; connections_list=None; v=None; vis=None
    test_rpt += "\n Total time: " + str (time.clock()- start)
##    QMessageBox.information(None, "Timing report:", str(test_rpt))              
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
    
    fields = QgsFields() #there's a BUG in QGIS here (?), normally : fields = .... 
    fields.append(QgsField("Source", QVariant.String ))
    fields.append(QgsField("Target", QVariant.String))
##    fields.append(QgsField("Source_lbl", QVariant.String, 'string',50))
##    fields.append(QgsField("Target_lbl", QVariant.String, 'string',50))
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
        l_start=QgsPoint(r[1]*pix + raster_x_min + half_pix, raster_y_max - half_pix- r[2]*pix)
        l_end = QgsPoint(r[4]*pix + raster_x_min + half_pix, raster_y_max - half_pix- r[5]*pix)
         
        feat.setGeometry(QgsGeometry.fromPolyline([l_start, l_end]))
        # do not cast ID to string: unicode problem  -- angle * distance in pixels -- distance * pixel_size
        #feat.setAttributes([ str(r[0]), str(r[3]), bool(r[6]), float(r[7] * r[8]),  ])
        feat.setFields(fields)
        feat['Source'] = r[0]
        feat['Target'] = r[3]
        feat['Visible'] = 'True' if r[6] else 'False'
        feat['TargetSize'] = float(r[7])
        feat['Distance'] = float(r[8] * pix)
        
        writer.addFeature(feat) 
        del feat

    del writer
    layer = None
    return file_name + ".shp"

