# Copyright (C) 2020, 2022 David Cattermole.
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
Library functions for creating and modifying image planes.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

import maya.cmds

import mmSolver.logger
import mmSolver.tools.createimageplane._lib.utilities as lib_utils
import mmSolver.utils.node as node_utils

LOG = mmSolver.logger.get_logger()


PolyPlaneNetworkNodes = collections.namedtuple(
    'PolyPlaneNetworkNodes',
    [
        'mesh_shape',
        'mesh_shape_original',
        'plane_creator',
        'deformer',
    ],
)


def create_poly_plane(name_mesh_shp, image_plane_tfm, cam_shp):
    """
    Create a default polygon image plane under camera.
    """
    mesh_shp = maya.cmds.createNode('mesh', name=name_mesh_shp, parent=image_plane_tfm)
    creator = maya.cmds.createNode('polyPlane')
    maya.cmds.connectAttr(creator + '.output', mesh_shp + '.inMesh')

    maya.cmds.setAttr(creator + '.subdivisionsWidth', 32)
    maya.cmds.setAttr(creator + '.subdivisionsHeight', 32)
    maya.cmds.setAttr(creator + '.axisX', 0.0)
    maya.cmds.setAttr(creator + '.axisY', 0.0)
    maya.cmds.setAttr(creator + '.axisZ', 1.0)

    # Make the polygon image plane non-selectable.
    display_type = 2  # 2 = 'Reference'
    maya.cmds.setAttr(image_plane_tfm + '.overrideEnabled', 1)
    maya.cmds.setAttr(image_plane_tfm + '.overrideDisplayType', display_type)

    deform_node = maya.cmds.deformer(image_plane_tfm, type='mmLensDeformer')[0]
    mkr_scl = maya.cmds.createNode('mmMarkerScale')
    inv_mult = maya.cmds.createNode('multiplyDivide')

    # Drive the Deformer node with the camera lens.
    src = cam_shp + '.outLens'
    dst = deform_node + '.inLens'
    src_attr_exists = node_utils.attribute_exists('outLens', cam_shp)
    if src_attr_exists is True and (not maya.cmds.isConnected(src, dst)):
        lib_utils.force_connect_attr(src, dst)

    # Get the intermediate mesh shape, so we can re-order the nodes
    # later and ensure the mmImagePlaneShape is first, so that users
    # will see the mmImagePlaneShape first in the Attribute Editor.
    shapes = (
        maya.cmds.listRelatives(
            image_plane_tfm,
            shapes=True,
            noIntermediate=False,
            fullPath=True,
            type='mesh',
        )
        or []
    )
    shapes = [x for x in shapes if maya.cmds.getAttr(x + '.intermediateObject') == 1]
    assert len(shapes) == 1
    mesh_shp_original = shapes[0]

    # Connect Image Plane dummy attrs to Marker Scale node.
    attrs = [
        'depth',
        'focalLength',
        'horizontalFilmAperture',
        'verticalFilmAperture',
        'horizontalFilmOffset',
        'verticalFilmOffset',
    ]
    for attr in attrs:
        src = image_plane_tfm + '.' + attr
        dst = mkr_scl + '.' + attr
        lib_utils.force_connect_attr(src, dst)

    attrs = [
        'focalLength',
        'horizontalFilmAperture',
        'verticalFilmAperture',
        'pixelAspect',
        'horizontalFilmOffset',
        'verticalFilmOffset',
    ]
    for attr in attrs:
        src = image_plane_tfm + '.' + attr
        dst = deform_node + '.' + attr
        lib_utils.force_connect_attr(src, dst)

    # Connect marker scale to transform node.
    lib_utils.force_connect_attr(mkr_scl + '.outScale', image_plane_tfm + '.scale')
    lib_utils.force_connect_attr(
        mkr_scl + '.outTranslateX', image_plane_tfm + '.translateX'
    )
    lib_utils.force_connect_attr(
        mkr_scl + '.outTranslateY', image_plane_tfm + '.translateY'
    )

    # Connect inverted depth to the transform TZ.
    lib_utils.force_connect_attr(mkr_scl + '.depth', inv_mult + '.input1Z')
    lib_utils.force_connect_attr(inv_mult + '.outputZ', image_plane_tfm + '.translateZ')
    maya.cmds.setAttr(inv_mult + '.operation', 1)  # Multiply operation
    maya.cmds.setAttr(inv_mult + '.input2Z', -1.0)

    # Lock and hide all the attributes
    attrs = [
        'tx',
        'ty',
        'tz',
        'rx',
        'ry',
        'rz',
        'sx',
        'sy',
        'sz',
        'shearXY',
        'shearXZ',
        'shearYZ',
        'rotateOrder',
        'rotateAxisX',
        'rotateAxisY',
        'rotateAxisZ',
    ]
    for attr in attrs:
        maya.cmds.setAttr(image_plane_tfm + '.' + attr, lock=True)
        maya.cmds.setAttr(image_plane_tfm + '.' + attr, keyable=False, channelBox=False)

    network = PolyPlaneNetworkNodes(
        mesh_shape=mesh_shp,
        mesh_shape_original=mesh_shp_original,
        plane_creator=creator,
        deformer=deform_node,
    )
    return network
