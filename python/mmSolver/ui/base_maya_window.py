# Copyright (C) 2019 David Cattermole.
#
# This file is part of mmSolver.
#
# mmSolver is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# mmSolver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
#
"""
The base window for usage inside Maya.

All windows inside Maya should sub-class from BaseMayaWindow.

Using the module::

    import mmSolver.tools.myTool.ui.ui_myTool as ui_myTool
    import mmSolver.ui.base_maya_window as base_maya_window

    class MyToolLayout(QWidget, ui_myTool.Ui_Widget):
        def __init__(self, parent=None, *args, **kwargs):
            super(MyToolLayout, self).__init__(parent=parent, *args, **kwargs)
            self.setupUi(self)

    class MyToolWindow(baseMayaWindow.BaseMayaWindow):
        def __init__(self, parent=None, *args, **kwargs):
            super(MyToolWindow, self).__init__(parent=parent, subLayout=MyToolLayout, *args, **kwargs)
            self.setWindowTitle('Re-Parent')
            self.applyBtn.clicked.connect(self.apply)

        def apply(self):
            print 'apply'

"""

import os
import os.path

from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt
import Qt.QtCore as QtCore
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.utils.config as config_utils
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.ui_base as ui_base


LOG = mmSolver.logger.get_logger()


class BaseMayaWindow(MayaQWidgetBaseMixin,
                     QtWidgets.QMainWindow,
                     ui_base.Ui_Window):

    name = 'BaseMayaWindow'
    instance = None

    def __init__(self, parent, name=None):
        super(BaseMayaWindow, self).__init__()
        self.windowGeometry = None

        # Destroy this widget when closed. Otherwise it will stay around.
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

        # Call the UI file contents.
        self.setupUi(self)
        if name is not None:
            self.setObjectName(name)

        # Get settings path.
        config_name = type(self).name + '.ini'
        config_path = config_utils.get_home_dir_path(config_name)
        self._settings_path = config_path
        return

    def baseHideStandardButtons(self):
        self.createBtn.hide()
        self.applyBtn.hide()
        self.resetBtn.hide()
        self.helpBtn.hide()
        self.closeBtn.hide()
        return

    def baseHideMenuBar(self):
        self.menubar.hide()
        return

    def baseHideProgressBar(self):
        self.progressBar.hide()
        return

    def addSubForm(self, SubForm):
        if SubForm is None:
            return None
        self.subForm = SubForm(self)
        self.optionsLayout.addWidget(self.subForm)
        return True

    def getSubForm(self):
        """
        Return an instance to the parented SubForm object.
        """
        return self.subForm

    def showEvent(self, event):
        super(BaseMayaWindow, self).showEvent(event)
        path = self._settings_path
        if os.path.isfile(path):
            settings_obj = QtCore.QSettings(path, QtCore.QSettings.IniFormat)
            win_geom = settings_obj.value('windowGeometry')
            self.restoreGeometry(win_geom)
        return

    def closeEvent(self, event):
        super(BaseMayaWindow, self).closeEvent(event)
        path = self._settings_path
        settings_obj = QtCore.QSettings(path, QtCore.QSettings.IniFormat)
        settings_obj.setValue('windowGeometry', self.saveGeometry())
        settings_obj.sync()  # write
        return

    @classmethod
    def get_instance(cls):
        instance = None
        if (cls.instance is not None
                and uiutils.isValidQtObject(cls.instance) is False):
            instance = cls.instance
        return instance

    @classmethod
    def open_window(cls, show=True, auto_raise=True, delete=False):
        if (cls is not None
                and uiutils.isValidQtObject(cls.instance) is False):
            if delete is True:
                cls.instance.close()
                cls.instance.deleteLater()

        if (cls.instance is None
                or uiutils.isValidQtObject(cls.instance) is False):
            name = cls.name
            app, parent = uiutils.getParent()
            cls.instance = cls(parent=parent, name=name)

        # Make sure the user can see this window.
        if cls.instance.isHidden():
            if show is True:
                cls.instance.show()
        else:
            if auto_raise is True:
                cls.instance.raise_()
                cls.instance.activateWindow()
        return cls.instance
