---
title: 'Advanced viewshed analysis: a Quantum GIS plug-in for the analysis of visual landscapes'
tags:
  - GIS
  - raster
  - viewshed
authors:
 - name: Zoran Cuckovic
   orcid: 0000-0001-7626-4086
   affiliation: UMR 6249 Laboratoire Chrono-environnement, Université Bourgogne Franche-Comté.
date: 29 July 2016
bibliography: paper.bib
---


# Summary

Viewshed analysis is a standard feature of GIS software packages, such as ArcGIS (ESRI 2016), GRASS (Neteler *et al.* 2015) or ERDAS (2015). However, these implementations vary considerably in terms of their versatility and robustness. Software in the free domain is particularly poor in this respect: visibility analysis is generally implemented as a simple binary query (true/false) for elevation datasets (eg. GRASS or SAGA GIS). In order to meet the demands of a typical analysis concerning visual landscapes we would be interested to find out how deep are certain locations below the visible horizon, what is the overall visual potential of a landscape or which sites are connected in visual networks (cf. Higuchi 1983; Llobera 2003; Čučković 2015).

Advanced viewshed analysis plug-in for open source Quantum GIS software has been made in order to meet some of these demands: besides standard binary viewshed it provides information on the depth at which objects may be hidden from view, mapping of visual horizon and analysis of intervisibility networks. As of version 0.5.1, the implemented algorithm has been adapted for intensive, repetitive viewshed calculation from multiple observation points. 

The plug-in is coded in Python and is dependant of the Quantum GIS framework. More specifically, it makes use of following libraries (bundled with Quantum GIS): numpy, gdal and QGIS core library.   
 
 An example of intervisibility output:
 ![Intervisibility network](Intervisibility.jpg)
 
# References 
Čučković, Z. 2015. Exploring intervisibility networks: a case study from Bronze and Iron Age Istria (Croatia and Slovenia). In F. Giligny, F. Djindjian, L. Costa, P. Moscati and S. Robert (eds.), *CAA 2014 - 21st Century Archaeology : Proceedings of the 42nd Annual Conference on Computer Applications and Quantitative Methods in Archaeology*, April 2014, Paris, France, 469 - 478.

ERDAS 2015. ERDAS Imagine Suite 2015. Norcross: Hexagon Geospatial. 

ESRI 2016. ArcGIS Desktop: Release 10.4. Redlands: Environmental Systems Research Institute.

Higuchi, T. 1983. *Visual and Spatial Structure of Landscapes*. Cambridge, Mass: MIT Press. 

Llobera, M. 2003. Extending GIS-based visual analysis: the concept of visualscapes. International journal of geographical information science 17(1), 25-48. doi: [10.1080/713811741](https://doi.org/10.1080/713811741)

Neteler M., Bowman, M.H., Landa, M., Metz, M. 2012. "GRASS GIS: A multi-purpose open source GIS." Environmental Modelling & Software. Vol 31, pp. 124–130. doi: [10.1016/j.envsoft.2011.11.014 ](http://dx.doi.org/10.1016/j.envsoft.2011.11.014)

# User manual

[zoran-cuckovic.github.io/QGIS-visibility-analysis/](http://zoran-cuckovic.github.io/QGIS-visibility-analysis/)
