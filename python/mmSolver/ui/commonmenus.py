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
Creation and editing of common menus such as "Edit" and "Help"
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger


LOG = mmSolver.logger.get_logger()


def _launch_default_help_page():
    import mmSolver.ui.helputils as helputils

    src = helputils.get_help_source()
    helputils.open_help_in_browser(help_source=src)
    return


def _launch_about_window():
    import mmSolver.tools.aboutwindow.tool as aboutwin_tool

    aboutwin_tool.open_window()
    return


def _launch_sysinfo_window():
    import mmSolver.tools.sysinfowindow.tool as sysinfowin_tool

    sysinfowin_tool.open_window()
    return


def create_edit_menu_items(menu, reset_settings_func=None):
    with_reset_settings = callable(reset_settings_func) is True

    label = 'Reset Settings'
    tooltip = "Reset the current tools's Settings."
    action = QtWidgets.QAction(label, menu)
    action.setStatusTip(tooltip)
    action.setEnabled(with_reset_settings)
    if with_reset_settings is True:
        action.triggered.connect(reset_settings_func)
    menu.addAction(action)
    return


def create_help_menu_items(menu, tool_help_func=None):
    label = 'Tool Help...'
    if callable(tool_help_func) is False:
        label = 'Help...'
        tool_help_func = _launch_default_help_page
    tooltip = 'Show help for this tool.'
    action = QtWidgets.QAction(label, menu)
    action.setStatusTip(tooltip)
    action.triggered.connect(tool_help_func)
    menu.addAction(action)

    label = 'System Information...'
    tooltip = 'Display detailed information about software and hardware.'
    action = QtWidgets.QAction(label, menu)
    action.setStatusTip(tooltip)
    action.triggered.connect(_launch_sysinfo_window)
    menu.addAction(action)

    label = 'About mmSolver...'
    tooltip = 'About the Maya MatchMove Solver project.'
    action = QtWidgets.QAction(label, menu)
    action.setStatusTip(tooltip)
    action.triggered.connect(_launch_about_window)
    menu.addAction(action)
    return
