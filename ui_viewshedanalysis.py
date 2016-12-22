# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_viewshedanalysis.ui'
#
# Created: Wed Dec 21 13:05:35 2016
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ViewshedAnalysis(object):
    def setupUi(self, ViewshedAnalysis):
        ViewshedAnalysis.setObjectName(_fromUtf8("ViewshedAnalysis"))
        ViewshedAnalysis.resize(448, 622)
        self.tabWidget = QtGui.QTabWidget(ViewshedAnalysis)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 427, 581))
        self.tabWidget.setAutoFillBackground(False)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.General_tab = QtGui.QWidget()
        self.General_tab.setObjectName(_fromUtf8("General_tab"))
        self.cmbPoints = QtGui.QComboBox(self.General_tab)
        self.cmbPoints.setGeometry(QtCore.QRect(10, 90, 201, 22))
        self.cmbPoints.setEditable(False)
        self.cmbPoints.setObjectName(_fromUtf8("cmbPoints"))
        self.label = QtGui.QLabel(self.General_tab)
        self.label.setGeometry(QtCore.QRect(10, 20, 111, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.General_tab)
        self.label_2.setGeometry(QtCore.QRect(10, 70, 131, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.cmbRaster = QtGui.QComboBox(self.General_tab)
        self.cmbRaster.setGeometry(QtCore.QRect(10, 40, 201, 22))
        self.cmbRaster.setObjectName(_fromUtf8("cmbRaster"))
        self.txtOutput = QtGui.QPlainTextEdit(self.General_tab)
        self.txtOutput.setGeometry(QtCore.QRect(220, 40, 181, 41))
        self.txtOutput.setObjectName(_fromUtf8("txtOutput"))
        self.label_5 = QtGui.QLabel(self.General_tab)
        self.label_5.setGeometry(QtCore.QRect(220, 20, 91, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.cmdBrowse = QtGui.QPushButton(self.General_tab)
        self.cmdBrowse.setGeometry(QtCore.QRect(320, 90, 75, 31))
        self.cmdBrowse.setObjectName(_fromUtf8("cmdBrowse"))
        self.Output_groupBox = QtGui.QGroupBox(self.General_tab)
        self.Output_groupBox.setGeometry(QtCore.QRect(10, 340, 391, 91))
        self.Output_groupBox.setObjectName(_fromUtf8("Output_groupBox"))
        self.chkBinary = QtGui.QRadioButton(self.Output_groupBox)
        self.chkBinary.setGeometry(QtCore.QRect(10, 30, 141, 22))
        self.chkBinary.setObjectName(_fromUtf8("chkBinary"))
        self.chkInvisibility = QtGui.QRadioButton(self.Output_groupBox)
        self.chkInvisibility.setGeometry(QtCore.QRect(190, 30, 141, 22))
        self.chkInvisibility.setObjectName(_fromUtf8("chkInvisibility"))
        self.chkIntervisibility = QtGui.QRadioButton(self.Output_groupBox)
        self.chkIntervisibility.setGeometry(QtCore.QRect(10, 60, 161, 17))
        self.chkIntervisibility.setObjectName(_fromUtf8("chkIntervisibility"))
        self.chkHorizon = QtGui.QRadioButton(self.Output_groupBox)
        self.chkHorizon.setGeometry(QtCore.QRect(190, 60, 81, 16))
        self.chkHorizon.setObjectName(_fromUtf8("chkHorizon"))
        self.chkHorizon_full = QtGui.QRadioButton(self.Output_groupBox)
        self.chkHorizon_full.setGeometry(QtCore.QRect(280, 60, 111, 17))
        self.chkHorizon_full.setObjectName(_fromUtf8("chkHorizon_full"))
        self.groupBox_3 = QtGui.QGroupBox(self.General_tab)
        self.groupBox_3.setGeometry(QtCore.QRect(10, 170, 391, 167))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.label_16 = QtGui.QLabel(self.groupBox_3)
        self.label_16.setGeometry(QtCore.QRect(260, 140, 121, 20))
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.txtAdaptRadiusObs = QtGui.QLineEdit(self.groupBox_3)
        self.txtAdaptRadiusObs.setGeometry(QtCore.QRect(40, 140, 31, 20))
        self.txtAdaptRadiusObs.setObjectName(_fromUtf8("txtAdaptRadiusObs"))
        self.label_15 = QtGui.QLabel(self.groupBox_3)
        self.label_15.setGeometry(QtCore.QRect(80, 140, 131, 20))
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.txtAdaptRadiusTarget = QtGui.QLineEdit(self.groupBox_3)
        self.txtAdaptRadiusTarget.setGeometry(QtCore.QRect(220, 140, 31, 20))
        self.txtAdaptRadiusTarget.setObjectName(_fromUtf8("txtAdaptRadiusTarget"))
        self.cmbTargetField = QtGui.QComboBox(self.groupBox_3)
        self.cmbTargetField.setEnabled(True)
        self.cmbTargetField.setGeometry(QtCore.QRect(260, 90, 121, 22))
        self.cmbTargetField.setEditable(False)
        self.cmbTargetField.setObjectName(_fromUtf8("cmbTargetField"))
        self.label_10 = QtGui.QLabel(self.groupBox_3)
        self.label_10.setGeometry(QtCore.QRect(190, 60, 61, 20))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.txtObserver = QtGui.QLineEdit(self.groupBox_3)
        self.txtObserver.setGeometry(QtCore.QRect(130, 60, 51, 20))
        self.txtObserver.setObjectName(_fromUtf8("txtObserver"))
        self.cmbObsField = QtGui.QComboBox(self.groupBox_3)
        self.cmbObsField.setGeometry(QtCore.QRect(260, 60, 121, 22))
        self.cmbObsField.setEditable(False)
        self.cmbObsField.setObjectName(_fromUtf8("cmbObsField"))
        self.label_11 = QtGui.QLabel(self.groupBox_3)
        self.label_11.setGeometry(QtCore.QRect(190, 90, 61, 20))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.label_4 = QtGui.QLabel(self.groupBox_3)
        self.label_4.setGeometry(QtCore.QRect(10, 90, 101, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_3 = QtGui.QLabel(self.groupBox_3)
        self.label_3.setGeometry(QtCore.QRect(10, 60, 121, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.txtTarget = QtGui.QLineEdit(self.groupBox_3)
        self.txtTarget.setGeometry(QtCore.QRect(130, 90, 51, 20))
        self.txtTarget.setObjectName(_fromUtf8("txtTarget"))
        self.label_6 = QtGui.QLabel(self.groupBox_3)
        self.label_6.setGeometry(QtCore.QRect(10, 120, 271, 16))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.txtRadius = QtGui.QLineEdit(self.groupBox_3)
        self.txtRadius.setGeometry(QtCore.QRect(130, 30, 51, 21))
        self.txtRadius.setObjectName(_fromUtf8("txtRadius"))
        self.label_8 = QtGui.QLabel(self.groupBox_3)
        self.label_8.setGeometry(QtCore.QRect(10, 30, 91, 16))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.groupBox = QtGui.QGroupBox(self.General_tab)
        self.groupBox.setGeometry(QtCore.QRect(10, 440, 401, 111))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.chkCurvature = QtGui.QCheckBox(self.groupBox)
        self.chkCurvature.setGeometry(QtCore.QRect(10, 50, 161, 22))
        self.chkCurvature.setObjectName(_fromUtf8("chkCurvature"))
        self.txtRefraction = QtGui.QLineEdit(self.groupBox)
        self.txtRefraction.setEnabled(False)
        self.txtRefraction.setGeometry(QtCore.QRect(180, 50, 51, 21))
        self.txtRefraction.setObjectName(_fromUtf8("txtRefraction"))
        self.label_17 = QtGui.QLabel(self.groupBox)
        self.label_17.setGeometry(QtCore.QRect(240, 50, 161, 20))
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.chkCumulative = QtGui.QCheckBox(self.groupBox)
        self.chkCumulative.setEnabled(True)
        self.chkCumulative.setGeometry(QtCore.QRect(10, 20, 261, 21))
        self.chkCumulative.setObjectName(_fromUtf8("chkCumulative"))
        self.label_12 = QtGui.QLabel(self.groupBox)
        self.label_12.setGeometry(QtCore.QRect(10, 80, 111, 16))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.cmbAlgorithm = QtGui.QComboBox(self.groupBox)
        self.cmbAlgorithm.setGeometry(QtCore.QRect(180, 80, 121, 22))
        self.cmbAlgorithm.setEditable(False)
        self.cmbAlgorithm.setObjectName(_fromUtf8("cmbAlgorithm"))
        self.cmbAlgorithm.addItem(_fromUtf8(""))
        self.cmbAlgorithm.addItem(_fromUtf8(""))
        self.cmbAlgorithm.addItem(_fromUtf8(""))
        self.cmbPointsTarget = QtGui.QComboBox(self.General_tab)
        self.cmbPointsTarget.setEnabled(True)
        self.cmbPointsTarget.setGeometry(QtCore.QRect(10, 140, 201, 22))
        self.cmbPointsTarget.setEditable(False)
        self.cmbPointsTarget.setObjectName(_fromUtf8("cmbPointsTarget"))
        self.label_7 = QtGui.QLabel(self.General_tab)
        self.label_7.setGeometry(QtCore.QRect(10, 120, 191, 20))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.tabWidget.addTab(self.General_tab, _fromUtf8(""))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.textBrowser_2 = QtGui.QTextBrowser(self.tab)
        self.textBrowser_2.setGeometry(QtCore.QRect(0, 0, 421, 551))
        self.textBrowser_2.setOpenExternalLinks(True)
        self.textBrowser_2.setObjectName(_fromUtf8("textBrowser_2"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.About_tab = QtGui.QWidget()
        self.About_tab.setObjectName(_fromUtf8("About_tab"))
        self.textBrowser = QtGui.QTextBrowser(self.About_tab)
        self.textBrowser.setGeometry(QtCore.QRect(0, 0, 421, 551))
        self.textBrowser.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.textBrowser.setFrameShape(QtGui.QFrame.Box)
        self.textBrowser.setFrameShadow(QtGui.QFrame.Sunken)
        self.textBrowser.setOpenExternalLinks(True)
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.tabWidget.addTab(self.About_tab, _fromUtf8(""))
        self.buttonBox = QtGui.QDialogButtonBox(ViewshedAnalysis)
        self.buttonBox.setGeometry(QtCore.QRect(270, 590, 161, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))

        self.retranslateUi(ViewshedAnalysis)
        self.tabWidget.setCurrentIndex(0)
        self.cmbAlgorithm.setCurrentIndex(1)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ViewshedAnalysis.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ViewshedAnalysis.reject)
        QtCore.QObject.connect(self.chkCurvature, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.txtRefraction.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(ViewshedAnalysis)

    def retranslateUi(self, ViewshedAnalysis):
        ViewshedAnalysis.setWindowTitle(_translate("ViewshedAnalysis", "Advanced viewshed analysis", None))
        self.label.setText(_translate("ViewshedAnalysis", "Elevation raster", None))
        self.label_2.setText(_translate("ViewshedAnalysis", "Observation points", None))
        self.label_5.setText(_translate("ViewshedAnalysis", "Output file", None))
        self.cmdBrowse.setText(_translate("ViewshedAnalysis", "Browse", None))
        self.Output_groupBox.setTitle(_translate("ViewshedAnalysis", "Output ", None))
        self.chkBinary.setText(_translate("ViewshedAnalysis", "Binary viewshed", None))
        self.chkInvisibility.setText(_translate("ViewshedAnalysis", "Invisibility depth", None))
        self.chkIntervisibility.setText(_translate("ViewshedAnalysis", "Intervisibility", None))
        self.chkHorizon.setText(_translate("ViewshedAnalysis", "Horizon", None))
        self.chkHorizon_full.setText(_translate("ViewshedAnalysis", "Horizon full", None))
        self.groupBox_3.setTitle(_translate("ViewshedAnalysis", "Settings ", None))
        self.label_16.setText(_translate("ViewshedAnalysis", "pixels for target", None))
        self.txtAdaptRadiusObs.setText(_translate("ViewshedAnalysis", "0", None))
        self.label_15.setText(_translate("ViewshedAnalysis", "pixels for observer", None))
        self.txtAdaptRadiusTarget.setText(_translate("ViewshedAnalysis", "0", None))
        self.label_10.setText(_translate("ViewshedAnalysis", "or field:", None))
        self.txtObserver.setText(_translate("ViewshedAnalysis", "1.6", None))
        self.label_11.setText(_translate("ViewshedAnalysis", "or field:", None))
        self.label_4.setText(_translate("ViewshedAnalysis", "Target height", None))
        self.label_3.setText(_translate("ViewshedAnalysis", "Observer height", None))
        self.txtTarget.setText(_translate("ViewshedAnalysis", "0", None))
        self.label_6.setText(_translate("ViewshedAnalysis", "Adapt to highest point at a distance of: ", None))
        self.txtRadius.setText(_translate("ViewshedAnalysis", "5000", None))
        self.label_8.setText(_translate("ViewshedAnalysis", "Search radius", None))
        self.groupBox.setTitle(_translate("ViewshedAnalysis", "Options", None))
        self.chkCurvature.setText(_translate("ViewshedAnalysis", "Use earth curvature", None))
        self.txtRefraction.setText(_translate("ViewshedAnalysis", "0.13", None))
        self.label_17.setText(_translate("ViewshedAnalysis", "Atmospheric refraction", None))
        self.chkCumulative.setText(_translate("ViewshedAnalysis", " Cumulative (for raster output)", None))
        self.label_12.setText(_translate("ViewshedAnalysis", "Precision", None))
        self.cmbAlgorithm.setItemText(0, _translate("ViewshedAnalysis", "Coarse", None))
        self.cmbAlgorithm.setItemText(1, _translate("ViewshedAnalysis", "Normal", None))
        self.cmbAlgorithm.setItemText(2, _translate("ViewshedAnalysis", "Fine", None))
        self.label_7.setText(_translate("ViewshedAnalysis", "Target points (intervisibility)", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.General_tab), _translate("ViewshedAnalysis", "General", None))
        self.textBrowser_2.setHtml(_translate("ViewshedAnalysis", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:16px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">Data</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:10pt; font-weight:600;\">Raster layer:</span><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\"> any supported raster format. For better performance the extent of the raster should be cropped to the analysed area. Too large of a raster will saturate memory.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:10pt; font-weight:600;\">Observer points:</span><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\"> shapefile containing observer points. The coordinate reference systems of the elevation raster and the observer/target point(s) </span><span style=\" font-family:\'Ubuntu\'; font-size:10pt; text-decoration: underline;\">must match</span><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\">. If field named</span><span style=\" font-family:\'Ubuntu\'; font-size:10pt; font-weight:600;\"> ID </span><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\">exists</span><span style=\" font-family:\'Ubuntu\'; font-size:10pt; font-weight:600;\">, </span><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\">it will be used for filenames and </span><span style=\" font-family:\'Ubuntu\'; font-size:10pt; text-decoration: underline;\">should be unique</span><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\">. Otherwise, the internal Id is used. By default a single viewshed will be produced for each point: check </span><span style=\" font-family:\'Ubuntu\'; font-size:10pt; text-decoration: underline;\">cumulative option</span><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\"> to obtain a sum of all viewsheds in a single raster.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:10pt; font-weight:600;\">Target points:</span><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\"> this option is used for intervisibility analysis only.</span></p>\n"
"<p style=\" margin-top:16px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:12pt; font-weight:600;\">Settings</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:10pt; font-weight:600;\">Search radius</span><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\">: size of the analysed area around each observer point.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:10pt; font-weight:600;\">Observer/target height:</span><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\"> height above ground from which the analysis is made. If the height should vary across points, it can be read from a table column. In case of error, the observer/target height specified in the textbox will be used.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:10pt; font-weight:600;\">Adapt to highest point: </span><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\">search the highest point in the vicinity. The search is made in a quadrangular window where the observer point is in the middle.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:12pt; font-weight:600;\">Output</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:10pt; font-weight:600;\">Viewshed:</span><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\"> standard true/false (binary) viewshed. Multiple viewsheds can be combined in a one raster layer using the cumulative option.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:10pt; font-weight:600;\">Intervisibility: </span><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\">produces a network of visual relationships between two sets of points (or within a single set). </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:10pt; font-weight:600;\">Invisibility depth:</span><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\"> measures the size an object should attain in order to become visible if placed in an area out of view. </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:10pt; font-weight:600;\">Horizon:</span><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\"> is the last visible place on the terrain, which corresponds to fringes of visible zones.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:12pt; font-weight:600;\">Algorithm options</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:10pt; font-weight:600;\">Cumulative: </span><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\">sum all outputs in a single raster. </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:10pt; font-weight:600;\">Earth curvature:</span><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\"> takes into account the slope of  Earth\'s surface around the observer point.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:10pt; font-weight:600;\">Atmospheric refraction:</span><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\">  coefficient used to calculate the bending down of the light due to the atmosphere.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:10pt; font-weight:600;\">Precision: </span><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\">choose between faster / less precise and slower / more precise calculation.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:10pt; text-decoration: underline;\">For more detailed reference see:</span><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\"> <br /></span><a href=\"http://zoran-cuckovic.from.hr/QGIS-visibility-analysis/\"><span style=\" font-family:\'Ubuntu\'; font-size:10pt; text-decoration: underline; color:#0000ff;\">www.zoran-cuckovic.from.hr/QGIS-visibility-analysis/</span></a><span style=\" font-family:\'Ubuntu\'; font-size:10pt;\"> </span></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("ViewshedAnalysis", "Reference", None))
        self.textBrowser.setHtml(_translate("ViewshedAnalysis", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:11pt;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:12pt; font-weight:600;\">Visibility analysis for QGIS</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:12pt; font-weight:600;\">Version 0.5.4</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:12pt; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:12pt;\">Licence: GNU GPL v. 3</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:12pt; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:11pt;\">Developed by Zoran Čučković, Laboratoire Chrono-environnement – UMR 6249, Université de Franche-Comté, Besançon (France).</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:11pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:11pt;\">For manual see: </span><a href=\"http://zoran-cuckovic.from.hr/QGIS-visibility-analysis/\"><span style=\" font-family:\'Ubuntu\'; font-size:11pt; text-decoration: underline; color:#0000ff;\">HERE</span></a><span style=\" font-family:\'Ubuntu\'; font-size:11pt;\"> </span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:11pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:11pt;\">For more on algoritm behaviour, tutorial(s), and case studies check: </span><a href=\"http://zoran-cuckovic.from.hr\"><span style=\" font-size:11pt; text-decoration: underline; color:#0000ff;\">zoran-cuckovic.from.hr</span></a><span style=\" font-family:\'Ubuntu\'; font-size:11pt;\">.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:11pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:600;\">Published as:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:11pt;\">Čučković, Z. (2016) Advanced viewshed analysis: a Quantum GIS plug-in for the analysis of visual landscapes. JOSS 1(4). [DOI:</span><a href=\"http://dx.doi.org/10.21105/joss.00032\"><span style=\" font-size:11pt; text-decoration: underline; color:#0000ff;\">10.21105/joss.00032</span></a><span style=\" font-family:\'Ubuntu\'; font-size:11pt;\">]</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:11pt;\"><br /></p>\n"
"<p align=\"right\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:11pt;\"><br /></p>\n"
"<p align=\"right\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:11pt;\"> </span><a href=\"http://zoran-cuckovic.from.hr/support/qgis-visibility\"><span style=\" font-family:\'Ubuntu\'; font-size:11pt; text-decoration: underline; color:#0000ff;\">Support Visibility analysis plugin &lt;3</span></a><span style=\" font-family:\'Ubuntu\'; font-size:11pt;\"> </span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.About_tab), _translate("ViewshedAnalysis", "About", None))

