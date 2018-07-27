# -*- coding: utf-8 -*-

from PyQt5.QtCore import QCoreApplication

from plugins.processing.gui import MessageBarProgress

from qgis.core import (QgsProcessing,
                       
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,

                       #individual files
                       QgsProcessingOutputRasterLayer,

                       
                      QgsProcessingParameterBoolean,
                      QgsProcessingParameterNumber,
                      QgsProcessingParameterField,
                       QgsProcessingParameterEnum ,
                      QgsProcessingParameterFile,

                      QgsProcessingException,

                       QgsMessageLog)


from .modules import visibility as ws
from .modules import Points as pts
from .modules import Raster as rst

import numpy as np


class ViewshedRaster(QgsProcessingAlgorithm):

    DEM = 'DEM'
    OBSERVER_POINTS = 'OBSERVER_POINTS'
    
    USE_CURVATURE = 'USE_CURVATURE'
    REFRACTION = 'REFRACTION'
    PRECISION = 'PRECISION'
    ANALYSIS_TYPE = 'ANALYSIS_TYPE'
    OPERATOR = 'OPERATOR'
    OUTPUT = 'OUTPUT'
   

    PRECISIONS = ['Coarse','Normal', 'Fine']

    #not used yet
    TYPES = ['Binary viewshed', 'Depth below horizon',
             'Horizon', 'Horizon - intermediate', 'Projected horizon']

    # not used yet
    OPERATORS = [ 'Addition', "Maximum", "Minimum"]

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config):

        self.addParameter(
            QgsProcessingParameterFeatureSource(
  
            self.OBSERVER_POINTS,
            self.tr('Observer location(s)'),
            [QgsProcessing.TypeVectorPoint]))

        self.addParameter(QgsProcessingParameterRasterLayer
                          (self.DEM,
            self.tr('Digital elevation model ')))


##        self.addParameter(ParameterSelection(
##            self.ANALYSIS_TYPE,
##            self.tr('Analysis type'),
##            self.TYPES,
##            0))
##
        self.addParameter(QgsProcessingParameterBoolean(
            self.USE_CURVATURE,
            self.tr('Take in account Earth curvature'),
            False))
        self.addParameter(QgsProcessingParameterNumber(
            self.REFRACTION,
            self.tr('Atmoshpheric refraction'),
            1, 0.13, False, 0.0, 1.0))
        
        
##        self.addParameter(QgsProcessingParameterEnum (
##            self.PRECISION,
##            self.tr('Algorithm precision'),
##            self.PRECISIONS,
##            defaultValue=1))

##        self.addParameter(QgsProcessingParameterEnum (
##            self.OPERATOR,
##            self.tr('Combining multiple outputs'),
##            self.OPERATORS,
##            defaultValue=0))

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
            self.tr("Output file")))

##    def shortHelpString(self):
##        return ("Viewshed maps are made over an elevation model,"
##               "from viewpoints created by the “Create viewpoints” routine.")

    #---------- not working ---------------- 
    def helpUrl(self):
        return 'https://zoran-cuckovic.github.io/QGIS-visibility-analysis/help_qgis3.html'
    # for local file : QUrl.fromLocalFile(os.path.join(helpPath, '{}.html'.format(self.grass7Name))).toString()
        

    def processAlgorithm(self, parameters, context, feedback):

        


        raster = self.parameterAsRasterLayer(parameters,self.DEM, context)
        observers = self.parameterAsSource(parameters,self.OBSERVER_POINTS,context)

        
        useEarthCurvature = self.parameterAsBool(parameters,self.USE_CURVATURE,context)
        refraction = self.parameterAsDouble(parameters,self.REFRACTION,context)
        precision = 1 #self.parameterAsInt(parameters,self.PRECISION,context)
        analysis_type = 0#self.getParameterValue(self.ANALYSIS_TYPE)
        operator = 1 #self.parameterAsInt(parameters,self.OPERATOR,context) + 1       

        output_path = self.parameterAsOutputLayer(parameters,self.OUTPUT,context)
 

        #getTempFilenameInTempFolder(
            #self.name + '.' + self.getDefaultFileExtension(alg)

            
        # output_dir = self.getOutputValue(self.OUTPUT_DIR)

        # convert meters to layer distance units
        # [this can be confusing when the module is used in a script,
        #  and it's 3.0 function ]
        #coef = QgsUnitTypes.fromUnitToUnitFactor(Qgis.DistanceMeters, dem.crs().mapUnits())
		
        #searchRadius = searchRadius * coef

