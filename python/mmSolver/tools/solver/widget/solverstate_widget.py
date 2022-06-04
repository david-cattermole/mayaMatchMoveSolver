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
Displays the current state of the solver UI, with status and previous
solve information.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtGui as QtGui
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.tools.solver.lib.collection as lib_collection
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.widget.ui_solverstate_widget as ui_solverstate_widget


LOG = mmSolver.logger.get_logger()


class SolverStateWidget(QtWidgets.QWidget, ui_solverstate_widget.Ui_Form):

    statusUpdated = QtCore.Signal()
    infoUpdated = QtCore.Signal()

    def __init__(self, parent=None, *args, **kwargs):
        s = time.time()
        super(SolverStateWidget, self).__init__(*args, **kwargs)
        self.setupUi(self)
        e = time.time()
        LOG.debug('SolverStateWidget init: %r seconds', e - s)
        return

    def updateModel(self):
        return

    def updateStatusWithSolveResult(self):
        col = lib_state.get_active_collection()
        if col is None:
            return
        info_fn = self.setSolveInfoLine
        solres_list = col.get_last_solve_results()
        timestamp = col.get_last_solve_timestamp()
        total_time = col.get_last_solve_duration()

        msg = 'No solve performed.'
        if len(solres_list) == 0:
            info_fn(msg)
        if timestamp is None:
            timestamp = time.time()
        if total_time is None:
            total_time = 0.0

        # We don't want to log every time we open the UI.
        log = None
        lib_collection.log_solve_results(
            log,
            solres_list,
            timestamp=timestamp,
            total_time=total_time,
            status_fn=info_fn,
        )
        return

    @QtCore.Slot(str)
    def setStatusLine(self, text):
        valid = uiutils.isValidQtObject(self)
        if valid is False:
            return
        valid = uiutils.isValidQtObject(self.statusLine_label)
        if valid is False:
            return
        self.statusLine_label.setText(text)
        self.statusUpdated.emit()
        return

    @QtCore.Slot(str)
    def setSolveInfoLine(self, text):
        valid = uiutils.isValidQtObject(self)
        if valid is False:
            return
        valid = uiutils.isValidQtObject(self.solveInfoLine_lineEdit)
        if valid is False:
            return
        self.solveInfoLine_lineEdit.setText(text)
        self.infoUpdated.emit()
        return
