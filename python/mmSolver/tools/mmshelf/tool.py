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
Build the mmSolver Maya shelf.
"""

import mmSolver.logger
import mmSolver.utils.config as config_utils
import mmSolver.ui.shelfutils as shelf_utils
import mmSolver.tools.mmshelf.constant as const
import mmSolver.tools.mmshelf.lib as lib


LOG = mmSolver.logger.get_logger()


def build_shelf():
    """
    Build the 'mmSolver' shelf.
    """
    LOG.info('Building mmSolver Shelf...')

    func_config_name = const.CONFIG_FILE_FUNCTIONS_NAME
    func_config = config_utils.get_config(func_config_name)
    if func_config is None:
        LOG.warning('Could not find %s config file', func_config_name)

    shelf_config_name = const.CONFIG_FILE_SHELF_NAME
    shelf_config = config_utils.get_config(shelf_config_name)
    if shelf_config is None:
        LOG.warning('Could not find %s config file', shelf_config_name)

    main_funcs = func_config.get_value('data', default_value={})
    shelf_funcs = shelf_config.get_value('data/functions', default_value={})
    funcs = [shelf_funcs, main_funcs]

    # Create main shelf.
    shelf_parent = shelf_utils.get_shelves_parent()
    shelf_name = str(const.SHELF_NAME)
    shelf = shelf_utils.create_shelf(
        parent=shelf_parent,
        name=shelf_name,
    )
    if shelf is None:
        msg = 'Cannot create shelf. Exiting without creating shelf buttons.'
        LOG.error(msg)
        return

    # Create the shelf buttons items
    items = shelf_config.get_value('data/items', default_value=[])
    items_to_create = lib.compile_items(items, funcs)
    lib.create_items(items_to_create, shelf)
    return shelf
