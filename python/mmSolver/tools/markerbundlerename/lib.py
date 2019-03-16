"""
This file holds all the helpful functions for markerbundlerename
"""
import maya.cmds


def prompt_for_new_node_name(title, message, text):
    """
    Ask the user for a new node name.

    :param title: Dialog box window title.
    :type title: str

    :param message: Read-only text to show the user, for making a
                    decision.
    :type message: str

    :param text: The initial text to prompt the user as a starting
                 point.
    :type text: str

    :return: New node name, or None if user cancelled.
    :rtype: str or None
    """
    name = None
    result = maya.cmds.promptDialog(
        title=title,
        message=message,
        text=text,
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel',
    )
    if result == 'OK':
        name = maya.cmds.promptDialog(query=True, text=True)
    return name
