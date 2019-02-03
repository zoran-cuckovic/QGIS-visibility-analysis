
[go to main page](https://zoran-cuckovic.github.io/QGIS-visibility-analysis)


Installation:
------------
The plugin is installed as any other from the official QGIS repository (In QGIS go to Plugins -> Manage and install ... ). Be sure to **enable experimental versions**.  

In case the usual install doesn't work, the plugin can be installed manually:  
First you need to locate your QGIS plugins folder. On Windows it would be 'C:\users\username\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins' (do a file search for 'QGIS3' ...)

Plugin code can then be extracted in a new folder inside the plugins folder (you should name the folder ViewshedAnalysis). Take care that the code is not inside a subfolder - the folder structure should be like this:  

+ QGIS3\profiles\default\python\plugins\
    + [some QGIS plugin folders...] 
    + ViewshedAnalysis   
        + visibility_plugin.py
		+ visibility_provider.py
        + [other files and folders...]  
	
Workflow
=======
Visibility analysis is broken down in two steps: first a set of observer points is created using *Create observer points* module, which are then fed to other modules. 

Input data
==========
- *Digital elevation model*: terrain model in a raster format (a pixel grid such as .tiff). Only **projected raster data** can be used. Latitude/longitude "projections", such as WGS84 are not allowed.
- *Observer/target points* have to be stored in a shapefile or other recognised vector formats. Lines or polygons cannot be used (unless broken up in points). Multi-point shapefiles will not work, neither. In case when point's coordinate system differ from the elevation model used, the vector data will be reprojected to match.

Modules
=======
## Create observer points

This is the **first step** for the visibility analysis. The result will be written as a geopackage file with standardised field names and reprojected to match the elevation model used (if needed). Data inside the table can be changed manually - but the names and data types of fields should remain unchanged. 

### Parameters

- *observer IDs*: viewpoints can be assigned individual names or id numbers, stored in the associated table. Otherwise, internal ids will be used (sequential numbers).
- *Observer height*: in meters
- *Target height*: height value to be added to all terrain areas checked for visibility from the observer point.
- *Radius of analysis*: maximum distance for visibility testing, in meters

All parameters (observer/target height, point ID, radius of analysis) are read from the associated data table for each view-point. In case of error (eg. an empty field) the fixed value specified in the text box will be applied. Note that input parameters are stored in the accompanying table and can be changed manually. Field names and formats need to remain as assigned, however.

Viewshed
-------------

This module will produce a visibility map where each data point of a terrain model will be assigned a true/false value (visible/not visible). When multiple observer points are used, individual viewsheds will be combined into a cumulative viewshed model representing the number of positive results for each data point.

### Parameters
 -  *Earth cuvature*and *refraction*: see below.

Intervisibility network
-----------------------

The output of the intervisibility network routine is a network, in vector format, of visual relationships between two sets of points (or within a single set). For each link the depth below/above visible horizon is calculated, as in many cases only a portion of the specified target is visible. 

### Parameters
 - *Observer points* and *Target points* are vector layers created by the *create viewpoints* routine. Note that each point can be both, observer and target: the height *as* target is always stored in the ``target_hgt`` field.
 - *Save negative links*: when allowed, non-visible relationships will be registered. These are recognisable as negative vaules of the ``TargetSize`` field.
 -  *Earth cuvature*and *refraction*: see below.
 
Depth below horizon
-----------------------
Rather than evaluating visibility as true/false, we can also calculate the depth at which lay invisible portions of the terrain. The value produced by this module can be understood as the theoretical height a construction should attain in order to appear on the horizon, as visible from the chosen observer point.

### Parameters

- *combining multiple outputs*: unlike simple true/false viewshed maps, depths under the horizon are not cumulative (in typical situations). For instance, if a same building is evaluated from different observing points, we would be interested in a best or worst case scenario: which height would be visible to all observers or, conversely, to none of the observers. Therefore we would search for minimum / maximum values, which is obtained by setting this parameter.      

Other parameters are the same as for the viewshed module.

See tutorial on [LandscapeArchaeology.org/2018/depth-below-horizon](https://landscapearchaeology.org/2018/depth-below-horizon)


## Earth curvature and refraction

Similar to other viewshed algorithms available, it is possible to account for effects of the Earth's curvature and refraction of the light when travelling through the atmosphere. The latter effect is due to differences in density and in composition between layers of the athmosphere, as for instance between air an water. These parameters are insignificant over smaller distances, especially for cuarse grained terrain models. 

 Following formula is used to adjust height values in the DEM:

z adjusted = z - (Dist 2 / Diam Earth ) \* (1 - Refraction)

Where:  
Dist: The planimetric distance between the observation point and the target point.  
Refraction: The refractivity coefficient of light (normally it has the opposite, but smaller, effect than the curvature).  
Diam: The diameter of the earth that is calculated as Semi-major axis + Semi-minor axis. These values are taken from the projection system assigned to the Raster by QGIS. In case of error or unrealistic values, the default Semi-major axis of 6378137 meters and flattening of 298.257 are used.

For more explanation cf. [ArcGIS web page](http://webhelp.esri.com/arcgisdesktop/9.3/index.cfm?TopicName=How%20Visibility%20works)

## General settings

These are acessed under Processing Options (search for Providers >> Visibility Analysis)

- *Activate*: self explanatory...
- *Maximum buffer size*: when working on multiple points, the algorithm can either hold all data in live memory (which is faster), or select, for each point, a smaller window corresponding to the specified radius (which is somewhat slower). The second approach will be used when the size of terrain model used (DEM) exceedes the specified buffer threshold. It is expressed in megapixels ([explained also here](https://landscapearchaeology.org/2018/visibility-analysis-0-6-4)).

Dependencies:
-------------
The plugin is coded in Python 3.6 and does not require any additional libraries than those provided by standard QGIS installation. These libraries include *numpy* and *gdal* for manipulating raster data, and *PyQt5* and *QGIS core libraries* for integration with QGIS.

Repository and download
------------------------
[https://github.com/zoran-cuckovic/QGIS-visibility-analysis/tree/experimental](https://github.com/zoran-cuckovic/QGIS-visibility-analysis/tree/experimental)

Tutorials
---------
Raster module: [LandscapeArchaeology.org/2018/visibility-analysis-0-6/](https://landscapearchaeology.org/2018/visibility-analysis-0-6/)

Depth below horizon: [LandscapeArchaeology.org/2018/depth-below-horizon](https://landscapearchaeology.org/2018/depth-below-horizon)
