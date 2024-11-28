# Copyright (C) 2018, 2019, 2020, 2022 David Cattermole.
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
Convert mmSolver API objects into UI objects that can be used in Qt models.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time

import mmSolver.logger

import mmSolver.api as mmapi
import mmSolver.tools.solver.ui.attr_nodes as attr_nodes
import mmSolver.tools.solver.ui.object_nodes as object_nodes

LOG = mmSolver.logger.get_logger()


def _generateCameraUINode(cam, mkr, line, root_node, cam_nodes_store, show_cam):
    assert isinstance(cam, mmapi.Camera)
    assert mkr is None or isinstance(mkr, mmapi.Marker)
    assert line is None or isinstance(line, mmapi.Line)
    assert isinstance(root_node, object_nodes.ObjectNode)

    if show_cam is False:
        cam_node = root_node
    else:
        cam_tfm_node = cam.get_transform_node()
        cam_name = cam.get_transform_node()
        cam_name = cam_name.rpartition('|')[-1]
        cam_node = None
        if cam_tfm_node in cam_nodes_store:
            cam_node = cam_nodes_store[cam_tfm_node]
        else:
            cam_uuid = cam.get_transform_uid()
            data = {
                'uuid': cam_uuid,
                'marker': mkr,
                'line': line,
                'camera': cam,
            }
            cam_node = object_nodes.CameraNode(cam_name, data=data, parent=root_node)
            cam_nodes_store[cam_tfm_node] = cam_node
    assert cam_node is not None
    return cam_node


def _generateMarkerUINodes(cam, mkr, bnd, root_node, mkr_name, show_mkr, show_bnd):
    assert isinstance(cam, mmapi.Camera)
    assert mkr is None or isinstance(mkr, mmapi.Marker)
    assert bnd is None or isinstance(bnd, mmapi.Bundle)
    assert isinstance(root_node, object_nodes.ObjectNode)

    mkr_node = root_node
    if show_mkr is True:
        mkr_uuid = mkr.get_node_uid()
        data = {
            'uuid': mkr_uuid,
            'marker': mkr,
            'camera': cam,
        }
        mkr_node = object_nodes.MarkerNode(mkr_name, data=data, parent=root_node)

    # Get Bundle under marker.
    if bnd is None:
        return
    if show_bnd is False:
        return
    bnd_name = bnd.get_node()
    bnd_name = bnd_name.rpartition('|')[-1]
    bnd_uuid = bnd.get_node_uid()
    data = {
        'marker': mkr,
        'bundle': bnd,
        'camera': cam,
        'uuid': bnd_uuid,
    }
    assert mkr_node is not None
    # bnd_node = object_nodes.BundleNode(bnd_name, data=data, parent=mkr_node)
    return


def _markersToUINodes(
    mkr_list,
    root_node,
    mkr_nodes_store_set,
    cam_nodes_store_dict,
    show_cam,
    show_mkr,
    show_bnd,
):
    assert isinstance(mkr_nodes_store_set, set)
    assert isinstance(show_cam, bool)
    assert isinstance(show_mkr, bool)
    assert isinstance(show_bnd, bool)

    for mkr in mkr_list:
        cam = mkr.get_camera()
        line = None
        cam_node = _generateCameraUINode(
            cam, mkr, line, root_node, cam_nodes_store_dict, show_cam
        )

        # Only Markers not seen will be displayed. This allows Markers to be
        # shown under Lines, but not duplicated under cameras as well.
        mkr_node = mkr.get_node()
        if mkr_node not in mkr_nodes_store_set:
            mkr_name = mkr_node.rpartition('|')[-1]
            bnd = mkr.get_bundle()
            _generateMarkerUINodes(
                cam, mkr, bnd, cam_node, mkr_name, show_mkr, show_bnd
            )
            mkr_nodes_store_set.add(mkr_node)

    return root_node


def _linesToUINodes(
    line_list,
    root_node,
    mkr_nodes_store_set,
    cam_nodes_store_dict,
    show_mkr,
    show_bnd,
    show_cam,
    show_line,
):
    assert isinstance(mkr_nodes_store_set, set)
    assert isinstance(cam_nodes_store_dict, dict)
    assert isinstance(show_cam, bool)
    assert isinstance(show_line, bool)

    if show_line is False:
        return

    for line in line_list:
        cam = line.get_camera()
        mkr = None
        cam_node = _generateCameraUINode(
            cam, mkr, line, root_node, cam_nodes_store_dict, show_cam
        )
        if cam_node is None:
            continue

        line_uuid = line.get_node_uid()
        data = {
            'uuid': line_uuid,
            'line': line,
            'camera': cam,
        }
        line_name = line.get_node()
        line_name = line_name.rpartition('|')[-1]
        line_node = object_nodes.LineNode(line_name, data=data, parent=cam_node)

        mkr_list = line.get_marker_list()
        for mkr in mkr_list:
            mkr_node = mkr.get_node()
            mkr_name = mkr_node.rpartition('|')[-1]
            bnd = mkr.get_bundle()
            _generateMarkerUINodes(
                cam, mkr, bnd, line_node, mkr_name, show_mkr, show_bnd
            )
            mkr_nodes_store_set.add(mkr_node)

    return


