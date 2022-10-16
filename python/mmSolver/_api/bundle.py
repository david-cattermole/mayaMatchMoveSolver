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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver.logger
import mmSolver.utils.event as event_utils
import mmSolver.utils.node as node_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver._api.constant as const
import mmSolver._api.marker


LOG = mmSolver.logger.get_logger()


def _lock_and_display_bundle_attributes(
    tfm,
    lock_translate=None,
    lock_rotate=None,
    lock_scale=None,
    lock_shear=None,
    display_translate=None,
    display_rotate=None,
    display_scale=None,
    display_shear=None,
):
    """
    Create the attributes expected to be on a Marker.

    :param node: Transform node for the Marker.
    :type node: str
    """
    assert lock_translate is not None
    assert lock_rotate is not None
    assert lock_scale is not None
    assert lock_shear is not None
    assert display_translate is not None
    assert display_rotate is not None
    assert display_scale is not None
    assert display_shear is not None

    maya.cmds.setAttr(tfm + '.tx', lock=lock_translate)
    maya.cmds.setAttr(tfm + '.ty', lock=lock_translate)
    maya.cmds.setAttr(tfm + '.tz', lock=lock_translate)
    maya.cmds.setAttr(tfm + '.rx', lock=lock_rotate)
    maya.cmds.setAttr(tfm + '.ry', lock=lock_rotate)
    maya.cmds.setAttr(tfm + '.rz', lock=lock_rotate)
    maya.cmds.setAttr(tfm + '.sx', lock=lock_scale)
    maya.cmds.setAttr(tfm + '.sy', lock=lock_scale)
    maya.cmds.setAttr(tfm + '.sz', lock=lock_scale)
    maya.cmds.setAttr(tfm + '.shxy', lock=lock_shear)
    maya.cmds.setAttr(tfm + '.shxz', lock=lock_shear)
    maya.cmds.setAttr(tfm + '.shyz', lock=lock_shear)

    maya.cmds.setAttr(tfm + '.tx', keyable=display_translate)
    maya.cmds.setAttr(tfm + '.ty', keyable=display_translate)
    maya.cmds.setAttr(tfm + '.tz', keyable=display_translate)
    maya.cmds.setAttr(tfm + '.rx', keyable=display_rotate)
    maya.cmds.setAttr(tfm + '.ry', keyable=display_rotate)
    maya.cmds.setAttr(tfm + '.rz', keyable=display_rotate)
    maya.cmds.setAttr(tfm + '.sx', keyable=display_scale)
    maya.cmds.setAttr(tfm + '.sy', keyable=display_scale)
    maya.cmds.setAttr(tfm + '.sz', keyable=display_scale)
    maya.cmds.setAttr(tfm + '.shxy', keyable=display_shear)
    maya.cmds.setAttr(tfm + '.shxz', keyable=display_shear)
    maya.cmds.setAttr(tfm + '.shyz', keyable=display_shear)
    return


def _create_bundle_shape(tfm_node):
    shp_name = tfm_node.rpartition('|')[-1] + 'Shape'
    shp = maya.cmds.createNode(
        const.BUNDLE_SHAPE_NODE_TYPE, name=shp_name, parent=tfm_node
    )
    maya.cmds.setAttr(shp + '.localPositionX', channelBox=False)
    maya.cmds.setAttr(shp + '.localPositionY', channelBox=False)
    maya.cmds.setAttr(shp + '.localPositionZ', channelBox=False)
    maya.cmds.setAttr(shp + '.localScaleX', channelBox=False)
    maya.cmds.setAttr(shp + '.localScaleY', channelBox=False)
    maya.cmds.setAttr(shp + '.localScaleZ', channelBox=False)

    # HACK: Allows the bundle to be point-snapped to. For some reason
    # the mmBundleShape does not allow users to snap objects to
    # them. By creating a locator, with no size under the same
    # transform we can work around this.
    shp_name = tfm_node.rpartition('|')[-1] + 'LocatorShape'
    locator_shp = maya.cmds.createNode('locator', name=shp_name, parent=tfm_node)
    maya.cmds.setAttr(locator_shp + '.localPositionX', channelBox=False)
    maya.cmds.setAttr(locator_shp + '.localPositionY', channelBox=False)
    maya.cmds.setAttr(locator_shp + '.localPositionZ', channelBox=False)
    maya.cmds.setAttr(locator_shp + '.localScaleX', channelBox=False)
    maya.cmds.setAttr(locator_shp + '.localScaleY', channelBox=False)
    maya.cmds.setAttr(locator_shp + '.localScaleZ', channelBox=False)
    maya.cmds.setAttr(locator_shp + '.localScaleX', 0.0)
    maya.cmds.setAttr(locator_shp + '.localScaleY', 0.0)
    maya.cmds.setAttr(locator_shp + '.localScaleZ', 0.0)
    return shp


def _set_bundle_icon(dag_path):
    icon_name = const.BUNDLE_SHAPE_ICON_NAME
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


