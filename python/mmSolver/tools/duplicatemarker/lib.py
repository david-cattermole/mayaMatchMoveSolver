# Copyright (C) 2019 Anil Reddy.
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
This file holds all the helpful functions for duplicate marker
"""

import maya.cmds
import mmSolver.tools.duplicatemarker.constant as const


def __copy_key_frames(source_mkr_node, new_mkr_node):
    """
    Copies keys from source and pastes it on given new node.

    :param source_mkr_node: Source marker node from which you want to
                            duplicate.
    :type source_mkr_node: str

    :param new_mkr_node: New marker node to paste source marker keys.
    :type new_mkr_node: str
    """
    plugs = const.MKR_ATTRS

    for plug_name in plugs:
        plug = '%s.%s' % (source_mkr_node, plug_name)
        anim_curves = maya.cmds.listConnections(plug, type='animCurve') or []
        if len(anim_curves) > 0:
            src_plug = '%s.%s' % (source_mkr_node, plug_name)
            dst_plug = '%s.%s' % (new_mkr_node, plug_name)
            maya.cmds.copyKey(src_plug, option='curve')
            maya.cmds.pasteKey(dst_plug)
        else:
            src_plug = '%s.%s' % (source_mkr_node, plug_name)
            dst_plug = '%s.%s' % (new_mkr_node, plug_name)
            value = maya.cmds.getAttr(src_plug)
            maya.cmds.setAttr(dst_plug, value)
    return


def __get_lock_state(node, attrs):
    """
    Gets lock state of given node and attrs
    :param node: Maya node
    :type node : str

    :param attrs: Maya node attrs
    :type attrs : list
    :return: Dict of attrs with lock state
    """
    plug_lock_state = {}
    for attr in attrs:
        plug = '%s.%s' % (node, attr)
        value = maya.cmds.getAttr(plug, lock=True)
        # BUG: The plug should be used as the key, not attr.
        plug_lock_state[attr] = value
    return plug_lock_state


def __set_lock_state(node, attrs, lock_attr_values):
    """
    Sets lock state for given node and attributes

    :param node: Maya node
    :type node : str

    :param attrs: Maya node attrs
    :type attrs : list

    :param lock_attr_values: Dict of attrs with lock state
    :type lock_attr_values: dict

    :return: None
    """
    for attr in attrs:
        # BUG: The plug should be used as the key, not attr.
        value = lock_attr_values.get(attr)
        plug = '%s.%s' % (node, attr)
        maya.cmds.setAttr(plug, lock=value)
    return
