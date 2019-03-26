# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/media/dev/mayaMatchMoveSolver/python/mmSolver/ui/base.ui'
#
# Created: Tue Mar 26 00:01:14 2019
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Window(object):
    def setupUi(self, Window):
        Window.setObjectName("Window")
        Window.resize(453, 185)
        Window.setDocumentMode(False)
        self.centralwidget = QtWidgets.QWidget(Window)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.options = QtWidgets.QWidget(self.centralwidget)
        self.options.setObjectName("options")
        self.optionsLayout = QtWidgets.QVBoxLayout(self.options)
        self.optionsLayout.setSpacing(3)
        self.optionsLayout.setContentsMargins(0, 0, 0, 0)
        self.optionsLayout.setContentsMargins(0, 0, 0, 0)
        self.optionsLayout.setObjectName("optionsLayout")
        self.verticalLayout.addWidget(self.options)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.createBtn = QtWidgets.QPushButton(self.centralwidget)
        self.createBtn.setObjectName("createBtn")
        self.horizontalLayout.addWidget(self.createBtn)
        self.applyBtn = QtWidgets.QPushButton(self.centralwidget)
        self.applyBtn.setObjectName("applyBtn")
        self.horizontalLayout.addWidget(self.applyBtn)
        self.resetBtn = QtWidgets.QPushButton(self.centralwidget)
        self.resetBtn.setObjectName("resetBtn")
        self.horizontalLayout.addWidget(self.resetBtn)
        self.helpBtn = QtWidgets.QPushButton(self.centralwidget)
        self.helpBtn.setObjectName("helpBtn")
        self.horizontalLayout.addWidget(self.helpBtn)
        self.closeBtn = QtWidgets.QPushButton(self.centralwidget)
        self.closeBtn.setObjectName("closeBtn")
        self.horizontalLayout.addWidget(self.closeBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        Window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 453, 46))
        self.menubar.setObjectName("menubar")
        Window.setMenuBar(self.menubar)

        self.retranslateUi(Window)
        QtCore.QObject.connect(self.closeBtn, QtCore.SIGNAL("clicked()"), Window.close)
        QtCore.QMetaObject.connectSlotsByName(Window)

    def retranslateUi(self, Window):
        Window.setWindowTitle(QtWidgets.QApplication.translate("Window", "MainWindow", None, -1))
        self.createBtn.setText(QtWidgets.QApplication.translate("Window", "Create", None, -1))
        self.applyBtn.setText(QtWidgets.QApplication.translate("Window", "Apply", None, -1))
        self.resetBtn.setText(QtWidgets.QApplication.translate("Window", "Reset", None, -1))
        self.helpBtn.setText(QtWidgets.QApplication.translate("Window", "Help", None, -1))
        self.closeBtn.setText(QtWidgets.QApplication.translate("Window", "Close", None, -1))

