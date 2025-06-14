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
Supporting functions for building the mmSolver menu.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import mmSolver.logger
import mmSolver.ui.menuutils as menu_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.tools.mmmenu.constant as const

LOG = mmSolver.logger.get_logger()


def split_key(key):
    """
    Split a key into separate name hierarchy, with a '/' character.
    """
    args = key.split('/')
    args = [k for k in args if len(k) > 0]
    return args


def get_function_definition(key, data_list):
    """
    Look up a function definition in the list of data given.
    """
    value = None
    for data in data_list:
        value = data.get(key, None)
        if value is not None:
            break
    return value


def compile_function_definition(item, funcs):
    """
    Find and create a function definition.
    """
    func_def = None
    if isinstance(item, pycompat.TEXT_TYPE):
        func_def = get_function_definition(item, funcs)
        if func_def is None and '---' in item:
            func_def = {'divider': True}
            label = item.strip('-')
            label = label.strip()
            if len(label) > 0:
                func_def['name'] = label
    elif isinstance(item, dict):
        func_def = item
    else:
        LOG.warning('item is not valid: %r', item)
    return func_def


def compile_items(items, function_defs):
    # Get hierarchy.
    items_to_create = []
    for item in items:
        item_hierarchy = split_key(item)

        item_keys = list(item_hierarchy)
        sub_items_to_create = []
        for sub_item_num in range(len(item_hierarchy)):
            is_sub_menu = sub_item_num > 0

            item_path = '/'.join(item_keys)
            item_key = item_path.strip('/')
            item_name = item_keys.pop()

            parent_item_path = '/'.join(item_keys)
            parent_item_key = parent_item_path.strip('/')

            func_def = compile_function_definition(item_name, function_defs)
            if func_def is None:
                msg = 'Cannot find function definition, skipping menu; '
                msg += 'item_name=%r item=%r'
                LOG.warning(msg, item_name, item)
                continue

            sub_items_to_create.append(
                (item_key, parent_item_key, func_def, is_sub_menu)
            )

        items_to_create += list(reversed(sub_items_to_create))

    return items_to_create


def create_item(parent_menu, func_def, is_sub_menu):
    """
    Create a menu item with a function definition.
    """
    name = func_def.get(const.NAME_KEY, None)
    tooltip = func_def.get(const.TOOLTIP_KEY, None)
    divider = func_def.get(const.DIVIDER_KEY, None)
    command_language = func_def.get(const.CMD_LANG_KEY, None)
    command = func_def.get(const.CMD_KEY, None)
    if isinstance(command, (list, tuple)):
        command = str(os.linesep).join(command)
    tearoff = func_def.get(const.TEAR_OFF_KEY, None)
    if not is_sub_menu:
        tearoff = None
    menu_item = menu_utils.create_menu_item(
        parent=parent_menu,
        name=name,
        tooltip=tooltip,
        cmd=command,
        cmdLanguage=command_language,
        divider=divider,
        subMenu=is_sub_menu,
        tearOff=tearoff,
    )

    # Create option box for menu item
    option_box = func_def.get(const.OPTBOX_KEY, None)
    if option_box is True:
        command_language = func_def.get(const.CMD_LANG_KEY, None)
        command = func_def.get(const.OPTBOX_CMD_KEY, None)
        if isinstance(command, (list, tuple)):
            command = str(os.linesep).join(command)
        menu_utils.create_menu_item(
            parent=parent_menu,
            cmd=command,
            cmdLanguage=command_language,
            optionBox=option_box,
        )
    return menu_item


def create_items(items_to_create, main_parent):
    # Create menu items
    created_items = {}
    for key, parent_key, func_def, is_sub_menu in items_to_create:
        menu_item = created_items.get(key)
        # We are able to have the same key multiple times if it is a
        # divider without a name.
        divider = key.endswith('---')
        if menu_item is not None and divider is not True:
            continue
        parent = created_items.get(parent_key)
        if parent is None:
            parent = main_parent
        menu_item = create_item(parent, func_def, is_sub_menu)
        created_items[key] = menu_item
    return created_items
