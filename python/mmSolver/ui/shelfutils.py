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
Functions to create Maya shelves and buttons.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import warnings

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.utils.python_compat as pycompat


LOG = mmSolver.logger.get_logger()


def get_shelves_parent():
    """
    Get Maya UI path to the parent of all shelves in Maya.

    :return: Maya UI path of shelf parent layout.
    :rtype: str
    """
    cmd = 'global string $gShelfTopLevel; string $temp = $gShelfTopLevel;'
    return maya.mel.eval(cmd)


def create_shelf(parent=None, name=None):
    """
    (Re-)Create a shelf.

    If a shelf with 'name' is already exists, the exising shelf will
    be deleted, and re-created under the 'parent' argument given.

    :param parent: What layout will this shelf be placed under?
    :type parent: str

    :param name: Name (label) of the shelf displayed to the user.
                 The value should only contain characters A-Z
                 (or a-z) and underscores '_'.
    :type name: str

    :return: Shelf UI path, or None if cannot be found.
    :rtype: str or None
    """
    assert name is not None
    assert parent is not None
    assert isinstance(name, pycompat.TEXT_TYPE)
    assert isinstance(parent, pycompat.TEXT_TYPE)
    if len(parent) == 0:
        return None
    shelf = str(name)
    exists = maya.cmds.shelfLayout(shelf, exists=True)
    if exists:
        # delete the shelf.
        children = maya.cmds.shelfLayout(name, query=True, childArray=True) or []
        for c in children:
            maya.cmds.deleteUI(c)
        maya.cmds.deleteUI(shelf)

    # Create the shelf under the new parent.
    shelf = maya.cmds.shelfLayout(
        name,
        parent=parent,
    )
    shelf = maya.cmds.shelfLayout(name, query=True, fullPathName=True)
    return shelf


def create_shelf_button(
    parent=None, name=None, tooltip=None, icon=None, cmd=None, cmdLanguage=None
):
    """
    Create a shelf button.

    :param parent: What should this control be placed under?
    :type parent: str

    :param name: Name (label) of the shelf button. Should be under
                 seven characters long.
    :type name: str

    :param tooltip: The text shown to the user when hovering the mouse
                    over the shelf button.
    :type tooltip: str

    :param icon: Choose the image to display on the shelf button.
                 Should be 32x32 pixels.
    :type icon: str

    :param cmd: The command text to run when the shelf button is
                pressed.
    :type cmd: str

    :param cmdLanguage: What language is 'cmd' argument in? 'python'
                        or 'mel'?
    :type cmdLanguage: str

    :returns: Maya button UI control path.
    :rtype: str
    """
    assert parent is not None
    assert isinstance(parent, pycompat.TEXT_TYPE)
    assert name is None or isinstance(name, pycompat.TEXT_TYPE)
    assert tooltip is None or isinstance(tooltip, pycompat.TEXT_TYPE)
    assert icon is None or isinstance(icon, pycompat.TEXT_TYPE)
    assert cmd is None or isinstance(cmd, pycompat.TEXT_TYPE)

    kwargs = {}
    label = 'label'
    imageOverlayLabel = 'label'
    annotation = 'tooltip'
    image = 'commandButton.png'
    image1 = 'commandButton.png'
    sourceType = 'python'
    command = None
    doubleClickCommand = None
    if isinstance(name, pycompat.TEXT_TYPE):
        imageOverlayLabel = str(name)
    if isinstance(tooltip, pycompat.TEXT_TYPE):
        label = str(tooltip)
        annotation = str(tooltip)
    if isinstance(icon, pycompat.TEXT_TYPE):
        image = str(icon)
        image1 = str(icon)

    if cmdLanguage is None:
        sourceType = 'python'
    elif isinstance(cmdLanguage, pycompat.TEXT_TYPE):
        sourceType = str(cmdLanguage)
    else:
        msg = 'cmdLanguage must be None or str: cmdLanguage=%r'
        LOG.error(msg, cmdLanguage)
        raise ValueError(msg, cmdLanguage)
    kwargs['sourceType'] = sourceType

    if isinstance(cmd, pycompat.TEXT_TYPE):
        command = str(cmd)
        kwargs['command'] = command

    button = maya.cmds.shelfButton(
        parent=parent,
        image=image,
        image1=image1,
        label=label,
        imageOverlayLabel=imageOverlayLabel,
        noDefaultPopup=True,
        preventOverride=True,
        **kwargs
    )
    return button


def create_shelf_separator(parent=None):
    """
    Create a shelf button separator.

    :param parent: What should this control be placed under?
    :type parent: str

    :returns: Maya separator UI control path.
    :rtype: str
    """
    assert parent is not None
    assert isinstance(parent, pycompat.TEXT_TYPE)
    control = maya.cmds.separator(parent=parent, style='shelf', horizontal=False)
    return control


def create_popup_menu(*args, **kwargs):
    msg = 'Deprecated, please use mmSolver.ui.menuutils.create_popup_menu'
    warnings.warn(msg, DeprecationWarning)
    import mmSolver.ui.menuutils as menu_utils

    return menu_utils.create_popup_menu(*args, **kwargs)


def create_menu_item(*args, **kwargs):
    msg = 'Deprecated, please use mmSolver.ui.menuutils.create_menu_item'
    warnings.warn(msg, DeprecationWarning)
    import mmSolver.ui.menuutils as menu_utils

    return menu_utils.create_menu_item(*args, **kwargs)
