# Copyright (C) 2018, 2019 David Cattermole.
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
Marker and the related objects, Camera and Bundle.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.cmds

import mmSolver.logger
import mmSolver.utils.event as event_utils
import mmSolver.utils.node as node_utils
import mmSolver.utils.animcurve as anim_utils
import mmSolver.utils.time as time_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver._api.constant as const
import mmSolver._api.utils as api_utils
import mmSolver._api.excep as excep
import mmSolver._api.bundle
import mmSolver._api.camera as camera
import mmSolver._api.markergroup as markergroup
import mmSolver._api.markerutils as markerutils
import mmSolver._api.solveresult as solveresult


LOG = mmSolver.logger.get_logger()


def _disconnect_camera_lens_from_marker(mkr_tfm):
    exists = node_utils.attribute_exists('inLens', mkr_tfm)
    if exists is False:
        return

    attr = mkr_tfm + '.inLens'
    conns = (
        maya.cmds.listConnections(
            attr, connections=True, plugs=True, source=True, destination=False
        )
        or []
    )
    for conn_src, conn_dst in zip(conns[0::2], conns[1::2]):
        print(conn_src, '->', conn_dst)
        if maya.cmds.isConnected(conn_src, conn_dst):
            print(conn_src, 'xxx', conn_dst)
            maya.cmds.disconnectAttr(conn_src, conn_dst)
    return


def _connect_camera_lens_to_marker(cam_shp, mkr_tfm):
    src_exists = node_utils.attribute_exists('inLens', mkr_tfm)
    if src_exists is False:
        return
    dst_exists = node_utils.attribute_exists('outLens', cam_shp)
    if dst_exists is False:
        return

    src = cam_shp + '.outLens'
    dst = mkr_tfm + '.inLens'

    if maya.cmds.isConnected(src, dst) is True:
        return

    _disconnect_camera_lens_from_marker(mkr_tfm)
    maya.cmds.connectAttr(src, dst)
    return


def _create_marker_transform(name):
    tfm = maya.cmds.createNode(const.MARKER_TRANSFORM_NODE_TYPE, name=name)
    tfm = node_utils.get_long_name(tfm)
    maya.cmds.setAttr(tfm + '.tz', -1.0)
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


def _create_marker_shape(tfm_node):
    shp_name = tfm_node.rpartition('|')[-1] + 'Shape'
    shp = maya.cmds.createNode(
        const.MARKER_SHAPE_NODE_TYPE, name=shp_name, parent=tfm_node
    )
    maya.cmds.setAttr(shp + '.localPositionX', channelBox=False)
    maya.cmds.setAttr(shp + '.localPositionY', channelBox=False)
    maya.cmds.setAttr(shp + '.localPositionZ', channelBox=False)
    maya.cmds.setAttr(shp + '.localScaleX', channelBox=False)
    maya.cmds.setAttr(shp + '.localScaleY', channelBox=False)
    maya.cmds.setAttr(shp + '.localScaleZ', channelBox=False)
    return shp


def _create_marker_attributes(node):
    """
    Create the attributes expected to be on a Marker.

    :param node: Transform node for the Marker.
    :type node: str
    """
    attr = const.MARKER_ATTR_LONG_NAME_ENABLE
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

    attr = const.MARKER_ATTR_LONG_NAME_WEIGHT
    if not node_utils.attribute_exists(attr, node):
        maya.cmds.addAttr(
            node,
            longName=attr,
            attributeType='double',
            minValue=0.0,
            defaultValue=1.0,
            keyable=True,
        )

    attr = const.MARKER_ATTR_LONG_NAME_DEVIATION
    if not node_utils.attribute_exists(attr, node):
        maya.cmds.addAttr(
            node,
            longName=attr,
            attributeType='double',
            minValue=-1.0,
            defaultValue=-1.0,
            keyable=True,
        )
        plug = '{0}.{1}'.format(node, attr)
        maya.cmds.setAttr(plug, lock=True)

    attr = const.MARKER_ATTR_LONG_NAME_AVG_DEVIATION
    if not node_utils.attribute_exists(attr, node):
        maya.cmds.addAttr(
            node,
            longName=attr,
            attributeType='double',
            minValue=-1.0,
            defaultValue=-1.0,
            keyable=True,
        )
        plug = '{0}.{1}'.format(node, attr)
        maya.cmds.setAttr(plug, lock=True)

    attr = const.MARKER_ATTR_LONG_NAME_MAX_DEVIATION
    if not node_utils.attribute_exists(attr, node):
        maya.cmds.addAttr(
            node,
            longName=attr,
            attributeType='double',
            minValue=-1.0,
            defaultValue=-1.0,
            keyable=True,
        )
        plug = '{0}.{1}'.format(node, attr)
        maya.cmds.setAttr(plug, lock=True)

    attr = const.MARKER_ATTR_LONG_NAME_MAX_DEV_FRAME
    if not node_utils.attribute_exists(attr, node):
        maya.cmds.addAttr(
            node,
            longName=attr,
            attributeType='long',
            minValue=-1,
            defaultValue=-1,
            keyable=True,
        )
        plug = '{0}.{1}'.format(node, attr)
        maya.cmds.setAttr(plug, lock=True)

    attr = const.MARKER_ATTR_LONG_NAME_BUNDLE
    if not node_utils.attribute_exists(attr, node):
        maya.cmds.addAttr(node, longName=attr, attributeType='message')

    attr = const.MARKER_ATTR_LONG_NAME_MARKER_NAME
    if not node_utils.attribute_exists(attr, node):
        maya.cmds.addAttr(node, longName=attr, dataType='string')
        plug = '{0}.{1}'.format(node, attr)
        maya.cmds.setAttr(plug, lock=True)

    attr = const.MARKER_ATTR_LONG_NAME_MARKER_ID
    if not node_utils.attribute_exists(attr, node):
        maya.cmds.addAttr(node, longName=attr, attributeType='long', defaultValue=-1)
        plug = '{0}.{1}'.format(node, attr)
        maya.cmds.setAttr(plug, lock=True)

    attr = const.MARKER_ATTR_LONG_NAME_MARKER_USED_HINT
    if not node_utils.attribute_exists(attr, node):
        maya.cmds.addAttr(
            node,
            longName=attr,
            attributeType='long',
            defaultValue=const.MARKER_USED_HINT_UNKNOWN_VALUE,
            keyable=True,
        )
        plug = '{0}.{1}'.format(node, attr)
        maya.cmds.setAttr(plug, lock=True)
    return


