# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_viewshedanalysis.ui'
#
# Created: Mon Dec  8 19:32:53 2014
#      by: PyQt4 UI code generator 4.10.4
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
        ViewshedAnalysis.resize(448, 568)
        self.tabWidget = QtGui.QTabWidget(ViewshedAnalysis)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 427, 521))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.General_tab = QtGui.QWidget()
        self.General_tab.setObjectName(_fromUtf8("General_tab"))
        self.label_9 = QtGui.QLabel(self.General_tab)
        self.label_9.setGeometry(QtCore.QRect(10, 120, 191, 16))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.cmbPoints = QtGui.QComboBox(self.General_tab)
        self.cmbPoints.setGeometry(QtCore.QRect(10, 90, 201, 22))
        self.cmbPoints.setEditable(False)
        self.cmbPoints.setObjectName(_fromUtf8("cmbPoints"))
        self.cmbPointsTarget = QtGui.QComboBox(self.General_tab)
        self.cmbPointsTarget.setGeometry(QtCore.QRect(10, 140, 201, 22))
        self.cmbPointsTarget.setEditable(False)
        self.cmbPointsTarget.setObjectName(_fromUtf8("cmbPointsTarget"))
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
        self.Output_groupBox.setGeometry(QtCore.QRect(10, 343, 391, 85))
        self.Output_groupBox.setObjectName(_fromUtf8("Output_groupBox"))
        self.chkCumulative = QtGui.QCheckBox(self.Output_groupBox)
        self.chkCumulative.setEnabled(False)
        self.chkCumulative.setGeometry(QtCore.QRect(40, 38, 111, 21))
        self.chkCumulative.setObjectName(_fromUtf8("chkCumulative"))
        self.chkBinary = QtGui.QRadioButton(self.Output_groupBox)
        self.chkBinary.setGeometry(QtCore.QRect(10, 17, 141, 22))
        self.chkBinary.setObjectName(_fromUtf8("chkBinary"))
        self.chkInvisibility = QtGui.QRadioButton(self.Output_groupBox)
        self.chkInvisibility.setGeometry(QtCore.QRect(170, 59, 141, 22))
        self.chkInvisibility.setObjectName(_fromUtf8("chkInvisibility"))
        self.chkIntervisibility = QtGui.QRadioButton(self.Output_groupBox)
        self.chkIntervisibility.setGeometry(QtCore.QRect(170, 20, 161, 17))
        self.chkIntervisibility.setObjectName(_fromUtf8("chkIntervisibility"))
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
        self.groupBox.setGeometry(QtCore.QRect(10, 430, 391, 51))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.chkCurvature = QtGui.QCheckBox(self.groupBox)
        self.chkCurvature.setGeometry(QtCore.QRect(10, 20, 161, 22))
        self.chkCurvature.setObjectName(_fromUtf8("chkCurvature"))
        self.txtRefraction = QtGui.QLineEdit(self.groupBox)
        self.txtRefraction.setEnabled(False)
        self.txtRefraction.setGeometry(QtCore.QRect(160, 20, 51, 21))
        self.txtRefraction.setObjectName(_fromUtf8("txtRefraction"))
        self.label_17 = QtGui.QLabel(self.groupBox)
        self.label_17.setGeometry(QtCore.QRect(220, 20, 161, 20))
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.tabWidget.addTab(self.General_tab, _fromUtf8(""))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.textBrowser_2 = QtGui.QTextBrowser(self.tab)
        self.textBrowser_2.setGeometry(QtCore.QRect(0, 0, 421, 435))
        self.textBrowser_2.setObjectName(_fromUtf8("textBrowser_2"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.About_tab = QtGui.QWidget()
        self.About_tab.setObjectName(_fromUtf8("About_tab"))
        self.textBrowser = QtGui.QTextBrowser(self.About_tab)
        self.textBrowser.setGeometry(QtCore.QRect(0, 0, 421, 435))
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.tabWidget.addTab(self.About_tab, _fromUtf8(""))
        self.buttonBox = QtGui.QDialogButtonBox(ViewshedAnalysis)
        self.buttonBox.setGeometry(QtCore.QRect(260, 536, 161, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.progressBar = QtGui.QProgressBar(ViewshedAnalysis)
        self.progressBar.setGeometry(QtCore.QRect(10, 540, 201, 23))
        self.progressBar.setObjectName(_fromUtf8("progressBar"))

        self.retranslateUi(ViewshedAnalysis)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ViewshedAnalysis.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ViewshedAnalysis.reject)
        QtCore.QObject.connect(self.chkBinary, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.chkCumulative.setEnabled)
        QtCore.QObject.connect(self.chkCurvature, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.txtRefraction.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(ViewshedAnalysis)

    def retranslateUi(self, ViewshedAnalysis):
        ViewshedAnalysis.setWindowTitle(_translate("ViewshedAnalysis", "Advanced viewshed analysis  0.3", None))
        self.label_9.setText(_translate("ViewshedAnalysis", "Target points (intervisibility)", None))
        self.label.setText(_translate("ViewshedAnalysis", "Elevation raster", None))
        self.label_2.setText(_translate("ViewshedAnalysis", "Observation points", None))
        self.label_5.setText(_translate("ViewshedAnalysis", "Output file", None))
        self.cmdBrowse.setText(_translate("ViewshedAnalysis", "Browse", None))
        self.Output_groupBox.setTitle(_translate("ViewshedAnalysis", "Output ", None))
        self.chkCumulative.setText(_translate("ViewshedAnalysis", "Cumulative ", None))
        self.chkBinary.setText(_translate("ViewshedAnalysis", "Binary viewshed", None))
        self.chkInvisibility.setText(_translate("ViewshedAnalysis", "Invisibility depth", None))
        self.chkIntervisibility.setText(_translate("ViewshedAnalysis", "Intervisibility", None))
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
        self.chkCurvature.setText(_translate("ViewshedAnalysis", "Earth curvature", None))
        self.txtRefraction.setText(_translate("ViewshedAnalysis", "0.13", None))
        self.label_17.setText(_translate("ViewshedAnalysis", "Atmospheric refraction", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.General_tab), _translate("ViewshedAnalysis", "General", None))
        self.textBrowser_2.setHtml(_translate("ViewshedAnalysis", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Raster layer:</span> any supported raster format. For better performance the extent of the raster should be cropped to the analysed area. Too large of a raster will saturate memory.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Observer points:</span> shapefile containing observer points. The coordinate reference systems of the elevation raster and the observer/target point(s) <span style=\" text-decoration: underline;\">must match</span>. If field named<span style=\" font-weight:600;\"> ID </span>exists<span style=\" font-weight:600;\">, </span>it will be used for filenames and <span style=\" text-decoration: underline;\">should be unique</span>. Otherwise, the internal Id is used.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Target points:</span> this option is normally used for intervisibility analysis. If chosen with other otput options it behaves as a mask, i.e. only the pixels corresponding to target points are analysed.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Search radius</span>: size of the analyzed area around each observer point.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Adapt to highest point: </span>search the highest point in the vicinity. The search is made in a quadrangular window where the observer point is in the middle.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Viewshed:</span> standard true/false (binary) viewshed. Multiple viewsheds can be combined in a one raster layer using the cumulative option.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Intervisibility: </span>produces a network of visual relationships between two sets of points (or whithin a single set). </p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Invisibility depth:</span> measures the size an object should attain in order to become visible if placed in an area out of view. </p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Earth curvature:</span> takes into account the slope of Earth\'s surface around the observer point.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Atmospheric refraction:</span> coefficient used to calculate the bending down of the light due to the atmosphere (it has the opposite, but smaller, effect than the curvature).</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">(Following formula is used:</p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">                        Dist<span style=\" vertical-align:super;\">2 </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Z<span style=\" vertical-align:sub;\">actual</span> = Z<span style=\" vertical-align:sub;\">surface</span> - ------------ * (1 - R<span style=\" vertical-align:sub;\">refr</span>)</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">                       Diam<span style=\" vertical-align:sub;\">earth</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Where:</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Dist : The planimetric distance between the observation point and the target point.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Diam : The diameter of the earth that is calculated as Semi-major axis + Semi-minor axis (which are defined by projection system of the raster layer).</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">R<span style=\" vertical-align:sub;\">refr </span>: The refractivity coefficient of light.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The formula is adapted from ArcGIS:<span style=\" font-size:9pt;\"> http://help.arcgis.com/en/arcgisdesktop/10.0/help/index.html#//009z000000v8000000.htm</span>) </p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("ViewshedAnalysis", "Reference", None))
        self.textBrowser.setHtml(_translate("ViewshedAnalysis", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:20px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Advanced viewshed analysis plugin for QGIS</span></p>\n"
"<p align=\"center\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">version 0.1 (experimental)</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Viewshed analysis is a standard feature of GIS software, but its potential cannot be fully explored by standard implementations. The idea behind this plugin is to provide alternative data outputs that cannot be obtained without difficulty (if at all) using simple binary viewsheds. On the downside, the speed and accuracy are inferior to common implementations (such as r.los in GRASS). Therefore, our plugin is not intended as a replacement of existing modules but instead as a complementary exploration tool.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><img src=\":plugins/ViewshedAnalysis/Fig1_small.png\" /></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">How does it work ?</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Our approach is to cast an array of lines-of-sight from the obseration point to the perimeter of the analysed area. We then record the position above or below the visibility line of each pixel encountered along the line. The height values for each pixel are interpolated with its nearest neighbour on the opposite side of the line-of-sight. </p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Observer and target point locations are approximated to the pixel centre. This may seem problematic since even sub-pixel variations of the observer point could have perceptible impacts on the final output. However, susceptibility to variations within the immediate observer context is an inherent problem of viewshed modeling in general. What is more, if our observer is a living being, some kind of movement and adaptation should always be expected: these very variations might be turned into his/her/its advantage. We need flexibility much more than precision. In any case, a finer DEM should be used (even if resampled) in order to obtain more detailed results with any viewshed algorithm.</p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:2px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:2px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"> Developed by Zoran Čučković</p>\n"
"<p align=\"center\" style=\" margin-top:2px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Laboratoire Chrono-environnement – UMR 6249</p>\n"
"<p align=\"center\" style=\" margin-top:2px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Université de Franche-Comté, Besançon (France)</p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; text-decoration: underline; color:#0000ff;\"><br /></p>\n"
"<p align=\"right\" style=\" margin-top:0px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt;\"> Revised on December 1 , 2014</span></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.About_tab), _translate("ViewshedAnalysis", "About", None))

