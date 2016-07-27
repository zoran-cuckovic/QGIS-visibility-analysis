Advanced viewshed analysis for QGIS 
===================================

Version: 0.5.1
------------
Licence: GNU GPLv3
-------------
Author: Zoran Čučković [zoran-cuckovic.from.hr](contact) 

Introduction:
-------------
Viewshed analysis plugin for QGIS calculates visible surface from a given observer point over a digital elevation model. The plugin is  intended for more complex modelling, such as the depth below the visible horizon or generation of intervisibilty networks between groups of points. It is particularly performant for multiple viewshed calculations form a set of fixed points.

Installation:
------------
The plugin is installed as any other from the official QGIS repository (In QGIS go to Plugins -> Manage and install ... ). Be sure to enable experimental versions if the latest plugin version is labelled as experimental.

In case the usual install doesn't work, the plugin can be installed manually:

First you need to locate your QGIS plugins folder. On windows it would be 'C:\users\username\.qgis2\python\plugins' and on Linux something like '~/home/.qgis2/python/plugins'. (do a file search for '.qgis2')

Plugin code can then be extracted in a new folder inside the plugins folder (you should name the folder ViewshedAnalysis). Click above to download the latest version (older versions can be found at QGIS plugins repository. 

Dependencies:
-------------
The plugin is coded in Python 2.7 and does not require any additional libraries than those provided by standard QGIS installation. These libraries include *numpy* and *gdal* for manipulating raster data, and *PyQt4* and *QGIS core libraries* for integration with QGIS.

Documentation:
--------------
A *user manual* is available at:  [http://zoran-cuckovic.github.io/QGIS-visibility-analysis/](http://zoran-cuckovic.github.io/QGIS-visibility-analysis/)
And more on *software use* at:
[http://zoran-cuckovic.from.hr/landscape-analysis/visibility/](http://zoran-cuckovic.from.hr/landscape-analysis/visibility/)
Bugs and issues can be submitted at [https://github.com/zoran-cuckovic/QGIS-visibility-analysis/issues] (GitHub) or reported directly at [zoran-cuckovic.from.hr/about/](author's web pages)