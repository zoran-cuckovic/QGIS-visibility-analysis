Parameters
==========

Single point
------------
Points: single point.shp
Elevation data: DEM.tiff

###Settings

Radius of analysis: 15 000
Observer height: 1.6 (default)
Earth curvature: Yes
refraction: default

Multiple point (cumulative)
--------------------------
Points: PointsB.shp
Elevation data: DEM.tiff

###Settings

Radius of analysis: 5 000
Observer height: 0
Target height: 1.6
Find higher point: 1 pixel 
Earth curvature: Yes
refraction: default

*NB. This ouptut is produced by a procedure described in [a use case] (http://zoran-cuckovic.from.hr/qgis-viewshed-plugin-a-tutorial/).
Note the difference between normal and fine algorithm options.