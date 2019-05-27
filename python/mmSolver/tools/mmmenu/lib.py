"""
Supporting functions for building the mmSolver menu.
"""

import os
import mmSolver.logger
import mmSolver.ui.menuutils as menu_utils

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
            func_def['divider'] = True
            label = item.strip('-')
            label = label.strip()
            if len(label) > 0:
                func_def['name'] = label
    elif isinstance(item, dict):
        func_def = item
    else:
        LOG.warning('item is not valid: %r', item)
    return func_def


def create_item(parent_menu, func_def, is_sub_menu):
    """
    Create a menu item with a function definition.
    """
    name = func_def.get('name', None)
    tooltip = func_def.get('tooltip', None)
    divider = func_def.get('divider', None)
    command_language = func_def.get('command_lang', None)
    command = func_def.get('command', None)
    if isinstance(command, (list, tuple)):
        command = str(os.linesep).join(command)
    menu_item = menu_utils.create_menu_item(
        parent=parent_menu,
        name=name,
        tooltip=tooltip,
        cmd=command,
        cmdLanguage=command_language,
        divider=divider,
        subMenu=is_sub_menu,
    )
    return menu_item
