[go to main page](https://zoran-cuckovic.github.io/QGIS-visibility-analysis)


Installation:
------------
The plugin is installed as any other from the official QGIS repository (In QGIS go to Plugins -> Manage and install ... ). Be sure to **enable experimental versions**.  

In case the usual install doesn't work, the plugin can be installed manually:  
First you need to locate your QGIS plugins folder. On Windows it would be 'C:\users\username\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins' (do a file search for 'QGIS3' ...)

Plugin code can then be extracted in a new folder inside the plugins folder (you should name the folder ViewshedAnalysis). Take care that the code is not inside a subfolder - the folder structure should be like this:  

+ QGIS3\profiles\default\python\__plugins__
    + [some QGIS plugin folders...] 
    + ViewshedAnalysis   
        + visibility_plugin.py
		+ visibility_provider.py
        + [other files and folders...]  
	
Modules 
=======

Create observer points
----------------------
This is the **first step** for the visibility analysis. The result will be written as a geopackage file with standardised field names and reprojected to match the elevation model used (if needed). Data inside the table can be changed manually - but the manes and data types of fields should remain unchanged. 

### Input
All input parameters are stored in the accompanying table and can be changed manually. Field names need to remain as assigned.

- *Observer points* have to be stored in a shapefile or other recognised vector formats. Lines or polygons cannot be used (unless broken up in points). Multi-point shapefiles will not work, neither. In case when point's coordinate system differ from the elevation model used, the vector data will be reprojected to match.

- *Digital elevation model* has to be in **projected** raster format. Latitude/longitude systems will produce unrealistic results (if they work at all) 

- *observer IDs*: viewpoints can be assigned individual names or id numbers, stored in the associated table. Otherwise, internal ids will be used (sequential numbers).
- *Observer height*: in meters
- *Target height*: height value to be added to all terrain areas checked for visibility from the observer point.
- *Radius of analysis*: maximum distance for visibility testing, in meters

Several parameters (observer/target height, point ID, radius of analysis) can be read from the associated data table for each view-point. In case of error (eg. an empty field) the fixed value specified in the text box will be applied.

Raster output (viewshed)
-------------

Viewshed maps are made over an elevation model, from viewpoints created by the "Create viewpoints" routine.

- *Observer points*: point type vector layer created by the *create viewpoints* routine.
- elevation model: raster data

Intervisibility network
-----------------------
**[ Work in progress as of 0.6.1 version ]**

The output of intervisibility network routine is a set of lines connecting viewpoints. 

### Input
- *Observer points*:  point type vector layer created by the *create viewpoints* routine. 
- *Target points*: point type vector layer created by the *create viewpoints* routine. **!** Target height is always specified in the ``target_hgt`` field, even when using the same file for observer and target points.
- *Save negative links*: save non-visible relationships.

General settings
---------------
- Maximum buffer size: [explined here](https://landscapearchaeology.org/2018/visibility-analysis-0-6-4)

Dependencies:
-------------
The plugin is coded in Python 3.6 and does not require any additional libraries than those provided by standard QGIS installation. These libraries include *numpy* and *gdal* for manipulating raster data, and *PyQt5* and *QGIS core libraries* for integration with QGIS.

Repository and download
------------------------
[https://github.com/zoran-cuckovic/QGIS-visibility-analysis/tree/experimental](https://github.com/zoran-cuckovic/QGIS-visibility-analysis/tree/experimental)

Tutorials
---------
Raster module: [https://landscapearchaeology.org/2018/visibility-analysis-0-6/](https://landscapearchaeology.org/2018/visibility-analysis-0-6/)
