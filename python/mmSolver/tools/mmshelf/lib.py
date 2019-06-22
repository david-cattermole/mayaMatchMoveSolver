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


def compile_items(items, function_defs):
    # Get hierarchy.
    items_to_create = []
    for item in items:
        item_hierarchy = split_key(item)

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

            func_def = compile_function_definition(item_name, function_defs)
            if func_def is None:
                msg = 'Cannot find function definition, skipping item; '
                msg += 'item_name=%r item=%r'
                LOG.warning(msg, item_name, item)
                continue

            sub_items_to_create.append(
                (item_key,
                 parent_item_key,
                 func_def,
                 is_first_item,
                 is_last_item)
            )

        items_to_create += list(sub_items_to_create)

    return items_to_create


def create_item(parents, func_def, is_first_item, is_last_item):
    """
    Create a shelf or menu item with a function definition.
    """
    # TODO: These values should be dynamically looked up once we knew
    # we are creating a menu or a shelf button, and should therefore
    # have a different KEY_SUFFIX_* value. This way we can dynamically
    # look up the correct label in a menu or shelf button.
    name = lookup_value(func_def, const.NAME_KEY, const.KEY_SUFFIX_SHELF)
    icon = lookup_value(func_def, const.ICON_KEY, const.KEY_SUFFIX_SHELF)
    tooltip = lookup_value(func_def, const.TOOLTIP_KEY, const.KEY_SUFFIX_SHELF)
    divider = lookup_value(func_def, const.DIVIDER_KEY, const.KEY_SUFFIX_SHELF)
    popup = lookup_value(func_def, const.POPUP_KEY, const.KEY_SUFFIX_SHELF)
    popupBtn = lookup_value(func_def, const.POPUP_BUTTON_KEY, const.KEY_SUFFIX_SHELF)
    cmdLang = lookup_value(func_def, const.CMD_LANG_KEY, const.KEY_SUFFIX_SHELF)
    command = lookup_value(func_def, const.CMD_KEY, const.KEY_SUFFIX_SHELF)
    if isinstance(command, (list, tuple)):
        command = str(os.linesep).join(command)
    tearoff = lookup_value(func_def, const.TEAR_OFF_KEY, const.KEY_SUFFIX_SHELF)

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

    items = []
    for parent in parents:
        if is_first_item:
            # The first item in a shelf must be a button.
            if divider:
                item = shelf_utils.create_shelf_separator(
                    parent=parent
                )
                items.append(item)
            else:
                item = shelf_utils.create_shelf_button(
                    parent=parent,
                    name=name,
                    tooltip=tooltip,
                    icon=icon,
                    cmd=command,
                )
                items.append(item)
        elif is_last_item:
            # Last item must be a menu item, not a menu or popup menu.
            item = menu_utils.create_menu_item(
                parent=parent,
                name=name,
                tooltip=tooltip,
                cmd=command,
                cmdLanguage=cmdLang,
                divider=divider,
                subMenu=False,
            )
            items.append(item)
        elif popup:
            # A pop-up menu on top of a shelf button. One menu may be
            # created for each mouse button needing to be clicked to
            # activate the pop-up menu..
            for index in popupBtnIndexList:
                item = menu_utils.create_popup_menu(
                    parent=parent,
                    button=index
                )
                items.append(item)
        else:
            # A sub-menu entry, a menu item that will contain other menu
            # items.
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


def create_items(items_to_create, main_parent):
    # Create shelf items
    created_items = {}
    for key, parent_key, func_def, is_first_item, is_last_item in items_to_create:
        items = created_items.get(key)
        if items is not None:
            continue

        parents = created_items.get(parent_key)
        if parents is None:
            parents = [main_parent]

        items = create_item(
            parents,
            func_def,
            is_first_item,
            is_last_item)
        created_items[key] = items
    return created_items
