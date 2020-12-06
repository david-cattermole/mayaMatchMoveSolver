# Copyright (C) 2019, 2020, Anil Reddy, David Cattermole.
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
This is a Ray cast Markers tool.
"""

import maya.cmds
import maya.OpenMaya
import mmSolver.utils.node as node_utils
import mmSolver.utils.raytrace as raytrace_utils
import mmSolver.utils.reproject as reproject_utils
import mmSolver.api as mmapi
import mmSolver.logger


LOG = mmSolver.logger.get_logger()


def _get_display_layer_visibility(node):
    vis = True
    conns = maya.cmds.listConnections(node, type='displayLayer') or []
    for conn in conns:
        layer_enabled = maya.cmds.getAttr(conn + '.enabled')
        if layer_enabled is True:
            vis = maya.cmds.getAttr(conn + '.visibility')
            break
    return vis


def _node_is_visible(node, cache):
    visible = cache.get(node)
    if visible is not None:
        return visible
    intermed = maya.cmds.getAttr(node + '.intermediateObject')
    vis = maya.cmds.getAttr(node + '.visibility')
    lod_vis = maya.cmds.getAttr(node + '.lodVisibility')
    layer_vis = _get_display_layer_visibility(node)
    return (intermed is False) and vis and lod_vis and layer_vis


def _visible(node, cache):
    visible = _node_is_visible(node, cache)
    cache[node] = visible
    if visible is False:
        return False
    # Note: We assume the node paths from 'get_node_parents' will
    # always be full paths.
    parents = node_utils.get_node_parents(node)
    for parent in parents:
        visible = _node_is_visible(parent, cache)
        cache[parent] = visible
        if visible is False:
            return False
    return True


def main():
    """Ray-casts each bundle connected to the selected markers on to the
    mesh from the associated camera.

    Select markers and mesh objects to ray-cast on to, if no mesh
    objects are selected the tool will ray-cast on to all visible mesh
    objects.

    If a bundle translate attribute is locked, it will be
    unlocked, then projected, and then the lock state will
    be reverted to the original value.

    .. note::

        The Marker node is the origin point of the ray-cast, *not* the
        camera's pivot position. This is intentional. If the user has a single
        dense (LIDAR) model node it can be helpful to project from a distance
        away from the camera origin. With a single dense mesh it is difficult
        to split the model up to use different mesh selections.

    Example::

        >>> import mmSolver.tools.raycastmarker.tool as tool
        >>> tool.main()

    """
    selection = maya.cmds.ls(selection=True) or []
    if not selection:
        LOG.warning('Please select a marker to rayCast.')
        return

    selected_markers = mmapi.filter_marker_nodes(selection)
    if not selected_markers:
        LOG.warning('No markers found in the selection list.')
        return

    meshes = []
    selected_meshes = maya.cmds.ls(
        sl=True,
        type='mesh',
        dagObjects=True,
        noIntermediate=True) or []
    if len(selected_meshes) > 0:
        meshes = selected_meshes
    else:
        meshes = maya.cmds.ls(type='mesh', visible=True, long=True) or []
        cache = {}
        meshes = [n for n in meshes if _visible(n, cache)]

    max_dist = 9999999999.0
    bnd_nodes = []
    for node in selected_markers:
        mkr = mmapi.Marker(node=node)
        bnd = mkr.get_bundle()
        if bnd is None:
            continue
        mkr_node = mkr.get_node()
        camera = mkr.get_camera()
        cam_tfm = camera.get_transform_node()
        direction = reproject_utils.get_camera_direction_to_point(
            cam_tfm, mkr_node
        )
        origin_point = maya.cmds.xform(
            mkr_node, query=True,
            translation=True,
            worldSpace=True
        )

        hit_point = raytrace_utils.closest_intersect(
            origin_point,
            direction,
            meshes,
            test_both_directions=False,
            max_dist=max_dist,
            use_smooth_mesh=True
        )
        if hit_point is None:
            LOG.warning('%s didn\'t hit the mesh.' % node)
            continue

        bnd_node = bnd.get_node()
        plugs = [
            '%s.translateX' % bnd_node,
            '%s.translateY' % bnd_node,
            '%s.translateZ' % bnd_node
        ]
        plug_lock_state = {}
        for plug_name in plugs:
            value = maya.cmds.getAttr(plug_name, lock=True)
            plug_lock_state[plug_name] = value
            maya.cmds.setAttr(plug_name, lock=False)
        hit_xyz = (hit_point.x, hit_point.y, hit_point.z)
        maya.cmds.xform(
            bnd_node,
            translation=hit_xyz,
            worldSpace=True,
        )
        for plug_name in plugs:
            value = plug_lock_state.get(plug_name)
            maya.cmds.setAttr(plug_name, lock=value)
        bnd_nodes.append(bnd_node)

    if len(bnd_nodes) > 0:
        maya.cmds.select(bnd_nodes)
    else:
        maya.cmds.select(selection)
    return
