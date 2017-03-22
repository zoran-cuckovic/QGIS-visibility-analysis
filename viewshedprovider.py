# -*- coding: utf-8 -*-

from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.ProcessingConfig import Setting, ProcessingConfig

from viewshedanalysis.viewshedfixed import ViewshedFixed
from viewshedanalysis.viewshedvariable import ViewshedVariable


class ViewshedProvider(AlgorithmProvider):

    def __init__(self):
        AlgorithmProvider.__init__(self)

        self.activate = True

        self.alglist = []
        self.alglist = [ViewshedFixed(), ViewshedVariable()]
        for alg in self.alglist:
            alg.provider = self

    def initializeSettings(self):
        AlgorithmProvider.initializeSettings(self)

    def unload(self):
        AlgorithmProvider.unload(self)

    def id(self):
        return 'visibility'

    def name(self):
        return 'Visibility analysis'

    def icon(self):
        return AlgorithmProvider.icon(self)

    def _loadAlgorithms(self):
        self.algs = self.alglist
