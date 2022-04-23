# Copyright (C) 2018, 2019, 2020 David Cattermole.
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


LOG = mmSolver.logger.get_logger()


def _set_lens_icon(dag_path):
    icon_name = const.LENS_SHAPE_ICON_NAME
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


class Lens(object):
    """
    The Lens to view the world and compute re-projection error;
    Markers are attached to lenses.

    Example usage::

        >>> import mmSolver.api as mmapi
        >>> lens = mmapi.Lens().create_node()
        >>> lens.get_node()
        'lens1'
        >>> cam = mmapi.Camera(transform='myCamera')
        >>> lens = cam.get_lens()
        >>> lens.get_node()
        'lens1'

    """

    def __init__(self, node=None):
        """
        Initialise a Lens object.

        If no 'node' is given, the Lens is uninitialized.

        :param node: The lens node.
        :type node: None or str

        """
        self._mfn_node = None
        if node is None:
            self._mfn_node = OpenMaya.MFnDependencyNode()
        else:
            self.set_node(node)
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
        Get the lens node.

        :return: The lens node or None
        :rtype: None or str or unicode
        """
        node = None
        try:
            obj = self._mfn_node.object()
        except RuntimeError:
            obj = None
        if obj is not None and obj.isNull() is False:
            try:
                node = self._mfn_node.name()
            except RuntimeError:
                pass
        if isinstance(node, pycompat.TEXT_TYPE) and len(node) == 0:
            node = None
        return node

    def get_node_uid(self):
        """
        Get the lens unique identifier.

        :return: The lens UUID or None
        :rtype: None or str or unicode
        """
        node = self.get_node()
        if node is None:
            return None
        uid = maya.cmds.ls(node, uuid=True) or []
        return uid[0]

    def set_node(self, node):
        """
        Change the underlying Maya nodes that this Lens class will
        manipulate.

        :param node: The existing Maya node.
        :type node: str
        """
        assert isinstance(node, pycompat.TEXT_TYPE)
        assert maya.cmds.objExists(node)

        self._mfn_node = None

        lens_obj = node_utils.get_as_object_apione(node)
        if lens_obj is not None:
            # assert lens_dag.apiType() in const.LENS_NODE_API_TYPES
            self._mfn_node = OpenMaya.MFnDependencyNode(lens_obj)

        if self._mfn_node is None:
            self._mfn_node = OpenMaya.MFnDependencyNode()
        return

    ############################################################################

    def create_node(self,
                    name='lens1',
                    model=None):
        """
        Create a lens node.

        :param name: Name of the lens to create.
        :type name: str

        :param model: The node-type name to create as the Lens.
        :type model: str

        :return: Lens object with newly created node.
        :rtype: Lens
        """
        assert isinstance(name, pycompat.TEXT_TYPE)
        if model is None:
            model = const.LENS_NODE_TYPE_DEFAULT
        assert isinstance(model, pycompat.TEXT_TYPE)
        node = maya.cmds.createNode(model, name=name)
        self.set_node(node)
        return self

    def delete_node(self):
        """
        Remove the Maya node (and all data) of this Lens object.

        :return: This Lens object, with Maya node removed.
        :rtype: Lens
        """
        lens_node = self.get_node()
        maya.cmds.delete(lens_node)
        return self

    ############################################################################

    def get_output_nodes(self):
        """Return objects connected to the output of this lens.

        :returns: A list of str. The list may be empty.
        """
        lens_node = self.get_node()
        output_nodes = maya.cmds.listConnections(
            lens_node + ".outLens",
            shapes=False,
            source=True) or []
        return output_nodes

    def get_input_node(self):
        """Return an object connected to the input of this lens.

        :returns: The returned object may be: str or None.
        """
        lens_node = self.get_node()
        input_nodes = maya.cmds.listConnections(
            lens_node + ".inLens",
            shapes=False,
            destination=True) or []
        input_node = None
        if len(input_nodes) > 0:
            assert len(input_nodes) == 1
            input_node = input_nodes[0]
        return input_node

    def _disconnect_input_nodes_from_lens(self, lens_node):
        """
        Disconnect all input nodes to this lens object.
        """
        assert len(lens_node) > 0
        lens_node_connections = maya.cmds.listConnections(
            lens_node + ".inLens",
            shapes=False,
            source=True,
            destination=False,
            connections=True,
            plugs=True) or []
        if len(lens_node_connections) > 0:
            num = len(lens_node_connections)
            src_list = lens_node_connections[1:num:2]
            dst_list = lens_node_connections[0:num:2]
            for src, dst in zip(src_list, dst_list):
                if maya.cmds.isConnected(src, dst):
                    maya.cmds.disconnectAttr(src, dst)
        return

    def set_input_lens(self, input_lens):
        """
        Connect the given node to the 'input' of this object.

        If input_lens is None, any existing input lens node will be
        disconnected from the Lens.
        """
        assert input_lens is None or isinstance(input_lens, Lens)
        lens_node = self.get_node()
        if lens_node is None:
            msg = "Lens object has no node: object=%r"
            LOG.warn(msg, self)
            return
        if input_lens is None:
            self._disconnect_input_nodes_from_lens(lens_node)
            return
        input_lens_node = input_lens.get_node()
        src = input_lens_node + '.outLens'
        dst = lens_node + '.inLens'
        if maya.cmds.isConnected(src, dst) is False:
            maya.cmds.connectAttr(src, dst)
        return

    ############################################################################

    def get_enable(self):
        """
        Get the 'enable' of the Lens.
        """
        lens_node = self.get_node()
        if lens_node is None:
            msg = "Lens object has no node: object=%r"
            LOG.warn(msg, self)
            return
        return maya.cmds.getAttr(lens_node + '.enable')

    def set_enable(self, value):
        """
        Set the 'enable' value of the Lens.

        Disabling the lens stops the lens from having an affect.
        """
        assert isinstance(value, bool)
        lens_node = self.get_node()
        if lens_node is None:
            msg = "Lens object has no node: object=%r"
            LOG.warn(msg, self)
            return
        maya.cmds.setAttr(lens_node + '.enable', value)
        return
