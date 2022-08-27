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
Line.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.OpenMaya as OpenMaya
import maya.cmds

import mmSolver.logger
import mmSolver.utils.event as event_utils
import mmSolver.utils.node as node_utils
import mmSolver.utils.time as time_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver._api.constant as const
import mmSolver._api.utils as api_utils
import mmSolver._api.excep as excep
import mmSolver._api.marker as marker
import mmSolver._api.bundle as bundle
import mmSolver._api.camera as camera
import mmSolver._api.naming as naming
import mmSolver._api.markergroup as markergroup


DEFAULT_MARKER_NAME = 'marker1'
DEFAULT_BUNDLE_NAME = 'bundle1'
LOG = mmSolver.logger.get_logger()


def _create_line_transform(name):
    tfm = maya.cmds.createNode(const.LINE_TRANSFORM_NODE_TYPE, name=name)
    tfm = node_utils.get_long_name(tfm)
    maya.cmds.setAttr(tfm + '.tx', lock=True)
    maya.cmds.setAttr(tfm + '.ty', lock=True)
    maya.cmds.setAttr(tfm + '.tz', lock=True)
    maya.cmds.setAttr(tfm + '.rx', lock=True)
    maya.cmds.setAttr(tfm + '.ry', lock=True)
    maya.cmds.setAttr(tfm + '.rz', lock=True)
    maya.cmds.setAttr(tfm + '.sx', lock=True)
    maya.cmds.setAttr(tfm + '.sy', lock=True)
    maya.cmds.setAttr(tfm + '.sz', lock=True)
    maya.cmds.setAttr(tfm + '.shxy', lock=True)
    maya.cmds.setAttr(tfm + '.shxz', lock=True)
    maya.cmds.setAttr(tfm + '.shyz', lock=True)
    maya.cmds.setAttr(tfm + '.tx', keyable=False, channelBox=False)
    maya.cmds.setAttr(tfm + '.ty', keyable=False, channelBox=False)
    maya.cmds.setAttr(tfm + '.tz', keyable=False, channelBox=False)
    maya.cmds.setAttr(tfm + '.rx', keyable=False, channelBox=False)
    maya.cmds.setAttr(tfm + '.ry', keyable=False, channelBox=False)
    maya.cmds.setAttr(tfm + '.rz', keyable=False, channelBox=False)
    maya.cmds.setAttr(tfm + '.sx', keyable=False, channelBox=False)
    maya.cmds.setAttr(tfm + '.sy', keyable=False, channelBox=False)
    maya.cmds.setAttr(tfm + '.sz', keyable=False, channelBox=False)
    maya.cmds.setAttr(tfm + '.shxy', keyable=False, channelBox=False)
    maya.cmds.setAttr(tfm + '.shxz', keyable=False, channelBox=False)
    maya.cmds.setAttr(tfm + '.shyz', keyable=False, channelBox=False)
    return tfm


def _create_line_shape(tfm_node):
    shp_name = tfm_node.rpartition('|')[-1] + 'Shape'
    shp = maya.cmds.createNode(
        const.LINE_SHAPE_NODE_TYPE, name=shp_name, parent=tfm_node
    )
    maya.cmds.setAttr(shp + '.localPositionX', channelBox=False)
    maya.cmds.setAttr(shp + '.localPositionY', channelBox=False)
    maya.cmds.setAttr(shp + '.localPositionZ', channelBox=False)
    maya.cmds.setAttr(shp + '.localScaleX', channelBox=False)
    maya.cmds.setAttr(shp + '.localScaleY', channelBox=False)
    maya.cmds.setAttr(shp + '.localScaleZ', channelBox=False)
    return shp


def _create_line_attributes(node):
    """
    Create the attributes expected to be on a Line.

    :param node: Transform node for the Line.
    :type node: str
    """
    attr = const.LINE_ATTR_LONG_NAME_ENABLE
    if not node_utils.attribute_exists(attr, node):
        maya.cmds.addAttr(
            node,
            longName=attr,
            attributeType='short',
            minValue=0,
            maxValue=1,
            defaultValue=1,
            keyable=True,
        )

    attr = const.LINE_ATTR_LONG_NAME_WEIGHT
    if not node_utils.attribute_exists(attr, node):
        maya.cmds.addAttr(
            node,
            longName=attr,
            attributeType='double',
            minValue=0.0,
            defaultValue=1.0,
            keyable=True,
        )
    return


