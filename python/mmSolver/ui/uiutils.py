"""
User interface utilities for Qt and Qt based applications.
"""

import sys

import Qt
import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets


def getHostApplication():
    result = None
    appName = QtWidgets.QApplication.applicationName()
    if appName is None or len(appName) == 0:
        result = 'standalone'
    elif 'maya' in str(appName).lower():
        result = 'maya'
    elif 'nuke' in str(appName).lower():
        result = 'nuke'
    elif 'houdini' in str(appName).lower():
        result = 'houdini'
    else:
        print('Warning: Unknown application name, %r' % appName)
        result = appName
    return result


def getMayaMainWindow():
    try:
        from shiboken2 import wrapInstance
    except ImportError:
        from shiboken import wrapInstance
    from maya import OpenMayaUI as omui
    windowPtr = omui.MQtUtil.mainWindow()
    window = wrapInstance(long(windowPtr), QtWidgets.QWidget)
    return window


def getParent():
    host = getHostApplication()

    # try running outside of maya
    app = None
    parent = None
    if host == 'standalone':
        app = QtWidgets.QApplication(sys.argv)
        parent = None
    elif host == 'maya':
        parent = getMayaMainWindow()
    else:
        assert False
    return app, parent


def getBaseWindow():
    BaseWindow = None
    baseModule = None
    host = getHostApplication()
    if host == 'standalone':
        import mmSolver.ui.base_standalone_window as baseModule
        # reload(baseModule)
        BaseWindow = baseModule.BaseStandaloneWindow
    elif host == 'maya':
        import mmSolver.ui.base_maya_window as baseModule
        # reload(baseModule)
        BaseWindow = baseModule.BaseMayaWindow
    else:
        print('Warning: Unknown application host, %r' % host)
    return baseModule, BaseWindow


def getFont(name=None):
    font = QtGui.QFont()
    name = name.lower()
    if 'normal' in name:
        font.setPointSize(8)
        font.setBold(False)
        font.setItalic(False)
    elif 'small' in name:
        font.setPointSize(6)
    elif 'mediumlarge' in name:
        font.setPointSize(10)
    elif 'large' in name:
        font.setPointSize(12)

    if 'monospace' in name:
        if 'monospace' in QtGui.QFont.__dict__:
            font.setStyleHint(QtGui.QFont.Monospace)

    if 'bold' in name:
        font.setBold(True)

    if 'italic' in name:
        font.setItalic(True)
    return font


def getIcon(path):
    assert isinstance(path, str)
    icon = QtGui.QIcon(QtGui.QPixmap(path))
    return icon


def setWindowWidthHeight(ui, widthHeight):
    pos = ui.pos()
    ui.setGeometry(pos.x(), pos.y(), widthHeight[0], widthHeight[1])
    return None


class QtInfoMixin(object):
    def __init__(self):
        super(QtInfoMixin, self).__init__()
        self.qtInitVersion()

    def qtInitVersion(self):
        # Save the Qt version number
        qt_ver = Qt.__qt_version__.split('.')
        self.qt_ver = qt_ver

        assert len(qt_ver) == 3
        self.qt_ver_major = int(self.qt_ver[0])
        self.qt_ver_minor = int(self.qt_ver[1])
        self.qt_ver_patch = int(self.qt_ver[2])
        return qt_ver

    def qtAboveVersion(self, major, minor, patch):
        self.qtInitVersion()
        return (self.qt_ver_major >= major and
                self.qt_ver_minor >= minor and
                self.qt_ver_patch >= patch)

    def qtEqualOrAbove_4_6_X(self):
        self.qtInitVersion()
        return self.qt_ver_major == 4 and self.qt_ver_minor >= 6

    def qtEqualOrAbove_4_7_X(self):
        self.qtInitVersion()
        return self.qt_ver_major == 4 and self.qt_ver_minor >= 7

    def qtEqualOrAbove_4_8_X(self):
        self.qtInitVersion()
        return self.qt_ver_major == 4 and self.qt_ver_minor >= 8

    def qtEqual_4_X_X(self):
        self.qtInitVersion()
        return self.qt_ver_major == 4

    def qtEqual_5_X_X(self):
        self.qtInitVersion()
        return self.qt_ver_major == 5

