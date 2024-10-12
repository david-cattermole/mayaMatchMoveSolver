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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver.logger
import mmSolver.utils.node as node_utils
import mmSolver.utils.camera as camera_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver._api.constant as const
import mmSolver._api.utils as api_utils
import mmSolver._api.lens as lensmodule


LOG = mmSolver.logger.get_logger()


def _create_camera_attributes(cam_shp):
    """
    Create the attributes expected to be on a camera.

    :param cam_shp: Shape node for the Camera.
    :type cam_shp: str
    """
    assert isinstance(cam_shp, pycompat.TEXT_TYPE)
    assert maya.cmds.nodeType(cam_shp) == 'camera'

    cam_shp_is_locked = maya.cmds.lockNode(cam_shp, query=True)[0]
    if cam_shp_is_locked is True:
        LOG.warn(
            'Cannot create camera attributes, camera shape is locked; cam_shp=%r',
            cam_shp,
        )
        return

    node_obj = node_utils.get_as_object_apione(cam_shp)
    dg_node_fn = OpenMaya.MFnDependencyNode(node_obj)

    api_utils.load_plugin()
    typedAttr = OpenMaya.MFnTypedAttribute()
    data_type_id = OpenMaya.MTypeId(const.LENS_DATA_TYPE_ID)

    already_exists = node_utils.attribute_exists('inLens', cam_shp)
    if already_exists is False:
        attr_obj = typedAttr.create("inLens", "ilns", data_type_id)
        typedAttr.setStorable(False)
        typedAttr.setKeyable(False)
        typedAttr.setReadable(True)
        typedAttr.setWritable(True)
        dg_node_fn.addAttribute(attr_obj)

    already_exists = node_utils.attribute_exists('outLens', cam_shp)
    if already_exists is False:
        attr_obj = typedAttr.create("outLens", "olns", data_type_id)
        typedAttr.setStorable(False)
        typedAttr.setKeyable(False)
        typedAttr.setReadable(True)
        typedAttr.setWritable(True)
        dg_node_fn.addAttribute(attr_obj)
    return


def _create_lens_toggle_setup(cam_tfm, cam_shp):
    cam_shp_is_locked = maya.cmds.lockNode(cam_shp, query=True)[0]
    if cam_shp_is_locked is False:
        _create_camera_attributes(cam_shp)

    in_lens_attr_exists = node_utils.attribute_exists('inLens', cam_shp)
    if in_lens_attr_exists is False:
        return None

    # When linking to a camera, if an attribute 'lens' does not
    # already exist, create it.
    toggle_nodes = (
        maya.cmds.listConnections(cam_shp + ".inLens", shapes=False, destination=True)
        or []
    )
    if len(toggle_nodes) == 0:
        api_utils.load_plugin()
        toggle_node = maya.cmds.createNode(
            'mmLensModelToggle', name=const.LENS_TOGGLE_NODE_NAME
        )

        out_lens_attr_exists = node_utils.attribute_exists('outLens', cam_shp)

        if in_lens_attr_exists:
            maya.cmds.connectAttr(cam_shp + '.inLens', toggle_node + '.inLens')
        if out_lens_attr_exists:
            maya.cmds.connectAttr(toggle_node + '.outLens', cam_shp + '.outLens')
    else:
        toggle_node = toggle_nodes[0]
    return toggle_node


def _link_lens_to_camera(cam_tfm, cam_shp, lens):
    """Connect the Lens to the Camera.

    Assumes that no lens is already connected to the camera."""
    assert isinstance(lens, lensmodule.Lens)

    in_lens_attr_exists = node_utils.attribute_exists('inLens', cam_shp)
    if in_lens_attr_exists is False:
        LOG.warn(
            'Cannot link lens to camera, missing "inLens" attribute; cam_shp=%r lens=%r',
            cam_shp,
            lens,
        )
        return

    lens_node = lens.get_node()
    src = lens_node + '.outLens'
    dst = cam_shp + '.inLens'
    if not maya.cmds.isConnected(src, dst):
        maya.cmds.connectAttr(src, dst)
    return


