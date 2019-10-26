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
Tool for allowing the user to switch the hotkey set.
"""

import datetime
import uuid

import maya.cmds

import mmSolver.logger
import mmSolver.tools.hotkeyswitcher.lib as lib
import mmSolver.tools.hotkeyswitcher.constant as const

LOG = mmSolver.logger.get_logger()


def create_menu(menu_name):
    LOG.debug('Create hotkey switcher menu: %r', menu_name)
    parent = menu_name

    # Remove existing menu items.
    maya.cmds.popupMenu(menu_name, edit=True, deleteAllItems=True)

    menu_collection = maya.cmds.radioMenuItemCollection(parent=menu_name)
    current_set = lib.get_current_hotkey_set()

    items = []
    names = lib.get_ordered_hotkey_sets()
    for name in names:
        value = current_set == name
        tooltip = const.MENU_TOOLTIP.format(name=name)
        cmd = const.MENU_CMD.format(name=name)
        cmdLang = const.MENU_CMD_LANG
        item = maya.cmds.menuItem(
            parent=parent,
            label=name,
            annotation=tooltip,
            command=cmd,
            sourceType=cmdLang,
            radioButton=value,
            collection=menu_collection,
            subMenu=False,
        )
        items.append(item)
    LOG.debug('Created hotkey switcher menu: %r', items)
    return items


def main(name=None):
    if name is None:
        LOG.error('Please give a hotkey set name.')
        return
    lib.switch_to_hotkey_set(name)
    return
