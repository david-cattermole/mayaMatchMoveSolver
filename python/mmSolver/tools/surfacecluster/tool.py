# Copyright (C) 2014, 2022, 2023 David Cattermole.
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
Create (and Edit) Surface Clusters.

Surface Clusters can be used to deform a surface, starting from the
surface position and orientation.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.tools.surfacecluster.constant as const
import mmSolver.tools.surfacecluster.lib as lib
import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.selection as selection_utils


LOG = mmSolver.logger.get_logger()


def create_single_surface_cluster():
    """
    Create a Surface Cluster on the selected Mesh component.

    Usage:
    1) Select 1 or more components (vertices, edges, faces, etc).
    2) Run this tool.
       - create a single surface cluster at the average position of all selected
         components.
       - (Optionally) Use current Soft Selection as default weighting - the
         same as the "update_weights_with_soft_selection" tool.

    :returns: None or a SurfaceCluster object with the nodes making up
        the setup.
    :rtype: SurfaceCluster or None
    """
    # Find the selected vertex/edge/face components.
    verts = selection_utils.get_mesh_vertex_selection()
    edges = selection_utils.get_mesh_edge_selection()
    faces = selection_utils.get_mesh_face_selection()
    component = None
    if (verts is not None) and (len(verts) == 1):
        component = verts[0]
    elif (edges is not None) and (len(edges) == 1):
        component = edges[0]
    elif (faces is not None) and (len(faces) == 1):
        component = faces[0]
    else:
        LOG.error(
            'Must have only one vertex, edge or face selected '
            '(and optionally a soft selection).'
        )
        return

    surface_cluster = lib.create_surface_cluster_on_component(component)
    if surface_cluster is None:
        LOG.error('Could not create surface cluster!')
        return

    maya.cmds.select(surface_cluster.control_transform, replace=True)
    return surface_cluster


def create_multiple_surface_clusters():
    """
    Create multiple surface clusters, one for each component
    selected.

    Usage:
    1) Select 1 or more components (vertices, edges, faces, etc).
    2) Run this tool.
       - For each component, create a surface cluster is created.

    :returns: A list of SurfaceCluster objects with the nodes making up
        the setup. The list may be empty.
    :rtype: [SurfaceCluster, ..] or []
    """
    # Find the selected vertex/edge/face components.
    verts = selection_utils.get_mesh_vertex_selection()
    edges = selection_utils.get_mesh_edge_selection()
    faces = selection_utils.get_mesh_face_selection()
    components = []
    if (verts is not None) and (len(verts) > 0):
        components += verts
    elif (edges is not None) and (len(edges) > 0):
        components += edges
    elif (faces is not None) and (len(faces) > 0):
        components += faces
    else:
        LOG.error('Please select at least one Mesh vertex, edge or face.')
        return

    surface_clusters = []
    for component in components:
        surface_cluster = lib.create_surface_cluster_on_component(component)
        if isinstance(surface_cluster, lib.SurfaceCluster):
            surface_clusters.append(surface_cluster)

    control_tfms = [x.control_transform for x in surface_clusters]
    if len(control_tfms) > 0:
        maya.cmds.select(control_tfms, replace=True)
    return surface_clusters


