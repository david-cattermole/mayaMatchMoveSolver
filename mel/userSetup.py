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

This file is automatically imported by Maya before version 2022. After
Maya 2022 this file is no longer imported and the functions must be
called explicitly.

To workaround this issue the mmSolver plug-in will
now call the mmSolver.startup.mmsolver_startup() Python function when
loaded, so you can enable auto-load for the 'mmSolver' plug-in and
mmSolver will be correctly started each time Maya loads. This
workaround unfortunately slows down Maya startup times.
"""

import os
import warnings

import maya.cmds
import maya.utils
import mmSolver.startup

# Backwards compatibility for users needing call individual start up
# scripts.
#
# These functions were moved to 'mmSolver.startup' because Maya 2022
# doesn't run the userSetup.py file defined in a module anymore.
def mmsolver_create_shelf():
    msg = 'Deprecated, please use mmSolver.startup.mmsolver_create_shelf()'
    warnings.warn(msg)
    mmSolver.startup.mmsolver_create_shelf()


def mmsolver_create_menu():
    msg = 'Deprecated, please use mmSolver.startup.mmsolver_create_menu()'
    warnings.warn(msg)
    mmSolver.startup.mmsolver_create_menu()


def mmsolver_create_hotkey_set():
    msg = 'Deprecated, please use mmSolver.startup.mmsolver_create_hotkey_set()'
    warnings.warn(msg)
    mmSolver.startup.mmsolver_create_hotkey_set()


def mmsolver_register_events():
    msg = 'Deprecated, please use mmSolver.startup.mmsolver_create_register_events()'
    warnings.warn(msg)
    mmSolver.startup.mmsolver_register_events()


def mmsolver_startup():
    msg = 'Deprecated, please use mmSolver.startup.mmsolver_startup()'
    warnings.warn(msg)
    mmSolver.startup.mmsolver_startup()


# Run Start up Function after Maya has loaded.
load_at_startup = bool(int(os.environ.get('MMSOLVER_LOAD_AT_STARTUP', 1)))
if load_at_startup is True:
    maya.utils.executeDeferred(mmSolver.startup.mmsolver_startup)