# --------------- verification of inputs ------------------

        raster_path= raster.source()
        dem = rst.Raster(raster_path, output=output_path)
        # TODO: ADD MORE TESTS (raster rotated [projections ??], rectnagular pixels [OK?]
                         
        points = pts.Points(observers)

        
        fields =["observ_hgt", "radius"]

        
        miss = points.test_fields(fields)
        
        if miss: raise QgsProcessingException(
                " \n ****** \n ERROR! \n Missing fields: \n" + "\n".join(miss))

        points.take(dem.extent, dem.pix)

        if points.count == 0:
            raise QgsProcessingException(
                "  \n ******* \n ERROR! \n No viewpoints in the chosen area!")
        elif points.count == 1:
            operator=0

        dem.set_buffer(operator)

        pt = points.pt #this is a dict of obs. points

# --------------------- analysis ----------------------   

        import time; start = time.clock()
        
        report=[]

        
        # should be explicit ( .max_radius(pixel=True) ) ...
        radius_float = points.max_radius
        radius_pix = int(radius_float/dem.pix)

        
        #for speed and convenience, use maximum sized window for all analyses
        #this is not clear! should set using entire size, not radius !!
        dem.set_master_window(radius_pix,
                            size_factor = precision ,
                            background_value=0,
                            pad = precision>0,
                            curvature =useEarthCurvature,
                            refraction = refraction )
        


##        #angular matrix ----- NOT USED YET ------
##
##
##        if points.test_fields(["azim_1", "azim_2"]) :
##            #test returns missing fields
##            angles = None
##        else:
##            
##            size = dem.window.shape[0]#it's square
##           
##            temp_x= np.arange(size)[::-1] - radius_pix
##            temp_y= np.arange(size) - radius_pix
##
##            angles=np.arctan2(temp_y[None,:], temp_x[:,None]) * 180 / np.pi
##            angles[angles<0] += 360


# TODO : vertical angle = filter angle based viewshed

        cnt = 0
       
        for id1 in pt :

            

            if feedback.isCanceled():  break

               
    ##        if diff: np_slice = np.s_[diff : radius_pix - diff,
    ##                                  diff : radius_pix - diff]
    ##
    ##        else: np_slice = np.s_[:]       

            matrix_vis = ws.viewshed_raster (analysis_type, pt[id1], dem,
                                          interpolate = precision > 0)

            
            # ----------- MASKING ------------
                  
            mask = dem.mx_dist [:] > pt[id1]["radius"]
            
##            **   angular - not used yet ** 
##            if isinstance(angles,np.ndarray):
##
##                az1 =  pt[id1]["azim_1"]
##                az2 = pt[id1]["azim_2"]
##
##                mask_az = np.logical_and( angles > az1 , angles < az2)
##  
##                # masked areas are positive (1) = reverse!
##                if az1 < az2: mask_az = ~ mask_az
##                
##                mask = np.logical_or (mask, mask_az)
##                           
            # we need zero background to sum up,
            # but not for other options
         
            fill = 0 if operator == 1 else np.nan
            matrix_vis[mask]=fill

            #---------------------------------
            
            #TODO: make some kind of general report system : inside raster class ???
            # algo 0 is fast, so skip to save some time (??)
            if precision > 0 :

                s_y, s_x = dem.inside_window_slice

                
                sl = np.s_[slice(*s_y), slice(*s_x)]
                #careful with areas outside raster ! 
                view_m = matrix_vis[sl]
# USE CONSTANTS !!
                if analysis_type == 1: #INVISIBILITY_DEPTH:
                   c= np.count_nonzero(view_m >= 0) 

                else:  c = np.count_nonzero(view_m)
                     
                # Count values outside mask (mask is True on the outside!)
                crop =np.count_nonzero(mask[sl])
                # Here, nans are in the outside (which are not zero!)
                if operator != 1: c -= crop
                # this is unmasked: sunbtract masked out areas!
                report.append([pt[id1]["id"], c , view_m.size - crop] )

            if operator > 0: dem.add_to_buffer (matrix_vis)
            else  :     dem.write_result(in_array= matrix_vis)


            cnt += 1

            feedback.setProgress(int((cnt/points.count) *100))
                
       
        
        if operator > 0: dem.write_result()     

        print (" Finished: " + str( round( (time.clock() - start
                                           ) / 60, 2)) + " minutes.")
                

        txt = ("\n Analysis time: " + str(
                            round( (time.clock() - start
                                    ) / 60, 2)) + " minutes."
              " \n.      RESULTS \n Point_ID, visible pixels, total pixels" )
        
        for l in report:
            txt = txt + "\n" + ' , '.join(str(x) for x in l)

        # TODO : write to Results viewer !!
        QgsMessageLog.logMessage( txt, "Viewshed info")
          
        results = {}
        
        for output in self.outputDefinitions():
            outputName = output.name()
                
            if outputName in parameters :
                results[outputName] = parameters[outputName]

    
        return results

    
    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """

        return 'Viewshed'
    
    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())
    
    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Analysis'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        #return ViewshedPoints() NORMALLY
        return type(self)()
