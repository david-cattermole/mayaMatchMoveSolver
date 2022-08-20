# Copyright (C) 2022 David Cattermole.
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
Functions to offset a camera to the origin.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.logger
import mmSolver.utils.node as node_utils
import mmSolver._api.solvercamerautils as solvercamerautils
import mmSolver.api as mmapi

LOG = mmSolver.logger.get_logger()


def get_origin_group(cam):
    assert isinstance(cam, mmapi.Camera)
    cam_tfm = cam.get_transform_node()

    node_attr = '{}.scale'.format(cam_tfm)
    conns1 = (
        maya.cmds.listConnections(
            node_attr,
            connections=False,
            source=True,
            destination=False,
            type='multiplyDivide',
        )
        or []
    )
    if len(conns1) == 0:
        return None

    node_attr = '{}.input2'.format(conns1[0])
    conns2 = (
        maya.cmds.listConnections(
            node_attr,
            connections=False,
            source=True,
            destination=False,
            type='transform',
        )
        or []
    )
    if len(conns2) == 0:
        return None

    group_node = node_utils.get_long_name(conns2[0])
    return group_node


def create_origin_group(cam):
    assert isinstance(cam, mmapi.Camera)
    cam_tfm = cam.get_transform_node()
    group_name = cam_tfm.rpartition('|')[-1]
    group_name = '{}_originGroup'.format(group_name)
    group_node = maya.cmds.createNode('transform', name=group_name)
    group_node = node_utils.get_long_name(group_node)
    return group_node


def parent_under_origin_group(group_node, cam, bnd_list):
    assert isinstance(cam, mmapi.Camera)
    assert isinstance(bnd_list, list)
    cam_tfm = cam.get_transform_node()

    cam_parents = maya.cmds.listRelatives(cam_tfm, parent=True, fullPath=True) or []
    if len(cam_parents) == 0 or cam_parents[0] != group_node:
        maya.cmds.parent(cam_tfm, group_node, relative=True)

        mult_div = maya.cmds.createNode('multiplyDivide')
        attr_x = '{}.input1X'.format(mult_div)
        attr_y = '{}.input1Y'.format(mult_div)
        attr_z = '{}.input1Z'.format(mult_div)
        attr_op = '{}.operation'.format(mult_div)
        maya.cmds.setAttr(attr_x, 1.0)
        maya.cmds.setAttr(attr_y, 1.0)
        maya.cmds.setAttr(attr_z, 1.0)
        maya.cmds.setAttr(attr_op, 2)

        src = '{}.scale'.format(group_node)
        dst = '{}.input2'.format(mult_div)
        if not maya.cmds.isConnected(src, dst):
            maya.cmds.connectAttr(src, dst)

        cam_tfm = cam.get_transform_node()
        src = '{}.output'.format(mult_div)
        dst = '{}.scale'.format(cam_tfm)
        if not maya.cmds.isConnected(src, dst):
            maya.cmds.connectAttr(src, dst)

    for bnd in bnd_list:
        bnd_node = bnd.get_node()
        bnd_parents = (
            maya.cmds.listRelatives(bnd_node, parent=True, fullPath=True) or []
        )
        if len(bnd_parents) == 0 or bnd_parents[0] != group_node:
            maya.cmds.parent(bnd_node, group_node, relative=True)
    return


def set_camera_origin_frame(
    cam, bnd_list, scene_scale, origin_frame, start_frame, end_frame
):
    assert isinstance(cam, mmapi.Camera)

    bnd_nodes = [x.get_node() for x in bnd_list]
    bnd_nodes = [x for x in bnd_nodes if x]
    cam_tfm = cam.get_transform_node()

    solvercamerautils._set_camera_origin_frame(
        cam_tfm, bnd_nodes, origin_frame, start_frame, end_frame, scene_scale
    )
    return
