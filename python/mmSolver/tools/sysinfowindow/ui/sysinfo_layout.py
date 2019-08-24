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
The 'Sysinfo' layout, the contents of the sysinfo window.
"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.tools.sysinfowindow.lib.message as lib_msg
import mmSolver.tools.sysinfowindow.ui.ui_sysinfo_layout as ui_sysinfo_layout


LOG = mmSolver.logger.get_logger()


class SysInfoLayout(QtWidgets.QWidget, ui_sysinfo_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(SysInfoLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)
        text = lib_msg.get_sysinfo_text()
        self.sysInfoTextEdit.setText(text)
        return
