"""
Functions to create Maya shelves and buttons.
"""

import maya.cmds
import maya.mel
import mmSolver.logger


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

    :return: Shelf UI path, or None if cannot be found.
    :rtype: str or None
    """
    assert name is not None
    assert parent is not None
    assert isinstance(name, basestring)
    assert isinstance(parent, basestring)
    if len(parent) == 0:
        return None
    shelf = str(name)
    exists = maya.cmds.shelfLayout(shelf, exists=True)
    if exists:
        # delete the shelf.
        children = maya.cmds.shelfLayout(
            name,
            query=True,
            childArray=True
        ) or []
        for c in children:
            maya.cmds.deleteUI(c)
        maya.cmds.deleteUI(shelf)

    # Create the shelf under the new parent.
    shelf = maya.cmds.shelfLayout(
        name,
        parent=parent,
    )
    shelf = maya.cmds.shelfLayout(
        name,
        query=True,
        fullPathName=True
    )
    return shelf


def create_shelf_button(parent=None,
                        name=None,
                        tooltip=None,
                        icon=None,
                        cmd=None,
                        cmdLanguage=None):
    """
    Create a shelf button.
    """
    assert parent is not None
    assert isinstance(parent, basestring)
    assert name is None or isinstance(name, basestring)
    assert tooltip is None or isinstance(tooltip, basestring)
    assert icon is None or isinstance(icon, basestring)
    assert cmd is None or isinstance(cmd, basestring)

    label = 'label'
    imageOverlayLabel = 'label'
    annotation = 'tooltip'
    image = 'commandButton.png'
    image1 = 'commandButton.png'
    sourceType = 'python'
    command = None
    doubleClickCommand = None
    if isinstance(name, basestring):
        imageOverlayLabel = str(name)
    if isinstance(tooltip, basestring):
        label = str(tooltip)
        annotation = str(tooltip)
    if isinstance(icon, basestring):
        image = str(icon)
        image1 = str(icon)
    if isinstance(cmd, basestring):
        command = str(cmd)
    if cmdLanguage is None:
        sourceType = 'python'
    elif isinstance(cmdLanguage, basestring):
        sourceType = str(cmdLanguage)
    else:
        msg = 'cmdLanguage must be None or str: cmdLanguag=%r'
        LOG.error(msg, cmdLanguage)
        raise ValueError(msg, cmdLanguage)

    button = maya.cmds.shelfButton(
        parent=parent,
        image=image,
        image1=image1,
        label=label,
        imageOverlayLabel=imageOverlayLabel,
        sourceType=sourceType,
        command=command,
        noDefaultPopup=True,
        preventOverride=True,
    )
    return button


def create_shelf_separator(parent=None):
    """
    Create a shelf button.
    """
    assert parent is not None
    assert isinstance(parent, basestring)
    control = maya.cmds.separator(
        parent=parent,
        style='shelf',
        horizontal=False
    )
    return control


def create_popup_menu(parent=None,
                      button=None):
    """
    Create a Pop-Up menu (for a shelf button).

    :param parent: What should this control be placed under?
    :type parent: str

    :param button: Which mouse button should active this pop-up menu?
                   1=left, 2=middle, 3=right mouse button.
    :type button: str

    :returns: Maya popup menu UI control path.
    :rtype: str
    """
    assert parent is not None
    assert isinstance(parent, basestring)
    if button is None:
        button = 3
    assert isinstance(button, int)
    menu = maya.cmds.popupMenu(
        parent=parent,
        button=button)
    return menu


def create_menu_item(parent=None,
                     name=None,
                     tooltip=None,
                     cmd=None,
                     cmdLanguage=None):
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

    :returns: Maya menu item UI control path.
    :rtype: str
    """
    assert parent is not None
    assert isinstance(parent, basestring)
    assert name is None or isinstance(name, basestring)
    assert tooltip is None or isinstance(tooltip, basestring)
    assert cmd is None or isinstance(cmd, basestring)

    label = 'label'
    annotation = ''
    sourceType = 'python'
    command = None
    if isinstance(name, basestring):
        label = str(name)
    if isinstance(cmd, basestring):
        command = str(cmd)
    if cmdLanguage is None:
        sourceType = 'python'
    elif isinstance(cmdLanguage, basestring):
        sourceType = str(cmdLanguage)
    else:
        msg = 'cmdLanguage must be None or str: cmdLanguage=%r'
        LOG.error(msg, cmdLanguage)
        raise ValueError(msg, cmdLanguage)

    item = maya.cmds.menuItem(
        parent=parent,
        label=label,
        annotation=annotation,
        command=cmd,
        sourceType=sourceType,

    )
    return item
