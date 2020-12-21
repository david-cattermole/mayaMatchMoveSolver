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


def __get_lock_state(node_get, attrs):
    """
    Gets lock state of given node_get and attrs

    :param node_get: Maya node to get Lock state from.
    :type node_get : str

    :param attrs: Maya node attribute names.
    :type attrs : [str, ..]

    :return: Dict of node plugs with lock state.
    """
    plug_lock_state = {}
    for attr in attrs:
        plug = '%s.%s' % (node_get, attr)
        value = maya.cmds.getAttr(plug, lock=True)
        plug_lock_state[plug] = value
    return plug_lock_state


def __set_lock_state(node_get, node_set, attrs, lock_attr_values):
    """
    Sets lock state for given node and attributes

    :param node_get: Maya node to query the lock state with.
    :type node_get : str

    :param node_set: Maya node to set a new lock state on.
    :type node_set : str

    :param attrs: Maya node attribute names to set lock state on.
    :type attrs : [str, ..]

    :param lock_attr_values: Dict of attrs with lock state
    :type lock_attr_values: dict

    :return: None
    """
    for attr in attrs:
        query_plug = '%s.%s' % (node_get, attr)
        set_plug = '%s.%s' % (node_set, attr)
        value = lock_attr_values.get(query_plug)
        maya.cmds.setAttr(set_plug, lock=value)
    return
