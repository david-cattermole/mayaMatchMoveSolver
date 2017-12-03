import maya.cmds
from maya import OpenMaya as OpenMaya

import mmSolver._api.utils as api_utils
import mmSolver._api.marker


class Bundle(object):
    """
    The 3D Bundle object.
    """
    def __init__(self, node=None):
        if node is not None:
            assert isinstance(node, (str, unicode))
            assert maya.cmds.objExists(node)
            dag = api_utils.get_as_dag_path(node)
            if dag is not None:
                self._mfn = OpenMaya.MFnDagNode(dag)
        else:
            self._mfn = OpenMaya.MFnDagNode()
        return

    def get_node(self):
        """
        Get the bundle transform node.

        :return: The bundle transform node or None
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
        if isinstance(node, (str, unicode)) and len(node) == 0:
            node = None
        return node

    def set_node(self, node):
        assert isinstance(node, (str, unicode))
        assert maya.cmds.objExists(node)
        dag = api_utils.get_as_dag_path(node)
        if dag is not None:
            self._mfn = OpenMaya.MFnDagNode(dag)
        else:
            self._mfn = OpenMaya.MFnDagNode()
        return

    ############################################################################

    def create_node(self,
                    name='bundle1',
                    colour=None):
        assert isinstance(name, (str, unicode))
        if colour is not None:
            assert isinstance(colour, str)
            # TODO: Look up the colour value from a string.

        # Transform
        tfm = maya.cmds.createNode('transform', name=name)
        tfm = api_utils.get_long_name(tfm)
        maya.cmds.setAttr(tfm + '.rx', lock=True)
        maya.cmds.setAttr(tfm + '.ry', lock=True)
        maya.cmds.setAttr(tfm + '.rz', lock=True)
        maya.cmds.setAttr(tfm + '.sx', lock=True)
        maya.cmds.setAttr(tfm + '.sy', lock=True)
        maya.cmds.setAttr(tfm + '.sz', lock=True)

        # Shape Node
        shp_name = tfm.rpartition('|')[-1] + 'Shape'
        shp = maya.cmds.createNode('locator', name=shp_name, parent=tfm)
        maya.cmds.setAttr(shp + '.localScaleX', 0.1)
        maya.cmds.setAttr(shp + '.localScaleY', 0.1)
        maya.cmds.setAttr(shp + '.localScaleZ', 0.1)

        self.set_node(tfm)
        return self

    def delete_node(self):
        node = self.get_node()
        maya.cmds.delete(node)
        return self

    ############################################################################

    def get_node_colour(self):
        pass

    def set_node_colour(self, name):
        # TODO: should we allow RGB values directly?
        # TODO: Look up the colour value from a string.
        pass

    ############################################################################

    def get_marker_list(self):
        node = self.get_node()
        node_attr = node + '.message'
        conns = maya.cmds.listConnections(node_attr) or []
        mkr_list = []
        for conn in conns:
            mkr = mmSolver._api.marker.Marker(name=conn)
            mkr_list.append(mkr)
        return mkr_list








