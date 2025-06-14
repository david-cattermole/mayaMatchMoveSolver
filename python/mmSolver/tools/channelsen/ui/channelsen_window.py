# Copyright (C) 2019 Anil Reddy.
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
Window for the Channel Sensitivity tool.

Usage::

   import mmSolver.tools.channelsen.ui.channelsen_window as tool
   tool.main()

"""

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.helputils as helputils
import mmSolver.tools.channelsen.ui.channelsen_layout as channelsen_layout


LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


class ChannelSenWindow(BaseWindow):

    name = 'ChannelSenWindow'

    def __init__(self, parent=None, name=None):
        super(ChannelSenWindow, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(channelsen_layout.ChannelSenLayout)

        self.setWindowTitle('Channel Box Sensitivity')
        self.setWindowType(qtpyutils.WINDOW_TYPE_DIALOG)

        # Standard Buttons
        self.baseHideStandardButtons()
        self.helpBtn.show()
        self.closeBtn.show()

        self.helpBtn.clicked.connect(self.help)

        # Hide irrelevant stuff
        self.baseHideMenuBar()
        self.baseHideProgressBar()

    def help(self):
        src = helputils.get_help_source()
        page = 'tools_attributetools.html#channel-sensitivity'
        helputils.open_help_in_browser(page=page, help_source=src)
        return


def main(show=True, auto_raise=True, delete=False):
    """
    Open the Channel Sensitivity UI window.

    :param show: Show the UI.
    :type show: bool

    :param auto_raise: If the UI is open, raise it to the front?
    :type auto_raise: bool

    :param delete: Delete the existing UI and rebuild it? Helpful when
                   developing the UI in Maya script editor.
    :type delete: bool

    :returns: A new channel sensitivity window, or None if the window
              cannot be opened.
    :rtype: ChannelSenWindow or None.
    """
    win = ChannelSenWindow.open_window(show=show, auto_raise=auto_raise, delete=delete)
    return win
