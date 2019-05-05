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
3D Bundle objects.
"""

import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver.logger
import mmSolver._api.utils as api_utils
import mmSolver._api.marker


LOG = mmSolver.logger.get_logger()


class Bundle(object):
    """
    The 3D Bundle object.

    A Bundle is named 'Bundle' as it represents bundles of light
    forming on an imaging sensor.

    Example usage::

        >>> bnd = mmapi.Bundle(node='myNode')
        >>> bnd.get_node()
        '|myNode'
        >>> bnd = mmapi.Bundle().create_node(name='myBundle1')
        >>> bnd.get_node()
        '|myBundle1'

    """

    def __init__(self, node=None):
        """
        Create a Bundle object initialised with 'node'.

        :param node: Maya node to attach this object to.
        :type node: str
        """
        if node is not None:
            assert isinstance(node, (str, unicode))
            assert maya.cmds.objExists(node)
            dag = api_utils.get_as_dag_path(node)
            if dag is not None:
                self._mfn = OpenMaya.MFnDagNode(dag)
        else:
            self._mfn = OpenMaya.MFnDagNode()
        return

    def __repr__(self):
        result = '<{class_name}('.format(class_name=self.__class__.__name__)
        result += '{hash} node={node}'.format(
            hash=hash(self),
            node=self.get_node(),
        )
        result += ')>'
        return result

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
        """
        This Bundle object will affect the given 'node'.

        :param node: Node to set to.
        :type node: str

        :return: Nothing.
        """
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
        """
        Create a Bundle.

        :param name: The name of the newly created Bundle.
        :type name: str

        :param colour: Colour of bundle as R, G and B.
                       'None' will leave as default.
        :type colour: (float, float, float) or None

        :return: Bundle object attached to newly created node.
        :rtype: Bundle
        """
        assert isinstance(name, (str, unicode))
        if colour is not None:
            assert isinstance(colour, (tuple, list))
            assert len(colour) == 3

        # Transform
        tfm = maya.cmds.createNode('transform', name=name)
        tfm = api_utils.get_long_name(tfm)
        maya.cmds.setAttr(tfm + '.rx', lock=True)
        maya.cmds.setAttr(tfm + '.ry', lock=True)
        maya.cmds.setAttr(tfm + '.rz', lock=True)
        maya.cmds.setAttr(tfm + '.sx', lock=True)
        maya.cmds.setAttr(tfm + '.sy', lock=True)
        maya.cmds.setAttr(tfm + '.sz', lock=True)
        maya.cmds.setAttr(tfm + '.shxy', lock=True)
        maya.cmds.setAttr(tfm + '.shxz', lock=True)
        maya.cmds.setAttr(tfm + '.shyz', lock=True)
        maya.cmds.setAttr(tfm + '.rx', keyable=False)
        maya.cmds.setAttr(tfm + '.ry', keyable=False)
        maya.cmds.setAttr(tfm + '.rz', keyable=False)
        maya.cmds.setAttr(tfm + '.sx', keyable=False)
        maya.cmds.setAttr(tfm + '.sy', keyable=False)
        maya.cmds.setAttr(tfm + '.sz', keyable=False)
        maya.cmds.setAttr(tfm + '.shxy', keyable=False)
        maya.cmds.setAttr(tfm + '.shxz', keyable=False)
        maya.cmds.setAttr(tfm + '.shyz', keyable=False)

        # Shape Node
        shp_name = tfm.rpartition('|')[-1] + 'Shape'
        shp = maya.cmds.createNode('locator', name=shp_name, parent=tfm)
        maya.cmds.setAttr(shp + '.localScaleX', 0.1)
        maya.cmds.setAttr(shp + '.localScaleY', 0.1)
        maya.cmds.setAttr(shp + '.localScaleZ', 0.1)

        self.set_node(tfm)

        # Set Colour (default is green)
        if colour is not None:
            self.set_colour_rgb(colour)
        else:
            green = (0.0, 1.0, 0.0)
            self.set_colour_rgb(green)
        return self

    def delete_node(self):
        """
        Remove the Maya node (and all data) of this Bundle object.

        :return: This Bundle object, with Maya node removed.
        :rtype: Bundle
        """
        node = self.get_node()
        maya.cmds.delete(node)
        return self

    ############################################################################

    def get_colour_rgb(self):
        """
        Get the current wire-frame colour of the Bundle.

        :returns: Tuple of red, green and blue, or None if colour
                  cannot be found.
        :rtype: (float, float, float) or None
        """
        node = self.get_node()
        if node is None:
            msg = 'Could not get node. self=%r'
            LOG.warning(msg, self)
            return None
        shps = maya.cmds.listRelatives(node, shapes=True) or []
        if len(shps) == 0:
            msg = 'Could not find shape to get colour. node=%r shps=%r'
            LOG.warning(msg, node, shps)
            return None
        shp = shps[0]
        v = api_utils.get_node_wire_colour_rgb(shp)
        return v

    def set_colour_rgb(self, rgb):
        """
        Change the Wireframe colour of the Bundle.

        :param rgb: Colour as R, G, B; Or None to reset to default colour.
        :type rgb: tuple

        :return: Nothing.
        :rtype: None
        """
        assert rgb is None or isinstance(rgb, (tuple, list))
        node = self.get_node()
        if node is None:
            msg = 'Could not get node. self=%r'
            LOG.warning(msg, self)
            return
        shps = maya.cmds.listRelatives(node, shapes=True) or []
        if len(shps) == 0:
            msg = 'Could not find shape to set colour. node=%r shps=%r'
            LOG.warning(msg, node, shps)
            return
        shp = shps[0]
        api_utils.set_node_wire_colour_rgb(shp, rgb)
        return

    ############################################################################

    def get_marker_list(self):
        """
        Get the list of Markers attached to this bundle.

        :return: List of Marker objects.
        :rtype: Marker
        """
        node = self.get_node()
        node_attr = node + '.message'
        conns = maya.cmds.listConnections(node_attr) or []
        mkr_list = []
        for conn in conns:
            mkr = mmSolver._api.marker.Marker(node=conn)
            mkr_list.append(mkr)
        return mkr_list
