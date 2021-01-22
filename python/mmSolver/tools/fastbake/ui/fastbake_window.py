# Copyright (C) 2021 Patcha Saheb Binginapalli.
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
Window for the Fast bake tool.

Usage::

   import mmSolver.tools.fastbake.ui.fastbake_window as fastbake_window
   fastbake_window.main()

"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.helputils as helputils
import mmSolver.tools.fastbake.constant as const
import mmSolver.tools.fastbake.ui.fastbake_layout as fastbake_layout
import mmSolver.tools.fastbake.tool as tool

LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


class FastBakeWindow(BaseWindow):
    name = 'FastBakeWindow'

    def __init__(self, parent=None, name=None):
        super(FastBakeWindow, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(fastbake_layout.FastBakeLayout)

        self.setWindowTitle(const.WINDOW_TITLE)
        self.setWindowFlags(QtCore.Qt.Tool)

        # Standard Buttons
        self.baseHideStandardButtons()
        self.applyBtn.show()
        self.resetBtn.show()
        self.helpBtn.show()
        self.closeBtn.show()
        self.applyBtn.setText('Bake')

        self.applyBtn.clicked.connect(tool.main)
        self.resetBtn.clicked.connect(self.reset_options)
        self.helpBtn.clicked.connect(self.help)

        # Hide irrelevant stuff
        self.baseHideMenuBar()
        self.baseHideProgressBar()

    def reset_options(self):
        form = self.getSubForm()
        form.reset_options()
        return

    def help(self):
        src = helputils.get_help_source()
        page = 'tools_generaltools.html#smooth-keyframes'
        helputils.open_help_in_browser(page=page, help_source=src)
        return
        

def main(show=True, auto_raise=True, delete=False):
    win = FastBakeWindow.open_window(
        show=show,
        auto_raise=auto_raise,
        delete=delete
    )
    return win
