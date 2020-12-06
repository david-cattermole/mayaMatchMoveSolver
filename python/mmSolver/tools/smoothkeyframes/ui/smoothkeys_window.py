# Copyright (C) 2019 David Cattermole
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
Window for the Smooth Keyframes tool.

Usage::

   import mmSolver.tools.smoothkeys.ui.smoothkeys_window as smoothkeys_window
   smoothkeys_window.main()

"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.helputils as helputils
import mmSolver.tools.smoothkeyframes.constant as const
import mmSolver.tools.smoothkeyframes.tool as tool
import mmSolver.tools.smoothkeyframes.ui.smoothkeys_layout as smoothkeys_layout


LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


class SmoothKeysWindow(BaseWindow):
    name = 'SmoothKeysWindow'

    def __init__(self, parent=None, name=None):
        super(SmoothKeysWindow, self).__init__(parent,
                                               name=name)
        self.setupUi(self)
        self.addSubForm(smoothkeys_layout.SmoothKeysLayout)

        self.setWindowTitle(const.WINDOW_TITLE)
        self.setWindowFlags(QtCore.Qt.Tool)

        # Standard Buttons
        self.baseHideStandardButtons()
        self.applyBtn.show()
        self.resetBtn.show()
        self.helpBtn.show()
        self.closeBtn.show()
        self.applyBtn.setText('Smooth')

        self.applyBtn.clicked.connect(tool.smooth_selected_keyframes)
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
        page = 'tools.html#smooth-keyframes'
        helputils.open_help_in_browser(page=page, help_source=src)
        return


def main(show=True, auto_raise=True, delete=False):
    """
    Open the Smooth Keyframes UI window.

    :param show: Show the UI.
    :type show: bool

    :param auto_raise: If the UI is open, raise it to the front?
    :type auto_raise: bool

    :param delete: Delete the existing UI and rebuild it? Helpful when
                   developing the UI in Maya script editor.
    :type delete: bool

    :returns: A new solver window, or None if the window cannot be
              opened.
    :rtype: SolverWindow or None.
    """
    win = SmoothKeysWindow.open_window(
        show=show,
        auto_raise=auto_raise,
        delete=delete
    )
    return win
