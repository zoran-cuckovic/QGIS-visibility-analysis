Advanced viewshed analysis for QGIS 
===================================

**Version: 0.5.2**

**Licence: GNU GPLv3**

**Author: Zoran Čučković ([contact](http://zoran-cuckovic.from.hr/about/))** 

Introduction:
-------------
Viewshed analysis plugin for QGIS calculates visible surface from a given observer point over a digital elevation model. The plugin is  intended for more complex modelling, such as the depth below the visible horizon or generation of intervisibilty networks between groups of points. It is particularly performant for multiple viewshed calculations form a set of fixed points.

Installation:
------------
The plugin is installed as any other from the official QGIS repository (In QGIS go to Plugins -> Manage and install ... ). Be sure to enable experimental versions if the latest plugin version is labelled as experimental.  

In case the usual install doesn't work, the plugin can be installed manually:  
First you need to locate your QGIS plugins folder. On Windows it would be 'C:\users\username\.qgis2\python\plugins' and on Linux something like '~/home/.qgis2/python/plugins'. (do a file search for '.qgis2')

Plugin code can then be extracted in a new folder inside the plugins folder (you should name the folder ViewshedAnalysis). Take care that the code is not inside a subfolder - the folder structure should be like this:  

+ .qgis2\python\ __plugins__
    + [some QGIS plugin folders...] 
    + ViewshedAnalysis   
        + viewshedanalysis.py   
        + [other files and folders...]  

Click above to download the latest version (older versions can be found at [QGIS plugins repository](https://plugins.qgis.org/plugins/ViewshedAnalysis/)). 

Dependencies:
-------------
The plugin is coded in Python 2.7 and does not require any additional libraries than those provided by standard QGIS installation. These libraries include *numpy* and *gdal* for manipulating raster data, and *PyQt4* and *QGIS core libraries* for integration with QGIS.

Community guidelines and feedback:
--------------------
This project is released with a Contributor Code of Conduct (Contributor_code.md). By participating in this project you agree to abide by its terms. Feedback, bug reports (and fixes!), and feature requests are welcome and can be submitted at [GitHub] (https://github.com/zoran-cuckovic/QGIS-visibility-analysis/issues) or reported directly through author's contact (above).

More information:
--------------
A user manual is available at:  [http://zoran-cuckovic.github.io/QGIS-visibility-analysis/](http://zoran-cuckovic.github.io/QGIS-visibility-analysis/)  
Data for testing purposes can be found at [test data branch](https://github.com/zoran-cuckovic/QGIS-visibility-analysis/tree/test-data).  
And more on software use at:
[http://zoran-cuckovic.from.hr/landscape-analysis/visibility/](http://zoran-cuckovic.from.hr/landscape-analysis/visibility/)