def _create_intersect_node(shp, mkr_node, bnd_node):
    intersect_node = maya.cmds.createNode(const.LINE_POINT_INTERSECT_NODE_TYPE)

    for axis in ['X', 'Y']:
        src_a = shp + '.outLinePointA' + axis
        src_b = shp + '.outLinePointB' + axis
        dst_a = intersect_node + '.linePointA' + axis
        dst_b = intersect_node + '.linePointB' + axis
        maya.cmds.connectAttr(src_a, dst_a)
        maya.cmds.connectAttr(src_b, dst_b)

    src_a = intersect_node + '.linePointAZ'
    src_b = intersect_node + '.linePointBZ'
    maya.cmds.setAttr(src_a, -1.0)
    maya.cmds.setAttr(src_b, -1.0)

    for axis in ['X', 'Y', 'Z']:
        src = mkr_node + '.translate' + axis
        dst = intersect_node + '.inPoint' + axis
        maya.cmds.connectAttr(src, dst)

    for axis in ['X', 'Y', 'Z']:
        src = intersect_node + '.outPoint' + axis
        dst = bnd_node + '.translate' + axis
        maya.cmds.connectAttr(src, dst)

    return intersect_node


def create_default_markers(line_shp, mkr_grp):
    mkr_name_a = naming.get_new_marker_name(DEFAULT_MARKER_NAME)
    bnd_name_a = naming.get_new_bundle_name(DEFAULT_BUNDLE_NAME)
    bnd_a = bundle.Bundle().create_node(name=bnd_name_a)
    mkr_a = marker.Marker().create_node(mkr_grp=mkr_grp, name=mkr_name_a, bnd=bnd_a)

    mkr_name_b = naming.get_new_marker_name(DEFAULT_MARKER_NAME)
    bnd_name_b = naming.get_new_bundle_name(DEFAULT_BUNDLE_NAME)
    bnd_b = bundle.Bundle().create_node(name=bnd_name_b)
    mkr_b = marker.Marker().create_node(mkr_grp=mkr_grp, name=mkr_name_b, bnd=bnd_b)

    mkr_node_a = mkr_a.get_node()
    mkr_node_b = mkr_b.get_node()
    bnd_node_a = bnd_a.get_node()
    bnd_node_b = bnd_b.get_node()

    maya.cmds.setAttr(mkr_node_a + '.tx', -0.25)
    maya.cmds.setAttr(mkr_node_b + '.tx', 0.25)
    maya.cmds.setAttr(mkr_node_a + '.ty', -0.15)
    maya.cmds.setAttr(mkr_node_b + '.ty', 0.15)

    maya.cmds.setAttr(bnd_node_a + '.visibility', 0)
    maya.cmds.setAttr(bnd_node_b + '.visibility', 0)

    src_a = mkr_node_a + '.message'
    src_b = mkr_node_b + '.message'
    dst = line_shp + '.objects'
    if not maya.cmds.isConnected(src_a, dst):
        maya.cmds.connectAttr(src_a, dst, nextAvailable=True)
    if not maya.cmds.isConnected(src_b, dst):
        maya.cmds.connectAttr(src_b, dst, nextAvailable=True)

    src_a = mkr_node_a + '.worldMatrix[0]'
    src_b = mkr_node_b + '.worldMatrix[0]'
    dst_a = line_shp + '.transformMatrix[0]'
    dst_b = line_shp + '.transformMatrix[1]'
    if not maya.cmds.isConnected(src_a, dst_a):
        maya.cmds.connectAttr(src_a, dst_a)
    if not maya.cmds.isConnected(src_b, dst_b):
        maya.cmds.connectAttr(src_b, dst_b)

    src = line_shp + '.parentInverseMatrix[0]'
    dst = line_shp + '.transformParentInverseMatrix'
    if not maya.cmds.isConnected(src, dst):
        maya.cmds.connectAttr(src, dst)

    intersect_a = _create_intersect_node(line_shp, mkr_node_a, bnd_node_a)
    intersect_b = _create_intersect_node(line_shp, mkr_node_b, bnd_node_b)

    return mkr_a, bnd_a, mkr_b, bnd_b


