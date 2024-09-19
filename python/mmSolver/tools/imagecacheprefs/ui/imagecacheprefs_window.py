# Copyright (C) 2024 David Cattermole
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
Window for the Image Cache tool.

Usage::

   import mmSolver.tools.imagecacheprefs.ui.imagecacheprefs_window as window
   window.main()

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.helputils as helputils
import mmSolver.ui.commonmenus as commonmenus
import mmSolver.tools.imagecache.lib as lib
import mmSolver.tools.imagecacheprefs.constant as const
import mmSolver.tools.imagecacheprefs.ui.imagecacheprefs_layout as imagecacheprefs_layout


LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


def _open_help():
    src = helputils.get_help_source()
    page = 'tools_generaltools.html#image-cache'
    helputils.open_help_in_browser(page=page, help_source=src)
    return


class ImageCachePrefsWindow(BaseWindow):
    name = 'ImageCachePrefsWindow'

    def __init__(self, parent=None, name=None):
        super(ImageCachePrefsWindow, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(imagecacheprefs_layout.ImageCachePrefsLayout)

        self.setWindowTitle(const.WINDOW_TITLE)
        self.setWindowFlags(QtCore.Qt.Tool)

        # Standard Buttons
        self.baseHideStandardButtons()
        self.applyBtn.show()
        self.closeBtn.show()
        self.applyBtn.setText('Apply Capacity')

        self.applyBtn.clicked.connect(self._apply)

        # Hide irrelevant stuff
        self.baseHideProgressBar()

        self.add_menus(self.menubar)
        self.menubar.show()

    def add_menus(self, menubar):
        edit_menu = QtWidgets.QMenu('Edit', menubar)
        commonmenus.create_edit_menu_items(
            edit_menu, reset_settings_func=self.reset_options
        )
        menubar.addMenu(edit_menu)

        help_menu = QtWidgets.QMenu('Help', menubar)
        commonmenus.create_help_menu_items(help_menu, tool_help_func=_open_help)
        menubar.addMenu(help_menu)

    def _apply(self):
        form = self.getSubForm()
        gpu_capacity_bytes = form.get_gpu_capacity_bytes()
        cpu_capacity_bytes = form.get_cpu_capacity_bytes()

        lib.set_gpu_cache_capacity_bytes(gpu_capacity_bytes)
        lib.set_cpu_cache_capacity_bytes(cpu_capacity_bytes)

        form.update_resource_values()
        form.save_options()
        return

    def reset_options(self):
        form = self.getSubForm()
        form.reset_options()
        return


def main(show=True, auto_raise=True, delete=False):
    """
    Open the Image Cache UI window.

    :param show: Show the UI.
    :type show: bool

    :param auto_raise: If the UI is open, raise it to the front?
    :type auto_raise: bool

    :param delete: Delete the existing UI and rebuild it? Helpful when
                   developing the UI in Maya script editor.
    :type delete: bool

    :returns: A new image cache window, or None if the window cannot be
              opened.
    :rtype: ImageCachePrefsWindow or None.
    """
    win = ImageCachePrefsWindow.open_window(
        show=show, auto_raise=auto_raise, delete=delete
    )
    return win
