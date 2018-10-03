"""
The base window for usage inside Maya.

All windows inside Maya should sub-class from BaseMayaWindow.

Run the default MayaBaseWindow::

    import mmSolver.ui.base_maya_window
    reload(mmSolver.ui.base_maya_window)
    mmSolver.ui.base_maya_window.create()

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


from maya import OpenMayaUI as omui
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

import Qt
import Qt.QtCore as QtCore
import Qt.QtWidgets as QtWidgets

try:
    from shiboken2 import wrapInstance
except ImportError:
    from shiboken import wrapInstance

import mmSolver.ui.ui_base as ui_base


WINDOW = None


def getMayaMainWindow():
    mainWindowPtr = omui.MQtUtil.mainWindow()
    mainWindow = wrapInstance(long(mainWindowPtr), QtWidgets.QWidget)
    return mainWindow


def findWidget(name, clsTyp):
    ptr = omui.MQtUtil.findControl(name)
    widget = None
    if ptr:
        widget = wrapInstance(long(ptr), clsTyp)
    return widget


class BaseMayaWindow(MayaQWidgetBaseMixin,
                     QtWidgets.QMainWindow,
                     ui_base.Ui_Window):
    def __init__(self, parent, name=None):
        super(BaseMayaWindow, self).__init__()

        # Destroy this widget when closed. Otherwise it will stay around.
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

        # Call the UI file contents.
        self.setupUi(self)
        if name is not None:
            self.setObjectName(name)

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





def delete():
    # TODO: Is this deprecated???
    global WINDOW
    if WINDOW is None:
        return

    name = 'BaseMayaWindow'
    WINDOW = findWidget(name, QtWidgets.QWidget)
    if WINDOW:
        # window.close()  # or .deleteLater() ?
        WINDOW.deleteLater()

    WINDOW = None
    return


def create(show=True):
    # TODO: Is this deprecated???
    global WINDOW
    delete()

    name = 'BaseMayaWindow'
    WINDOW = BaseMayaWindow(name=name)
    if show:
        WINDOW.show()

    return WINDOW
