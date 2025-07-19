# Copyright (C) 2019, 2020, 2021, Anil Reddy, David Cattermole.
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
import maya.api.OpenMaya as OpenMaya2

import mmSolver.logger

import mmSolver.utils.constant as utils_const
import mmSolver.utils.node as node_utils
import mmSolver.utils.raytrace as raytrace_utils
import mmSolver.utils.reproject as reproject_utils
import mmSolver.utils.time as time_utils
import mmSolver.utils.transform as tfm_utils
import mmSolver.api as mmapi

import mmSolver.tools.raycastmarker.constant as const


LOG = mmSolver.logger.get_logger()
BND_TRANSLATE_ATTRS = ['translateX', 'translateY', 'translateZ']
BND_ROTATE_ATTRS = ['rotateX', 'rotateY', 'rotateZ']


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
        if mkr_node is None:
            LOG.warn("Cannot ray-cast; Marker %r is not valid.", mkr_node)
            continue
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
        cam_shp = cam.get_shape_node()
        has_lens = node_utils.attribute_exists('outLens', cam_shp)
        node_list.append((mkr_node, bnd_node, cam_tfm, cam_shp, has_lens))
    return node_list


def _get_bundle_modify_attributes(bundle_rotate_mode):
    attrs = list(BND_TRANSLATE_ATTRS)
    modify_modes = [
        const.BUNDLE_ROTATE_MODE_AIM_AT_CAMERA_VALUE,
        const.BUNDLE_ROTATE_MODE_MESH_NORMAL_VALUE,
    ]
    if bundle_rotate_mode in modify_modes:
        attrs += list(BND_ROTATE_ATTRS)
    return attrs


def _unlock_bundle_attrs(node_list, bundle_rotate_mode):
    plug_lock_state = {}
    attrs = _get_bundle_modify_attributes(bundle_rotate_mode)
    for _, bnd_node, _, _, _ in node_list:
        for attr in attrs:
            plug_name = '{0}.{1}'.format(bnd_node, attr)
            value = maya.cmds.getAttr(plug_name, lock=True)
            plug_lock_state[plug_name] = value
            maya.cmds.setAttr(plug_name, lock=False)
    return plug_lock_state


def _relock_bundle_attrs(node_list, plug_lock_state, bundle_rotate_mode):
    attrs = _get_bundle_modify_attributes(bundle_rotate_mode)
    for _, bnd_node, _, _, _ in node_list:
        for attr in attrs:
            plug_name = '{0}.{1}'.format(bnd_node, attr)
            value = plug_lock_state.get(plug_name)
            maya.cmds.setAttr(plug_name, lock=value)
    return


def _create_look_at_matrix(dir_x, dir_y, dir_z):
    forward = OpenMaya2.MVector(dir_x, dir_y, dir_z).normal()
    right = OpenMaya2.MVector(0.0, 1.0, 0.0) ^ forward
    up = forward ^ right
    right.normalize()
    up.normalize()

    mat = OpenMaya2.MMatrix()
    mat.setToIdentity()
    mat.setElement(0, 0, right.x)
    mat.setElement(0, 1, right.y)
    mat.setElement(0, 2, right.z)
    mat.setElement(1, 0, up.x)
    mat.setElement(1, 1, up.y)
    mat.setElement(1, 2, up.z)
    mat.setElement(2, 0, forward.x)
    mat.setElement(2, 1, forward.y)
    mat.setElement(2, 2, forward.z)
    return mat


