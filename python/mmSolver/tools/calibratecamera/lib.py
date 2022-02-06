# Copyright (C) 2021 David Cattermole.
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
The camera calibration tool.
"""

from __future__ import print_function
from __future__ import absolute_import

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi


LOG = mmSolver.logger.get_logger()


def _create_line(cam, mkr_grp, base_name):
    name = '{base}_{num}_MKR'
    mkr_name1 = name.format(base=base_name, num=1)
    mkr_name2 = name.format(base=base_name, num=2)

    mkr1 = mmapi.Marker().create_node(mkr_grp=mkr_grp, name=mkr_name1)
    mkr2 = mmapi.Marker().create_node(mkr_grp=mkr_grp, name=mkr_name2)
    mkr1_node = mkr1.get_node()
    mkr2_node = mkr2.get_node()

    # mkr_grp_node = mkr_grp.get_node()

    # Create the line visualisation.
    line_name = '{base}_LINE'.format(base=base_name)
    line_shape_name = '{base}_LINEShape'.format(base=base_name)
    line_tfm = maya.cmds.createNode(
        'transform',
        name=line_name,
        # parent=mkr_grp_node
    )
    line_shp = maya.cmds.createNode(
        'mmLineShape',
        parent=line_tfm,
        name=line_shape_name)
    src_a = mkr1_node + '.worldMatrix[0]'
    src_b = mkr2_node + '.worldMatrix[0]'
    dst = line_shp + '.matrixArray'
    maya.cmds.connectAttr(src_a, dst, nextAvailable=True)
    maya.cmds.connectAttr(src_b, dst, nextAvailable=True)

    # Make line non-selectable.
    display_type = 2  # 2 = 'Reference'
    maya.cmds.setAttr(line_tfm + '.overrideEnabled', 1)
    maya.cmds.setAttr(line_tfm + '.overrideDisplayType', display_type)

    # Lock the transform.
    maya.cmds.setAttr(line_tfm + '.tx', lock=True)
    maya.cmds.setAttr(line_tfm + '.ty', lock=True)
    maya.cmds.setAttr(line_tfm + '.tz', lock=True)
    maya.cmds.setAttr(line_tfm + '.rx', lock=True)
    maya.cmds.setAttr(line_tfm + '.ry', lock=True)
    maya.cmds.setAttr(line_tfm + '.rz', lock=True)
    maya.cmds.setAttr(line_tfm + '.sx', lock=True)
    maya.cmds.setAttr(line_tfm + '.sy', lock=True)
    maya.cmds.setAttr(line_tfm + '.sz', lock=True)
    maya.cmds.setAttr(line_tfm + '.shxy', lock=True)
    maya.cmds.setAttr(line_tfm + '.shxz', lock=True)
    maya.cmds.setAttr(line_tfm + '.shyz', lock=True)

    return mkr1, mkr2, line_tfm, line_shp


def _create_vanishing_point(line1, line2, mkr_grp):
    assert len(line1) == 4
    assert len(line2) == 4
    vp_intersect_name = 'vanishingLineIntersect1'
    intersect_node = maya.cmds.createNode(
        'mmLineIntersect',
        name=vp_intersect_name)

    vp_name = 'vanishingPoint1'
    vp_mkr = mmapi.Marker().create_node(mkr_grp=mkr_grp, name=vp_name)
    vp_mkr_node = vp_mkr.get_node()

    mkr_a = line1[0].get_node()
    mkr_b = line1[1].get_node()
    mkr_c = line2[0].get_node()
    mkr_d = line2[1].get_node()

    # Create "parallel factor" attribute, for the cosine angle.
    attr_name = 'parallelFactor'
    maya.cmds.addAttr(
        vp_mkr_node,
        longName=attr_name)
    parallel_attr = '{}.{}'.format(vp_mkr_node, attr_name)

    # Create connections.
    src_dst_attr_list = [
        # Connect input line markers to line intersect node.
        ['{}.translateX'.format(mkr_a),
         '{}.pointAX'.format(intersect_node)],
        ['{}.translateY'.format(mkr_a),
         '{}.pointAY'.format(intersect_node)],
        ['{}.translateX'.format(mkr_b),
         '{}.pointBX'.format(intersect_node)],
        ['{}.translateY'.format(mkr_b),
         '{}.pointBY'.format(intersect_node)],
        ['{}.translateX'.format(mkr_c),
         '{}.pointCX'.format(intersect_node)],
        ['{}.translateY'.format(mkr_c),
         '{}.pointCY'.format(intersect_node)],
        ['{}.translateX'.format(mkr_d),
         '{}.pointDX'.format(intersect_node)],
        ['{}.translateY'.format(mkr_d),
         '{}.pointDY'.format(intersect_node)],

        # The computed vanishing point is visualized in the locator.
        ['{}.outVanishingPointX'.format(intersect_node),
         '{}.translateX'.format(vp_mkr_node)],
        ['{}.outVanishingPointY'.format(intersect_node),
         '{}.translateY'.format(vp_mkr_node)],

        # Cosine angle
        ['{}.outCosineAngle'.format(intersect_node),
         parallel_attr],
    ]
    for src, dst in src_dst_attr_list:
        if maya.cmds.isConnected(src, dst) is False:
            maya.cmds.connectAttr(src, dst)

    maya.cmds.setAttr(parallel_attr, keyable=True)
    maya.cmds.setAttr(parallel_attr, lock=True)
    return intersect_node, vp_mkr


def _set_default_axis_values(line1, line2, invert_x=None):
    assert isinstance(invert_x, bool)
    mkr_a = line1[0].get_node()
    mkr_b = line1[1].get_node()
    mkr_c = line2[0].get_node()
    mkr_d = line2[1].get_node()

    mkr_a_tx = '{}.translateX'.format(mkr_a)
    mkr_a_ty = '{}.translateY'.format(mkr_a)
    mkr_b_tx = '{}.translateX'.format(mkr_b)
    mkr_b_ty = '{}.translateY'.format(mkr_b)
    mkr_c_tx = '{}.translateX'.format(mkr_c)
    mkr_c_ty = '{}.translateY'.format(mkr_c)
    mkr_d_tx = '{}.translateX'.format(mkr_d)
    mkr_d_ty = '{}.translateY'.format(mkr_d)

    x_factor = 1.0
    y_factor = 1.0
    if invert_x is True:
        x_factor = -1.0

    x = -0.167
    y = -0.005
    maya.cmds.setAttr(mkr_a_tx, x * x_factor)
    maya.cmds.setAttr(mkr_a_ty, y * y_factor)

    x = -0.404
    y = -0.108
    maya.cmds.setAttr(mkr_b_tx, x * x_factor)
    maya.cmds.setAttr(mkr_b_ty, y * y_factor)

    x = -0.158
    y = -0.177
    maya.cmds.setAttr(mkr_c_tx, x * x_factor)
    maya.cmds.setAttr(mkr_c_ty, y * y_factor)

    x = -0.364
    y = -0.339
    maya.cmds.setAttr(mkr_d_tx, x * x_factor)
    maya.cmds.setAttr(mkr_d_ty, y * y_factor)
    return


def _set_default_horizon_values(mkr1, mkr2):
    mkr1_node = mkr1.get_node()
    mkr2_node = mkr2.get_node()

    mkr1_tx = '{}.translateX'.format(mkr1_node)
    mkr1_ty = '{}.translateY'.format(mkr1_node)
    mkr2_tx = '{}.translateX'.format(mkr2_node)
    mkr2_ty = '{}.translateY'.format(mkr2_node)

    x = -0.25
    y = 0.0
    maya.cmds.setAttr(mkr1_tx, x)
    maya.cmds.setAttr(mkr1_ty, y)

    x = 0.25
    y = 0.0
    maya.cmds.setAttr(mkr2_tx, x)
    maya.cmds.setAttr(mkr2_ty, y)
    return


def create_new_setup():
    """
    Create the default setup
    """
    maya.cmds.loadPlugin('matrixNodes', quiet=True)
    mmapi.load_plugin()

    # Create a camera and image plane (or validate and use the given one)
    cam_tfm = maya.cmds.createNode('transform', name='camera')
    cam_shp = maya.cmds.createNode('camera', name='cameraShape', parent=cam_tfm)
    cam = mmapi.Camera(shape=cam_shp)

    # Create image plane.
    img_pl_tfm, img_pl_shp = maya.cmds.imagePlane(camera=cam_shp)

    # Using a "To Size" fit mode will forcibly change the image to
    # stretch it to match the size given. Therefore it is important
    # the image plane size (including the aspect ratio) is correct.
    maya.cmds.setAttr('{}.fit'.format(img_pl_shp), 4)  # 4 = To Size

    # Image plane is almost at far-clipping plane distance.
    maya.cmds.setAttr('{}.depth'.format(img_pl_shp), 9990)

    # Darken the imagePlane.
    value = 0.5
    maya.cmds.setAttr(
        '{}.colorGain'.format(img_pl_shp),
        value, value, value, type='double3')

    # Make the image plane non-selectable.
    maya.cmds.setAttr('{}.overrideEnabled'.format(img_pl_shp), 1)
    maya.cmds.setAttr(
        '{}.overrideDisplayType'.format(img_pl_shp),
        2)  # 2 == 'Reference' display type.

    # Create a "Calibrate" marker group.
    mkr_grp = mmapi.MarkerGroup().create_node(cam=cam, name='calibrate')

    origin_mkr = mmapi.Marker().create_node(
        mkr_grp=mkr_grp, name='originPoint')
    origin_mkr_node = origin_mkr.get_node()

    # Axis 1
    line_a = _create_line(cam, mkr_grp, 'LineA')
    line_b = _create_line(cam, mkr_grp, 'LineB')
    intersect_node_a, vp_a_mkr = _create_vanishing_point(
        line_a, line_b,
        mkr_grp)
    _set_default_axis_values(line_a, line_b, invert_x=False)

    # Axis 2
    line_c = _create_line(cam, mkr_grp, 'LineC')
    line_d = _create_line(cam, mkr_grp, 'LineD')
    intersect_node_b, vp_b_mkr = _create_vanishing_point(
        line_c, line_d,
        mkr_grp)
    _set_default_axis_values(line_c, line_d, invert_x=True)

    # Horizon Line
    horizon_line_mkr1, horizon_line_mkr2, horizon_line_tfm, horizon_line_shp = \
        _create_line(cam, mkr_grp, 'HorizonLine')
    _set_default_horizon_values(horizon_line_mkr1, horizon_line_mkr2)
    horizon_line_mkr1_node = horizon_line_mkr1.get_node()
    horizon_line_mkr2_node = horizon_line_mkr2.get_node()

    # Create a mmCameraCalibrate node.
    calib_node = maya.cmds.createNode('mmCameraCalibrate')
    maya.cmds.setAttr(
        '{}.calibrationMode'.format(calib_node),
        3)  # 3 = "Two Vanishing Points".

    decompose_node = maya.cmds.createNode('decomposeMatrix')
    maya.cmds.setAttr(
        '{}.inputRotateOrder'.format(decompose_node),
        2)  # 2 = ZXY (good default for cameras aimed at the horizon.)

    maya.cmds.addAttr(
        calib_node,
        attributeType='float',
        minValue=0.0,
        defaultValue=1920.0,
        longName='imageWidth')
    maya.cmds.addAttr(
        calib_node,
        attributeType='float',
        minValue=0.0,
        defaultValue=1080.0,
        longName='imageHeight')
    maya.cmds.addAttr(
        calib_node,
        attributeType='float',
        minValue=0.0,
        defaultValue=1.0,
        longName='imagePixelAspectRatio')
    maya.cmds.addAttr(
        calib_node,
        attributeType='float',
        minValue=0.0,
        defaultValue=1.0,
        longName='imageAspectRatio')

    exp = (
        'imageAspectRatio = (imageWidth * imagePixelAspectRatio) / imageHeight;'
        'verticalFilmAperture = horizontalFilmAperture / imageAspectRatio;'
    )
    maya.cmds.expression(object=calib_node, string=exp)

    maya.cmds.addAttr(
        calib_node,
        attributeType='message',
        longName='vanishingPointNodeA')
    maya.cmds.addAttr(
        calib_node,
        attributeType='message',
        longName='vanishingPointNodeB')

    maya.cmds.addAttr(
        calib_node,
        attributeType='message',
        longName='horizonPointNodeA')
    maya.cmds.addAttr(
        calib_node,
        attributeType='message',
        longName='horizonPointNodeB')

    maya.cmds.addAttr(
        calib_node,
        attributeType='message',
        longName='originPointNode')

    # Create connections.
    src_dst_attr_list = [
        # Camera shape viewing attributes.
        ['{}.outCameraAperture'.format(calib_node),
         '{}.cameraAperture'.format(cam_shp)],
        ['{}.outFocalLength'.format(calib_node),
         '{}.focalLength'.format(cam_shp)],

        ['{}.outMatrix'.format(calib_node),
         '{}.inputMatrix'.format(decompose_node)],

        ['{}.outputTranslate'.format(decompose_node),
         '{}.translate'.format(cam_tfm)],
        ['{}.outputRotate'.format(decompose_node),
         '{}.rotate'.format(cam_tfm)],
        ['{}.inputRotateOrder'.format(decompose_node),
         '{}.rotateOrder'.format(cam_tfm)],

        # Connections so we can find the intersection values from the
        # calibration, without creating a dependency
        # 'attributeAffects' relationship in the DG.
        ['{}.message'.format(intersect_node_a),
         '{}.vanishingPointNodeA'.format(calib_node)],
        ['{}.message'.format(intersect_node_b),
         '{}.vanishingPointNodeB'.format(calib_node)],
        ['{}.message'.format(origin_mkr_node),
         '{}.originPointNode'.format(calib_node)],

        ['{}.message'.format(horizon_line_mkr1_node),
         '{}.horizonPointNodeA'.format(calib_node)],
        ['{}.message'.format(horizon_line_mkr2_node),
         '{}.horizonPointNodeB'.format(calib_node)],

        ['{}.coverageX'.format(img_pl_shp),
         '{}.imageWidth'.format(calib_node)],
        ['{}.coverageY'.format(img_pl_shp),
         '{}.imageHeight'.format(calib_node)],

        ['{}.horizontalFilmAperture'.format(cam_shp),
         '{}.sizeX'.format(img_pl_shp)],
        ['{}.verticalFilmAperture'.format(cam_shp),
         '{}.sizeY'.format(img_pl_shp)],
    ]
    for src, dst in src_dst_attr_list:
        if maya.cmds.isConnected(src, dst) is False:
            maya.cmds.connectAttr(src, dst)
    return


def get_calibrate_node_from_camera(cam):
    assert isinstance(cam, mmapi.Camera)
    cam_shp = cam.get_shape_node()
    conns = maya.cmds.listConnections(
        cam_shp,
        source=True,
        destination=False,
        type='mmCameraCalibrate') or []
    calib_node = None
    if len(conns) > 0:
        calib_node = conns[0]
    return calib_node


def _get_vanishing_point_nodes_from_calibrate_node(calibrate_node):
    assert maya.cmds.objExists(calibrate_node) is True
    assert maya.cmds.nodeType(calibrate_node) == 'mmCameraCalibrate'
    node_a = None
    node_b = None
    attr_a = '{}.vanishingPointNodeA'.format(calibrate_node)
    attr_b = '{}.vanishingPointNodeB'.format(calibrate_node)
    nodes_a = maya.cmds.listConnections(
        attr_a,
        source=True,
        destination=False,
        type='mmLineIntersect') or []
    nodes_b = maya.cmds.listConnections(
        attr_b,
        source=True,
        destination=False,
        type='mmLineIntersect') or []
    if len(nodes_a) == 0:
        LOG.error('Cannot find intersect node for vanishing point A')
        return node_a, node_b
    if len(nodes_b) == 0:
        LOG.error('Cannot find intersect node for vanishing point B')
        return node_a, node_b
    node_a = nodes_a[0]
    node_b = nodes_b[0]
    return node_a, node_b


def _get_horizon_point_nodes_from_calibrate_node(calibrate_node):
    assert maya.cmds.objExists(calibrate_node) is True
    assert maya.cmds.nodeType(calibrate_node) == 'mmCameraCalibrate'
    node_a = None
    node_b = None
    attr_a = '{}.horizonPointNodeA'.format(calibrate_node)
    attr_b = '{}.horizonPointNodeB'.format(calibrate_node)
    nodes_a = maya.cmds.listConnections(
        attr_a,
        source=True,
        destination=False,
        type='transform') or []
    nodes_b = maya.cmds.listConnections(
        attr_b,
        source=True,
        destination=False,
        type='transform') or []
    if len(nodes_a) == 0:
        LOG.error('Cannot find intersect node for horizon point A')
        return node_a, node_b
    if len(nodes_b) == 0:
        LOG.error('Cannot find intersect node for horizon point B')
        return node_a, node_b
    node_a = nodes_a[0]
    node_b = nodes_b[0]
    return node_a, node_b


def _get_origin_point_node_from_calibrate_node(calibrate_node):
    assert maya.cmds.objExists(calibrate_node) is True
    assert maya.cmds.nodeType(calibrate_node) == 'mmCameraCalibrate'
    node = None
    attr_a = '{}.originPointNode'.format(calibrate_node)
    nodes = maya.cmds.listConnections(
        attr_a,
        source=True,
        destination=False,
        type='transform') or []
    if len(nodes) == 0:
        LOG.error('Cannot find for origin point.')
        return node
    node = nodes[0]
    return node


def update_calibrate_values(calibrate_node):
    """This function will query the translate attributes from the marker
    nodes and set the values on the mmLineIntersect nodes.

    This is to break the DG dependency between the markers and the
    camera transform.
    """
    assert maya.cmds.objExists(calibrate_node) is True
    assert maya.cmds.nodeType(calibrate_node) == 'mmCameraCalibrate'

    # 1) Get the vanishing points "connected" to the calibrate_node.
    vp_node_a, vp_node_b = \
        _get_vanishing_point_nodes_from_calibrate_node(calibrate_node)
    origin_node = _get_origin_point_node_from_calibrate_node(calibrate_node)
    horizon_node_a, horizon_node_b = \
        _get_horizon_point_nodes_from_calibrate_node(calibrate_node)
    assert vp_node_a is not None
    assert vp_node_b is not None
    assert origin_node is not None
    assert horizon_node_a is not None
    assert horizon_node_b is not None

    # Query the values of the vanishing points, then set the attribute values
    # on the calibrate_node.
    out_attr_a_x = '{}.outVanishingPointX'.format(vp_node_a)
    out_attr_a_y = '{}.outVanishingPointY'.format(vp_node_a)
    out_attr_b_x = '{}.outVanishingPointX'.format(vp_node_b)
    out_attr_b_y = '{}.outVanishingPointY'.format(vp_node_b)

    in_attr_a_x = '{}.vanishingPointAX'.format(calibrate_node)
    in_attr_a_y = '{}.vanishingPointAY'.format(calibrate_node)
    in_attr_b_x = '{}.vanishingPointBX'.format(calibrate_node)
    in_attr_b_y = '{}.vanishingPointBY'.format(calibrate_node)

    out_horizon_attr_a_x = '{}.translateX'.format(horizon_node_a)
    out_horizon_attr_a_y = '{}.translateY'.format(horizon_node_a)
    out_horizon_attr_b_x = '{}.translateX'.format(horizon_node_b)
    out_horizon_attr_b_y = '{}.translateY'.format(horizon_node_b)

    in_horizon_attr_a_x = '{}.horizonPointAX'.format(calibrate_node)
    in_horizon_attr_a_y = '{}.horizonPointAY'.format(calibrate_node)
    in_horizon_attr_b_x = '{}.horizonPointBX'.format(calibrate_node)
    in_horizon_attr_b_y = '{}.horizonPointBY'.format(calibrate_node)

    out_origin_attr_x = '{}.translateX'.format(origin_node)
    out_origin_attr_y = '{}.translateY'.format(origin_node)

    in_origin_attr_x = '{}.originPointX'.format(calibrate_node)
    in_origin_attr_y = '{}.originPointY'.format(calibrate_node)

    src_dst_attrs = [
        [out_attr_a_x, in_attr_a_x],
        [out_attr_a_y, in_attr_a_y],
        [out_attr_b_x, in_attr_b_x],
        [out_attr_b_y, in_attr_b_y],

        [out_horizon_attr_a_x, in_horizon_attr_a_x],
        [out_horizon_attr_a_y, in_horizon_attr_a_y],
        [out_horizon_attr_b_x, in_horizon_attr_b_x],
        [out_horizon_attr_b_y, in_horizon_attr_b_y],

        [out_origin_attr_x, in_origin_attr_x],
        [out_origin_attr_y, in_origin_attr_y],
    ]
    for src_attr, dst_attr in src_dst_attrs:
        value = maya.cmds.getAttr(src_attr)
        maya.cmds.setAttr(dst_attr, value)
    return True


def get_calibrate_update_mode(calibrate_node):
    # const.CALIBRATE_UPDATE_MODE_NON_INTERACTIVE
    # const.CALIBRATE_UPDATE_MODE_INTERACTIVE
    # const.CALIBRATE_UPDATE_MODE_LOCKED
    raise NotImplementedError


def set_calibrate_update_mode(calibrate_node, mode_value):
    # if mode_value == const.CALIBRATE_UPDATE_MODE_NON_INTERACTIVE:
    #     pass
    # elif mode_value == const.CALIBRATE_UPDATE_MODE_INTERACTIVE:
    #     pass
    # elif mode_value == const.CALIBRATE_UPDATE_MODE_LOCKED:
    #     pass
    raise NotImplementedError
