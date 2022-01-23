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
Modify and query the Hotkey Sets.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.utils.python_compat as pycompat
import mmSolver.tools.hotkeyswitcher.constant as const

LOG = mmSolver.logger.get_logger()

def get_ordered_hotkey_sets():
    names = maya.cmds.hotkeySet(query=True, hotkeySetArray=True)
    names = list(sorted(names))
    names.remove(const.HOTKEY_SET_NAME_DEFAULT)
    names.insert(0, const.HOTKEY_SET_NAME_DEFAULT)
    return names


def get_current_hotkey_set():
    return maya.cmds.hotkeySet(query=True, current=True)


def switch_to_hotkey_set(name):
    assert isinstance(name, pycompat.TEXT_TYPE)
    exists = maya.cmds.hotkeySet(name, exists=True)
    if not exists:
        msg = 'Hotkey Set %r does not exist, cannot switch.'
        LOG.warn(msg, name)
    maya.cmds.hotkeySet(name, edit=True, current=True)
    return

