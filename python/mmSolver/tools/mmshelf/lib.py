"""
Supporting functions for building the mmSolver menu.
"""

import os
import mmSolver.logger
import mmSolver.ui.shelfutils as shelf_utils
import mmSolver.ui.menuutils as menu_utils
import mmSolver.tools.mmshelf.constant as const

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
    if isinstance(item, basestring):
        func_def = get_function_definition(item, funcs)
        if func_def is None and '---' in item:
            func_def = {}
            func_def[const.DIVIDER_KEY] = True
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
    """
    value = data.get(name + suffix, None)
    if value is None:
        value = data.get(name, None)
    return value


def create_item(parent, func_def, is_first_item, is_last_item):
    """
    Create a shelf or menu item with a function definition.
    """
    name = lookup_value(func_def, const.NAME_KEY, const.KEY_SUFFIX)
    icon = lookup_value(func_def, const.ICON_KEY, const.KEY_SUFFIX)
    tooltip = lookup_value(func_def, const.TOOLTIP_KEY, const.KEY_SUFFIX)
    divider = lookup_value(func_def, const.DIVIDER_KEY, const.KEY_SUFFIX)
    popup = lookup_value(func_def, const.POPUP_KEY, const.KEY_SUFFIX)
    popupBtn = lookup_value(func_def, const.POPUP_BUTTON_KEY, const.KEY_SUFFIX)
    cmdLang = lookup_value(func_def, const.CMD_LANG_KEY, const.KEY_SUFFIX)
    command = lookup_value(func_def, const.CMD_KEY, const.KEY_SUFFIX)
    if isinstance(command, (list, tuple)):
        command = str(os.linesep).join(command)

    popupBtnMap = {'left': 1, 'middle': 2, 'right': 3}
    popupBtnIndex = 0
    if popupBtn is not None:
        popupBtnIndex = popupBtnMap.get(popupBtn, None)

    item = None
    if is_first_item:
        if divider:
            item = shelf_utils.create_shelf_separator(
                parent=parent
            )
        else:
            item = shelf_utils.create_shelf_button(
                parent=parent,
                name=name,
                tooltip=tooltip,
                icon=icon,
                cmd=command,
            )
    elif is_last_item:
        item = menu_utils.create_menu_item(
            parent=parent,
            name=name,
            tooltip=tooltip,
            cmd=command,
            cmdLanguage=cmdLang,
            divider=divider,
            subMenu=False,
        )
    elif popup:
        item = menu_utils.create_popup_menu(
            parent=parent,
            button=popupBtnIndex
        )

    return item