def solverObjectsToUINodes(
    mkr_list, line_list, show_cam, show_mkr, show_bnd, show_line
):
    """
    Convert a list of markers and lines into a hierarchy to show the user.

    :param mkr_list: List of Marker objects to convert into UI nodes.
    :type mkr_list: [Marker, ..]

    :param line_list: List of Marker objects to convert into UI nodes.
    :type line_list: [Line, ..]

    :param show_cam: Should we show cameras?
    :type show_cam: bool

    :param show_mkr: Should we show markers?
    :type show_mkr: bool

    :param show_bnd: Should we show bundles?
    :type show_bnd: bool

    :param show_line: Should we show lines?
    :type show_line: bool

    :return: A root node for a tree of UI ObjectNode objects.
    :rtype: ObjectNode
    """
    s = time.time()
    assert isinstance(show_cam, bool)
    assert isinstance(show_mkr, bool)
    assert isinstance(show_bnd, bool)
    assert isinstance(show_line, bool)
    root_node = object_nodes.ObjectNode('root')

    # This is a cache filled by functions below.
    mkr_nodes_store_set = set()
    cam_nodes_store_dict = {}

    _linesToUINodes(
        line_list,
        root_node,
        mkr_nodes_store_set,
        cam_nodes_store_dict,
        show_mkr,
        show_bnd,
        show_cam,
        show_line,
    )
    _markersToUINodes(
        mkr_list,
        root_node,
        mkr_nodes_store_set,
        cam_nodes_store_dict,
        show_cam,
        show_mkr,
        show_bnd,
    )

    e = time.time()
    LOG.debug('solverObjectsToUINodes: %r seconds', e - s)
    return root_node


def attributesToUINodes(col, attr_list, show_anm, show_stc, show_lck):
    """
    Convert a list of mmSolver API Attributes into classes to be used
    in the Solver UI.

    :param col: The Collection the Attributes belong to.
    :param col: Collection

    :param attr_list: List of Attributes to convert.
    :type attr_list: [Attribute, ..]

    :param show_anm: Should the animated attributes be visible?
    :type show_anm: bool

    :param show_stc: Should the static attributes be visible?
    :type show_stc: bool

    :param show_lck: Should the locked attributes be visible?
    :type show_lck: bool

    :returns: A hierarchy of UI nodes to be viewed in a 'tree view'.
    :rtype: PlugNode
    """
    s = time.time()
    root = attr_nodes.PlugNode('root')
    maya_nodes = dict()
    for attr in attr_list:
        attr_state = attr.get_state()
        is_animated = attr_state == mmapi.ATTR_STATE_ANIMATED
        is_static = attr_state == mmapi.ATTR_STATE_STATIC
        is_locked = attr_state == mmapi.ATTR_STATE_LOCKED
        if is_animated is True and show_anm is False:
            continue
        elif is_static is True and show_stc is False:
            continue
        elif is_locked is True and show_lck is False:
            continue
        full_name = attr.get_node(full_path=True)
        maya_node = maya_nodes.get(full_name)
        data = {'data': attr, 'collection': col}
        if maya_node is None:
            node_data = dict()
            # Add only the first attribute to the MayaNode
            # object. Other attributes will be added as they come up.
            node_data['data'] = [attr]
            node_data['uuid'] = attr.get_node_uid()
            short_name = full_name.rpartition('|')[-1]
            maya_node = attr_nodes.MayaNode(short_name, data=node_data, parent=root)
            maya_node.setNeverHasChildren(False)
            maya_nodes[full_name] = maya_node
        else:
            # Add subsequent attributes to the MayaNode object.
            node_data = maya_node.data()
            node_data['data'].append(attr)
            maya_node.setData(node_data)

        attr_name = attr.get_attr_alias_name()
        if attr_name is None:
            attr_name = attr.get_attr_nice_name()

        attr_node = attr_nodes.AttrNode(attr_name, data=data, parent=maya_node)
        attr_node.setNeverHasChildren(True)
    e = time.time()
    LOG.debug('attributesToUINodes: %r seconds', e - s)
    return root
