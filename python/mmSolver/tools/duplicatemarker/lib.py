"""
This file holds all the helpful functions for duplicate marker
"""

import maya.cmds


def __copy_key_frames(source_mkr_node, new_mkr_node):
    """

    :param source_mkr_node: source marker node from which you want to
    duplicate.
    :param new_mkr_node: new marker node to paste source marker keys
    :return: None
    """

    plugs = ['translateX', 'translateY']

    for plug_name in plugs:
        anim_curves = maya.cmds.listConnections(
                                '%s.%s' % (source_mkr_node, plug_name),
                                type='animCurve') or []
        if anim_curves:
            maya.cmds.copyKey('%s.%s' % (source_mkr_node, plug_name),
                              option='curve')
            maya.cmds.pasteKey('%s.%s' % (new_mkr_node, plug_name))

        else:
            value = maya.cmds.getAttr('%s.%s' % (source_mkr_node,
                                                 plug_name))
            maya.cmds.setAttr('%s.%s' % (new_mkr_node, plug_name),
                              value)
    return
