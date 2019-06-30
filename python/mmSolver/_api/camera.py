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
import maya.cmds
from maya import OpenMaya as OpenMaya

import mmSolver.logger
import mmSolver.utils.node as node_utils
import mmSolver._api.constant as const
import mmSolver._api.utils as api_utils


LOG = mmSolver.logger.get_logger()


class Camera(object):
    """
    The Camera to view the world and compute re-projection error;
    Markers are attached to cameras.

    Example usage::

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
        if isinstance(node, (str, unicode)) and len(node) == 0:
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
        assert isinstance(name, (str, unicode))
        assert maya.cmds.objExists(name)

        self._mfn_tfm = None
        self._mfn_shp = None

        tfm_dag = node_utils.get_as_dag_path(name)
        if tfm_dag is not None:
            assert tfm_dag.apiType() == OpenMaya.MFn.kTransform

            # Get camera shape from transform.
            dag = node_utils.get_as_dag_path(name)
            num_children = dag.childCount()
            if num_children > 0:
                for i in xrange(num_children):
                    child_obj = dag.child(i)
                    if child_obj.apiType() == OpenMaya.MFn.kCamera:
                        dag.push(child_obj)
                        self._mfn_shp = OpenMaya.MFnDagNode(dag)
                        break

            self._mfn_tfm = OpenMaya.MFnDagNode(tfm_dag)

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
        if isinstance(node, (str, unicode)) and len(node) == 0:
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
        assert isinstance(name, (str, unicode))
        assert maya.cmds.objExists(name)

        self._mfn_tfm = None
        self._mfn_shp = None

        shp_dag = node_utils.get_as_dag_path(name)
        if shp_dag is not None:
            assert shp_dag.apiType() == OpenMaya.MFn.kCamera

            # Get transform from shape.
            tfm_dag = node_utils.get_as_dag_path(name)
            tfm_dag.pop(1)
            assert tfm_dag.apiType() == OpenMaya.MFn.kTransform

            self._mfn_shp = OpenMaya.MFnDagNode(shp_dag)
            self._mfn_tfm = OpenMaya.MFnDagNode(tfm_dag)

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
        resolution = (const.DEFAULT_PLATE_WIDTH,
                      const.DEFAULT_PLATE_HEIGHT)
        shp = self.get_shape_node()
        if shp is None:
            LOG.warning('Could not get Camera shape node.')
            return resolution
        plug = shp + '.imagePlane'
        img_planes = maya.cmds.listConnections(plug, type='imagePlane') or []
        img_planes = [node_utils.get_long_name(n) for n in img_planes]

        if len(img_planes) == 0:
            return resolution  # no image planes
        elif len(img_planes) > 1:
            msg = 'Multiple image planes on camera, using first;'
            msg += 'camera=%r nodes=%r'
            LOG.warning(msg, shp, img_planes)
        img_plane = img_planes[0]

        width = maya.cmds.getAttr(img_plane + '.coverageX')
        height = maya.cmds.getAttr(img_plane + '.coverageY')
        if width > 0 and height > 0:
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
        below_nodes = maya.cmds.ls(
            node,
            dag=True,
            long=True,
            type='transform') or []

        mkr_list = []
        ver = maya.cmds.about(apiVersion=True)
        if ver < 201600:
            mkr_list = [mmSolver._api.marker.Marker(node=n)
                        for n in below_nodes
                        if api_utils.get_object_type(n) == const.OBJECT_TYPE_MARKER]
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
        if ((cam_tfm is None) or
                (cam_shp is None) or
                (maya.cmds.objExists(cam_tfm) is False) or
                (maya.cmds.objExists(cam_shp) is False)):
            return False
        return True
