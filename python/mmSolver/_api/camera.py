import maya.cmds
from maya import OpenMaya as OpenMaya

import mmSolver._api.utils as api_utils


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
        assert isinstance(name, (str, unicode))
        assert maya.cmds.objExists(name)

        self._mfn_tfm = None
        self._mfn_shp = None

        tfm_dag = api_utils.get_as_dag_path(name)
        if tfm_dag is not None:
            assert tfm_dag.apiType() == OpenMaya.MFn.kTransform

            # Get camera shape from transform.
            dag = api_utils.get_as_dag_path(name)
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
        assert isinstance(name, (str, unicode))
        assert maya.cmds.objExists(name)

        self._mfn_tfm = None
        self._mfn_shp = None

        shp_dag = api_utils.get_as_dag_path(name)
        if shp_dag is not None:
            assert shp_dag.apiType() == OpenMaya.MFn.kCamera

            # Get transform from shape.
            tfm_dag = api_utils.get_as_dag_path(name)
            tfm_dag.pop(1)
            assert tfm_dag.apiType() == OpenMaya.MFn.kTransform

            self._mfn_shp = OpenMaya.MFnDagNode(shp_dag)
            self._mfn_tfm = OpenMaya.MFnDagNode(tfm_dag)

        if self._mfn_tfm is None or self._mfn_shp is None:
            self._mfn_tfm = OpenMaya.MFnDagNode()
            self._mfn_shp = OpenMaya.MFnDagNode()

        return

    ############################################################################

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
