Advanced viewshed analysis for QGIS 
===================================

**Version: 1.8**

**Supported QGIS version: 3.x**

**Licence: GNU GPLv3**

**Documentation**: [LandscapeArchaeology.org/qgis-visibility-analysis](https://landscapearchaeology.org/qgis-visibility-analysis/)

**Author: Zoran Čučković ([web page](http://zoran-cuckovic.from.hr))** 

Introduction:
-------------
Viewshed analysis plugin for QGIS calculates visible surface from a given observer point over a digital elevation model. The plugin is  intended for more complex modelling, such as the depth below the visible horizon or generation of intervisibilty networks between groups of points. It is particularly performant for multiple viewshed calculations form a set of fixed points.

Installation:
------------
The plugin is installed as any other from the official QGIS repository (In QGIS go to Plugins -> Manage and install ... ). Be sure to enable experimental versions if the latest plugin version is labelled as experimental.  

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

Community guidelines and feedback:
--------------------
This project is released with a Contributor Code of Conduct (Contributor_code.md). By participating in this project you agree to abide by its terms. Feedback, bug reports (and fixes!), and feature requests are welcome and can be submitted at [GitHub] (https://github.com/zoran-cuckovic/QGIS-visibility-analysis/issues) or reported directly through author's contact (above).

More information:
--------------
Documentation, tutorials and other stuff can be found on the plugin's webpage:  [https://zoran-cuckovic.github.io/QGIS-visibility-analysis](https://zoran-cuckovic.github.io/QGIS-visibility-analysis)  
Data for testing purposes can be found at [test data branch](https://github.com/zoran-cuckovic/QGIS-visibility-analysis/tree/test-data).  

