"""
The 2D Marker object.
"""

import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver.api.utils as api_utils
import mmSolver.api.bundle as bundle


class Marker(object):
    def __init__(self, name=None):
        if isinstance(name, (str, unicode)):
            dag = api_utils.get_as_dag_path(name)
            self._mfn = OpenMaya.MFnDagNode(dag)
        else:
            self._mfn = OpenMaya.MFnDagNode()
        return

    def get_node(self):
        try:
            node = self._mfn.fullPathName()
        except RuntimeError:
            node = None
        return node

    def set_node(self, name):
        dag = api_utils.get_as_dag_path(name)
        try:
            self._mfn = OpenMaya.MFnDagNode(dag)
        except RuntimeError:
            raise
        return

    ############################################################################

    def create_node(self, name='marker1'):
        # Transform
        tfm = maya.cmds.createNode('transform', name=name)
        tfm = api_utils.get_long_name(tfm)

        # Shape Node
        shp_name = tfm.rpartition('|')[-1] + 'Shape'
        shp = maya.cmds.createNode('locator', name=shp_name, parent=tfm)

        # Add attrs
        maya.cmds.addAttr(tfm, longName='enable', at='bool',
                          defaultValue=True)
        maya.cmds.addAttr(tfm, longName='weight', at='double',
                          minValue=0.0, defaultValue=1.0)
        maya.cmds.addAttr(tfm, longName='bundle', at='message')

        self.set_node(tfm)
        return self

    def delete_node(self):
        pass

    ############################################################################

    def get_bundle(self):
        pass

    def link_to_bundle(self, bnd):
        # output bundle.message to marker.bundle attr
        # api_utils.
        assert isinstance(bnd, bundle.Bundle)

        bnd_node = bnd.get_node()
        assert isinstance(bnd_node, (str, unicode))
        assert maya.cmds.objExists(bnd_node)

        mkr_node = self.get_node()
        assert isinstance(mkr_node, (str, unicode))
        assert maya.cmds.objExists(mkr_node)

        attr_name = 'bundle'
        attr_names = maya.cmds.listAttr(mkr_node)
        if attr_name not in attr_names:
            maya.cmds.addAttr(mkr_node, longName=attr_name, at='message')

        src = bnd_node+'.message'
        dst = mkr_node + '.' + attr_name
        if not maya.cmds.isConnected(src, dst):
            maya.cmds.connectAttr(src, dst)
        else:
            msg = 'Marker and Bundle are already linked; '
            msg += 'marker={0}, bundle={1}'
            maya.cmds.warning(msg.format(mkr_node, bnd_node))

        # maya.cmds.listConnections(nodeA+'.'+attr_name)
        return

    def unlink_from_bundle(self, bnd):
        pass

    ############################################################################