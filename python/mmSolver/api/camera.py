import maya.cmds
from maya import OpenMaya as OpenMaya

from mmSolver.api import utils as api_utils


class Camera(object):
    """
    The Camera to view the world and compute re-projection error;
    Markers are attached to cameras.
    """

    def __init__(self, transform=None, shape=None):
        if transform is None and shape is None:
            self._mfn_tfm = OpenMaya.MFnDagNode()
            self._mfn_shp = OpenMaya.MFnDagNode()

        elif shape is not None:
            assert isinstance(shape, (str, unicode))
            assert maya.cmds.objExists(shape)
            shp_dag = api_utils.get_as_dag_path(shape)
            if shp_dag is not None:
                assert shp_dag.apiType() == OpenMaya.MFn.kCamera

                # Get transform from shape.
                tfm_dag = api_utils.get_as_dag_path(shape)
                tfm_dag.pop(1)
                assert tfm_dag.apiType() == OpenMaya.MFn.kTransform

                self._mfn_shp = OpenMaya.MFnDagNode(shp_dag)
                self._mfn_tfm = OpenMaya.MFnDagNode(tfm_dag)
            else:
                self._mfn_shp = OpenMaya.MFnDagNode()
                self._mfn_tfm = OpenMaya.MFnDagNode()

        elif transform is not None:
            assert isinstance(transform, (str, unicode))
            assert maya.cmds.objExists(transform)
            tfm_dag = api_utils.get_as_dag_path(transform)
            if tfm_dag is not None:
                assert tfm_dag.apiType() == OpenMaya.MFn.kTransform
                self._mfn_tfm = None

                # Get camera shape from transform.
                self._mfn_shp = None
                dag = api_utils.get_as_dag_path(transform)
                num_children = dag.childCount()
                if num_children > 0:
                    for i in xrange(num_children):
                        child_obj = dag.child(i)
                        if child_obj.apiType() == OpenMaya.MFn.kCamera:
                            dag.push(child_obj)
                            self._mfn_shp = OpenMaya.MFnDagNode(dag)
                            break
                if self._mfn_shp is not None:
                    self._mfn_tfm = OpenMaya.MFnDagNode(tfm_dag)
            else:
                self._mfn_tfm = OpenMaya.MFnDagNode()

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

    def set_transform_node(self, value):
        assert False
        pass

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

    def set_shape_node(self, value):
        assert False
        pass

    def is_valid(self):
        cam_tfm = self.get_transform_node()
        cam_shp = self.get_shape_node()
        if ((cam_tfm is None) or
                (cam_shp is None) or
                (maya.cmds.objExists(cam_tfm) is False) or
                (maya.cmds.objExists(cam_shp) is False)):
            return False
        return True

    ############################################################################