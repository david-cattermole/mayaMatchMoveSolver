# Copyright (C) 2020 David Cattermole.
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
Functions to help create a screen-space motion trail.
"""

import maya.cmds
import maya.OpenMaya

import mmSolver.logger
import mmSolver.api as mmapi

import mmSolver.utils.node as node_utils
import mmSolver.utils.time as time_utils
import mmSolver.utils.camera as camera_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.tools.screenspacemotiontrail.constant as const

LOG = mmSolver.logger.get_logger()


def _create_trail_frame_attrs(node,
                              use_frame_range,
                              start_frame,
                              end_frame,
                              pre_frame,
                              post_frame,
                              increment,
                              keyable=None):
    if keyable is None:
        keyable = False

    all_attrs = maya.cmds.listAttr(node) or []

    attr_name = 'useFrameRange'
    if attr_name not in all_attrs:
        plug_name = node + '.' + attr_name
        maya.cmds.addAttr(
            node,
            longName=attr_name,
            attributeType='bool'
        )
        maya.cmds.setAttr(plug_name, keyable=keyable)
        maya.cmds.setAttr(plug_name, use_frame_range)

    attr_name = 'preFrame'
    if attr_name not in all_attrs:
        plug_name = node + '.' + attr_name
        maya.cmds.addAttr(
            node,
            longName=attr_name,
            attributeType='double',
            minValue=0.0,
        )
        maya.cmds.setAttr(plug_name, keyable=keyable)
        maya.cmds.setAttr(plug_name, pre_frame)

    attr_name = 'postFrame'
    if attr_name not in all_attrs:
        plug_name = node + '.' + attr_name
        maya.cmds.addAttr(
            node,
            longName=attr_name,
            attributeType='double',
            minValue=0.0,
        )
        maya.cmds.setAttr(plug_name, keyable=keyable)
        maya.cmds.setAttr(plug_name, post_frame)

    attr_name = 'frameRangeStart'
    if attr_name not in all_attrs:
        plug_name = node + '.' + attr_name
        maya.cmds.addAttr(
            node,
            longName=attr_name,
            attributeType='double',
        )
        maya.cmds.setAttr(plug_name, keyable=keyable)
        maya.cmds.setAttr(plug_name, start_frame)

    attr_name = 'frameRangeEnd'
    if attr_name not in all_attrs:
        plug_name = node + '.' + attr_name
        maya.cmds.addAttr(
            node,
            longName=attr_name,
            attributeType='double',
        )
        maya.cmds.setAttr(plug_name, keyable=keyable)
        maya.cmds.setAttr(plug_name, end_frame)

    attr_name = 'increment'
    if attr_name not in all_attrs:
        plug_name = node + '.' + attr_name
        maya.cmds.addAttr(
            node,
            longName=attr_name,
            attributeType='double',
            minValue=0.02,
        )
        maya.cmds.setAttr(plug_name, keyable=keyable)
        maya.cmds.setAttr(plug_name, post_frame)
    return


def create_motion_trail_setup(node_tfm,
                              trail_handle_grp,
                              name,
                              use_frame_range,
                              start_frame,
                              end_frame,
                              pre_frame,
                              post_frame,
                              increment,
                              update_mode):
    handle_tfm, trail_shp = maya.cmds.snapshot(
        node_tfm,
        name=name,
        constructionHistory=True,
        motionTrail=True,
        startTime=start_frame,
        endTime=end_frame,
        increment=increment,
        update=update_mode,
    )
    handle_shp = maya.cmds.listRelatives(
        handle_tfm,
        shapes=True,
        fullPath=True,
        type='motionTrailShape',
    )[0]

    # Create attributes on trail node, hidden to the channel box.
    _create_trail_frame_attrs(
        trail_shp,
        use_frame_range,
        start_frame,
        end_frame,
        pre_frame,
        post_frame,
        increment,
        keyable=False)

    # Create attributes on handle transform node, visible to the
    # channel box.
    _create_trail_frame_attrs(
        handle_tfm,
        use_frame_range,
        start_frame,
        end_frame,
        pre_frame,
        post_frame,
        increment,
        keyable=True)

    # Drive trail_shp by attributes on handle_tfm
    attr_names = [
        'useFrameRange',
        'preFrame',
        'postFrame',
        'frameRangeStart',
        'frameRangeEnd',
        'increment',
    ]
    for attr_name in attr_names:
        src = handle_tfm + '.' + attr_name
        dst = trail_shp + '.' + attr_name
        maya.cmds.connectAttr(src, dst)

    # Re-parent to the camera, so the user can see it.
    handle_tfm = maya.cmds.parent(
        handle_tfm, trail_handle_grp,
        relative=True
    )[0]
    handle_tfm = node_utils.get_long_name(handle_tfm)

    # Create Expression to control the calculated trail frame range.
    cmd = (
        'if (useFrameRange) {'
        '    startTime = frameRangeStart;'
        '    endTime = frameRangeEnd;'
        '} else {'
        '    startTime = frame - preFrame;'
        '    endTime = frame + postFrame;'
        '}'
    )
    maya.cmds.expression(object=trail_shp, string=cmd)
    return handle_tfm, handle_shp, trail_shp


def create_screen_space_motion_trail(cam, tfm,
                                     name=None,
                                     use_frame_range=None,
                                     pre_frame=None,
                                     post_frame=None,
                                     start_frame=None,
                                     end_frame=None,
                                     increment=None):
    """
    Create a Screen-Space Maya Locator that may be solved in Screen XYZ.
    """
    assert isinstance(cam, pycompat.TEXT_TYPE)
    assert isinstance(tfm, pycompat.TEXT_TYPE)
    if name is None:
        name = tfm.rpartition('|')[-1]

    frame_range = time_utils.get_maya_timeline_range_inner()
    if use_frame_range is None:
        use_frame_range = const.USE_FRAME_RANGE_DEFAULT
    if pre_frame is None:
        pre_frame = const.PRE_FRAME_DEFAULT
    if post_frame is None:
        post_frame = const.POST_FRAME_DEFAULT
    if start_frame is None:
        start_frame = frame_range.start
    if end_frame is None:
        end_frame = frame_range.end
    if increment is None:
        if use_frame_range:
            increment = const.FRAME_RANGE_INCREMENT_DEFAULT
        else:
            increment = const.PER_FRAME_INCREMENT_DEFAULT

    tfm_attrs = [
        'translateX', 'translateY', 'translateZ',
        'rotateX', 'rotateY', 'rotateZ',
        'scaleX', 'scaleY', 'scaleZ'
    ]

    maya.cmds.loadPlugin('matrixNodes', quiet=True)
    cam_tfm, cam_shp = camera_utils.get_camera(cam)

    # Create temporary group
    temp_grp_name = const.TEMP_OBJECT_NAME
    temp_grp = temp_grp_name
    if not maya.cmds.objExists(temp_grp):
        temp_grp = maya.cmds.createNode('transform', name=temp_grp_name)
        maya.cmds.setAttr(temp_grp + '.visibility', False)

    # Create Temporary transform node to calculate motion path on.
    temp_tfm_name = name + '_TEMP_NULL'
    temp_tfm_name = mmapi.find_valid_maya_node_name(temp_tfm_name)
    temp_tfm = maya.cmds.createNode(
        'transform',
        parent=temp_grp,
        name=temp_tfm_name
    )

    # Create trail group under the camera.
    trail_handle_grp_name = const.MOTION_PATH_GROUP_NAME
    trail_handle_grp = cam_tfm + '|' + trail_handle_grp_name
    if not maya.cmds.objExists(trail_handle_grp):
        trail_handle_grp = maya.cmds.createNode(
            'transform',
            name=trail_handle_grp_name,
            parent=cam_tfm
        )
        # Trails are non-selectable by default.
        plug_name = trail_handle_grp + '.template'
        maya.cmds.setAttr(plug_name, True)

        # Lock transform attributes.
        for attr in tfm_attrs:
            plug_name = trail_handle_grp + '.' + attr
            maya.cmds.setAttr(plug_name, lock=True)

    # Matrix Multiply
    mult_mat = maya.cmds.createNode('multMatrix')
    src = tfm + '.worldMatrix[0]'
    dst = mult_mat + '.matrixIn[0]'
    maya.cmds.connectAttr(src, dst)

    src = cam_tfm + '.worldInverseMatrix[0]'
    dst = mult_mat + '.matrixIn[1]'
    maya.cmds.connectAttr(src, dst)

    # Decompose Matrix
    decompose = maya.cmds.createNode('decomposeMatrix')
    src = mult_mat + '.matrixSum'
    dst = decompose + '.inputMatrix'
    maya.cmds.connectAttr(src, dst)

    src = decompose + '.outputTranslate'
    dst = temp_tfm + '.translate'
    maya.cmds.connectAttr(src, dst)

    # Lock the temporary transform node.
    for attr in tfm_attrs:
        plug_name = temp_tfm + '.' + attr
        maya.cmds.setAttr(plug_name, lock=True)

    # Create Motion Trail
    update_mode = 'always'
    handle_tfm, handle_shp, trail_shp = create_motion_trail_setup(
        temp_tfm,
        trail_handle_grp,
        name,
        use_frame_range,
        start_frame,
        end_frame,
        pre_frame,
        post_frame,
        increment,
        update_mode,
    )
    return handle_tfm, handle_shp, trail_shp
