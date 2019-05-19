"""
Build the mmSolver menu.
"""

import mmSolver.logger
import mmSolver.utils.config as config_utils
import mmSolver.ui.menuutils as menu_utils
import mmSolver.tools.mmmenu.constant as const
import mmSolver.tools.mmmenu.lib as lib

LOG = mmSolver.logger.get_logger()


def build_menu():
    """
    Build the 'mmSolver' menu.
    """
    LOG.info('Building mmSolver Menu...')
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
    main_parent = menu_utils.get_maya_window_parent()
    mm_menu = menu_utils.create_menu(parent=main_parent, name=const.MENU_NAME)

    # Get hierarchy.
    items_to_create = []
    for item in items:
        item_hierarchy = lib.split_key(item)

        item_path = ''
        item_keys = list(item_hierarchy)
        sub_items_to_create = []
        for sub_item_num in range(len(item_hierarchy)):
            is_sub_menu = sub_item_num > 0

            item_path = '/'.join(item_keys)
            item_key = item_path.strip('/')
            item_name = item_keys.pop()

            parent_item_path = '/'.join(item_keys)
            parent_item_key = parent_item_path.strip('/')

            func_def = lib.compile_function_definition(item_name, funcs)
            if func_def is None:
                msg = 'Cannot find function definition, skipping menu; '
                msg += 'item_name=%r item=%r'
                LOG.warning(msg, item_name, item)
                continue

            sub_items_to_create.append((item_key, parent_item_key, func_def, is_sub_menu))

        items_to_create += list(reversed(sub_items_to_create))

    # Create menu items
    created_items = {}
    for key, parent_key, func_def, is_sub_menu in items_to_create:
        menu_item = created_items.get(key)
        if menu_item is not None:
            continue
        parent = created_items.get(parent_key)
        if parent is None:
            parent = mm_menu
        menu_item = lib.create_item(parent, func_def, is_sub_menu)
        created_items[key] = menu_item

    return mm_menu
