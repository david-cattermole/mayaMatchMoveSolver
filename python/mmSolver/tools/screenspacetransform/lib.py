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
Position locator at the screen-space position.
"""

import maya.cmds
import maya.OpenMaya

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.node as node_utils

LOG = mmSolver.logger.get_logger()


def create_screen_space_locator(cam, name=None):
    """
    Create a Screen-Space Maya Locator that may be solved in Screen XYZ.
    """
    if name is None:
        name = 'screenSpace'

    mkr_grp = mmapi.MarkerGroup().create_node(cam=cam, name=name)
    mkr_grp_node = mkr_grp.get_node()
    maya.cmds.setAttr(mkr_grp_node + '.depth', 1.0)
    maya.cmds.setAttr(mkr_grp_node + '.depth', lock=True)
    maya.cmds.setAttr(mkr_grp_node + '.overscanX', lock=True)
    maya.cmds.setAttr(mkr_grp_node + '.overscanY', lock=True)

    depth_tfm = maya.cmds.createNode('transform', name='depth', parent=mkr_grp_node)
    depth_tfm = node_utils.get_long_name(depth_tfm)
    maya.cmds.setAttr(depth_tfm + '.translateX', lock=True)
    maya.cmds.setAttr(depth_tfm + '.translateY', lock=True)
    maya.cmds.setAttr(depth_tfm + '.translateZ', lock=True)
    maya.cmds.setAttr(depth_tfm + '.rotateX', lock=True)
    maya.cmds.setAttr(depth_tfm + '.rotateY', lock=True)
    maya.cmds.setAttr(depth_tfm + '.rotateZ', lock=True)
    src = depth_tfm + '.scaleX'
    dst1 = depth_tfm + '.scaleY'
    dst2 = depth_tfm + '.scaleZ'
    maya.cmds.connectAttr(src, dst1)
    maya.cmds.connectAttr(src, dst2)
    maya.cmds.setAttr(depth_tfm + '.scaleY', lock=True)
    maya.cmds.setAttr(depth_tfm + '.scaleZ', lock=True)

    loc_name = 'point'
    loc_tfm = maya.cmds.createNode('transform', name=name, parent=depth_tfm)
    loc_tfm = node_utils.get_long_name(loc_tfm)
    loc_shp = maya.cmds.createNode('locator', parent=loc_tfm)
    loc_shp = node_utils.get_long_name(loc_shp)
    maya.cmds.setAttr(loc_tfm + '.localScaleX', 0.1)
    maya.cmds.setAttr(loc_tfm + '.localScaleY', 0.1)
    maya.cmds.setAttr(loc_tfm + '.localScaleZ', 0.0)
    maya.cmds.setAttr(loc_tfm + '.translateZ', -1.0)
    maya.cmds.setAttr(loc_tfm + '.translateZ', lock=True)
    maya.cmds.setAttr(loc_tfm + '.rotateX', lock=True)
    maya.cmds.setAttr(loc_tfm + '.rotateY', lock=True)
    maya.cmds.setAttr(loc_tfm + '.rotateZ', lock=True)
    maya.cmds.setAttr(loc_tfm + '.scaleX', lock=True)
    maya.cmds.setAttr(loc_tfm + '.scaleY', lock=True)
    maya.cmds.setAttr(loc_tfm + '.scaleZ', lock=True)
    maya.cmds.setAttr(loc_tfm + '.shearXY', lock=True)
    maya.cmds.setAttr(loc_tfm + '.shearXZ', lock=True)
    maya.cmds.setAttr(loc_tfm + '.shearYZ', lock=True)
    return mkr_grp_node, depth_tfm, loc_tfm, loc_shp
