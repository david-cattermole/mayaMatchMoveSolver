"""
Build the mmSolver menu.
"""

import os
import mmSolver.logger
import mmSolver.tools.mmmenu.constant as const
import mmSolver.ui.menuutils as menu_utils
import mmSolver.utils.config as config_utils

LOG = mmSolver.logger.get_logger()


def create_item(parent_menu, func_def):
    LOG.warning('create_item func_def=%r', func_def)
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
    )
    return menu_item


def _split_key(key):
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


def build_menu():
    """
    Build the 'mmSolver' menu.
    """
    func_config = config_utils.get_config("functions.json")
    if func_config is None:
        LOG.warning('Could not find functions.json config file')
    menu_config = config_utils.get_config("menu.json")
    if menu_config is None:
        LOG.warning('Could not find menu.json config file')
    
    main_funcs = func_config.get_value('data', default_value={})
    menu_funcs = menu_config.get_value('data/functions', default_value={})
    funcs = [menu_funcs, main_funcs]

    items = menu_config.get_value('data/items', default_value=[])

    # Create main menu.
    parent = menu_utils.get_maya_window_parent()
    mm_menu = menu_utils.create_menu(parent=parent, name=const.MENU_NAME)

    # Create menu items
    for item in items:
        # TODO: Allow creation of sub-menus.
        # item_hierachy = _split_key(item)
        
        func_def = None
        if isinstance(item, basestring):
            func_def = get_function_definition(item, funcs)
            if func_def is None and '---' in item:
                func_def = {}
                func_def['divider'] = True
                label = item.strip('-')
                if len(label) > 0:
                    func_def['name'] = label
        elif isinstance(item, dict):
            func_def = item
        else:
            LOG.warning('item is not valid: %r', item)

        if func_def is None:
            msg = 'Cannot find function definition, skipping menu; %r'
            LOG.warning(msg, item)
            continue
        menu_item = create_item(mm_menu, func_def)

    return mm_menu
