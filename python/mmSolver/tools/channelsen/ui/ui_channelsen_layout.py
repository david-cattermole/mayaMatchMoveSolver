# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\"USERNAME"\Documents\mmsovler\mayaMatchMoveSolver\python\mmSolver\tools\channelsen\ui\channelsen_layout.ui'
#
# Created: Sat Feb  9 22:53:00 2019
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(320, 88)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.sensitivity_label = QtWidgets.QLabel(Form)
        self.sensitivity_label.setObjectName("sensitivity_label")
        self.horizontalLayout_2.addWidget(self.sensitivity_label)
        self.buttons_verticalLayout = QtWidgets.QVBoxLayout()
        self.buttons_verticalLayout.setObjectName("buttons_verticalLayout")
        self.up_pushButton = QtWidgets.QPushButton(Form)
        self.up_pushButton.setObjectName("up_pushButton")
        self.buttons_verticalLayout.addWidget(self.up_pushButton)
        self.default_pushButton = QtWidgets.QPushButton(Form)
        self.default_pushButton.setObjectName("default_pushButton")
        self.buttons_verticalLayout.addWidget(self.default_pushButton)
        self.down_pushButton = QtWidgets.QPushButton(Form)
        self.down_pushButton.setObjectName("down_pushButton")
        self.buttons_verticalLayout.addWidget(self.down_pushButton)
        self.horizontalLayout_2.addLayout(self.buttons_verticalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtWidgets.QApplication.translate("Form", "Form", None, -1))
        self.sensitivity_label.setText(QtWidgets.QApplication.translate("Form", "Sensitivity: 0.01", None, -1))
        self.up_pushButton.setText(QtWidgets.QApplication.translate("Form", "Up", None, -1))
        self.default_pushButton.setText(QtWidgets.QApplication.translate("Form", "Default", None, -1))
        self.down_pushButton.setText(QtWidgets.QApplication.translate("Form", "Down", None, -1))

