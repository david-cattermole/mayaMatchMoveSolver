"""
User interface utilities for Qt and Qt based applications.
"""

import sys

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt
import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets


def getHostApplication():
    """
    Get the name of the application we are currently running inside of.

    Supported hosts to check for are::

        - 'standalone' (outside any host application)

        - 'maya' (Autodesk Maya)

        - 'nuke' (The Foundry Nuke)

        - 'houdini' (SideFX Houdini)

    :return: The application name, or None if the application could not
             be recognised.
    :rtype: str or None
    """
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
    """
    Get the Maya application QWidget window.

    .. note::

        For Maya only.

    :return: The Maya main window, as a Qt Widget object.
    :rtype: QWidget
    """
    import maya.OpenMayaUI as omui
    window_ptr = omui.MQtUtil.mainWindow()
    window = Qt.QtCompat.wrapInstance(long(window_ptr), QtWidgets.QMainWindow)
    return window


def findControlMayaWidget(name, clsTyp):
    import maya.OpenMayaUI as omui
    ptr = omui.MQtUtil.findControl(name)
    widget = None
    if ptr:
        widget = Qt.QtCompat.wrapInstance(long(ptr), clsTyp)
    return widget


def isValidQtObject(obj):
    """
    Does the Python object given contain a valid Qt reference pointer?

    Only supports host 'maya'.

    :param obj: Qt class object.

    :returns: Is the given object valid in C++?
    :rtype: bool
    """
    v = None
    host = getHostApplication()
    if host == 'standalone':
        raise NotImplementedError
    elif host == 'maya':
        try:
            from shiboken2 import isValid
        except ImportError:
            from shiboken import isValid
        v = isValid(obj)
    else:
        raise NotImplementedError
    assert isinstance(v, bool) is True
    return v


def getParent():
    """
    Get the parent Qt QApplication object.

    Only supports hosts 'standalone' and 'maya'.

    :return: Qt object for the top level parent object.
    """
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
        msg = 'Host application is not valid: host=%r'
        raise ValueError(msg % host)
    return app, parent


def getBaseWindow():
    """
    Get pre-defined preset "Base Window" for the currently running host.

    This function allows dynamic look-up of the intended window for all
    custom UIs to be built around.

    Only supports hosts 'standalone' and 'maya'.

    :return: The module and class to be used.
    :rtype: (module, class)
    """
    BaseWindow = None
    baseModule = None
    host = getHostApplication()
    if host == 'standalone':
        import mmSolver.ui.base_standalone_window as baseModule
        BaseWindow = baseModule.BaseStandaloneWindow
    elif host == 'maya':
        import mmSolver.ui.base_maya_window as baseModule
        BaseWindow = baseModule.BaseMayaWindow
    else:
        print('Warning: Unknown application host, %r' % host)
    return baseModule, BaseWindow


def getFont(name=None):
    """
    Create a Qt font, using a name containing hints/keywords.

    :param name: Font name to create. Can contain multiple sub-strings.
                 Supported sub-strings are 'normal', 'small',
                 'mediumlarge', 'large', 'monospace', 'bold', 'italic'.
    :type name: str

    :return: Qt QFont object, with names used to set the font.
    :rtype: QFont
    """
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
    """
    Creates an Qt Icon from a resource path.

    :param path: Resource file path.
    :type path: str

    :return: Qt Icon object.
    :rtype: QIcon
    """
    assert isinstance(path, str)
    icon = QtGui.QIcon(QtGui.QPixmap(path))
    return icon


def setWindowWidthHeight(ui, width_height):
    """
    Set a window's width and height.

    :param ui: Qt Window UI to set.
    :type ui: QWidget

    :param width_height: Width and height to set.
    :type width_height: (int, int)
    """
    pos = ui.pos()
    ui.setGeometry(pos.x(), pos.y(), width_height[0], width_height[1])
    return


class QtInfoMixin(object):
    """
    Mix-in class to provide simple functions for checking Qt versions.
    """

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