def _do_raycast(
    node_list,
    mesh_nodes,
    frame_range,
    max_dist,
    use_smooth_mesh,
    bundle_rotate_mode,
):
    bnd_nodes = set()
    cur_frame = maya.cmds.currentTime(query=True)
    if frame_range is None:
        frame_range = time_utils.FrameRange(int(cur_frame), int(cur_frame))
    frames = range(frame_range.start, frame_range.end + 1)
    is_multi_frame = len(frames) > 1
    keyable_attrs = _get_bundle_modify_attributes(bundle_rotate_mode)
    for frame in frames:
        maya.cmds.currentTime(frame, edit=True, update=True)
        for mkr_node, bnd_node, cam_tfm, cam_shp, has_lens in node_list:
            assert mkr_node is not None
            assert bnd_node is not None
            assert cam_tfm is not None
            assert cam_shp is not None
            assert isinstance(has_lens, bool)

            origin_point = maya.cmds.mmReprojection(
                mkr_node,
                camera=(cam_tfm, cam_shp),
                time=(frame,),
                # NOTE: We don't need to account for lens distortion
                # here (at least in Maya 2024), because the Marker
                # transform node is already un-distorting
                # automatically.
                distortMode=utils_const.DISTORT_MODE_NONE,
                asWorldPoint=True,
            )

            direction = reproject_utils.get_camera_direction_to_world_position(
                cam_tfm,
                origin_point,
            )
            hit_point, hit_normal = raytrace_utils.closest_intersect_with_normal(
                origin_point,
                direction,
                mesh_nodes,
                test_both_directions=False,
                max_dist=max_dist,
                use_smooth_mesh=use_smooth_mesh,
            )
            if hit_point is None:
                if is_multi_frame is False:
                    LOG.warn("%s didn't hit the mesh.", mkr_node)
                continue
            hit_xyz = (hit_point.x, hit_point.y, hit_point.z)
            hit_normal = (hit_normal.x, hit_normal.y, hit_normal.z)

            maya.cmds.xform(
                bnd_node,
                translation=hit_xyz,
                worldSpace=True,
            )

            # Set rotations.
            if bundle_rotate_mode == const.BUNDLE_ROTATE_MODE_NO_CHANGE_VALUE:
                pass
            elif bundle_rotate_mode in [
                const.BUNDLE_ROTATE_MODE_AIM_AT_CAMERA_VALUE,
                const.BUNDLE_ROTATE_MODE_MESH_NORMAL_VALUE,
            ]:
                mat = None
                if bundle_rotate_mode == const.BUNDLE_ROTATE_MODE_AIM_AT_CAMERA_VALUE:
                    mat = _create_look_at_matrix(
                        -direction[0], -direction[1], -direction[2]
                    )
                elif bundle_rotate_mode == const.BUNDLE_ROTATE_MODE_MESH_NORMAL_VALUE:
                    mat = _create_look_at_matrix(
                        hit_normal[0], hit_normal[1], hit_normal[2]
                    )

                rotate_order = maya.cmds.xform(bnd_node, query=True, rotateOrder=True)
                rotate_order_api = tfm_utils.ROTATE_ORDER_STR_TO_APITWO_CONSTANT[
                    rotate_order
                ]

                tfm_mat = OpenMaya2.MTransformationMatrix(mat)
                tfm_mat.reorderRotation(rotate_order_api)
                prev_rot = (0.0, 0.0, 0.0)
                components = tfm_utils.decompose_matrix(tfm_mat, prev_rot)
                _, _, _, rx, ry, rz, _, _, _ = components
                maya.cmds.xform(
                    bnd_node,
                    rotation=(rx, ry, rz),
                    worldSpace=True,
                )

            else:
                msg = 'Invalid bundle rotate mode: ' % bundle_rotate_mode
                raise NotImplementedError(msg)

            if is_multi_frame is True:
                maya.cmds.setKeyframe(bnd_node, attribute=keyable_attrs)
            bnd_nodes.add(bnd_node)
    maya.cmds.currentTime(cur_frame, edit=True, update=True)
    return bnd_nodes


def raycast_markers_onto_meshes(
    mkr_list,
    mesh_nodes,
    frame_range=None,
    unlock_bnd_attrs=None,
    relock_bnd_attrs=None,
    max_distance=None,
    use_smooth_mesh=None,
    bundle_rotate_mode=None,
):
    if max_distance is None:
        max_distance = utils_const.RAYTRACE_MAX_DIST
    if bundle_rotate_mode is None:
        bundle_rotate_mode = const.BUNDLE_ROTATE_MODE_NO_CHANGE_VALUE
    assert bundle_rotate_mode in const.BUNDLE_ROTATE_MODE_VALUES
    assert frame_range is None or isinstance(frame_range, time_utils.FrameRange)

    # Get baked down list of nodes to compute.
    node_list = _get_nodes_to_raycast(mkr_list)

    # Unlock bundle attributes
    plug_lock_state = {}
    if unlock_bnd_attrs is True:
        plug_lock_state = _unlock_bundle_attrs(node_list, bundle_rotate_mode)

    # Ensure the plug-in is loaded, to use mmReprojection command.
    mmapi.load_plugin()

    # Do the ray-casting...
    bnd_nodes = _do_raycast(
        node_list,
        mesh_nodes,
        frame_range,
        max_distance,
        use_smooth_mesh,
        bundle_rotate_mode,
    )

    # Avoid euler flips in the rotation.
    if (
        len(bnd_nodes) > 0
        and bundle_rotate_mode != const.BUNDLE_ROTATE_MODE_NO_CHANGE_VALUE
    ):
        maya.cmds.filterCurve(list(bnd_nodes))

    # Re-lock bundle attributes
    if relock_bnd_attrs is True:
        _relock_bundle_attrs(node_list, plug_lock_state, bundle_rotate_mode)
    return list(sorted(bnd_nodes))