def _replace_marker_transform(dag_path):
    # 0) Check the marker transform needs to be replaced - if not return.
    # 1) Get the shape nodes.
    # 2) Get the current values from the transform node.
    # 3) Get the locked state of the attributes.
    # 4) disconnect any nodes (such as animcurves) from the dag_path.
    # 5) Create a new node with a temp name.
    # 6) Reconnect nodes to new node.
    # 7) re-parent the shape nodes under the new node.
    # 8) Set the locked state of the attributes.
    # 9) Delete the original transform node.
    # 10) Rename the new node to have the exact same name as the input.
    raise NotImplementedError


def _replace_marker_shape(dag_path):
    dag_shps = node_utils.get_dag_path_shapes_below_apione(dag_path)
    if len(dag_shps) > 0:
        shape_nodes = []
        for dag_shp in dag_shps:
            mfn_shp = OpenMaya.MFnDagNode(dag_shp)
            type_name = mfn_shp.typeName()
            if type_name != const.MARKER_SHAPE_NODE_TYPE:
                shape_nodes.append(dag_shp.fullPathName())
        if len(shape_nodes) > 0:
            maya.cmds.delete(shape_nodes)
            _create_marker_shape(dag_path.fullPathName())
    else:
        _create_marker_shape(dag_path.fullPathName())
    return


def _set_marker_icon(dag_path):
    """Set the icon for all shape nodes under dag_path to use the
    mmMarkerShape icon.

    This is not needed when using the mmMarkerShape directly.
    """
    icon_name = const.MARKER_SHAPE_ICON_NAME
    dag_shps = node_utils.get_dag_path_shapes_below_apione(dag_path)
    if len(dag_shps) > 0:
        for dag_shp in dag_shps:
            mfn_shp = OpenMaya.MFnDagNode(dag_shp)
            mfn_shp.setIcon(icon_name)
    else:
        # Set icon on transform, because there are no shapes.
        mfn_tfm = OpenMaya.MFnDagNode(dag_path)
        mfn_tfm.setIcon(icon_name)
    return


