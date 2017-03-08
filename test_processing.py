# -*- coding: utf-8 -*-

"""
/***************************************************************************
 test_processing
                                 A QGIS plugin
 uuu
                              -------------------
        begin                : 2017-02-27
        copyright            : (C) 2017 by hhhh
        email                : na
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

__author__ = 'hhhh'
__date__ = '2017-02-27'
__copyright__ = '(C) 2017 by hhhh'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import sys
import inspect

from processing.core.Processing import Processing
from test_processing_provider import test_processingProvider

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class test_processingPlugin:

    def __init__(self):
        self.provider = test_processingProvider()

    def initGui(self):
        Processing.addProvider(self.provider)

    def unload(self):
        Processing.removeProvider(self.provider)
