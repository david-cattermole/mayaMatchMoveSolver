"""
Build the mmSolver Maya shelf.
"""

import mmSolver.logger
import mmSolver.utils.config as config_utils
import mmSolver.ui.shelfutils as shelf_utils
import mmSolver.tools.mmshelf.constant as const
import mmSolver.tools.mmshelf.lib as lib


LOG = mmSolver.logger.get_logger()


def build_shelf():
    """
    Build the 'mmSolver' shelf.
    """
    LOG.info('Building mmSolver Shelf...')
    func_config = config_utils.get_config("functions.json")
    if func_config is None:
        LOG.warning('Could not find functions.json config file')
    shelf_config = config_utils.get_config("shelf.json")
    if shelf_config is None:
        LOG.warning('Could not find shelf.json config file')

    main_funcs = func_config.get_value('data', default_value={})
    shelf_funcs = shelf_config.get_value('data/functions', default_value={})
    funcs = [shelf_funcs, main_funcs]

    items = shelf_config.get_value('data/items', default_value=[])

    # Create main shelf.
    shelf_parent = shelf_utils.get_shelves_parent()
    shelf_name = str(const.SHELF_NAME)
    shelf = shelf_utils.create_shelf(
        parent=shelf_parent,
        name=shelf_name
    )
    if shelf is None:
        return

    # Get hierarchy.
    items_to_create = []
    for item in items:
        item_hierarchy = lib.split_key(item)

        is_first_item = None
        is_last_item = None
        item_path = ''
        item_keys = []
        sub_items_to_create = []
        for sub_item_num in range(len(item_hierarchy)):
            is_first_item = sub_item_num == 0
            is_last_item = sub_item_num == (len(item_hierarchy)-1)

            item_name = item_hierarchy[sub_item_num]
            item_keys.append(item_name)

            item_path = '/'.join(item_keys)
            item_key = item_path.strip('/')
            item_name = item_keys[-1]

            parent_item_path = '/'.join(item_keys[:len(item_keys)-1])
            parent_item_key = parent_item_path.strip('/')

            func_def = lib.compile_function_definition(item_name, funcs)
            if func_def is None:
                msg = 'Cannot find function definition, skipping item; '
                msg += 'item_name=%r item=%r'
                LOG.warning(msg, item_name, item)
                continue

            sub_items_to_create.append((item_key, parent_item_key, func_def, is_first_item, is_last_item))

        items_to_create += list(sub_items_to_create)

    # Create shelf items
    created_items = {}
    for key, parent_key, func_def, is_first_item, is_last_item in items_to_create:
        item = created_items.get(key)
        if item is not None:
            continue

        parent = created_items.get(parent_key)
        if parent is None:
            parent = shelf

        item = lib.create_item(parent, func_def, is_first_item, is_last_item)
        created_items[key] = item

    return shelf
