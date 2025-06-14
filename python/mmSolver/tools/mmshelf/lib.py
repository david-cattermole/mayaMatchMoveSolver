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

import maya.mel
import maya.cmds

import os
import mmSolver.logger
import mmSolver.ui.shelfutils as shelf_utils
import mmSolver.ui.menuutils as menu_utils
import mmSolver.utils.config as config_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.tools.mmshelf.constant as const

LOG = mmSolver.logger.get_logger()


def activate_shelf_tab(shelf_tab_name):
    """
    Set the Maya shelf to the shelf with 'shelf_tab_name' as the name.

    :param shelf_tab_name: The shelf name to activate.
    :rtype: None
    """
    # The MEL procedure "jumpToNamedShelf" can be found in the file:
    # "${MAYA_LOCATION}/scripts/startup/shelf.mel"
    mel_cmd = 'jumpToNamedShelf(\"{}\");'.format(shelf_tab_name)
    maya.cmds.evalDeferred(lambda: maya.mel.eval(mel_cmd))
    return


def split_key(key):
    """
    Split a key into separate name hierarchy, with a '/' character.

    :param key: Split this string into a list.
    :type key: str

    :returns: List of keys.
    :rtype: [str, ..]
    """
    args = key.split('/')
    args = [k for k in args if len(k) > 0]
    return args


def get_function_definition(key, data_list):
    """
    Look up a function definition in the list of data given.

    :param key: String to look up the function definition.
    :type key: str

    :param data_list: List of dictionary to look up.
    :type data_list: [{..}, ..]

    :returns: Get the value at the key.
    :rtype: str or None
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

    :param item: Item to compile.
    :type item: str or dict

    :param funcs: Function data structures.
    :type funcs: dict

    :returns: The function definition data structure.
    :rtype: dict or None
    """
    func_def = None
    if isinstance(item, pycompat.TEXT_TYPE):
        func_def = get_function_definition(item, funcs)
        if func_def is None and '---' in item:
            func_def = {const.DIVIDER_KEY: True}
            label = item.strip('-')
            label = label.strip()
            if len(label) > 0:
                func_def[const.NAME_KEY] = label
    elif isinstance(item, dict):
        func_def = item
    else:
        LOG.warning('item is not valid: %r', item)
    return func_def


def lookup_value(data, name, suffix):
    """
    Look up a key on the data, preferring the key ending with suffix
    rather than name.

    :param data: Search into this data structure for a value.
    :type data: {str: .., ..}

    :param name: Key to look-up.
    :type name: str

    :param suffix: Test the key and suffix.
    :type suffix: str

    :returns: The found value, or None if nothing was found.
    """
    value = data.get(name + suffix, None)
    if value is None:
        value = data.get(name, None)
    return value


def compile_items(items, function_defs):
    """
    Convert a list of items and function definitions in configs, to a
    list of command items.

    :param items: The item name paths to look up and create.
    :type items: [str, ..]

    :param function_defs: Function definitions, describing how the item
         will be created and what it will do.
    :type function_defs: [{str: any}, ..]

    :returns:
    :rtype:
    """
    # Get hierarchy.
    items_to_create = []
    for item in items:
        item_hierarchy = split_key(item)

        item_keys = []
        sub_items_to_create = []
        for sub_item_num in range(len(item_hierarchy)):
            is_first_item = sub_item_num == 0
            is_last_item = sub_item_num == (len(item_hierarchy) - 1)

            item_name = item_hierarchy[sub_item_num]
            item_keys.append(item_name)

            item_path = '/'.join(item_keys)
            item_key = item_path.strip('/')
            item_name = item_keys[-1]

            parent_item_path = '/'.join(item_keys[: len(item_keys) - 1])
            parent_item_key = parent_item_path.strip('/')

            func_def = compile_function_definition(item_name, function_defs)
            if func_def is None:
                msg = 'Cannot find function definition, '
                msg += 'skipping item (and children items); '
                msg += 'item_name=%r item=%r'
                LOG.warning(msg, item_name, item)
                break

            sub_items_to_create.append(
                (item_key, parent_item_key, func_def, is_first_item, is_last_item)
            )

        items_to_create += list(sub_items_to_create)
    return items_to_create


def create_items(items_to_create, main_parent):
    """
    Create shelf items.

    :param items_to_create: List of items to be created.
    :type items_to_create: [{}, ..]

    :param main_parent: The parent index name.
    :type main_parent: str

    :returns: The created items in a dictionary data structure.
    :rtype: {str: {}, ..}
    """
    created_items = {}
    for key, parent_key, func_def, is_first_item, is_last_item in items_to_create:
        items = created_items.get(key)
        # We are able to have the same key multiple times if it is a
        # divider without a name.
        divider = key.endswith('---')
        if items is not None and divider is not True:
            continue

        parents = created_items.get(parent_key)
        if parents is None:
            parents = [main_parent]

        items = create_item(parents, func_def, is_first_item, is_last_item)
        created_items[key] = items
    return created_items


