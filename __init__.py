# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ViewshedAnalysis
                                 A QGIS plugin
 ------description-------
                             -------------------
        begin                : 2013-05-22
        copyright            : (C) 2013 by Z
        email                : reee
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
    return "Calculates binary viewshed for multiple points."


def version():
    return "Version 0.13"


def icon():
    return "icon.png"


def qgisMinimumVersion():
    return "1.8"

def author():
    return "Zoran Čučković"

def email():
    return "n/a"

def classFactory(iface):
    # load ViewshedAnalysis class from file ViewshedAnalysis
    from viewshedanalysis import ViewshedAnalysis
    return ViewshedAnalysis(iface)
