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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
import os
import os.path

import maya.cmds

# In Maya 2025 the
# 'maya.app.general.mayaMixin.MayaQWidgetDockableMixin' class is
# creating an error with mmSolver UIs (because they all inherit from
# BaseMayaWindow). This conditional is used to disable the use of
# 'MayaQWidgetDockableMixin' and avoid the problem while also avoiding
# code changes.
#
# See https://github.com/david-cattermole/mayaMatchMoveSolver/issues/267
#
_USE_MAYA_MIX_IN = maya.cmds.about(apiVersion=True) < 20250000
if _USE_MAYA_MIX_IN is True:
    from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
else:

    # Stub class for compatibility only.
    class MayaQWidgetDockableMixin(object):
        def __init__(self, parent=None, *args, **kwargs):
            super(MayaQWidgetDockableMixin, self).__init__()

        def setDockableParameters(self, *args, **kwargs):
            pass


import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.utils.config as config_utils
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.ui_base as ui_base


LOG = mmSolver.logger.get_logger()
ALL_CLASS_INSTANCES = set()


class BaseMayaWindow(
    MayaQWidgetDockableMixin, QtWidgets.QMainWindow, ui_base.Ui_Window
):

    name = 'BaseMayaWindow'
    instance = None

    def __init__(self, parent, name=None):
        s = time.time()
        super(BaseMayaWindow, self).__init__()
        self.windowGeometry = None

        global ALL_CLASS_INSTANCES
        ALL_CLASS_INSTANCES.add(self)

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
        e = time.time()
        LOG.debug('BaseMayaWindow init: %r seconds', e - s)
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
        if cls.instance is not None and uiutils.isValidQtObject(cls.instance) is True:
            instance = cls.instance
        return instance

    @classmethod
    def close_all_instances(cls):
        global ALL_CLASS_INSTANCES
        for instance in ALL_CLASS_INSTANCES:
            if not instance:
                continue
            if uiutils.isValidQtObject(instance) is False:
                continue
            LOG.debug("Closing: %r", instance.objectName())
            instance.deleteLater()
            instance.close()
        del ALL_CLASS_INSTANCES
        ALL_CLASS_INSTANCES = set()
        return

    @classmethod
    def open_window(cls, show=True, auto_raise=True, delete=False, dock=False):
        s = time.time()
        if cls is not None and uiutils.isValidQtObject(cls.instance) is True:
            if delete is True:
                cls.instance.close()
                cls.instance.deleteLater()

        if cls.instance is None or uiutils.isValidQtObject(cls.instance) is False:
            name = cls.name
            app, parent = uiutils.getParent()
            cls.instance = cls(parent=parent, name=name)
            # Do not retain the workspaceController after the window
            # has closed, if retain=True this causes errors when
            # windows are closed.
            retain = False
            cls.instance.setDockableParameters(dockable=dock, retain=retain)

        # Make sure the user can see this window.
        if cls.instance.isHidden():
            if show is True:
                cls.instance.show()
        if auto_raise is True:
            # Force the window state to bring the window to the
            # front, and "restore" the state, even if the window
            # is minimised. Confirmed to work on MS Windows 10.
            state = cls.instance.windowState()
            state = QtCore.Qt.WindowNoState
            state |= QtCore.Qt.WindowActive
            cls.instance.setWindowState(state)

            cls.instance.raise_()
            cls.instance.show()
            cls.instance.activateWindow()
        e = time.time()
        LOG.debug('BaseWindow init: %r seconds', e - s)
        return cls.instance
