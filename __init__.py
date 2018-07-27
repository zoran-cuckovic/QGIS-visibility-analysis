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
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'AUthor'
__date__ = '2018-03-18'
__copyright__ = '(C) 2018 by AUthor'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load senscape class from file senscape.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .visibility_plugin import VisibilityPlugin
    return VisibilityPlugin(iface)

	
