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

    :return: Shelf UI path.
    :rtype: str
    """
    assert name is not None
    assert parent is not None
    assert isinstance(name, basestring)
    assert isinstance(parent, basestring)
    assert len(parent) > 0
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
        doubleClickCommand = str(cmd)
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
        doubleClickCommand=doubleClickCommand,
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
