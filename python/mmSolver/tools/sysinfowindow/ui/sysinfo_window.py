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
The window for the 'Sysinfo' window tool.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.tools.sysinfowindow.constant as const
import mmSolver.tools.sysinfowindow.ui.sysinfo_layout as sysinfo_layout

LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


class SysInfoWindow(BaseWindow):

    name = 'SysInfoWindow'

    def __init__(self, parent=None, name=None):
        super(SysInfoWindow, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(sysinfo_layout.SysInfoLayout)
        self.setWindowTitle(const.WINDOW_TITLE_BAR)
        self.setWindowType(qtpyutils.WINDOW_TYPE_DIALOG)

        # Hide default stuff
        self.baseHideMenuBar()
        self.baseHideStandardButtons()
        self.baseHideProgressBar()

        self.subForm.okButton.clicked.connect(self.close)
        return


def main(show=True, auto_raise=True, delete=False):
    """
    Open the System Info window.

    :param show: Show the UI.
    :type show: bool

    :param auto_raise: If the UI is open, raise it to the front?
    :type auto_raise: bool

    :param delete: Delete the existing UI and rebuild it? Helpful when
                   developing the UI in Maya script editor.
    :type delete: bool

    :returns: A new sys-info window, or None if the window cannot be
              opened.
    :rtype: SysinfoWindow or None.
    """
    win = SysInfoWindow.open_window(show=show, auto_raise=auto_raise, delete=delete)
    return win
