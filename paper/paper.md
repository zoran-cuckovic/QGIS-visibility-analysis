---
title: 'Advanced viewshed analysis: a Quantum GIS plug-in for the analysis of visual landscapes'
tags:
  - GIS
  - raster
  - viewshed
authors:
 - name: Zoran Čučković
   orcid: 0000-0001-7626-4086
   affiliation: UMR 6249 Laboratoire Chrono-environnement, Université Bourgogne Franche-Comté.
date: 24 June 2016
bibliography: paper.bib
---

# Summary

Viewshed analysis is a standard feature of GIS software packages, such as ArcGIS (ESRI 2016), GRASS (2015) or ERDAS (2015). However, these implementations vary considerably in terms of their versatility and robustness. Software in the free domain is particularly poor in this respect: visibility analysis is generally implemented as a simple binary query (true/false) for elevation datasets (eg. GRASS or SAGA GIS). In order to meet the demands of a typical analysis concerning visual landscapes we would be interested to find out how deep are certain locations below the visible horizon, what is the overall visual potential of a landscape or which sites are connected in visual networks (cf. Higouchi 1983; Llobera 2003; Čučković 2015).

Advanced viewshed analysis plug-in for open source Quantum GIS software has been made in order to meet some of these demands: besides standard binary viewshed it provides information on the depth at which objects may be hidden from view, mapping of visual horizon and analysis of intervisibility networks. As of version 0.5.1, the implemented algorithm has been adapted for intensive, repetitive viewshed calculation from multiple observation points. 

The plug-in is coded in Python and is dependant of the Quantum GIS framework. More specifically, it makes use of following libraries (bundled with Quantum GIS): numpy, gdal and QGIS core library.   
 

# References 
Čučković, Z. 2015. Exploring intervisibility networks: a case study from Bronze and Iron Age Istria (Croatia and Slovenia). In F. Giligny, F. Djindjian, L. Costa, P. Moscati and S. Robert (eds.), _CAA 2014 - 21st Century Archaeology : Proceedings of the 42nd Annual Conference on Computer Applications and Quantitative Methods in Archaeology_, April 2014, Paris, France, 469 - 478.
ERDAS 2015. ERDAS Imagine Suite 2015. Norcross: Hexagon Geospatial. 
ESRI 2016. ArcGIS Desktop: Release 10.4. Redlands: Environmental Systems Research Institute.
GRASS 2015. Geographic Resources Analysis Support System (GRASS) Software, Version 6.4. Open Source Geospatial Foundation.
Higouchi, T. 1983. _Visual and Spatial Structure Of Landscapes_. Cambridge, Mass: MIT Press. 
Llobera, M. 2003. Extending GIS-based visual analysis: the concept of visualscapes. International journal of geographical information science 17(1), 25-48.

