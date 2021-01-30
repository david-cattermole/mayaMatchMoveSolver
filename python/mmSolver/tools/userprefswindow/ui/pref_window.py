# Copyright (C) 2020 David Cattermole.
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
The window for the 'About' window tool.
"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.helputils as helputils
import mmSolver.ui.commonmenus as commonmenus
import mmSolver.utils.config as config_utils
import mmSolver.tools.userpreferences.lib as userprefs_lib
import mmSolver.tools.userpreferences.constant as pref_const
import mmSolver.tools.userprefswindow.constant as const
import mmSolver.tools.userprefswindow.ui.pref_layout as pref_layout

LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


def _open_help():
    src = helputils.get_help_source()
    page = 'tools_generaltools.html#user-preferences-tool-ref'
    helputils.open_help_in_browser(page=page, help_source=src)
    return


class PrefWindow(BaseWindow):

    name = 'UserPreferencesWindow'

    def __init__(self, parent=None, name=None):
        super(PrefWindow, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(pref_layout.PrefLayout)
        self.setWindowTitle(const.WINDOW_TITLE_BAR)
        self.setWindowFlags(QtCore.Qt.Tool)

        # Hide default stuff
        self.baseHideStandardButtons()
        self.baseHideProgressBar()

        self._config = userprefs_lib.get_config()
        self.subForm.set_config(self._config)
        self.subForm.buttonBox.accepted.connect(self.save_prefs_and_close)
        self.subForm.buttonBox.rejected.connect(self.close)

        self.add_menus(self.menubar)
        self.menubar.show()

    def add_menus(self, menubar):
        edit_menu = QtWidgets.QMenu('Edit', menubar)
        commonmenus.create_edit_menu_items(
            edit_menu,
            save_settings_func=self.save_prefs,
            reset_settings_func=self.reset_prefs)
        menubar.addMenu(edit_menu)

        help_menu = QtWidgets.QMenu('Help', menubar)
        commonmenus.create_help_menu_items(
            help_menu,
            tool_help_func=_open_help)
        menubar.addMenu(help_menu)

    def reset_prefs(self):
        config = self._config
        option_keys = [
            pref_const.REG_EVNT_ADD_NEW_MKR_TO_KEY,
            pref_const.SOLVER_UI_VALIDATE_ON_OPEN_KEY,
            pref_const.SOLVER_UI_SHOW_VALIDATE_BTN_KEY,
            pref_const.SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_KEY,
        ]
        for key in option_keys:
            value = pref_const.DEFAULT_VALUE_MAP[key]
            userprefs_lib.set_value(config, key, value)

        form = self.getSubForm()
        form.populateUI(config)
        return

    def save_prefs(self):
        config = self._config
        options = [
            (pref_const.REG_EVNT_ADD_NEW_MKR_TO_KEY,
             self.subForm.getAddNewMarkersToConfigValue),
            (pref_const.SOLVER_UI_VALIDATE_ON_OPEN_KEY,
             self.subForm.getSolverUIValidateOnOpenConfigValue),
            (pref_const.SOLVER_UI_SHOW_VALIDATE_BTN_KEY,
             self.subForm.getSolverUIShowValidateButtonConfigValue),
            (pref_const.SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_KEY,
             self.subForm.getSolverUIMinimalUIWhileSolvingConfigValue),
        ]
        for key, func in options:
            value = func()
            userprefs_lib.set_value(config, key, value)

        config.write()
        return

    def save_prefs_and_close(self):
        self.save_prefs()
        self.close()
        return


def main(show=True, auto_raise=True, delete=False):
    """
    Open the Pref window.

    :param show: Show the UI.
    :type show: bool

    :param auto_raise: If the UI is open, raise it to the front?
    :type auto_raise: bool

    :param delete: Delete the existing UI and rebuild it? Helpful when
                   developing the UI in Maya script editor.
    :type delete: bool

    :returns: A new pref window, or None if the window cannot be
              opened.
    :rtype: PrefWindow or None.
    """
    win = PrefWindow.open_window(
        show=show,
        auto_raise=auto_raise,
        delete=delete
    )
    return win
