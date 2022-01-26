# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Visibility analysis for QGIS (**to be installed in ViewshedAnalysis folder**)
                              

                              -------------------
        begin                : 2018-03-18
        copyright            : (C) 2018 by Z. Cuckovic
        homepage             : https://zoran-cuckovic.github.io/QGIS-visibility-analysis/
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'AUthor'
__date__ = '2018-03-18'
__copyright__ = '(C) 2018 by AUthor'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import sys
import inspect

from qgis.core import QgsProcessingAlgorithm, QgsApplication
from .visibility_provider import VisibilityProvider

##  this was making problems ??
##cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
##
##if cmd_folder not in sys.path:
##    sys.path.insert(0, cmd_folder)

class VisibilityPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.provider = VisibilityProvider()
        
    def initGui(self):
        self.initProcessing()

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
        
    def initProcessing(self):
        QgsApplication.processingRegistry().addProvider(self.provider)
