"""
The base window for usage in (standalone) Python.

Run the default BaseStandaloneWindow:
>>> import mmSolver.ui.base_standalone_window
>>> mmSolver.ui.base_standalone_window.main()
"""

import sys

import Qt
import Qt.QtCore as QtCore
import Qt.QtWidgets as QtWidgets

import qtLearn.windows.ui_base as ui_base


class BaseStandaloneWindow(QtWidgets.QMainWindow,
                           ui_base.Ui_Window):
    def __init__(self, parent, name=None):
        super(BaseStandaloneWindow, self).__init__()

        # Destroy this widget when closed. Otherwise it will stay around.
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

        # Call the UI file contents.
        self.setupUi(self)
        if name:
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

    def baseHideToolBar(self):
        self.toolBar.hide()
        return

    def baseHideProgressBar(self):
        self.progressBar.hide()
        return

    def baseHideStatusBar(self):
        self.statusBar.hide()
        return

    def addSubForm(self, SubForm):
        if SubForm is None:
            return None
        self.subForm = SubForm(self)
        self.optionsLayout.addWidget(self.subForm)
        return True


def main():
    name = 'StandaloneBaseWindow'
    app = QtWidgets.QApplication(sys.argv)
    ui = BaseStandaloneWindow(None, name=name)
    ui.show()
    return sys.exit(app.exec_())


if __name__ == '__main__':
    main()
