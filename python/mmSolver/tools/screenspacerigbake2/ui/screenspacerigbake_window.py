# Copyright (C) 2022 Patcha Saheb Binginapalli.
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
Window for the screen space rig bake tool.

Usage::

   import mmSolver.tools.screenspacerigbake2.ui.screenspacerigbake2_window as window
   window.main()
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtGui as QtGui
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.helputils as helputils
import mmSolver.ui.commonmenus as commonmenus
import mmSolver.tools.screenspacerigbake2.constant as const
import mmSolver.tools.screenspacerigbake2.ui.screenspacerigbake_layout as screenspacerigbake_layout

LOG = mmSolver.logger.get_logger()


baseModule, BaseWindow = uiutils.getBaseWindow()

def _open_help():
    src = helputils.get_help_source()
    page = 'tools_attributetools.html#attribute-bake'
    helputils.open_help_in_browser(page=page, help_source=src)
    return


class ScreenSpaceRigBakeWindow(BaseWindow):
    name = 'ScreenSpaceRigBakeWindow'

    def __init__(self, parent=None, name=None):
        super(ScreenSpaceRigBakeWindow, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(screenspacerigbake_layout.ScreenSpaceRigBakeLayout)

        self.setWindowTitle(const.WINDOW_TITLE)
        self.setWindowFlags(QtCore.Qt.Tool)

        # Standard Buttons
        form = self.getSubForm()
        self.baseHideStandardButtons()

        # Hide irrelevant stuff
        self.baseHideProgressBar()

def main(show=True, auto_raise=True, delete=False):
    win = ScreenSpaceRigBakeWindow.open_window(show=show,
                                               auto_raise=auto_raise,
                                               delete=delete)
    return win
