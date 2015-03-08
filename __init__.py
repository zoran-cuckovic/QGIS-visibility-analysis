# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ViewshedAnalysis
                                 A QGIS plugin
 ------description-------
                             -------------------
        begin                : 2013-05-22
        copyright            : (C) 2013 by Zoran Čučković 
        email                : 
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


def name():
    return "Viewshed Analysis"


def description():
    return "Calculates viewsheds, intervisibility networks, invisibility depth and visible horizon for multiple points."


def version():
    return "Version 0.4.2"


def icon():
    return "icon.png"


def qgisMinimumVersion():
    return "2.0"

def author():
    return "Zoran Čučković"

def email():
    return "n/a"

def classFactory(iface):
    # load ViewshedAnalysis class from file ViewshedAnalysis
    from viewshedanalysis import ViewshedAnalysis
    return ViewshedAnalysis(iface)
