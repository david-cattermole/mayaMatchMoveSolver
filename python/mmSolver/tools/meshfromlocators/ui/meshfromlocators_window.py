# Copyright (C) 2024 Patcha Saheb Binginapalli
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
Window for the Mesh From Locators tool.

Usage::

   import mmSolver.tools.meshfromlocators.ui.meshfromlocators_window as meshfromlocators_window
   meshfromlocators_window.main()

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import maya.cmds

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.tools.meshfromlocators.ui.meshfromlocators_layout as meshfromlocators_layout
import mmSolver.tools.meshfromlocators.constant as const

LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


class MeshFromLocatorsWindow(BaseWindow):
    name = 'MeshFromLocatorsWindow'

    def __init__(self, parent=None, name=None):
        super(MeshFromLocatorsWindow, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(meshfromlocators_layout.MeshFromLocatorsLayout)

        self.setWindowTitle(const.WINDOW_TITLE)
        self.setWindowFlags(QtCore.Qt.Tool)
        # Hide irrelevant stuff
        self.baseHideStandardButtons()
        self.baseHideProgressBar()


def main(show=True, auto_raise=True, delete=False):
    """
    Open the Mesh From Locators UI.

    :param show: Show the UI.
    :type show: bool

    :param auto_raise: If the UI is open, raise it to the front?
    :type auto_raise: bool

    :param delete: Delete the existing UI and rebuild it? Helpful when
                   developing the UI in Maya script editor.
    :type delete: bool

    :returns: A new ui window, or None if the window cannot be
              opened.
    :rtype: MeshFromLocatorsWindow or None
    """
    win = MeshFromLocatorsWindow.open_window(
        show=show, auto_raise=auto_raise, delete=delete
    )
    return win