class Marker(object):
    """
    The 2D Marker object.

    A Marker defines a wrapper around a Maya node that contains 2D
    information, in a camera's screen-space.

    Example usage::

        >>> mkr = mmapi.Marker(node='myNode')
        >>> mkr.get_node()
        '|myNode'
        >>> bnd = mmapi.Bundle().create_node(name='myBundle1')
        >>> mkr = mmapi.Marker().create_node(name='myMarker1', bnd=bnd)
        >>> mkr.get_node()
        '|myMarker1'

    """

    def __init__(self, node=None):
        """
        Initialize a Marker, give a name to connect to an existing Maya node.

        :param node: The Maya node to connect to.
        :type node: None or str
        """
        if isinstance(node, pycompat.TEXT_TYPE):
            try:
                dag = node_utils.get_as_dag_path(node)
                self._mfn = OpenMaya.MFnDagNode(dag)
            except RuntimeError as e:
                msg = 'Given Marker node name is invalid: name=%r'
                LOG.error(msg, node)
                raise e

            # Replace locator transform and shape with custom nodes.
            # dag = _replace_marker_transform(dag)
            # try:
            #     self._mfn = OpenMaya.MFnDagNode(dag)
            # except RuntimeError:
            #     raise
            _replace_marker_shape(dag)

            # Ensure the deviation attribute exists.
            self.add_attributes()
        else:
            self._mfn = OpenMaya.MFnDagNode()
        self._MFnAnimCurve_deviation = None
        self.set_deviation_anim_curve_fn(None)
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

        :return: The node this Marker object is bound to, or None.
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
        Change the underlying Maya node that this Marker class will manipulate.

        :param node: The existing Maya node.
        :type node: str
        """
        assert isinstance(node, pycompat.TEXT_TYPE)
        dag = node_utils.get_as_dag_path(node)
        try:
            self._mfn = OpenMaya.MFnDagNode(dag)
        except RuntimeError:
            raise

        # Replace locator transform and shape with custom nodes.
        # dag = _replace_marker_transform(dag)
        # try:
        #     self._mfn = OpenMaya.MFnDagNode(dag)
        # except RuntimeError:
        #     raise
        _replace_marker_shape(dag)

        # Ensure the deviation attribute exists.
        self.add_attributes()
        return

    def get_node_uid(self):
        """
        Get the marker transform unique identifier.

        :return: The marker UUID or None
        :rtype: None or str or unicode
        """
        node = self.get_node()
        if node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
            return None
        uids = maya.cmds.ls(node, uuid=True) or []
        return uids[0]

    ############################################################################

    def get_deviation_anim_curve_fn(self):
        """
        Get the MFnAnimCurve object for the deviation
        attribute animCurve.

        .. note:: Returned object is Maya API 1.0.

        :returns: Maya animCurve function set.
        :rtype: maya.OpenMayaAnim.MFnAnimCurve or None
        """
        animFn = self._MFnAnimCurve_deviation
        if animFn is None:
            node = self.get_node()
            if node is None:
                LOG.warn('Could not get Marker node. self=%r', self)
                return animFn
            plug_name = '{0}.{1}'.format(node, const.MARKER_ATTR_LONG_NAME_DEVIATION)
            animCurves = maya.cmds.listConnections(plug_name, type='animCurveTU') or []
            if len(animCurves) > 0:
                mobj = node_utils.get_as_object(animCurves[0])
                animFn = OpenMayaAnim.MFnAnimCurve(mobj)
        return animFn

    def set_deviation_anim_curve_fn(self, value):
        """
        Set the deviation animCurve function set.

        :param value:
            AnimCurve object to set, or use 'None' to remove the
            reference to the existing animCurve object
        :type value: maya.OpenMayaAnim.MFnAnimCurve or None
        """
        assert value is None or isinstance(value, OpenMayaAnim.MFnAnimCurve)
        self._MFnAnimCurve_deviation = value
        return

    ############################################################################

    def create_node(
        self, name='marker1', colour=None, cam=None, mkr_grp=None, bnd=None
    ):
        """
        Create a marker node network from scratch.

        :param name: Name of the marker to create.
        :type name: str

        :param colour: Colour of marker as R, G and B.
                       'None' will leave as default.
        :type colour: (float, float, float) or None

        :param cam: The camera to create the marker underneath.
        :type cam: Camera

        :param mkr_grp: The marker group to create the marker underneath.
        :type mkr_grp: MarkerGroup

        :param bnd: The bundle to attach to the newly created marker.
        :type bnd: Bundle

        :return: Marker object with newly created node.
        :rtype: Marker
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
        if bnd is not None:
            assert isinstance(bnd, mmSolver._api.bundle.Bundle)
        if colour is not None:
            assert isinstance(colour, (tuple, list))
            assert len(colour) == 3

        # Transform
        tfm = _create_marker_transform(name)

        # Shape Node
        _create_marker_shape(tfm)

        # Add attrs
        _create_marker_attributes(tfm)

        src = '{0}.{1}'.format(tfm, const.MARKER_ATTR_LONG_NAME_ENABLE)
        dst = '{0}.{1}'.format(tfm, 'lodVisibility')
        maya.cmds.connectAttr(src, dst)

        self.set_node(tfm)

        # Set Colour (default is red)
        if colour is not None:
            self.set_colour_rgb(colour)
        else:
            red = (1.0, 0.0, 0.0)
            self.set_colour_rgb(red)

        # Link to Camera
        if cam is not None:
            self.set_camera(cam)

        # Link to MarkerGroup
        if mkr_grp is not None:
            self.set_marker_group(mkr_grp)

        # Link to Bundle
        if bnd is not None:
            self.set_bundle(bnd)

        # Connect the marker to the camera.
        cam = self.get_camera()
        if cam is not None:
            cam_shp = cam.get_shape_node()
            tfm = self.get_node()
            _connect_camera_lens_to_marker(cam_shp, tfm)

        event_utils.trigger_event(const.EVENT_NAME_MARKER_CREATED, mkr=self)
        return self

    def delete_node(self):
        """
        Remove the Maya node (and all data) of this Marker object.

        :return: This Marker object, with Maya node removed.
        :rtype: Marker
        """
        node = self.get_node()
        if node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
            return self
        maya.cmds.delete(node)
        return self

    def add_attributes(self):
        """
        Add dynamic attributes to marker.
        """
        tfm = self.get_node()
        if tfm is not None:
            _create_marker_attributes(tfm)
        return

    ############################################################################

    def compute_deviation(self, times):
        """
        Compute the deviation for the marker.

        .. note:: This function assumes the camera film aperture (the
           film back) is not animated over the times given.

        :param times: The times to query the deviation on, if not
                      given the current frame is used.
        :type times: [float, ..]

        :returns: The deviation of the marker-to-bundle re-projection
                  in pixels. The length of the list returned will
                  always equal the length of the 'times' argument.
        :rtype: [float, ..]
        """
        v = None
        node = self.get_node()
        if node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
            return v
        cam = self.get_camera()
        if cam is None:
            LOG.warn('Could not get Camera node. self=%r', self)
            return v
        bnd = self.get_bundle()
        if bnd is None:
            LOG.warn('Could not get Bundle node. self=%r', self)
            return v

        assert len(times) > 0
        cam_tfm = cam.get_transform_node()
        cam_shp = cam.get_shape_node()
        hfa_plug = cam_shp + '.horizontalFilmAperture'
        vfa_plug = cam_shp + '.verticalFilmAperture'
        hfa = maya.cmds.getAttr(hfa_plug, time=times[0])
        vfa = maya.cmds.getAttr(vfa_plug, time=times[0])
        image_width, _ = cam.get_plate_resolution()
        image_width = float(image_width)
        image_height = image_width * (vfa / hfa)

        weights_list = [self.get_weight(time=t) for t in times]
        enabled_list = [self.get_enable(time=t) for t in times]

        bnd_node = bnd.get_node()
        dev_list = markerutils.calculate_marker_deviation(
            node,
            bnd_node,
            cam_tfm,
            cam_shp,
            times,
            weights_list,
            enabled_list,
            image_width,
            image_height,
        )
        if dev_list is None:
            dev_list = [-1.0] * times
        assert len(dev_list) == len(times)
        return dev_list

    def get_enable(self, time=None):
        """
        Get the enabled state of the Marker.

        :param time: The time to query the enable, if not given the
                      current frame is used.
        :type time: float

        :returns: The enabled state of the marker.
        :rtype: int
        """
        node = self.get_node()
        if node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
            return None
        plug = '{0}.{1}'.format(node, const.MARKER_ATTR_LONG_NAME_ENABLE)
        if time is None:
            v = maya.cmds.getAttr(plug)
        else:
            v = maya.cmds.getAttr(plug, time=time)
        return v

    def get_enabled_frames(self, frame_range_start=None, frame_range_end=None):
        """
        Get the list of frames that this Marker is enabled.

        If there is no animation curve on a Marker we use the
        frame_range_start and frame_range_end arguments to determine
        the enabled frame list. If these frame_range_* arguments are
        not given the default Maya outer timeline range is used.

        :param frame_range_start: The frame range start of the marker
                                  to consider when no animCurve exists.
        :type frame_range_start: int

        :param frame_range_end: The frame range end of the marker
                                to consider when no animCurve exists.
        :type frame_range_end: int

        :returns: The enabled frame numbers of the marker.
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
        plug = '{0}.{1}'.format(node, const.MARKER_ATTR_LONG_NAME_ENABLE)

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
        Get the weight value Marker.

        :param time: The time to query the weight, if not given the
                     current frame is used.
        :type time: float

        :returns: The weight of the marker.
        :rtype: float
        """
        node = self.get_node()
        if node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
            return None
        plug = '{0}.{1}'.format(node, const.MARKER_ATTR_LONG_NAME_WEIGHT)
        if time is None:
            v = maya.cmds.getAttr(plug)
        else:
            v = maya.cmds.getAttr(plug, time=time)
        return v

    def get_average_deviation(self):
        """
        Calculate a single float number (in pixels) representing the
        average deviation of this Marker.
        """
        node = self.get_node()
        if node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
            return None
        attr_name = const.MARKER_ATTR_LONG_NAME_AVG_DEVIATION
        plug_name = '{0}.{1}'.format(node, attr_name)
        dev = maya.cmds.getAttr(plug_name)
        return dev

    def set_average_deviation(self, value):
        """
        Calculate a single float number (in pixels) representing the
        average deviation of this Marker.
        """
        node = self.get_node()
        if node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
            return None
        attr_name = const.MARKER_ATTR_LONG_NAME_AVG_DEVIATION
        plug_name = '{0}.{1}'.format(node, attr_name)
        try:
            maya.cmds.setAttr(plug_name, lock=False)
            maya.cmds.setAttr(plug_name, value)
        finally:
            maya.cmds.setAttr(plug_name, lock=True)
        return

    def get_maximum_deviation(self):
        """
        Return a tuple of (value, frame) for the deviation
        value and frame number that is the highest.
        """
        node = self.get_node()
        if node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
            return None
        attr_name = const.MARKER_ATTR_LONG_NAME_MAX_DEVIATION
        plug_name = '{0}.{1}'.format(node, attr_name)
        max_dev = maya.cmds.getAttr(plug_name)

        attr_name = const.MARKER_ATTR_LONG_NAME_MAX_DEV_FRAME
        plug_name = '{0}.{1}'.format(node, attr_name)
        max_frm = maya.cmds.getAttr(plug_name)
        return max_dev, max_frm

    def set_maximum_deviation(self, max_dev, max_frm):
        """
        Return a tuple of (value, frame) for the deviation
        value and frame number that is the highest.
        """
        node = self.get_node()
        if node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
            return None
        attr_name = const.MARKER_ATTR_LONG_NAME_MAX_DEVIATION
        value_plug = '{0}.{1}'.format(node, attr_name)

        attr_name = const.MARKER_ATTR_LONG_NAME_MAX_DEV_FRAME
        frame_plug = '{0}.{1}'.format(node, attr_name)
        try:
            maya.cmds.setAttr(value_plug, lock=False)
            maya.cmds.setAttr(frame_plug, lock=False)
            maya.cmds.setAttr(value_plug, max_dev)
            maya.cmds.setAttr(frame_plug, max_frm)
        finally:
            maya.cmds.setAttr(value_plug, lock=True)
            maya.cmds.setAttr(frame_plug, lock=True)
        return

    def get_deviation_frames(self, frame_range_start=None, frame_range_end=None):
        """
        Get the list of frames that this Marker has deviation set.

        If there is no animation curve on a Marker we use the
        frame_range_start and frame_range_end arguments to determine
        the deviation frame list. If these frame_range_* arguments are
        not given the default Maya outer timeline range is used.

        :param frame_range_start: The frame range start of the marker
                                  to consider when no animCurve exists.
        :type frame_range_start: int

        :param frame_range_end: The frame range end of the marker
                                to consider when no animCurve exists.
        :type frame_range_end: int

        :returns: The deviation frame numbers of the marker.
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
            LOG.warn('Could not get Marker node. self=%r', self)
            return times
        anim_curve_fn = self.get_deviation_anim_curve_fn()

        if anim_curve_fn is None:
            enable_times = list(range(frame_range_start, frame_range_end + 1))
        else:
            num_keys = anim_curve_fn.numKeys()
            enable_times = [None] * num_keys
            for i in range(num_keys):
                mtime = anim_curve_fn.time(i)
                enable_times[i] = int(mtime.value())
            if num_keys == 0:
                enable_times = list(range(frame_range_start, frame_range_end + 1))

        start_frame = int(min(enable_times))
        end_frame = int(max(enable_times))
        frame_range = list(range(start_frame, end_frame + 1))
        dev_list = self.get_deviation(times=frame_range)
        for frm, dev_val in zip(frame_range, dev_list):
            if dev_val > 0.0:
                times.append(frm)
        return times

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

    def get_deviation(self, times=None):
        """
        Get the deviation for the marker from the internal animCurve.

        :param times: The times to query the deviation on, if not
                      given the current frame is used.
        :type times: [float, ..]

        :returns: The deviation of the marker-to-bundle re-projection
                  (in pixels), for each time given.
        :rtype: [float, ..]
        """
        node = self.get_node()
        if node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
            return None

        frames = []
        if times is None:
            frames = [maya.cmds.currentTime(query=True)]
        else:
            frames = times
        assert len(frames) > 0

        attr_name = const.MARKER_ATTR_LONG_NAME_DEVIATION
        plug_name = '{0}.{1}'.format(node, attr_name)
        anim_curve_fn = self.get_deviation_anim_curve_fn()

        dev_list = [None] * len(frames)
        if anim_curve_fn is not None:
            # Evaluate Curve
            unit = OpenMaya.MTime.uiUnit()
            for i, frame in enumerate(frames):
                frame_time = OpenMaya.MTime(float(frame), unit)
                value = anim_curve_fn.evaluate(frame_time)
                dev_list[i] = value

            self.set_deviation_anim_curve_fn(anim_curve_fn)
        else:
            # Note: We assume if there is not animCurve then the
            # deviation value is static. We do not account for a
            # non-animCurve node connected to the deviation attribute,
            # as that is considered an error.
            v = maya.cmds.getAttr(plug_name)
            dev_list = [v] * len(frames)
        return dev_list

    def set_deviation(self, times, values):
        """
        Set deviation keyframes on the marker.

        :param times: Times to set deviation values for.
        :type times: [float, ..]

        :param values: Values of deviation to set at each time.
        :type values: [float, ..]
        """
        assert isinstance(times, (list, tuple))
        assert isinstance(values, (list, tuple))
        assert len(times) > 0
        assert len(values) > 0
        assert len(times) == len(values)

        node = self.get_node()
        if node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
            return
        attr_name = const.MARKER_ATTR_LONG_NAME_DEVIATION
        plug = '{0}.{1}'.format(node, attr_name)
        try:
            maya.cmds.setAttr(plug, lock=False)
            anim_curve_fn = anim_utils.create_anim_curve_node_apione(
                times,
                values,
                node_attr=plug,
                anim_type=OpenMayaAnim.MFnAnimCurve.kAnimCurveTU,
            )
            self.set_deviation_anim_curve_fn(anim_curve_fn)
        finally:
            maya.cmds.setAttr(plug, lock=True)
        return

    ############################################################################

    def get_colour_rgb(self):
        """
        Get the current RGBA colour (0.0 to 1.0) of the Marker.

        :returns:
           Tuple of red, green and blue, or None if colour cannot be
           found. Each channel is floating point; 0.0 to 1.0.
        :rtype: (float, float, float) or None
        """
        node = self.get_node()
        if node is None:
            msg = 'Could not get node. self=%r'
            LOG.warn(msg, self)
            return None
        shps = (
            maya.cmds.listRelatives(
                node, shapes=True, fullPath=True, type=const.MARKER_SHAPE_NODE_TYPE
            )
            or []
        )
        if len(shps) == 0:
            msg = 'Could not find shape to get colour. node=%r shps=%r'
            LOG.warn(msg, node, shps)
            return None
        shp = shps[0]

        v = maya.cmds.getAttr(shp + '.color')[0]
        return tuple(v)

    def set_colour_rgb(self, rgb):
        """
        Change the RGBA colour (0.0 to 1.0) of the Marker.

        :param rgb:
           Colour as R, G, B; Or None to reset to default colour.
           Each channel is floating point; 0.0 to 1.0.
        :type rgb: tuple or None

        :rtype: None
        """
        if rgb is None:
            rgb = (1.0, 0.0, 0.0)
        assert isinstance(rgb, (tuple, list))
        assert len(rgb) >= 3

        node = self.get_node()
        if node is None:
            msg = 'Could not get node. self=%r'
            LOG.warn(msg, self)
            return
        shps = (
            maya.cmds.listRelatives(
                node, shapes=True, fullPath=True, type=const.MARKER_SHAPE_NODE_TYPE
            )
            or []
        )
        if len(shps) == 0:
            msg = 'Could not find shape to set colour. node=%r shps=%r'
            LOG.warn(msg, node, shps)
            return
        shp = shps[0]

        maya.cmds.setAttr(shp + '.colorR', rgb[0])
        maya.cmds.setAttr(shp + '.colorG', rgb[1])
        maya.cmds.setAttr(shp + '.colorB', rgb[2])
        return

    def get_colour_rgba(self):
        """
        Get the current RGBA colour (0.0 to 1.0) of the Marker.

        :returns:
           Tuple of red, green, blue, and alpha, or None if colour
           cannot be found. Each channel is floating point; 0.0 to 1.0.
        :rtype: (float, float, float, float) or None
        """
        node = self.get_node()
        if node is None:
            msg = 'Could not get node. self=%r'
            LOG.warn(msg, self)
            return None
        shps = (
            maya.cmds.listRelatives(
                node, shapes=True, fullPath=True, type=const.MARKER_SHAPE_NODE_TYPE
            )
            or []
        )
        if len(shps) == 0:
            msg = 'Could not find shape to get colour. node=%r shps=%r'
            LOG.warn(msg, node, shps)
            return None
        shp = shps[0]

        rgb = maya.cmds.getAttr(shp + '.color')[0]
        alpha = maya.cmds.getAttr(shp + '.alpha')
        return (rgb[0], rgb[1], rgb[2], alpha)

    def set_colour_rgba(self, rgba):
        """
        Change the RGB colour (0.0 to 1.0) of the Marker.

        :param rgba:
            Colour as R, G, B, A; Or None to reset to default colour.
            Each channel is floating point; 0.0 to 1.0.
        :type rgba: tuple

        :rtype: None
        """
        if rgba is None:
            rgba = (1.0, 0.0, 0.0, 1.0)
        assert rgba is None or isinstance(rgba, (tuple, list))
        assert len(rgba) >= 4
        node = self.get_node()
        if node is None:
            msg = 'Could not get node. self=%r'
            LOG.warn(msg, self)
            return
        shps = (
            maya.cmds.listRelatives(
                node, shapes=True, fullPath=True, type=const.MARKER_SHAPE_NODE_TYPE
            )
            or []
        )
        if len(shps) == 0:
            msg = 'Could not find shape to set colour. node=%r shps=%r'
            LOG.warn(msg, node, shps)
            return
        shp = shps[0]
        maya.cmds.setAttr(shp + '.colorR', rgba[0])
        maya.cmds.setAttr(shp + '.colorG', rgba[1])
        maya.cmds.setAttr(shp + '.colorB', rgba[2])
        maya.cmds.setAttr(shp + '.alpha', rgba[3])
        return

    ############################################################################

    def get_bundle(self):
        """
        Get the Bundle connected to this Marker node.

        :returns: a Bundle object or None if no Bundle is connected.
        :rtype: Bundle or None
        """
        bnd = None
        node = self.get_node()
        if node is not None:
            assert maya.cmds.objExists(node)
            bnd_node = None
            node_attr = node + '.bundle'
            bnd_nodes = (
                maya.cmds.listConnections(
                    node_attr, type=const.BUNDLE_TRANSFORM_NODE_TYPE
                )
                or []
            )
            if len(bnd_nodes) > 0:
                bnd_node = bnd_nodes[0]
            if bnd_node is not None and len(bnd_node) > 0:
                bnd = mmSolver._api.bundle.Bundle(bnd_node)
        return bnd

    def set_bundle(self, bnd):
        """
        Connect the given Bundle to this Marker.

        :param bnd: Bundle to connect to.
        :type bnd: Bundle
        """
        if bnd is None:
            self._unlink_from_bundle()
        elif isinstance(bnd, mmSolver._api.bundle.Bundle):
            self._link_to_bundle(bnd)
        return

    def _link_to_bundle(self, bnd):
        """
        Connect a Bundle to the Marker.

        A Marker may only have one connected Bundle object.

        :param bnd: The Bundle to connect to.
        :type bnd: Bundle

        :returns: None.
        """
        # output message to marker.bundle attr
        assert isinstance(bnd, mmSolver._api.bundle.Bundle)

        bnd_node = bnd.get_node()
        assert isinstance(bnd_node, pycompat.TEXT_TYPE)
        assert maya.cmds.objExists(bnd_node)

        mkr_node = self.get_node()
        if mkr_node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
            return None
        assert isinstance(mkr_node, pycompat.TEXT_TYPE)
        assert maya.cmds.objExists(mkr_node)

        attr_name = 'bundle'
        attr_names = maya.cmds.listAttr(mkr_node)
        if attr_name not in attr_names:
            maya.cmds.addAttr(mkr_node, longName=attr_name, at='message')

        src = bnd_node + '.message'
        dst = mkr_node + '.' + attr_name
        if not maya.cmds.isConnected(src, dst):
            maya.cmds.connectAttr(src, dst)
        else:
            msg = 'Marker and Bundle are already linked; '
            msg += 'marker={0}, bundle={1}'
            msg = msg.format(repr(mkr_node), repr(bnd_node))
            raise excep.AlreadyLinked(msg)
        return

    def _unlink_from_bundle(self):
        """
        Remove the connection between the connected Bundle and Marker.

        :returns: None
        """
        bnd = self.get_bundle()
        if bnd is None:
            LOG.warn('Could not get Bundle. self=%r', self)
            return
        mkr_node = self.get_node()
        if mkr_node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
            return
        bnd_node = bnd.get_node()
        if bnd_node is None:
            LOG.warn('Could not get Bundle node. self=%r', self)
            return
        src = bnd_node + '.message'
        dst = mkr_node + '.bundle'
        if maya.cmds.isConnected(src, dst):
            maya.cmds.disconnectAttr(src, dst)
        return

    ############################################################################

    def get_camera(self):
        """
        Get the camera connected implicitly with the Marker.

        :returns: Camera object, or None if Marker does not have a
                  Camera (for example it's unparented to world).
        :rtype: None or Camera
        """
        mkr_node = self.get_node()
        if mkr_node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
            return None

        cam_tfm, cam_shp = node_utils.get_camera_above_node(mkr_node)

        # Make the camera object.
        cam = None
        if cam_tfm is not None and cam_shp is not None:
            cam = camera.Camera(transform=cam_tfm, shape=cam_shp)
        return cam

    def set_camera(self, cam):
        """
        Connect this Marker to the given camera.

        Connecting Markers to cameras happens by parenting a Marker
        under a Camera's Marker Group.

        .. note:: If the `cam` argument is None, the Marker is
            disconnected from any camera.

        :param cam: The camera to connect this Marker to.
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
        Parent a marker under the marker group which is under the given camera.
        If there is no marker group, one is created.

        :param cam: The camera to connect this Marker to.
        :type cam: None or Camera

        :returns: None
        """
        assert isinstance(cam, camera.Camera)

        mkr_node = self.get_node()
        if mkr_node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
            return
        cam_tfm = cam.get_transform_node()
        cam_shp = cam.get_shape_node()

        # Make sure the camera is valid for us to link to.
        if cam.is_valid() is False:
            msg = 'Cannot link Marker to Camera; Camera is not valid.'
            msg += ' marker={0} camera={1}'
            msg = msg.format(repr(mkr_node), repr(cam_shp))
            raise excep.NotValid(msg)

        # Check if we're trying to link the the camera that we're already
        # linked to.
        current_cam = self.get_camera()
        if current_cam is not None:
            assert isinstance(current_cam, camera.Camera)
            current_cam_shp = current_cam.get_shape_node()
            if current_cam_shp == cam_shp:
                msg = 'Marker is already linked to camera, skipping.'
                msg += ' marker={0} camera={1}'
                msg = msg.format(repr(mkr_node), repr(cam_shp))
                raise excep.AlreadyLinked(msg)

        # Connect the marker to the camera.
        cam_shp = cam.get_shape_node()
        if cam_shp is not None:
            _connect_camera_lens_to_marker(cam_shp, mkr_node)

        # Create Marker Group
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

        # Link to Marker Group
        self.set_marker_group(mkr_grp)
        return

    def _unlink_from_camera(self):
        """
        Re-parent the current marker to the world; it will live under no camera.

        :returns: None
        """
        mkr_node = self.get_node()
        if mkr_node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
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
            msg = 'Marker is already unlinked from all cameras, skipping.'
            msg += ' marker={0} camera={1}'
            msg = msg.format(repr(mkr_node), repr(cam_shp))
            raise excep.AlreadyUnlinked(msg)

        _disconnect_camera_lens_from_marker(mkr_node)

        # Move the marker under the world root, don't modify the marker in
        # any way otherwise (so we use 'relative' flag).
        maya.cmds.parent(mkr_node, relative=True, world=True)
        return

    ############################################################################

    def get_marker_group(self):
        """
        Get the marker group that implicitly connected to this Marker.

        :returns: Marker group object.
        :rtype: MarkerGroup or None
        """
        mkr_node = self.get_node()
        if mkr_node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
            return

        mkr_grp_node = api_utils.get_marker_group_above_node(mkr_node)

        # Make the marker group object.
        mkr_grp = None
        if mkr_grp_node is not None:
            mkr_grp = markergroup.MarkerGroup(node=mkr_grp_node)
        return mkr_grp

    def set_marker_group(self, mkr_grp):
        """
        Set the MarkerGroup for this Marker, or None to unlink the Marker.

        :param mkr_grp: Marker group object to link to this Marker.
        :type mkr_grp: MarkerGroup or None
        """
        if mkr_grp is None:
            self._unlink_from_marker_group()
        elif isinstance(mkr_grp, markergroup.MarkerGroup):
            self._link_to_marker_group(mkr_grp)
        return

    def _link_to_marker_group(self, mkr_grp):
        """
        Parent a marker under a Marker Group.
        """
        assert isinstance(mkr_grp, markergroup.MarkerGroup)

        mkr_node = self.get_node()
        if mkr_node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
            return
        mkr_grp_node = mkr_grp.get_node()

        # Make sure the camera is valid for us to link to.
        if mkr_grp.is_valid() is False:
            msg = 'Cannot link Marker to Marker Group; Marker Group is not valid.'
            msg += ' marker={0} marker group={1}'
            msg = msg.format(repr(mkr_node), repr(mkr_grp_node))
            raise excep.NotValid(msg)

        # Check if we're trying to link the the camera that we're already
        # linked to.
        current_mkr_grp = self.get_marker_group()
        if current_mkr_grp is not None:
            assert isinstance(current_mkr_grp, markergroup.MarkerGroup)
            current_mkr_grp = current_mkr_grp.get_node()
            if current_mkr_grp == mkr_grp_node:
                msg = 'Marker is already linked to Marker Group, skipping.'
                msg += ' marker={0} marker group={1}'
                msg = msg.format(repr(mkr_node), repr(mkr_grp_node))
                raise excep.AlreadyLinked(msg)

        # Move the marker under the marker group, make sure the relative
        # marker attribute values are maintained.
        maya.cmds.parent(mkr_node, mkr_grp_node, relative=True)

        # Connect the marker to the camera.
        cam = self.get_camera()
        if cam is not None:
            cam_shp = cam.get_shape_node()
            _connect_camera_lens_to_marker(cam_shp, mkr_node)

        return

    def _unlink_from_marker_group(self):
        """
        Re-parent the current marker to the world; it will live under no
        """
        mkr_node = self.get_node()
        if mkr_node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
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
            msg = 'Marker is already unlinked from all cameras, skipping.'
            msg += ' marker={0} camera={1}'
            msg = msg.format(repr(mkr_node), repr(cam_shp))
            raise excep.AlreadyUnlinked(msg)

        _disconnect_camera_lens_from_marker(mkr_node)

        # Move the marker under the world root, don't modify the marker in
        # any way otherwise.
        maya.cmds.parent(mkr_node, relative=True, world=True)
        return

    ############################################################################

    def get_used_hint(self):
        """
        Is the Marker used by the solver?

        This attribute does not affect the solve, but is provided as a hint
        to show users (in UIs), that a marker is unused.

        :returns: A value of MARKER_USED_HINT_LIST that indicates
            the current used state hint.
        :rtype: int
        """
        # TODO: Does this need to be updated to work with frame numbers?
        node = self.get_node()
        if node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
            return None
        attr_name = const.MARKER_ATTR_LONG_NAME_MARKER_USED_HINT
        plug_name = '{0}.{1}'.format(node, attr_name)
        value = maya.cmds.getAttr(plug_name)
        assert value in const.MARKER_USED_HINT_LIST
        return value

    def set_used_hint(self, value):
        """
        Set the value indicating this Marker is used by the solver.

        See the Marker.get_used_hint() method for details.

        :param value: The value to set, a value in MARKER_USED_HINT_LIST.
        :type value: int
        """
        # TODO: Does this need to be updated to work with frame numbers?
        assert isinstance(value, pycompat.INT_TYPES)
        assert value in const.MARKER_USED_HINT_LIST
        node = self.get_node()
        if node is None:
            LOG.warn('Could not get Marker node. self=%r', self)
            return None
        attr_name = const.MARKER_ATTR_LONG_NAME_MARKER_USED_HINT
        plug_name = '{0}.{1}'.format(node, attr_name)
        try:
            maya.cmds.setAttr(plug_name, lock=False)
            maya.cmds.setAttr(plug_name, value)
        finally:
            maya.cmds.setAttr(plug_name, lock=True)
        return


def update_deviation_on_markers(mkr_list, solres_list):
    """
    Calculate marker deviation, and set it on the marker.

    :param mkr_list: Marker objects to update deviation on.
    :type mkr_list: [Marker, ..]

    :param solres_list: The solve results to calculate deviation frames from.
    :type solres_list: [SolveResult, ..]
    """
    frame_list = solveresult.merge_frame_list(solres_list)
    frame_list = [int(x) for x in frame_list]
    frame_list_set = set(frame_list)
    for mkr in mkr_list:
        mkr_frames = mkr.get_enabled_frames()
        mkr_frames = [int(x) for x in mkr_frames]
        mkr_frames_set = set(mkr_frames).intersection(frame_list_set)
        mkr_frames = list(mkr_frames_set)
        if len(mkr_frames) > 0:
            deviation_list = mkr.compute_deviation(mkr_frames)

            # Note: Extra frame is given at start and end.
            frame_range_set = set(
                range(min(mkr_frames_set) - 1, max(mkr_frames_set) + 2)
            )
            diff_set = frame_range_set.difference(mkr_frames_set)

            frm_list = list(sorted(frame_range_set))
            dev_list = [None] * len(frame_range_set)
            assert len(frm_list) == len(dev_list)
            idx = 0
            for i, frm in enumerate(sorted(frame_range_set)):
                if frm in diff_set:
                    # Deviation should be zero on a frame that is not
                    # enabled.
                    dev_list[i] = -1.0
                else:
                    # Look up value from deviation_list.
                    dev_list[i] = deviation_list[idx]
                    idx += 1
            assert idx == (len(deviation_list))
            mkr.set_deviation(frm_list, dev_list)

            # Average Deviation
            avg_dev = markerutils.calculate_average_deviation(dev_list)
            mkr.set_average_deviation(avg_dev)

            # Max Deviation
            max_dev, max_frm = markerutils.calculate_maximum_deviation(
                frm_list, dev_list
            )
            mkr.set_maximum_deviation(max_dev, int(max_frm))
    return
