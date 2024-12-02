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

from qgis.core import QgsProcessingProvider
from processing.core.ProcessingConfig import Setting, ProcessingConfig

from PyQt5.QtGui import QIcon
from os import path


from .algorithms.viewshed_points import ViewshedPoints
from .algorithms.viewshed_raster import ViewshedRaster
from .algorithms.viewshed_intervisibility import Intervisibility
from .algorithms.viewshed_index import VisibilityIndex
from .algorithms.move_points import MovePoints


class VisibilityProvider(QgsProcessingProvider):

    def __init__(self):
        super().__init__()

		
    def load(self):

        ProcessingConfig.settingIcons[self.name()] = self.icon()
	# Activate provider by default
        ProcessingConfig.addSetting(
            Setting(self.name(), 'VISIBILITY_ANALYSIS_ACTIVATED',
                                    'Activate', True))
        ProcessingConfig.addSetting(
            Setting(self.name(), 'MEMORY_BUFFER_SIZE',
                                    'Memory buffer size (mega-pixels)', 100))
									
        ProcessingConfig.readSettings()
        self.refreshAlgorithms()
        return True

    def unload(self):
        """
        Unloads the provider. Any tear-down steps required by the provider
        should be implemented here.
        """
		
        ProcessingConfig.removeSetting('VISIBILITY_ANALYSIS_ACTIVATED')

    def loadAlgorithms(self):
        """
        Loads all algorithms belonging to this provider.
        
        """

        for alg in [ViewshedPoints(), ViewshedRaster(),
                    Intervisibility() , VisibilityIndex(), 
                    MovePoints()]: self.addAlgorithm( alg )
            
    def isActive(self):
        """Return True if the provider is activated and ready to run algorithms"""
        return ProcessingConfig.getSetting('VISIBILITY_ANALYSIS_ACTIVATED')

    def setActive(self, active):
        ProcessingConfig.setSettingValue('VISIBILITY_ANALYSIS_ACTIVATED', active)
        


    def id(self):
        """
        Returns the unique provider id, used for identifying the provider. This
        string should be a unique, short, character only string, eg "qgis" or
        "gdal". This string should not be localised.
        """
        return 'visibility'

    def name(self):
        """
        Returns the provider name, which is used to describe the provider
        within the GUI.

        This string should be short (e.g. "Lastools") and localised.
        """
        return 'Visibility analysis'

    def longName(self):
        """
        Returns the a longer version of the provider name, which can include
        extra details such as version numbers. E.g. "Lastools LIDAR tools
        (version 2.2.1)". This string should be localised. The default
        implementation returns the same string as name().
        """
        return self.name()

    def icon(self):
        """
		We return the default icon.
		QgsProcessingProvider.icon(self)
        """
        return QIcon(path.dirname(__file__) + '/icon.png')
