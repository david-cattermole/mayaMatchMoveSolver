# Copyright (C) 2026 David Cattermole.
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
Camera Solver window.

Usage::

   import mmSolver.tools.camerasolver.ui.camerasolver_window as camerasolver_window
   camerasolver_window.main()

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.utils.python_compat as pycompat
import mmSolver.tools.camerasolver.constant as const
import mmSolver.tools.camerasolver.ui.camerasolver_layout as camerasolver_layout


LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


class CameraSolverWindow(BaseWindow):
    name = 'CameraSolverWindow'

    def __init__(self, parent=None, name=None):
        # type: (...) -> None
        super(CameraSolverWindow, self).__init__(parent=parent, name=name)
        self.setupUi(self)
        self.setWindowTitle(const.WINDOW_TITLE_BAR)
        self.baseHideStandardButtons()
        self.baseHideProgressBar()
        self.baseHideMenuBar()
        self.addSubForm(camerasolver_layout.CameraSolverLayout)

    def setStatusLine(self, text):
        # type: (pycompat.TEXT_TYPE) -> None
        assert isinstance(text, pycompat.TEXT_TYPE)
        subform = self.getSubForm()
        if subform is not None and uiutils.isValidQtObject(subform):
            subform.setStatusLine(text)


def main(show=True, auto_raise=True, delete=False, dock=False):
    """
    Open the Camera Solver UI window.

    :param show: Show the UI.
    :type show: bool

    :param auto_raise: If the UI is open, raise it to the front?
    :type auto_raise: bool

    :param delete: Delete the existing UI and rebuild it? Helpful when
                   developing the UI in Maya script editor.
    :type delete: bool

    :param dock: Dock the window in the Maya UI?
    :type dock: bool

    :returns: A new camera solver window, or None if the window cannot be
              opened.
    :rtype: CameraSolverWindow or None.
    """
    # type: (...) -> CameraSolverWindow | None
    return CameraSolverWindow.open_window(
        show=show, auto_raise=auto_raise, delete=delete, dock=dock
    )
