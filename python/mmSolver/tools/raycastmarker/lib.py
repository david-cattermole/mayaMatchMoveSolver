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
This is a Ray cast Markers library.
"""

import maya.cmds
import maya.OpenMaya
import mmSolver.utils.constant as utils_const
import mmSolver.utils.node as node_utils
import mmSolver.utils.raytrace as raytrace_utils
import mmSolver.utils.reproject as reproject_utils
import mmSolver.utils.time as time_utils
import mmSolver.logger


LOG = mmSolver.logger.get_logger()
BND_ATTRS = ['translateX', 'translateY', 'translateZ']


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


def is_visible_node(node, cache):
    value = _node_is_visible(node, cache)
    cache[node] = value
    if value is False:
        return False
    # Note: We assume the node paths from 'get_node_parents' will
    # always be full paths.
    parents = node_utils.get_node_parents(node)
    for parent in parents:
        value = _node_is_visible(parent, cache)
        cache[parent] = value
        if value is False:
            return False
    return True


def _get_nodes_to_raycast(mkr_list):
    node_list = []
    for mkr in mkr_list:
        mkr_node = mkr.get_node()
        bnd = mkr.get_bundle()
        if bnd is None:
            LOG.warn("Cannot ray-cast; Marker %r has no Bundle.", mkr_node)
            continue
        bnd_node = bnd.get_node()
        cam = mkr.get_camera()
        if cam is None:
            LOG.warn("Cannot ray-cast; Marker %r has no Camera.", mkr_node)
            continue
        cam_tfm = cam.get_transform_node()
        node_list.append((mkr_node, bnd_node, cam_tfm))
    return node_list


def _unlock_bundle_attrs(node_list):
    plug_lock_state = {}
    for mkr_node, bnd_node, cam_tfm in node_list:
        for attr in BND_ATTRS:
            plug_name = '{0}.{1}'.format(bnd_node, attr)
            value = maya.cmds.getAttr(plug_name, lock=True)
            plug_lock_state[plug_name] = value
            maya.cmds.setAttr(plug_name, lock=False)
    return plug_lock_state


def _relock_bundle_attrs(node_list, plug_lock_state):
    for mkr_node, bnd_node, cam_tfm in node_list:
        for attr in BND_ATTRS:
            plug_name = '{0}.{1}'.format(bnd_node, attr)
            value = plug_lock_state.get(plug_name)
            maya.cmds.setAttr(plug_name, lock=value)
    return


def _do_raycast(node_list, mesh_nodes, frame_range, max_dist, use_smooth_mesh):
    bnd_nodes = set()
    cur_frame = maya.cmds.currentTime(query=True)
    if frame_range is None:
        frame_range = time_utils.FrameRange(int(cur_frame), int(cur_frame))
    frames = range(frame_range.start, frame_range.end + 1)
    is_multi_frame = len(frames) > 1
    for frame in frames:
        maya.cmds.currentTime(frame, edit=True, update=True)
        for mkr_node, bnd_node, cam_tfm in node_list:
            assert bnd_node is not None
            assert cam_tfm is not None

            direction = reproject_utils.get_camera_direction_to_point(
                cam_tfm, mkr_node
            )
            origin_point = maya.cmds.xform(
                mkr_node, query=True,
                translation=True,
                worldSpace=True)
            hit_point = raytrace_utils.closest_intersect(
                origin_point,
                direction,
                mesh_nodes,
                test_both_directions=False,
                max_dist=max_dist,
                use_smooth_mesh=use_smooth_mesh)
            if hit_point is None:
                if is_multi_frame is False:
                    LOG.warn("%s didn't hit the mesh.", mkr_node)
                continue

            hit_xyz = (hit_point.x, hit_point.y, hit_point.z)
            maya.cmds.xform(
                bnd_node,
                translation=hit_xyz,
                worldSpace=True,
            )
            if is_multi_frame is True:
                maya.cmds.setKeyframe(bnd_node, attribute=BND_ATTRS)
            bnd_nodes.add(bnd_node)
    maya.cmds.currentTime(cur_frame, edit=True, update=True)
    return bnd_nodes


def raycast_markers_onto_meshes(mkr_list, mesh_nodes, frame_range=None,
                                unlock_bnd_attrs=None,
                                relock_bnd_attrs=None,
                                max_distance=None,
                                use_smooth_mesh=None):
    if max_distance is None:
        max_distance = utils_const.RAYTRACE_MAX_DIST
    assert frame_range is None or isinstance(frame_range, time_utils.FrameRange)

    # Get baked down list of nodes to compute.
    node_list = _get_nodes_to_raycast(mkr_list)

    # Unlock bundle attributes
    plug_lock_state = {}
    if unlock_bnd_attrs is True:
        plug_lock_state = _unlock_bundle_attrs(node_list)

    # Do the ray-casting...
    bnd_nodes = _do_raycast(
        node_list, mesh_nodes, frame_range, max_distance, use_smooth_mesh)

    # Re-lock bundle attributes
    if relock_bnd_attrs is True:
        _relock_bundle_attrs(node_list, plug_lock_state)
    return list(sorted(bnd_nodes))
