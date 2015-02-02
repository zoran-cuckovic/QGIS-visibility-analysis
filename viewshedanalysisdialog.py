# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ViewshedAnalysisDialog
                                 A QGIS plugin
 ------description-------
                             -------------------
        begin                : 2013-05-22
        copyright            : (C) 2013 by Zoran Čučković
        email                : ----
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

from PyQt4 import QtCore, QtGui
from ui_viewshedanalysis import Ui_ViewshedAnalysis
# novo
from qgis.core import * #treba radi QGis.point (srediti ???)
#from qgis.gui import *

import qgis #jer referencira qgis.utils.iface (zapravo treba samo utils ?)
import subprocess, os, sys

class ViewshedAnalysisDialog(QtGui.QDialog):
   
    def __init__(self):
        
        QtGui.QDialog.__init__(self)
        
        # Set up the user interface from Designer.
        self.ui = Ui_ViewshedAnalysis()
        self.ui.setupUi(self)
        #self.loadLayers()  IZBRISANO
        
        #connections
        self.ui.cmdBrowse.clicked.connect(self.fileOutput)
##        self.ui.cmdAbout.clicked.connect(self.OpenPDFfile)

    def returnPointLayer(self):
        #ovo mu daje varant sa svim podaccima
        l=self.ui.cmbPoints.itemData(self.ui.cmbPoints.currentIndex())
        return str(l)
    
    def returnRasterLayer(self):
        #ovo mu daje varant sa svim podaccima
        l=self.ui.cmbRaster.itemData(self.ui.cmbRaster.currentIndex())
        return str(l)
    
    def returnOutputFile(self):
        #ovo mu daje varant sa svim podaccima
        l=self.ui.txtOutput.toPlainText() #inace text()..
        return str(l)
    
    def returnTargetLayer(self):
        k=self.ui.cmbPointsTarget.currentIndex()
        if k>0:
            l=self.ui.cmbPointsTarget.itemData(k)
            return str(l)
        else: return 0
        
    
    def returnObserverHeight(self):
        try: l = float(self.ui.txtObserver.text())
        except: l=0
        return l

    def returnTargetHeight(self):
        try: l = float(self.ui.txtTarget.text())
        except: l = 0
        return l
    
    def returnRadius(self):
        try: l = float(self.ui.txtRadius.text())
        except: l = 0
        return l
    
    def returnSearchTopObserver(self):
        try: l = int(self.ui.txtAdaptRadiusObs.text())
        except: l=0
        return l
    
    def returnSearchTopTarget(self):
        try: l = int(self.ui.txtAdaptRadiusTarget.text())
        except: l=0
        return l
    
    def returnOutputOptions(self):
        #the idea is to loop through checkboxes, but how ???
        opt = [0,0,0]# list to accomodate for sub options (cumulative, horizon min distance etc)

        if self.ui.chkBinary.isChecked(): opt[0] = "Binary"
        elif self.ui.chkInvisibility.isChecked(): opt[0] = "Invisibility" 
        elif self.ui.chkHorizon.isChecked():
            opt [0]= "Horizon"
  #          try: opt [2]= float(self.ui.txtHorizonDepth.text())
   #         except: pass #will be 0
        elif self.ui.chkIntervisibility.isChecked():  opt [0]= "Intervisibility"

        if self.ui.chkCumulative.isChecked(): opt [1]= "cumulative" 
    
        return opt

    def fileOutput(self): #problem je ekstenzija!!!!
        homedir = os.path.expanduser('~') # ...works on at least windows and linux. 
        
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', homedir, '*')
        try :
            fname = open(filename, 'w')
            self.ui.txtOutput.clear()
            self.ui.txtOutput.insertPlainText(filename)
            #fname.write(txtOutput.toPlainText())
            fname.close()
        except: pass
        
    def returnCurvature (self): # and refraction
        if self.ui.chkCurvature.isChecked():
            try: r=float(self.ui.txtRefraction.text())
            except: r=0
            return (True, r)
        else: return None

    def OpenPDFfile(self):
        
        filepath = os.path.dirname(os.path.abspath(__file__)) + "/help/Advanced viewshed analysis.pdf" 
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', filepath))
        elif os.name == 'nt':
            os.startfile(filepath)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', filepath))

    def setProgressBar(self, total):
        self.ui.progressBar.setMinimum(1)
        self.ui.progressBar.setMaximum(total)

    def updateProgressBar(self, val):
        self.ui.progressBar.setValue(val)

    
        
