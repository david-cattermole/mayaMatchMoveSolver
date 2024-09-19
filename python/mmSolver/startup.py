#
# Copyright (C) 2018, 2019 David Cattermole.
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
A start-up script for mmSolver.

The functions defined in this module should be used to load the various
components of mmSolver.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import maya.cmds
import maya.utils
import mmSolver.logger


LOG = mmSolver.logger.get_logger()
MMSOLVER_STARTED = False


def mmsolver_create_shelf():
    """
    Build the mmSolver shelf.
    """
    import mmSolver.tools.mmshelf.tool

    mmSolver.tools.mmshelf.tool.build_shelf()


def mmsolver_create_menu():
    """
    Build the mmSolver menu.
    """
    import mmSolver.tools.mmmenu.tool

    mmSolver.tools.mmmenu.tool.build_menu()


def mmsolver_create_hotkey_set():
    """
    Create the mmSolver Hotkey Set.
    """
    import mmSolver.tools.mmhotkeyset.tool

    mmSolver.tools.mmhotkeyset.tool.build_hotkey_set()


def mmsolver_register_events():
    """
    Initialise the built-in (non-maya) events for mmSolver.
    """
    import mmSolver.tools.registerevents.tool

    mmSolver.tools.registerevents.tool.register_events()


def mmsolver_image_cache_initalize():
    """
    Initialise the mmSolver ImageCache.
    """
    import mmSolver.tools.imagecache.initialize

    mmSolver.tools.imagecache.initialize.main()


def mmsolver_startup():
    """
    Responsible for starting up mmSolver, including creating shelves,
    hotkeys and menus.
    """
    global MMSOLVER_STARTED
    if MMSOLVER_STARTED is True:
        LOG.debug('Skipping MM Solver Startup, MM Solver is already started.')
        return
    MMSOLVER_STARTED = True

    LOG.info('MM Solver Startup...')

    # Only run GUI code when the Maya interactive GUI opens.
    is_batch_mode = maya.cmds.about(batch=True)
    LOG.debug('Batch Mode: %r', is_batch_mode)
    if is_batch_mode is False:
        # Create Menu.
        build_menu = bool(int(os.environ.get('MMSOLVER_CREATE_MENU', 1)))
        LOG.debug('Build Menu: %r', build_menu)
        if build_menu is True:
            maya.utils.executeDeferred(mmsolver_create_menu)

        # Create Shelf.
        build_shelf = bool(int(os.environ.get('MMSOLVER_CREATE_SHELF', 1)))
        LOG.debug('Build Shelf: %r', build_shelf)
        if build_shelf is True:
            maya.utils.executeDeferred(mmsolver_create_shelf)

        # Create Hotkey Set.
        build_hotkey_set = bool(int(os.environ.get('MMSOLVER_CREATE_HOTKEY_SET', 1)))
        LOG.debug('Build Hotkey Set: %r', build_hotkey_set)
        if build_hotkey_set is True:
            maya.utils.executeDeferred(mmsolver_create_hotkey_set)

        # Register Events.
        maya.utils.executeDeferred(mmsolver_register_events)

        # Start up the image cache.
        maya.utils.executeDeferred(mmsolver_image_cache_initalize)
    return
