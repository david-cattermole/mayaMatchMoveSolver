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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.logger
import mmSolver.ui.shelfutils as shelf_utils
import mmSolver.tools.mmshelf.constant as const
import mmSolver.tools.mmshelf.lib as lib


LOG = mmSolver.logger.get_logger()


def build_shelf():
    """
    Build the 'mmSolver' shelf.
    """
    LOG.info('Building mmSolver Shelf...')

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

    func_config_name = const.CONFIG_FILE_FUNCTIONS_NAME
    shelf_config_name = const.CONFIG_FILE_SHELF_DEFAULT_NAME
    result = lib.build(shelf, func_config_name, shelf_config_name)
    lib.activate_shelf_tab(shelf_name)
    return result


def build_minimal_shelf_items(shelf):
    """
    Build a smaller number of shelf items.

    This function is designed to be used for integration with an
    already created shelf-building system. Simply call this function
    with the parent shelf and the items will be created.
    """
    LOG.info('Building mmSolver Minimal Shelf Items...')

    if shelf is None:
        msg = 'Cannot create shelf. Exiting without creating shelf buttons.'
        LOG.error(msg)
        return

    func_config_name = const.CONFIG_FILE_FUNCTIONS_NAME
    shelf_config_name = const.CONFIG_FILE_SHELF_MINIMAL_NAME
    return lib.build(shelf, func_config_name, shelf_config_name)