def create_item(parents, func_def, is_first_item, is_last_item):
    """
    Create a shelf or menu item with a function definition.

    :param parents: The list of parent items this item will be created
                    under.
    :type parents: [str, ..]

    :param func_def: Function definition.
    :type func_def: {str: .., ..}

    :param is_first_item: Will this item be the start of the hierarchy?
    :type is_first_item: bool

    :param is_last_item: Will this item be the end of the hierarchy?
    :type is_last_item: bool

    :returns: List of items created.
    :rtype: [{}, ..]
    """
    key_suffix = const.KEY_SUFFIX_SHELF
    popup = lookup_value(func_def, const.POPUP_KEY, key_suffix)

    items = []
    for parent in parents:
        if is_first_item:
            # The first item in a shelf must be a button.
            key_suffix = const.KEY_SUFFIX_SHELF
            name = lookup_value(func_def, const.NAME_KEY, key_suffix)
            icon = lookup_value(func_def, const.ICON_KEY, key_suffix)
            tooltip = lookup_value(func_def, const.TOOLTIP_KEY, key_suffix)
            divider = lookup_value(func_def, const.DIVIDER_KEY, key_suffix)
            cmdLang = lookup_value(func_def, const.CMD_LANG_KEY, key_suffix)
            command = lookup_value(func_def, const.CMD_KEY, key_suffix)
            if isinstance(command, (list, tuple)):
                command = str(os.linesep).join(command)

            if divider:
                item = shelf_utils.create_shelf_separator(parent=parent)
                items.append(item)
            else:
                item = shelf_utils.create_shelf_button(
                    parent=parent,
                    name=name,
                    tooltip=tooltip,
                    icon=icon,
                    cmd=command,
                    cmdLanguage=cmdLang,
                )
                items.append(item)
        elif is_last_item:
            # Last item must be a menu item, not a menu or popup menu.
            key_suffix = const.KEY_SUFFIX_MENU
            name = lookup_value(func_def, const.NAME_KEY, key_suffix)
            tooltip = lookup_value(func_def, const.TOOLTIP_KEY, key_suffix)
            divider = lookup_value(func_def, const.DIVIDER_KEY, key_suffix)
            cmdLang = lookup_value(func_def, const.CMD_LANG_KEY, key_suffix)
            command = lookup_value(func_def, const.CMD_KEY, key_suffix)
            if isinstance(command, (list, tuple)):
                command = str(os.linesep).join(command)

            # Create menu item
            menu_item = menu_utils.create_menu_item(
                parent=parent,
                name=name,
                tooltip=tooltip,
                cmd=command,
                cmdLanguage=cmdLang,
                divider=divider,
                subMenu=False,
            )
            items.append(menu_item)

            # Create option box for menu item
            option_box = lookup_value(func_def, const.OPTBOX_KEY, key_suffix)
            if option_box is True:
                key_suffix = const.KEY_SUFFIX_OPTION_BOX
                cmdLang = lookup_value(func_def, const.CMD_LANG_KEY, key_suffix)
                command = lookup_value(func_def, const.CMD_KEY, key_suffix)
                if isinstance(command, (list, tuple)):
                    command = str(os.linesep).join(command)

                option_box_item = menu_utils.create_menu_item(
                    parent=parent,
                    cmd=command,
                    cmdLanguage=cmdLang,
                    optionBox=option_box,
                )
                items.append(option_box_item)
        elif popup:
            key_suffix = const.KEY_SUFFIX_MENU
            popupBtn = lookup_value(func_def, const.POPUP_BUTTON_KEY, key_suffix)
            popupPostCmd = lookup_value(func_def, const.POPUP_POST_CMD_KEY, key_suffix)
            if isinstance(popupPostCmd, (list, tuple)):
                popupPostCmd = str(os.linesep).join(popupPostCmd)

            # Create list of popup buttons, for each button-click used
            # to open them.
            popupBtnMap = {'left': 1, 'middle': 2, 'right': 3}
            popupBtnIndexList = []
            if popupBtn is None:
                popupBtnIndexList = [None]
            else:
                assert isinstance(popupBtn, (list, tuple))
                assert len(popupBtn) > 0
                for btn in popupBtn:
                    index = popupBtnMap.get(btn, None)
                    if index not in popupBtnIndexList:
                        popupBtnIndexList.append(index)

            # A pop-up menu on top of a shelf button. One menu may be
            # created for each mouse button needing to be clicked to
            # activate the pop-up menu..
            for index in popupBtnIndexList:
                item = menu_utils.create_popup_menu(
                    parent=parent, postCmd=popupPostCmd, button=index
                )
                items.append(item)
        else:
            # A sub-menu entry, a menu item that will contain other menu
            # items.
            key_suffix = const.KEY_SUFFIX_MENU
            name = lookup_value(func_def, const.NAME_KEY, key_suffix)
            tooltip = lookup_value(func_def, const.TOOLTIP_KEY, key_suffix)
            divider = lookup_value(func_def, const.DIVIDER_KEY, key_suffix)
            tearoff = lookup_value(func_def, const.TEAR_OFF_KEY, key_suffix)

            item = menu_utils.create_menu_item(
                parent=parent,
                name=name,
                tooltip=tooltip,
                divider=divider,
                subMenu=True,
                tearOff=tearoff,
            )
            items.append(item)
    return items


def build(shelf, func_config_name, shelf_config_name):
    """
    Build shelf items with configuration file names.

    :param shelf: Maya shelf UI path.
    :type shelf: str

    :param func_config_name: Function configuration file name.
    :type func_config_name: str

    :param shelf_config_name: Shelf configuration file name.
    :type shelf_config_name: str

    :returns: The Maya shelf UI path.
    :rtype: str
    """
    func_config = config_utils.get_config(func_config_name)
    if func_config is None:
        LOG.warning('Could not find %s config file', func_config_name)

    shelf_config = config_utils.get_config(shelf_config_name)
    if shelf_config is None:
        LOG.warning('Could not find %s config file', shelf_config_name)

    main_funcs = func_config.get_value('data', default_value={})
    shelf_funcs = shelf_config.get_value('data/functions', default_value={})
    funcs = [shelf_funcs, main_funcs]

    # Create the shelf buttons items
    items = shelf_config.get_value('data/items', default_value=[])
    items_to_create = compile_items(items, funcs)
    create_items(items_to_create, shelf)
    return shelf
