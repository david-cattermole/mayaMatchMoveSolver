"""
Functions to create Maya menus.

"""

import maya.cmds
import maya.mel
import mmSolver.logger


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
    """
    assert parent is not None
    assert isinstance(parent, basestring)
    menu = maya.cmds.menu(parent=parent, label=name, **kwargs)
    return menu


def create_menu_item(parent=None,
                     name=None,
                     tooltip=None,
                     cmd=None,
                     cmdLanguage=None,
                     divider=None,
                     subMenu=None):
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

    :returns: Maya menu item UI control path.
    :rtype: str
    """
    assert parent is not None
    assert isinstance(parent, basestring)
    assert name is None or isinstance(name, basestring)
    assert tooltip is None or isinstance(tooltip, basestring)
    assert cmd is None or isinstance(cmd, basestring)
    assert divider is None or isinstance(divider, bool)
    assert subMenu is None or isinstance(subMenu, bool)

    label = 'label'
    annotation = ''
    sourceType = 'python'
    command = ''

    if isinstance(name, basestring):
        label = str(name)

    item = None
    if divider is not True and subMenu is not True:
        kwargs = {}
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
            kwargs['command'] = command
            kwargs['sourceType'] = sourceType

        item = maya.cmds.menuItem(
            parent=parent,
            label=label,
            annotation=annotation,
            **kwargs
        )
    elif subMenu is True:
        item = maya.cmds.menuItem(
            parent=parent,
            label=label,
            annotation=annotation,
            subMenu=True
        )
    elif divider is True:
        # Divider
        kwargs = {}
        if name is not None:
            kwargs['dividerLabel'] = str(label)
        item = maya.cmds.menuItem(
            parent=parent,
            divider=True,
            **kwargs
        )
    else:
        raise RuntimeError
    return item


def create_popup_menu(parent=None,
                      button=None):
    """
    Create a Pop-Up menu (for a shelf button).

    :param parent: What should this control be placed under?
    :type parent: str

    :param button: Which mouse button should active this pop-up menu?
                   1=left, 2=middle, 3=right mouse button.
    :type button: int

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