def create_new_line_marker(line_tfm, line_shp, mkr_grp):
    mkr_new_name = naming.get_new_marker_name(DEFAULT_MARKER_NAME)
    bnd_new_name = naming.get_new_bundle_name(DEFAULT_BUNDLE_NAME)
    bnd_new = bundle.Bundle().create_node(name=mkr_new_name)
    mkr_new = marker.Marker().create_node(
        mkr_grp=mkr_grp, name=mkr_new_name, bnd=bnd_new
    )

    mkr_node_b = mkr_new.get_node()
    bnd_node_b = bnd_new.get_node()

    maya.cmds.setAttr(bnd_node_b + '.visibility', 0)

    _create_intersect_node(line_shp, mkr_node_b, bnd_node_b)

    return mkr_new, bnd_new


class Line(object):
    """
    The 2D Line object.

    A Line defines a wrapper around a Maya node that contains 2D
    information, in a camera's screen-space.

    Example usage::

        >>> line = mmapi.Line(node='myNode')
        >>> line.get_node()
        '|myNode'
        >>> cam = mmapi.Camera().create_node(name='myCamera1')
        >>> line = mmapi.Line().create_node(name='myLine1', cam=cam)
        >>> line.get_node()
        '|myLine1'

    """

    def __init__(self, node=None):
        """
        Initialize a Line, give a name to connect to an existing Maya node.

        :param node: The Maya node to connect to.
        :type node: None or str
        """
        if isinstance(node, pycompat.TEXT_TYPE):
            try:
                dag = node_utils.get_as_dag_path(node)
                self._mfn = OpenMaya.MFnDagNode(dag)
            except RuntimeError as e:
                msg = 'Given Line node name is invalid: name=%r'
                LOG.error(msg, node)
                raise e

            # Ensure the deviation attribute exists.
            self.add_attributes()
        else:
            self._mfn = OpenMaya.MFnDagNode()
        return

    def __repr__(self):
        result = '<{class_name}('.format(class_name=self.__class__.__name__)
        result += '{hash} node={node}'.format(
            hash=hex(hash(self)),
            node=self.get_node(),
        )
        result += ')>'
        return result

    def get_node(self):
        """
        Get the Maya node this object is bound to.

        :return: The node this Line object is bound to, or None.
        :rtype: None or str or unicode
        """
        node = None
        try:
            obj = self._mfn.object()
        except RuntimeError:
            obj = None
        if obj is not None and obj.isNull() is False:
            try:
                node = self._mfn.fullPathName()
            except RuntimeError:
                pass
        if isinstance(node, pycompat.TEXT_TYPE) and len(node) == 0:
            node = None
        return node

    def set_node(self, node):
        """
        Change the underlying Maya node that this Line class will manipulate.

        :param node: The existing Maya node.
        :type node: str
        """
        assert isinstance(node, pycompat.TEXT_TYPE)
        dag = node_utils.get_as_dag_path(node)
        try:
            self._mfn = OpenMaya.MFnDagNode(dag)
        except RuntimeError:
            raise

        # Ensure the deviation attribute exists.
        self.add_attributes()
        return

    def get_node_uid(self):
        """
        Get the line transform unique identifier.

        :return: The line UUID or None
        :rtype: None or str or unicode
        """
        node = self.get_node()
        if node is None:
            LOG.warn('Could not get Line node. self=%r', self)
            return None
        uids = maya.cmds.ls(node, uuid=True) or []
        return uids[0]

    def _get_shape_node(self):
        """
        Parent a line under a Marker Group.
        """
        tfm = self.get_node()
        if tfm is None:
            return
        shps = (
            maya.cmds.listRelatives(tfm, shapes=True, type=const.LINE_SHAPE_NODE_TYPE)
            or []
        )
        shp = None
        if len(shps) > 0:
            shp = shps[0]
        return shp

    ############################################################################

    def create_node(self, name='line1', colour=None, cam=None, mkr_grp=None):
        """
        Create a line node network from scratch.

        :param name: Name of the line to create.
        :type name: str

        :param colour: Colour of line as R, G and B.
                       'None' will leave as default.
        :type colour: (float, float, float) or None

        :param cam: The camera to create the line underneath.
        :type cam: Camera

        :param mkr_grp: The marker group to create the line underneath.
        :type mkr_grp: MarkerGroup

        :return: Line object with newly created node.
        :rtype: Line
        """
        assert isinstance(name, pycompat.TEXT_TYPE)
        if cam is not None:
            if mkr_grp is not None:
                msg = 'Cannot specify both camera and marker group, '
                msg += 'please choose only one.'
                raise excep.NotValid(msg)
            assert isinstance(cam, camera.Camera)
        if mkr_grp is not None:
            if cam is not None:
                msg = 'Cannot specify both camera and marker group, '
                msg += 'please choose only one.'
                raise excep.NotValid(msg)
            assert isinstance(mkr_grp, markergroup.MarkerGroup)
        if colour is not None:
            assert isinstance(colour, (tuple, list))
            assert len(colour) == 3

        # Transform
        tfm = _create_line_transform(name)

        # Shape Node
        shp = _create_line_shape(tfm)

        # Make the line non-selectable in the viewport.
        display_type = 2  # 2 = Reference
        maya.cmds.setAttr(shp + '.overrideEnabled', 1)
        maya.cmds.setAttr(shp + '.overrideDisplayType', display_type)

        # Add attrs
        _create_line_attributes(tfm)

        src = '{0}.{1}'.format(tfm, const.LINE_ATTR_LONG_NAME_ENABLE)
        dst = '{0}.{1}'.format(tfm, 'lodVisibility')
        maya.cmds.connectAttr(src, dst)

        # Create two Markers.
        mkr_a, bnd_a, mkr_b, bnd_b = create_default_markers(shp, mkr_grp)
        mkr_node_a = mkr_a.get_node()
        mkr_node_b = mkr_b.get_node()
        bnd_node_a = bnd_a.get_node()
        bnd_node_b = bnd_b.get_node()

        maya.cmds.parent(mkr_node_a, tfm, relative=True)
        maya.cmds.parent(bnd_node_a, tfm, relative=True)
        maya.cmds.parent(mkr_node_b, tfm, relative=True)
        maya.cmds.parent(bnd_node_b, tfm, relative=True)
        self.set_node(tfm)

        # Set Colour (default is magenta)
        if colour is not None:
            self.set_colour_rgb(colour)
        else:
            magenta = (1.0, 0.0, 1.0)
            self.set_colour_rgb(magenta)

        # Link to Camera
        if cam is not None:
            self.set_camera(cam)

        # Link to MarkerGroup
        if mkr_grp is not None:
            self.set_marker_group(mkr_grp)

        event_utils.trigger_event(const.EVENT_NAME_LINE_CREATED, line=self)
        return self

    def delete_node(self):
        """
        Remove the Maya node (and all data) of this Line object.

        :return: This Line object, with Maya node removed.
        :rtype: Line
        """
        node = self.get_node()
        if node is None:
            LOG.warn('Could not get Line node. self=%r', self)
            return self
        maya.cmds.delete(node)
        return self

    def add_attributes(self):
        """
        Add dynamic attributes to line.
        """
        tfm = self.get_node()
        if tfm is not None:
            _create_line_attributes(tfm)
        return

    ############################################################################

    def get_enable(self, time=None):
        """
        Get the enabled state of the Line.

        :param time: The time to query the enable, if not given the
                      current frame is used.
        :type time: float

        :returns: The enabled state of the line.
        :rtype: int
        """
        node = self.get_node()
        if node is None:
            LOG.warn('Could not get Line node. self=%r', self)
            return None
        plug = '{0}.{1}'.format(node, const.LINE_ATTR_LONG_NAME_ENABLE)
        if time is None:
            v = maya.cmds.getAttr(plug)
        else:
            v = maya.cmds.getAttr(plug, time=time)
        return v

    def get_enabled_frames(self, frame_range_start=None, frame_range_end=None):
        """
        Get the list of frames that this Line is enabled.

        If there is no animation curve on a Line we use the
        frame_range_start and frame_range_end arguments to determine
        the enabled frame list. If these frame_range_* arguments are
        not given the default Maya outer timeline range is used.

        :param frame_range_start: The frame range start of the line
                                  to consider when no animCurve exists.
        :type frame_range_start: int

        :param frame_range_end: The frame range end of the line
                                to consider when no animCurve exists.
        :type frame_range_end: int

        :returns: The enabled frame numbers of the line.
        :rtype: [int, ..]
        """
        start_frame, end_frame = time_utils.get_maya_timeline_range_outer()
        if frame_range_start is None:
            frame_range_start = start_frame
        if frame_range_end is None:
            frame_range_end = end_frame

        times = []
        node = self.get_node()
        if node is None:
            LOG.warn('Could not get node. self=%r', self)
            return times
        plug = '{0}.{1}'.format(node, const.LINE_ATTR_LONG_NAME_ENABLE)

        anim_curves = maya.cmds.listConnections(plug, type='animCurve') or []
        if len(anim_curves) == 0:
            enable_times = list(range(frame_range_start, frame_range_end + 1))
        else:
            anim_curve = anim_curves[0]
            enable_times = (
                maya.cmds.keyframe(anim_curve, query=True, timeChange=True) or []
            )
            if len(enable_times) == 0:
                enable_times = list(range(frame_range_start, frame_range_end + 1))

        start_frame = int(min(enable_times))
        end_frame = int(max(enable_times))
        for f in range(start_frame, end_frame + 1):
            v = self.get_enable(time=f)
            if v:
                times.append(f)
        return times

    def get_weight(self, time=None):
        """
        Get the current wire-frame colour of the Line.

        :param time: The time to query the weight, if not given the
                     current frame is used.
        :type time: float

        :returns: The weight of the line.
        :rtype: float
        """
        node = self.get_node()
        if node is None:
            LOG.warn('Could not get Line node. self=%r', self)
            return None
        plug = '{0}.{1}'.format(node, const.LINE_ATTR_LONG_NAME_WEIGHT)
        if time is None:
            v = maya.cmds.getAttr(plug)
        else:
            v = maya.cmds.getAttr(plug, time=time)
        return v

    def _get_enabled_solved_frames(self, frame_range_start=None, frame_range_end=None):
        """
        Calculate the frames that are both solved and enabled.
        """
        enable_frames_set = set(self.get_enabled_frames())
        if len(enable_frames_set) == 0:
            enable_frames_set = set([maya.cmds.currentTime(query=True)])

        dev_frames_set = set(
            self.get_deviation_frames(
                frame_range_start=frame_range_start, frame_range_end=frame_range_end
            )
        )
        frames = list(enable_frames_set.intersection(dev_frames_set))
        return frames

    def get_colour_rgb(self):
        """
        Get the current wire-frame colour of the Line.

        :returns: Tuple of red, green and blue, or None if colour
                  cannot be found.
        :rtype: (float, float, float) or None
        """
        node = self.get_node()
        if node is None:
            LOG.warn('Could not get Line node. self=%r', self)
            return None
        shps = maya.cmds.listRelatives(node, shapes=True, fullPath=True) or []
        if len(shps) == 0:
            LOG.warn('Could not find shape to get colour. node=%r shps=%r', node, shps)
            return
        shp = shps[0]
        v = node_utils.get_node_wire_colour_rgb(shp)
        return v

    def set_colour_rgb(self, rgb):
        """
        Change the Wireframe colour of the Line.

        :param rgb: Colour as R, G, B; Or None to reset to default colour.
        :type rgb: tuple
        """
        assert rgb is None or isinstance(rgb, (tuple, list))
        node = self.get_node()
        if node is None:
            LOG.warn('Could not get Line node. self=%r', self)
            return
        shps = maya.cmds.listRelatives(node, shapes=True, fullPath=True) or []
        if len(shps) == 0:
            LOG.warn('Could not find shape to set colour. node=%r shps=%r', node, shps)
            return
        shp = shps[0]
        node_utils.set_node_wire_colour_rgb(shp, rgb)
        return

    ############################################################################

    def get_camera(self):
        """
        Get the camera connected implicitly with the Line.

        :returns: Camera object, or None if Line does not have a
                  Camera (for example it's unparented to world).
        :rtype: None or Camera
        """
        mkr_node = self.get_node()
        if mkr_node is None:
            LOG.warn('Could not get Line node. self=%r', self)
            return None

        cam_tfm, cam_shp = node_utils.get_camera_above_node(mkr_node)

        # Make the camera object.
        cam = None
        if cam_tfm is not None and cam_shp is not None:
            cam = camera.Camera(transform=cam_tfm, shape=cam_shp)
        return cam

    def set_camera(self, cam):
        """
        Connect this Line to the given camera.

        Connecting Lines to cameras happens by parenting a Line
        under a Camera's Line Group.

        .. note:: If the `cam` argument is None, the Line is
            disconnected from any camera.

        :param cam: The camera to connect this Line to.
        :type cam: None or Camera

        :returns: None
        """
        if cam is None:
            self._unlink_from_camera()
        elif isinstance(cam, camera.Camera):
            self._link_to_camera(cam)
        return

    def _link_to_camera(self, cam):
        """
        Parent a line under the line group which is under the given camera.
        If there is no line group, one is created.

        :param cam: The camera to connect this Line to.
        :type cam: None or Camera

        :returns: None
        """
        assert isinstance(cam, camera.Camera)

        mkr_node = self.get_node()
        if mkr_node is None:
            LOG.warn('Could not get Line node. self=%r', self)
            return
        cam_tfm = cam.get_transform_node()
        cam_shp = cam.get_shape_node()

        # Make sure the camera is valid for us to link to.
        if cam.is_valid() is False:
            msg = 'Cannot link Line to Camera; Camera is not valid.'
            msg += ' line={0} camera={1}'
            msg = msg.format(repr(mkr_node), repr(cam_shp))
            raise excep.NotValid(msg)

        # Check if we're trying to link the the camera that we're already
        # linked to.
        current_cam = self.get_camera()
        if current_cam is not None:
            assert isinstance(current_cam, camera.Camera)
            current_cam_shp = current_cam.get_shape_node()
            if current_cam_shp == cam_shp:
                msg = 'Line is already linked to camera, skipping.'
                msg += ' line={0} camera={1}'
                msg = msg.format(repr(mkr_node), repr(cam_shp))
                raise excep.AlreadyLinked(msg)

        # Create Line Group
        mkr_grp = None
        mkr_grp_nodes = (
            maya.cmds.ls(cam_tfm, dag=True, long=True, type='mmMarkerGroupTransform')
            or []
        )
        mkr_grp_nodes = sorted(mkr_grp_nodes)
        if len(mkr_grp_nodes) == 0:
            mkr_grp = markergroup.MarkerGroup().create_node(cam=cam)
        else:
            mkr_grp = markergroup.MarkerGroup(node=mkr_grp_nodes[0])

        # Link to Line Group
        self.set_marker_group(mkr_grp)
        return

    def _unlink_from_camera(self):
        """
        Re-parent the current line to the world; it will live under no camera.

        :returns: None
        """
        mkr_node = self.get_node()
        if mkr_node is None:
            LOG.warn('Could not get Line node. self=%r', self)
            return
        cam = self.get_camera()
        cam_tfm = cam.get_transform_node()
        cam_shp = cam.get_shape_node()
        if (
            (cam_tfm is None)
            or (cam_shp is None)
            or (maya.cmds.objExists(cam_tfm) is False)
            or (maya.cmds.objExists(cam_shp) is False)
        ):
            msg = 'Line is already unlinked from all cameras, skipping.'
            msg += ' line={0} camera={1}'
            msg = msg.format(repr(mkr_node), repr(cam_shp))
            raise excep.AlreadyUnlinked(msg)

        # Move the line under the world root, don't modify the line in
        # any way otherwise (so we use 'relative' flag).
        maya.cmds.parent(mkr_node, relative=True, world=True)
        return

    ############################################################################

    def get_marker_group(self):
        """
        Get the marker group that implicitly connected to this Line.

        :returns: Marker group object.
        :rtype: MarkerGroup or None
        """
        mkr_node = self.get_node()
        if mkr_node is None:
            LOG.warn('Could not get Line node. self=%r', self)
            return

        mkr_grp_node = api_utils.get_marker_group_above_node(mkr_node)

        # Make the marker group object.
        mkr_grp = None
        if mkr_grp_node is not None:
            mkr_grp = markergroup.MarkerGroup(node=mkr_grp_node)
        return mkr_grp

    def set_marker_group(self, mkr_grp):
        """
        Set the MarkerGroup for this Line, or None to unlink the Line.

        :param mkr_grp: Marker group object to link to this Line.
        :type mkr_grp: MarkerGroup or None
        """
        if mkr_grp is None:
            self._unlink_from_marker_group()
        elif isinstance(mkr_grp, markergroup.MarkerGroup):
            self._link_to_marker_group(mkr_grp)
        return

    def _link_to_marker_group(self, mkr_grp):
        """
        Parent a line under a Marker Group.
        """
        assert isinstance(mkr_grp, markergroup.MarkerGroup)

        mkr_node = self.get_node()
        if mkr_node is None:
            LOG.warn('Could not get Line node. self=%r', self)
            return
        mkr_grp_node = mkr_grp.get_node()

        # Make sure the camera is valid for us to link to.
        if mkr_grp.is_valid() is False:
            msg = 'Cannot link Line to Marker Group; Marker Group is not valid.'
            msg += ' line={0} marker group={1}'
            msg = msg.format(repr(mkr_node), repr(mkr_grp_node))
            raise excep.NotValid(msg)

        # Check if we're trying to link the the camera that we're already
        # linked to.
        current_mkr_grp = self.get_marker_group()
        if current_mkr_grp is not None:
            assert isinstance(current_mkr_grp, markergroup.MarkerGroup)
            current_mkr_grp = current_mkr_grp.get_node()
            if current_mkr_grp == mkr_grp_node:
                msg = 'Line is already linked to Marker Group, skipping.'
                msg += ' line={0} marker group={1}'
                msg = msg.format(repr(mkr_node), repr(mkr_grp_node))
                raise excep.AlreadyLinked(msg)

        # Move the line under the marker group, make sure the relative
        # line attribute values are maintained.
        maya.cmds.parent(mkr_node, mkr_grp_node, relative=True)
        return

    def _unlink_from_marker_group(self):
        """
        Re-parent the current marker to the world; it will live under no
        """
        mkr_node = self.get_node()
        if mkr_node is None:
            LOG.warn('Could not get Line node. self=%r', self)
            return
        cam = self.get_camera()
        cam_tfm = cam.get_transform_node()
        cam_shp = cam.get_shape_node()
        if (
            (cam_tfm is None)
            or (cam_shp is None)
            or (maya.cmds.objExists(cam_tfm) is False)
            or (maya.cmds.objExists(cam_shp) is False)
        ):
            msg = 'Line is already unlinked from all cameras, skipping.'
            msg += ' line={0} camera={1}'
            msg = msg.format(repr(mkr_node), repr(cam_shp))
            raise excep.AlreadyUnlinked(msg)

        # Move the line under the world root, don't modify the line in
        # any way otherwise.
        maya.cmds.parent(mkr_node, relative=True, world=True)
        return

    ############################################################################

    def get_marker_list(self):
        """
        Get the markers connected implicitly with the Line.

        :returns: Marker objects, or empty list if Line does not have
            any Markers connected.
        :rtype: List of Markers
        """
        line_node = self.get_node()
        if line_node is None:
            LOG.warn('Could not get Line node. self=%r', self)
            return None

        shp = self._get_shape_node()
        if shp is None:
            return []

        node_attr = shp + '.objects'
        conns = (
            maya.cmds.listConnections(
                node_attr,
                source=True,
                destination=False,
                connections=True,
                plugs=True,
                type=const.MARKER_TRANSFORM_NODE_TYPE,
            )
            or []
        )
        conns += (
            maya.cmds.listConnections(
                node_attr,
                source=True,
                destination=False,
                connections=True,
                plugs=True,
                type=const.MARKER_TRANSFORM_OLD_NODE_TYPE,
            )
            or []
        )

        # Sorts the markers based on the .objects attribute
        # element index.
        if len(conns) == 0:
            return []
        num_conns = int(len(conns) * 0.5)
        mkr_nodes = []
        for i in range(num_conns):
            src_idx = i * 2
            dst_idx = src_idx + 1
            src = conns[src_idx]
            dst = conns[dst_idx]
            name = src + '#' + dst
            mkr_nodes.append(name)
        mkr_nodes = sorted(set(mkr_nodes))
        mkr_nodes = [x.split('#')[-1] for x in mkr_nodes]
        mkr_nodes = [x.split('.')[0] for x in mkr_nodes]

        mkr_list = [marker.Marker(node=mkr_node) for mkr_node in mkr_nodes]
        return mkr_list

    def _clear_marker_list(self, shp):
        attr_names = ['objects', 'transformMatrix']
        for attr_name in attr_names:
            node_attr = shp + '.' + attr_name
            prev_mkr_node_list = (
                maya.cmds.listConnections(
                    node_attr,
                    source=True,
                    destination=False,
                    plugs=False,
                    type=const.MARKER_TRANSFORM_NODE_TYPE,
                )
                or []
            )
            prev_mkr_node_list += (
                maya.cmds.listConnections(
                    node_attr,
                    source=True,
                    destination=False,
                    plugs=False,
                    type=const.MARKER_TRANSFORM_OLD_NODE_TYPE,
                )
                or []
            )

        for i, prev_mkr_node in enumerate(prev_mkr_node_list):
            src = prev_mkr_node + '.message'
            dst = shp + '.objects[{}]'.format(i)
            if maya.cmds.isConnected(src, dst):
                maya.cmds.disconnectAttr(src, dst)

            src = prev_mkr_node + '.worldMatrix[0]'
            dst = shp + '.transformMatrix[{}]'.format(i)
            if maya.cmds.isConnected(src, dst):
                maya.cmds.disconnectAttr(src, dst)

    def set_marker_list(self, mkr_list):
        """
        Connect this Line to the given marker.

        Connecting Lines to markers happens by parenting a Line
        under a Marker's Line Group.

        .. note:: If the `cam` argument is None, the Line is
            disconnected from any marker.

        :param cam: The marker to connect this Line to.
        :type cam: None or Marker

        :returns: None
        """
        line_tfm = self.get_node()
        line_shp = self._get_shape_node()
        if line_shp is None:
            return

        self._clear_marker_list(line_shp)

        for i, mkr in enumerate(mkr_list):
            mkr_node = mkr.get_node()
            src_a = mkr_node + '.message'
            src_b = mkr_node + '.worldMatrix[0]'

            dst_a = line_shp + '.objects[{}]'.format(i)
            dst_b = line_shp + '.transformMatrix[{}]'.format(i)
            if not maya.cmds.isConnected(src_a, dst_a):
                maya.cmds.connectAttr(src_a, dst_a)
                maya.cmds.connectAttr(src_b, dst_b)
        return

    def get_marker_point_intersect(self, mkr):
        """
        Get the mmLinePointIntersect node connected to the given Marker,
        or return None.

        :rtype: str
        """
        mkr_node = mkr.get_node()
        if mkr_node is None:
            return None
        plug = mkr_node + '.translateX'
        nodes = maya.cmds.listConnections(plug, type='mmLinePointIntersect') or []
        if len(nodes) == 0:
            return None
        return nodes[0]
