# Copyright (C) 2025 David Cattermole.
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

import mmSolver.logger
import mmSolver.utils.time as time_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.utils.node as node_utils
import mmSolver.ui.channelboxutils as channelbox_utils
import mmSolver.tools.attributecurvefilterpops.constant as const


LOG = mmSolver.logger.get_logger()


def get_frame_range(frame_range_mode, custom_start_frame, custom_end_frame):
    assert isinstance(frame_range_mode, pycompat.TEXT_TYPE)
    assert frame_range_mode in const.FRAME_RANGE_MODE_VALUES
    assert isinstance(custom_start_frame, pycompat.INT_TYPES)
    assert isinstance(custom_end_frame, pycompat.INT_TYPES)
    LOG.debug("frame_range_mode: %r", frame_range_mode)

    frame_range = None
    if frame_range_mode == const.FRAME_RANGE_MODE_TIMELINE_INNER_VALUE:
        frame_range = time_utils.get_maya_timeline_range_inner()
    elif frame_range_mode == const.FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE:
        frame_range = time_utils.get_maya_timeline_range_outer()
    elif frame_range_mode == const.FRAME_RANGE_MODE_CUSTOM_VALUE:
        frame_range = time_utils.FrameRange(custom_start_frame, custom_end_frame)
    else:
        LOG.error("Invalid frame range mode: %r", frame_range_mode)
    return frame_range


def _get_node_attrs_for_selected_keyframes():
    """Get animCurve nodes from the selected keyframes (in the graph
    editor).
    """
    selected_anim_curve_nodes = (
        maya.cmds.keyframe(query=True, selected=True, name=True) or []
    )
    node_attrs = set()
    for anim_curve_node in selected_anim_curve_nodes:
        node_attr = anim_curve_node + '.output'
        conns = (
            maya.cmds.listConnections(
                node_attr, destination=False, source=False, plugs=True
            )
            or []
        )
        node_attrs |= set(conns)
    return list(sorted(node_attrs))


def _get_selected_graph_editor_outliner_node_attributes():
    """
    Get the attributes from the selected graph editor outliner.
    """
    # NOTE: Do we need to support multiple graph editors?
    connection_object = 'graphEditor1FromOutliner'
    objects = (
        maya.cmds.selectionConnection(connection_object, query=True, object=True) or []
    )

    node_attrs = set()
    for obj in objects:
        if not isinstance(obj, pycompat.TEXT_TYPE):
            continue
        if '.' in obj:
            node_attrs.add(obj)
    return list(sorted(node_attrs))


def _get_selected_channelbox_attributes():
    """Get the selected attributes from the channel box."""
    name = channelbox_utils.get_ui_name()
    attrs = maya.cmds.channelBox(name, query=True, selectedMainAttributes=True) or []
    return attrs


def get_selected_node_attrs(nodes):
    """
    Get the selected node attributes, from the Graph Editor or
    Channel Box.

    A universal function to get whatever the user has "selected" for
    the animation curve. This includes looking at the channel box, or
    using the selected curves in the Graph Editor, etc.
    """
    node_attrs = _get_node_attrs_for_selected_keyframes()
    if len(node_attrs) > 0:
        return node_attrs

    node_attrs = _get_selected_graph_editor_outliner_node_attributes()
    if len(node_attrs) > 0:
        return node_attrs

    channelbox_attrs = _get_selected_channelbox_attributes()
    if len(channelbox_attrs) == 0:
        LOG.warn("Please select at least 1 attribute in the Channel Box.")
        return

    # Combine nodes with attributes
    node_attrs = []
    for node in nodes:
        for attr in channelbox_attrs:
            if node_utils.attribute_exists(attr, node):
                node_attr = '{}.{}'.format(node, attr)
                node_attrs.append(node_attr)

    return node_attrs


def get_attribute_anim_curves(node_attrs):
    """
    Return anim curve nodes from attributes.

    :param node_attrs: Node attribute names.
    :rtype: []
    """
    assert len(node_attrs) > 0
    assert isinstance(node_attrs, (list, set))
    anim_curve_node = maya.cmds.listConnections(node_attrs, type='animCurve') or []

    anim_curve_nodes = []
    if isinstance(anim_curve_node, pycompat.TEXT_TYPE):
        anim_curve_nodes = [anim_curve_node]
    elif isinstance(anim_curve_node, list):
        anim_curve_nodes = anim_curve_node
    return anim_curve_nodes


def filter_curves_pops(anim_curve_nodes, start_frame, end_frame, threshold):
    """
    Filter pops from curves on the attributes on nodes.

    :param anim_curve_nodes: AnimCurve nodes to filter.
    :param start_frame: Start frame to filter.
    :param end_frame: End frame to filter.
    :param threshold: The threshold to use for pop detection.
    """
    assert len(anim_curve_nodes) > 0
    assert isinstance(start_frame, pycompat.INT_TYPES)
    assert isinstance(end_frame, pycompat.INT_TYPES)
    assert isinstance(threshold, float)

    maya.cmds.mmAnimCurveFilterPops(
        anim_curve_nodes,
        startFrame=start_frame,
        endFrame=end_frame,
        threshold=threshold,
    )
    return