def _replace_bundle_shape(dag_path):
    dag_shps = node_utils.get_dag_path_shapes_below_apione(dag_path)
    if len(dag_shps) > 0:
        shape_nodes = []
        bundle_shape_nodes = []
        for dag_shp in dag_shps:
            mfn_shp = OpenMaya.MFnDagNode(dag_shp)
            type_name = mfn_shp.typeName()
            if type_name != const.BUNDLE_SHAPE_NODE_TYPE:
                shape_nodes.append(dag_shp.fullPathName())
            else:
                bundle_shape_nodes.append(dag_shp.fullPathName())
        if len(bundle_shape_nodes) == 1 and len(shape_nodes) == 0:
            # For backwards compatibility with mmSolver
            # "v0.4.0-alpha*" releases.
            maya.cmds.delete(bundle_shape_nodes)
            _create_bundle_shape(dag_path.fullPathName())
        elif len(bundle_shape_nodes) == 0 and len(shape_nodes) > 0:
            maya.cmds.delete(shape_nodes)
            _create_bundle_shape(dag_path.fullPathName())
    else:
        _create_bundle_shape(dag_path.fullPathName())
    return


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
            assert isinstance(node, pycompat.TEXT_TYPE)
            assert maya.cmds.objExists(node)
            dag = node_utils.get_as_dag_path(node)
            if dag is not None:
                self._mfn = OpenMaya.MFnDagNode(dag)

            # Replace locator shape with mmBundleShape node.
            _replace_bundle_shape(dag)
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
        if isinstance(node, pycompat.TEXT_TYPE) and len(node) == 0:
            node = None
        return node

    def set_node(self, node):
        """
        This Bundle object will affect the given 'node'.

        :param node: Node to set to.
        :type node: str

        :return: Nothing.
        """
        assert isinstance(node, pycompat.TEXT_TYPE)
        assert maya.cmds.objExists(node)
        dag = node_utils.get_as_dag_path(node)
        if dag is not None:
            self._mfn = OpenMaya.MFnDagNode(dag)

            # Replace locator shape with mmBundleShape node.
            _replace_bundle_shape(dag)
        else:
            self._mfn = OpenMaya.MFnDagNode()
        return

    def get_node_uid(self):
        """
        Get the bundle transform unique identifier.

        :return: The bundle UUID or None
        :rtype: None or str or unicode
        """
        node = self.get_node()
        if node is None:
            return None
        uids = maya.cmds.ls(node, uuid=True) or []
        return uids[0]

    ############################################################################

    def create_node(self, name='bundle1', colour=None):
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
        assert isinstance(name, pycompat.TEXT_TYPE)
        if colour is not None:
            assert isinstance(colour, (tuple, list))
            assert len(colour) == 3

        # Transform
        tfm = maya.cmds.createNode(const.BUNDLE_TRANSFORM_NODE_TYPE, name=name)
        tfm = node_utils.get_long_name(tfm)

        # Show the bundle transform attributes in the channel box, but
        # the attributes are locked, so this is compatible with
        # versions before v0.3.15.
        lock_rot_scale = True
        display_rot_scale = True
        lock_shear = True
        display_shear = False
        _lock_and_display_bundle_attributes(
            tfm,
            lock_translate=False,
            lock_rotate=lock_rot_scale,
            lock_scale=lock_rot_scale,
            lock_shear=lock_shear,
            display_translate=True,
            display_rotate=display_rot_scale,
            display_scale=display_rot_scale,
            display_shear=display_shear,
        )

        # Shape Node
        _create_bundle_shape(tfm)

        self.set_node(tfm)

        # Set Colour (default is green)
        if colour is not None:
            self.set_colour_rgb(colour)
        else:
            green = (0.0, 1.0, 0.0)
            self.set_colour_rgb(green)

        event_utils.trigger_event(const.EVENT_NAME_BUNDLE_CREATED, bnd=self)
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
        Get the current RGBA colour (0.0 to 1.0) of the Bundle.

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
                node, shapes=True, fullPath=True, type=const.BUNDLE_SHAPE_NODE_TYPE
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
        Change the RGBA colour (0.0 to 1.0) of the Bundle.

        :param rgb:
           Colour as R, G, B; Or None to reset to default colour.
           Each channel is floating point; 0.0 to 1.0.
        :type rgb: tuple

        :rtype: None
        """
        if rgb is None:
            rgb = (0.0, 1.0, 0.0)
        assert isinstance(rgb, (tuple, list))
        assert len(rgb) >= 3

        node = self.get_node()
        if node is None:
            msg = 'Could not get node. self=%r'
            LOG.warn(msg, self)
            return
        shps = (
            maya.cmds.listRelatives(
                node, shapes=True, fullPath=True, type=const.BUNDLE_SHAPE_NODE_TYPE
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
        Get the current RGBA colour (0.0 to 1.0) of the Bundle.

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
                node, shapes=True, fullPath=True, type=const.BUNDLE_SHAPE_NODE_TYPE
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
        Change the RGB colour (0.0 to 1.0) of the Bundle.

        :param rgba:
            Colour as R, G, B, A; Or None to reset to default colour.
            Each channel is floating point; 0.0 to 1.0.
        :type rgba: tuple

        :rtype: None
        """
        if rgba is None:
            rgba = (0.0, 1.0, 0.0, 1.0)
        assert rgba is None or isinstance(rgba, (tuple, list))
        assert len(rgba) >= 4
        node = self.get_node()
        if node is None:
            msg = 'Could not get node. self=%r'
            LOG.warn(msg, self)
            return
        shps = (
            maya.cmds.listRelatives(
                node, shapes=True, fullPath=True, type=const.BUNDLE_SHAPE_NODE_TYPE
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

    def get_marker_list(self):
        """
        Get the list of Markers attached to this bundle.

        :return: List of Marker objects.
        :rtype: Marker
        """
        node = self.get_node()
        node_attr = node + '.message'
        conns = (
            maya.cmds.listConnections(
                node_attr,
                type=const.MARKER_TRANSFORM_NODE_TYPE,
                skipConversionNodes=True,
            )
            or []
        )
        conns += (
            maya.cmds.listConnections(
                node_attr,
                type=const.MARKER_TRANSFORM_OLD_NODE_TYPE,
                skipConversionNodes=True,
            )
            or []
        )
        mkr_list = []
        for conn in sorted(set(conns)):
            mkr = mmSolver._api.marker.Marker(node=conn)
            mkr_list.append(mkr)
        return mkr_list