def _unlink_lens_from_camera(cam_tfm, cam_shp):
    """Disconnect Lens(es) from the Camera attribute."""
    in_lens_attr_exists = node_utils.attribute_exists('inLens', cam_shp)
    if in_lens_attr_exists is False:
        LOG.warn(
            'Cannot unlink lens from camera, missing "inLens" attribute; cam_shp=%r',
            cam_shp,
        )
        return

    lens_node_connections = (
        maya.cmds.listConnections(
            cam_shp + ".inLens",
            shapes=False,
            source=True,
            destination=False,
            connections=True,
            plugs=True,
        )
        or []
    )
    if len(lens_node_connections) > 0:
        num = len(lens_node_connections)
        src_list = lens_node_connections[1:num:2]
        dst_list = lens_node_connections[0:num:2]
        for src, dst in zip(src_list, dst_list):
            if maya.cmds.isConnected(src, dst):
                maya.cmds.disconnectAttr(src, dst)
    return


class Camera(object):
    """
    The Camera to view the world and compute re-projection error;
    Markers are attached to cameras.

    Example usage::

        >>> import mmSolver.api as mmapi
        >>> cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
        >>> cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
        >>> cam = mmapi.Camera(shape=cam_shp)
        >>> cam.get_transform_node()
        '|cam_tfm'
        >>> cam.get_shape_node()
        '|cam_tfm|cam_shp'

    """

    def __init__(self, transform=None, shape=None):
        """
        Initialise a Camera object.

        Give either a transform or shape node and the object will find
        the other node.

        If no 'transform' or 'shape' is given, the Camera is
        uninitialized.

        :param transform: The camera transform node.
        :type transform: None or str

        :param shape: The camera shape node.
        :type shape: None or str
        """
        self._mfn_tfm = None
        self._mfn_shp = None
        self._cache_marker_list = dict()

        if transform is None and shape is None:
            self._mfn_tfm = OpenMaya.MFnDagNode()
            self._mfn_shp = OpenMaya.MFnDagNode()
        elif shape is not None:
            self.set_shape_node(shape)
        elif transform is not None:
            self.set_transform_node(transform)
        return

    def __repr__(self):
        result = '<{class_name}('.format(class_name=self.__class__.__name__)
        result += '{hash} tfm_node={tfm_node} shp_node={shp_node}'.format(
            hash=hex(hash(self)),
            tfm_node=self.get_transform_node(),
            shp_node=self.get_shape_node(),
        )
        result += ')>'
        return result

    def get_transform_node(self):
        """
        Get the camera transform node.

        :return: The camera transform node or None
        :rtype: None or str or unicode
        """
        node = None
        try:
            obj = self._mfn_tfm.object()
        except RuntimeError:
            obj = None
        if obj is not None and obj.isNull() is False:
            try:
                node = self._mfn_tfm.fullPathName()
            except RuntimeError:
                pass
        if isinstance(node, pycompat.TEXT_TYPE) and len(node) == 0:
            node = None
        return node

    def get_transform_uid(self):
        """
        Get the camera transform unique identifier.

        :return: The camera transform UUID or None
        :rtype: None or str or unicode
        """
        node = self.get_transform_node()
        if node is None:
            return None
        uid = maya.cmds.ls(node, uuid=True) or []
        return uid[0]

    def set_transform_node(self, name):
        """
        Change the underlying Maya nodes that this Camera class will
        manipulate.

        This function will automatically set the Camera shape node based
        this transform node.

        :param name: The existing Maya node.
        :type name: str
        """
        assert isinstance(name, pycompat.TEXT_TYPE)
        assert maya.cmds.objExists(name)

        self._mfn_tfm = None
        self._mfn_shp = None

        tfm_dag = node_utils.get_as_dag_path(name)
        if tfm_dag is not None:
            assert tfm_dag.apiType() in const.CAMERA_TRANSFORM_NODE_API_TYPES
            cam_tfm = tfm_dag.fullPathName()

            # Get camera shape from transform.
            cam_shp = None
            dag = node_utils.get_as_dag_path(name)
            num_children = dag.childCount()
            if num_children > 0:
                for i in range(num_children):
                    child_obj = dag.child(i)
                    if child_obj.apiType() in const.CAMERA_SHAPE_NODE_API_TYPES:
                        dag.push(child_obj)
                        self._mfn_shp = OpenMaya.MFnDagNode(dag)
                        cam_shp = dag.fullPathName()
                        break

            self._mfn_tfm = OpenMaya.MFnDagNode(tfm_dag)
            _create_lens_toggle_setup(cam_tfm, cam_shp)

        if self._mfn_tfm is None or self._mfn_shp is None:
            self._mfn_tfm = OpenMaya.MFnDagNode()
            self._mfn_shp = OpenMaya.MFnDagNode()
        return

    def get_shape_node(self):
        """
        Get the camera shape node.

        :return: The camera shape node or None
        :rtype: None or str or unicode
        """
        node = None
        try:
            obj = self._mfn_shp.object()
        except RuntimeError:
            obj = None
        if obj is not None and obj.isNull() is False:
            try:
                node = self._mfn_shp.fullPathName()
            except RuntimeError:
                pass
        if isinstance(node, pycompat.TEXT_TYPE) and len(node) == 0:
            node = None
        return node

    def get_shape_uid(self):
        """
        Get the camera shape unique identifier.

        :return: The camera shape UUID or None
        :rtype: None or str or unicode
        """
        node = self.get_shape_node()
        if node is None:
            return None
        uids = maya.cmds.ls(node, uuid=True) or []
        return uids[0]

    def set_shape_node(self, name):
        """
        Change the underlying Maya nodes that this Camera class will
        manipulate.

        This function will automatically set the Camera transform node
        based this shape node.

        :param name: The existing Maya node.
        :type name: str
        """
        assert isinstance(name, pycompat.TEXT_TYPE)
        assert maya.cmds.objExists(name)

        self._mfn_tfm = None
        self._mfn_shp = None

        shp_dag = node_utils.get_as_dag_path(name)
        if shp_dag is not None:
            assert shp_dag.apiType() in const.CAMERA_SHAPE_NODE_API_TYPES
            cam_shp = shp_dag.fullPathName()

            # Get transform from shape.
            tfm_dag = node_utils.get_as_dag_path(name)
            tfm_dag.pop(1)
            assert tfm_dag.apiType() in const.CAMERA_TRANSFORM_NODE_API_TYPES
            cam_tfm = tfm_dag.fullPathName()

            self._mfn_shp = OpenMaya.MFnDagNode(shp_dag)
            self._mfn_tfm = OpenMaya.MFnDagNode(tfm_dag)
            _create_lens_toggle_setup(cam_tfm, cam_shp)

        if self._mfn_tfm is None or self._mfn_shp is None:
            self._mfn_tfm = OpenMaya.MFnDagNode()
            self._mfn_shp = OpenMaya.MFnDagNode()

        return

    ############################################################################

    def get_plate_resolution(self):
        """
        Get the resolution of the image attached to this camera, or
        return a default value if no image is attached.

        :return: Tuple of X and Y resolution.
        :rtype: (int, int)
        """
        resolution = (const.DEFAULT_PLATE_WIDTH, const.DEFAULT_PLATE_HEIGHT)
        shp = self.get_shape_node()
        if shp is None:
            LOG.warning('Could not get Camera shape node.')
            return resolution

        tfm = self.get_transform_node()
        img_planes = camera_utils.get_image_plane_shapes_from_camera(tfm, shp)
        if len(img_planes) == 0:
            return resolution  # no image planes
        elif len(img_planes) > 1:
            msg = 'Multiple image planes on camera, using first;'
            msg += 'camera=%r nodes=%r'
            LOG.warning(msg, shp, img_planes)
        img_plane = img_planes[0]

        width = maya.cmds.getAttr(img_plane + '.coverageX')
        height = maya.cmds.getAttr(img_plane + '.coverageY')
        if width > 1 and height > 1:
            resolution = (width, height)
        else:
            msg = 'Get plate resolution failed, using to default values;'
            msg += 'camera=%r nodes=%r width=%r height=%r'
            LOG.debug(msg, shp, img_planes, width, height)
        return resolution

    def get_average_deviation(self):
        """
        Get the average deviation for all marker under the camera.

        :returns: The deviation of the marker-to-bundle re-projection in pixels.
        :rtype: float
        """
        dev = None
        node = self.get_transform_node()
        if node is None:
            msg = 'Could not get Camera transform node. self=%r'
            LOG.warning(msg, self)
            return dev

        total = 0
        dev_sum = 0.0
        mkr_list = self.get_marker_list()
        for mkr in mkr_list:
            dev_value = mkr.get_average_deviation()
            dev_sum += dev_value
            total += 1
        if total > 0:
            dev = dev_sum / total
        return dev

    def get_deviation(self, times=None):
        """
        Get the deviation for all marker under the camera at the current times.

        :param times: The times to query the deviation on, if not
                      given the current frame is used.
        :type times: float

        :returns: The deviation of the marker-to-bundle re-projection in pixels.
        :rtype: float
        """
        dev = None
        node = self.get_transform_node()
        if node is None:
            msg = 'Could not get Camera transform node. self=%r'
            LOG.warning(msg, self)
            return dev

        total = 0
        dev_sum = 0.0
        mkr_list = self.get_marker_list()
        for mkr in mkr_list:
            if not mkr.get_enable():
                continue
            dev_values = mkr.get_deviation(times=times)
            dev_sum += dev_values[0]
            total += 1
        if total > 0:
            dev = dev_sum / total
        return dev

    def get_maximum_deviation(self):
        """
        Get the maximum deviation (and frame) for all marker under the camera.

        :param times: The times to query the deviation on, if not
                      given the current frame is used.
        :type times: float

        :returns:
        :rtype: (float, float)
        """
        max_dev = -1.0
        max_frm = -1.0
        node = self.get_transform_node()
        if node is None:
            msg = 'Could not get Camera transform node. self=%r'
            LOG.warning(msg, self)
            return max_dev, max_frm

        mkr_list = self.get_marker_list()
        for mkr in mkr_list:
            val, frm = mkr.get_maximum_deviation()
            if val > max_dev:
                max_dev = val
                max_frm = frm
        return max_dev, max_frm

    ############################################################################

    def get_marker_list(self):
        """
        Get the list of Markers under this camera.

        :return: List of Marker objects.
        :rtype: Marker
        """
        import mmSolver._api.marker

        node = self.get_transform_node()
        below_nodes = maya.cmds.ls(node, dag=True, long=True, type='transform') or []

        mkr_list = []
        ver = maya.cmds.about(apiVersion=True)
        if ver < 201600:
            mkr_list = [
                mmSolver._api.marker.Marker(node=n)
                for n in below_nodes
                if api_utils.get_object_type(n) == const.OBJECT_TYPE_MARKER
            ]
        else:
            # Note: Use UUIDs to cache nodes, this is only supported
            # on Maya 2016 and above.
            for n in below_nodes:
                uids = maya.cmds.ls(node, uuid=True) or []
                mkr = self._cache_marker_list.get(uids[0])
                if mkr is None:
                    if api_utils.get_object_type(n) == const.OBJECT_TYPE_MARKER:
                        mkr = mmSolver._api.marker.Marker(node=n)
                if mkr is not None:
                    mkr_list.append(mkr)

        return mkr_list

    def is_valid(self):
        """
        Is this Camera object valid?
        Does the Camera have both transform and shape nodes and they both exist?

        :return: True or False, is this Camera object valid?
        :rtype: bool
        """
        cam_tfm = self.get_transform_node()
        cam_shp = self.get_shape_node()
        if (
            (cam_tfm is None)
            or (cam_shp is None)
            or (maya.cmds.objExists(cam_tfm) is False)
            or (maya.cmds.objExists(cam_shp) is False)
        ):
            return False
        return True

    ############################################################################

    def get_lens_enable(self):
        """
        Get the lens distortion mode of the camera.
        """
        cam_tfm = self.get_transform_node()
        cam_shp = self.get_shape_node()
        if cam_tfm is None or cam_shp is None:
            msg = "Camera object has no transform/shape node: object=%r"
            LOG.warn(msg, self)
            return

        toggle_node = _create_lens_toggle_setup(cam_tfm, cam_shp)
        if toggle_node is None:
            msg = "Camera node toggle could not be found or created: object=%r"
            LOG.warn(msg, self)
            return

        return maya.cmds.getAttr(toggle_node + '.enable')

    def set_lens_enable(self, value):
        """
        Set the lens distortion mode of the camera.
        """
        assert isinstance(value, bool)
        cam_tfm = self.get_transform_node()
        cam_shp = self.get_shape_node()
        if cam_tfm is None or cam_shp is None:
            msg = "Camera object has no transform/shape node: object=%r"
            LOG.warn(msg, self)
            return

        toggle_node = _create_lens_toggle_setup(cam_tfm, cam_shp)
        if toggle_node is None:
            msg = "Camera node toggle could not be found or created: object=%r"
            LOG.warn(msg, self)
            return

        maya.cmds.setAttr(toggle_node + '.enable', value)
        return

    def get_lens(self):
        """
        Get the lens connected to the camera.

        :returns: Lens object, or None if Camera does not have a
                  Lens.
        :rtype: None or Lens
        """
        lens = None
        cam_tfm = self.get_transform_node()
        cam_shp = self.get_shape_node()
        if cam_tfm is None or cam_shp is None:
            msg = "Camera object has no transform/shape node: object=%r"
            LOG.warn(msg, self)
            return lens

        _create_lens_toggle_setup(cam_tfm, cam_shp)
        in_lens_attr_exists = node_utils.attribute_exists('inLens', cam_shp)
        if in_lens_attr_exists is not True:
            msg = 'Camera node "inLens" attribute not found: object=%r'
            LOG.warn(msg, self)
            return

        nodes = (
            maya.cmds.listConnections(
                cam_shp + '.inLens', source=True, destination=False, shapes=False
            )
            or []
        )
        if len(nodes) > 0:
            assert len(nodes) == 1
            lens = lensmodule.Lens(node=nodes[0])
        return lens

    def set_lens(self, lens):
        """
        Connect this Camera to the given Lens.

        .. note:: If the `lens` argument is None, the Camera is
            disconnected from any lens.

        :param lens: The Lens to connect this Camera to.
        :type lens: None or Lens

        :returns: None
        """
        assert isinstance(lens, lensmodule.Lens)
        cam_tfm = self.get_transform_node()
        cam_shp = self.get_shape_node()
        if cam_tfm is None or cam_shp is None:
            msg = "Camera object has no transform or shape node: object=%r"
            LOG.warn(msg, self)
            return
        if lens is None:
            _unlink_lens_from_camera(cam_tfm, cam_shp)
        elif isinstance(lens, lensmodule.Lens):
            _create_lens_toggle_setup(cam_tfm, cam_shp)
            _unlink_lens_from_camera(cam_tfm, cam_shp)
            _link_lens_to_camera(cam_tfm, cam_shp, lens)
        return
