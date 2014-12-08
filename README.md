Advanced viewshed analysis for QGIS
===================================

Viewshed analysis calculates visible surface from a given observer point over a digital elevation model. Basic viewshed analysis can  be be made in QGIS environment through performant GRASS viewshed algorithm *r.los* or SAGA viewshed module. However, these solutions give only a simple binary viewshed (true/false for each evaluated location). For more complex (and more interesting!) analyses a good amount of programming is required. 

Viewshed analysis plugin is native to QGIS and intended for more complex modelling, such as the depth below the visible horizon or generation of intervisibilty networks between groups of points. It is reasonably performant for standard viewsheds as well (which is dependent on the amount of RAM memory as well). 


