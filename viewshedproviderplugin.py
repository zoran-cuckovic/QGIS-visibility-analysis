# -*- coding: utf-8 -*-

import os
import sys
import inspect

from processing.core.Processing import Processing

from viewshedanalysis.viewshedprovider import ViewshedProvider

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class ViewshedProviderPlugin(object):

    def __init__(self):
        self.provider = ViewshedProvider()

    def initGui(self):
        Processing.addProvider(self.provider)

    def unload(self):
        Processing.removeProvider(self.provider)
