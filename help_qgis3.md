[go to main page](https://zoran-cuckovic.github.io/QGIS-visibility-analysis)

# Work in progress

see [https://landscapearchaeology.org/2018/visibility-analysis-0-6/](https://landscapearchaeology.org/2018/visibility-analysis-0-6/) for a basic tutorial


Installation:
------------
The plugin is installed as any other from the official QGIS repository (In QGIS go to Plugins -> Manage and install ... ). Be sure to **enable experimental versions**.  

In case the usual install doesn't work, the plugin can be installed manually:  
First you need to locate your QGIS plugins folder. On Windows it would be 'C:\users\username\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins' (do a file search for 'QGIS3' ...)

Plugin code can then be extracted in a new folder inside the plugins folder (you should name the folder VisibilityAnalysis). Take care that the code is not inside a subfolder - the folder structure should be like this:  

+ QGIS3\profiles\default\python\__plugins__
    + [some QGIS plugin folders...] 
    + VisibilityAnalysis   
        + visibility_plugin.py
		+ visibility_provider.py
        + [other files and folders...]  


Dependencies:
-------------
The plugin is coded in Python 3.6 and does not require any additional libraries than those provided by standard QGIS installation. These libraries include *numpy* and *gdal* for manipulating raster data, and *PyQt5* and *QGIS core libraries* for integration with QGIS.

Repository and download
------------------------
[https://github.com/zoran-cuckovic/QGIS-visibility-analysis/tree/experimental](https://github.com/zoran-cuckovic/QGIS-visibility-analysis/tree/experimental)
