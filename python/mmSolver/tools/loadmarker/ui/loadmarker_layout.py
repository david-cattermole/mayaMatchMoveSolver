"""

Usage::

   import mmSolver.tools.solver.ui.solver_window as solver_window;
   reload(solver_window)
   solver_window.main()

"""

import sys
import time
from functools import partial

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets


import mmSolver.logger
import mmSolver.tools.loadmarker.ui.ui_loadmarker_layout as ui_loadmarker_layout


LOG = mmSolver.logger.get_logger(level='DEBUG')


class LoadMarkerLayout(QtWidgets.QWidget, ui_loadmarker_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(LoadMarkerLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Collection Add and Remove buttons
        self.filepath_pushButton.clicked.connect(self.filePathBrowseClicked)

    def filePathBrowseClicked(self):
        LOG.debug('filePathBrowseClicked')
        return

    def getFilePath(self):
        LOG.debug('getFilePath')
        # return self.startFrameSpinBox.value()
        return '/my/path/to/file.uv'
