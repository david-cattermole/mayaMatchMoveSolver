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
Functions to create Maya menus.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds
import maya.mel
import mmSolver.logger
import mmSolver.utils.python_compat as pycompat


LOG = mmSolver.logger.get_logger()


def get_maya_window_parent():
    """
    Get Maya UI path to the parent Maya Window.

    :return: Maya UI path of shelf parent layout.
    :rtype: str
    """
    cmd = 'global string $gMainWindow; string $temp = $gMainWindow;'
    return maya.mel.eval(cmd)


def create_menu(parent=None, name=None, **kwargs):
    """
    Create a Maya menu.

    :param parent: Which menu should this menu item be placed under?
    :type parent: str

    :param name: Name (label) of the menu item button.
    :type name: str
    """
    assert parent is not None
    assert isinstance(parent, pycompat.TEXT_TYPE)
    menu = maya.cmds.menu(parent=parent, label=name, **kwargs)
    return menu


def create_menu_item(
    parent=None,
    name=None,
    tooltip=None,
    cmd=None,
    cmdLanguage=None,
    divider=None,
    subMenu=None,
    tearOff=None,
    optionBox=None,
):
    """
    Create a Menu Item on a menu.

    :param parent: Which menu should this menu item be placed under?
    :type parent: str

    :param name: Name (label) of the menu item button.
    :type name: str

    :param tooltip: The text shown to the user in the status line, when
                    the user has the mouse over the menu item.
    :type tooltip: str

    :param cmd: The command text to run when the menu item is pressed.
    :type cmd: str

    :param cmdLanguage: What language is 'cmd' argument in? 'python'
                        or 'mel'?
    :type cmdLanguage: str

    :param divider: Should this menu item be a divider (separator)?
    :type divider: bool

    :param subMenu: Will this menu item have other menu items under it?
    :type subMenu: bool

    :param tearOff: Allow users to tear-off a copy of the menu? This
                    is not valid for menu items, only sub-menus.
    :type tearOff: bool

    :param optionBox: Create an Option Box, not a menu item.
    :type optionBox: bool

    :returns: Maya menu item UI control path.
    :rtype: str
    """
    assert parent is not None
    assert isinstance(parent, pycompat.TEXT_TYPE)
    assert name is None or isinstance(name, pycompat.TEXT_TYPE)
    assert tooltip is None or isinstance(tooltip, pycompat.TEXT_TYPE)
    assert cmd is None or isinstance(cmd, pycompat.TEXT_TYPE)
    assert divider is None or isinstance(divider, bool)
    assert subMenu is None or isinstance(subMenu, bool)
    assert tearOff is None or isinstance(tearOff, bool)

    if optionBox is None:
        optionBox = False
    assert isinstance(optionBox, bool)

    label = 'label'
    annotation = ''

    if isinstance(name, pycompat.TEXT_TYPE):
        label = str(name)
    if isinstance(tooltip, pycompat.TEXT_TYPE):
        annotation = str(tooltip)

    item = None
    if divider is not True and subMenu is not True:
        kwargs = {}
        if isinstance(cmd, pycompat.TEXT_TYPE):
            command = str(cmd)
            if cmdLanguage is None:
                sourceType = 'python'
            elif isinstance(cmdLanguage, pycompat.TEXT_TYPE):
                sourceType = str(cmdLanguage)
            else:
                msg = 'cmdLanguage must be None or str: cmdLanguage=%r'
                LOG.error(msg, cmdLanguage)
                raise ValueError(msg, cmdLanguage)
            kwargs['command'] = command
            kwargs['sourceType'] = sourceType

        if optionBox is True:
            kwargs['optionBox'] = optionBox

        item = maya.cmds.menuItem(
            parent=parent, label=label, annotation=annotation, **kwargs
        )
    elif subMenu is True:
        kwargs = {}
        if tearOff is not None:
            kwargs['tearOff'] = tearOff
        item = maya.cmds.menuItem(
            parent=parent, label=label, annotation=annotation, subMenu=True, **kwargs
        )
    elif divider is True:
        kwargs = {}
        if name is not None:
            kwargs['dividerLabel'] = str(label)
        item = maya.cmds.menuItem(parent=parent, divider=True, **kwargs)
    else:
        raise RuntimeError
    return item


def create_popup_menu(parent=None, postCmd=None, button=None):
    """
    Create a Pop-Up menu (for a shelf button).

    :param parent: What should this control be placed under?
    :type parent: str

    :param postCmd: Command to be run before the popup menu is shown.
                    Replaces '{menu}' with the full menu name.
    :type postCmd: None or str

    :param button: Which mouse button should active this pop-up menu?
                   1=left, 2=middle, 3=right mouse button.
    :type button: int

    :returns: Maya popup menu UI control path.
    :rtype: str
    """
    assert parent is not None
    assert isinstance(parent, pycompat.TEXT_TYPE)
    assert postCmd is None or isinstance(postCmd, pycompat.TEXT_TYPE)
    if button is None:
        button = 3
    assert isinstance(button, int)
    menu = maya.cmds.popupMenu(parent=parent, button=button)
    if postCmd is not None:
        cmd = str(postCmd).format(menu=menu)
        maya.cmds.popupMenu(menu, edit=True, postMenuCommand=cmd)
    return menu
