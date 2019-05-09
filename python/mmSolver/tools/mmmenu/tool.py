"""
Build the mmSolver menu.
"""

import mmSolver.logger
import mmSolver.tools.mmmenu.constant as const
import mmSolver.ui.menuutils as menu_utils


LOG = mmSolver.logger.get_logger()


def build_menu():
    """
    Build the 'mmSolver' menu.
    """
    parent = menu_utils.get_maya_window_parent()
    mm_menu = menu_utils.create_menu(parent=parent, name=const.MENU_NAME)
    for i in range(10):
        name = 'name' + str(i)
        item = menu_utils.create_menu_item(parent=mm_menu, name=name)
    return mm_menu
