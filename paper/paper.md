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

# User manual

[zoran-cuckovic.github.io/QGIS-visibility-analysis/](http://zoran-cuckovic.github.io/QGIS-visibility-analysis/)