def update_weights_with_soft_selection():
    """
    Update the cluster deformer weights using the current
    component soft-selection.

    Usage:
    1) Enable Soft Selection.
    2) Select 1 or more components (vertices, edges, faces, etc).
    3) Select surface cluster control.
    4) Run this tool.
       - The weights of the surface cluster are updated with the soft
         selection.

    :rtype: None
    """
    sel = maya.cmds.ls(selection=True, long=True) or []
    tfms = [x for x in sel if maya.cmds.nodeType(x) == 'transform']
    if len(sel) == 0 or len(tfms) != 1:
        LOG.error(
            'Please select 1 Surface Cluster Control '
            'and some mesh components (with soft-selection enabled).'
        )
        return
    control_tfm = tfms[0]

    # Ensure soft-selection is enabled, if not error.
    soft_select_enabled = maya.cmds.softSelect(query=True, softSelectEnabled=True)
    if soft_select_enabled is False:
        LOG.warn(
            'Soft-Selection is not enabled, '
            'please enable soft-selection to update surface cluster weights.'
        )
        return

    # Get the selected surface cluster transform.
    surface_cluster = lib.get_surface_cluster_from_control_transform(control_tfm)
    if surface_cluster is None:
        LOG.error(
            'Could not find Surface Cluster from Control transform: %r', control_tfm
        )
        return

    # Get the selected vertex/edge/face components.
    verts = selection_utils.get_mesh_vertex_selection()
    edges = selection_utils.get_mesh_edge_selection()
    faces = selection_utils.get_mesh_face_selection()
    components = []
    if (verts is not None) and (len(verts) > 0):
        components += verts
    elif (edges is not None) and (len(edges) > 0):
        components += edges
    elif (faces is not None) and (len(faces) > 0):
        components += faces
    else:
        LOG.error('Please select at least one Mesh vertex, edge or face.')
        return

    try:
        # Update the surface cluster weights with the soft-selection
        # weights.
        maya.cmds.select(components, replace=True)
        soft_selection_weights = selection_utils.get_soft_selection_weights(
            only_shape_node=surface_cluster.mesh_shape
        )
        if len(soft_selection_weights) > 0:
            soft_selection_weights = soft_selection_weights[0]
            lib.set_cluster_deformer_weights(
                surface_cluster.cluster_deformer_node,
                surface_cluster.mesh_shape,
                soft_selection_weights,
            )
    finally:
        maya.cmds.select(sel, replace=True)
    return


def open_paint_weights_tool():
    """
    Open the paint weights tool for the selected surface cluster.

    Usage:
    1) Select a surface cluster control.
    2) Run tool.
       - The paint weights tool is opened.
    3) User paints weights.

    :rtype: None
    """
    sel = maya.cmds.ls(selection=True, long=True) or []
    tfms = [x for x in sel if maya.cmds.nodeType(x) == 'transform']
    if len(sel) == 0 or len(tfms) != 1:
        LOG.error('Please select only 1 Surface Cluster Control.')
        return
    control_tfm = tfms[0]

    # Get the selected surface cluster transform.
    surface_cluster = lib.get_surface_cluster_from_control_transform(control_tfm)
    if surface_cluster is None:
        LOG.error(
            'Could not find Surface Cluster from Control transform: %r', control_tfm
        )
        return

    # Open paint weights tool.
    lib.paint_cluster_weights_on_mesh(
        surface_cluster.mesh_transform, surface_cluster.cluster_deformer_node
    )
    return


def main():
    """
    Create surface clusters using the values defined in the UI.

    Use open_window() function to open the UI to edit the values as
    needed.

    :rtype: None
    """
    name = const.CONFIG_CREATE_MODE_KEY
    create_mode = configmaya.get_scene_option(name, default=const.DEFAULT_CREATE_MODE)
    LOG.debug('key=%r value=%r', name, create_mode)

    name = const.CONFIG_OPEN_PAINT_WEIGHTS_KEY
    open_paint_weights = configmaya.get_scene_option(
        name, default=const.DEFAULT_OPEN_PAINT_WEIGHTS
    )
    LOG.debug('key=%r value=%r', name, open_paint_weights)
    assert isinstance(open_paint_weights, bool)

    if create_mode == const.CREATE_MODE_SINGLE_VALUE:
        surface_cluster = create_single_surface_cluster()
        if surface_cluster is not None and open_paint_weights is True:
            lib.paint_cluster_weights_on_mesh(
                surface_cluster.mesh_transform, surface_cluster.cluster_deformer_node
            )
    elif create_mode == const.CREATE_MODE_MULTIPLE_VALUE:
        surface_clusters = create_multiple_surface_clusters()
        if len(surface_clusters) > 0 and open_paint_weights is True:
            surface_cluster = surface_cluster[0]
            lib.paint_cluster_weights_on_mesh(
                surface_cluster.mesh_transform, surface_cluster.cluster_deformer_node
            )
    else:
        LOG.error("Surface Cluster Create Mode is invalid; %r", create_mode)
    return


def open_window():
    """
    Open the Surface Cluster UI.

    :rtype: None
    """
    import mmSolver.tools.surfacecluster.ui.surfacecluster_window as window

    window.main()
