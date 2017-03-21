# -*- coding: utf-8 -*-

from viewshedanalysis.viewshedproviderplugin import ViewshedProviderPlugin


def classFactory(iface):
    return ViewshedProviderPlugin()
