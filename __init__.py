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
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'hhhh'
__date__ = '2017-02-27'
__copyright__ = '(C) 2017 by hhhh'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load test_processing class from file test_processing.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .test_processing import test_processingPlugin
    return test_processingPlugin()
