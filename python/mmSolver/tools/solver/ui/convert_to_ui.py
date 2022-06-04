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
"""
Convert mmSolver API objects into UI objects that can be used in Qt models.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.logger

import mmSolver.api as mmapi
import mmSolver.tools.solver.lib.solver_step as solver_step
import mmSolver.tools.solver.ui.attr_nodes as attr_nodes
import mmSolver.tools.solver.ui.object_nodes as object_nodes
import mmSolver.tools.solver.ui.solver_nodes as solver_nodes


LOG = mmSolver.logger.get_logger()


def markersToUINodes(mkr_list, show_cam, show_mkr, show_bnd):
    """
    Convert a list of markers into a hierarchy to show the user.

    :param mkr_list: List of Marker objects to convert into UI nodes.
    :type mkr_list: [Marker, ..]

    :param show_cam: Should we show cameras?
    :type show_cam: bool

    :param show_mkr: Should we show markers?
    :type show_mkr: bool

    :param show_bnd: Should we show bundles?
    :type show_bnd: bool

    :return: A list of UI MarkerNode objects.
    :rtype: [MarkerNode, ..]
    """
    assert isinstance(show_cam, bool)
    assert isinstance(show_mkr, bool)
    assert isinstance(show_bnd, bool)
    root = object_nodes.ObjectNode('root')
    cam_nodes_store = {}
    for mkr in mkr_list:
        mkr_name = mkr.get_node()
        mkr_name = mkr_name.rpartition('|')[-1]
        cam = mkr.get_camera()
        bnd = mkr.get_bundle()

        # Get camera
        if show_cam is False:
            cam_node = root
        else:
            cam_tfm_node = cam.get_transform_node()
            cam_name = cam.get_transform_node()
            cam_name = cam_name.rpartition('|')[-1]
            cam_node = None
            if cam_tfm_node not in cam_nodes_store:
                cam_uuid = cam.get_transform_uid()
                data = {
                    'uuid': cam_uuid,
                    'marker': mkr,
                    'camera': cam,
                }
                cam_node = object_nodes.CameraNode(cam_name, data=data, parent=root)
                cam_nodes_store[cam_tfm_node] = cam_node
            else:
                cam_node = cam_nodes_store[cam_tfm_node]
        assert cam_node is not None

        # The marker.
        mkr_node = cam_node
        if show_mkr is True:
            mkr_uuid = mkr.get_node_uid()
            data = {
                'uuid': mkr_uuid,
                'marker': mkr,
                'camera': cam,
            }
            mkr_node = object_nodes.MarkerNode(mkr_name, data=data, parent=cam_node)

        # Get Bundle under marker.
        if bnd is None:
            continue
        if show_bnd is False:
            continue
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
        bnd_node = object_nodes.BundleNode(bnd_name, data=data, parent=mkr_node)
    return root


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
            short_name = full_name.rpartition('|')[-1]
            maya_node = attr_nodes.MayaNode(short_name, data=node_data, parent=root)
            maya_node.setNeverHasChildren(False)
            maya_nodes[full_name] = maya_node
        else:
            # Add subsequent attributes to the MayaNode object.
            node_data = maya_node.data()
            node_data['data'].append(attr)
            maya_node.setData(node_data)
        a = attr.get_attr()
        attr_node = attr_nodes.AttrNode(a, data=data, parent=maya_node)
        attr_node.setNeverHasChildren(True)
    return root


def solverStepsToUINodes(step_list, col):
    node_list = []
    for step in step_list:
        assert isinstance(step, solver_step.SolverStep) is True
        name = step.get_name()
        node = solver_nodes.SolverStepNode(name, col)
        node_list.append(node)
    return node_list
