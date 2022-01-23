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
Build the mmSolver menu.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.logger
import mmSolver.utils.config as config_utils
import mmSolver.ui.menuutils as menu_utils
import mmSolver.tools.mmmenu.constant as const
import mmSolver.tools.mmmenu.lib as lib

LOG = mmSolver.logger.get_logger()


def build_menu():
    """
    Build the 'mmSolver' menu.
    """
    LOG.info('Building mmSolver Menu...')

    func_config_name = const.CONFIG_FILE_FUNCTIONS_NAME
    func_config = config_utils.get_config(func_config_name)
    if func_config is None:
        LOG.warning('Could not find %s config file', func_config_name)

    menu_config_name = const.CONFIG_FILE_MENU_NAME
    menu_config = config_utils.get_config(menu_config_name)
    if menu_config is None:
        LOG.warning('Could not find %s config file', menu_config_name)

    main_funcs = func_config.get_value('data', default_value={})
    menu_funcs = menu_config.get_value('data/functions', default_value={})
    funcs = [menu_funcs, main_funcs]

    # Create main menu.
    main_parent = menu_utils.get_maya_window_parent()
    mm_menu = menu_utils.create_menu(
        parent=main_parent,
        name=const.MENU_NAME,
        tearOff=const.MENU_TEAR_OFF)

    # Create the menu items
    items = menu_config.get_value('data/items', default_value=[])
    items_to_create = lib.compile_items(items, funcs)
    lib.create_items(items_to_create, mm_menu)
    return mm_menu
