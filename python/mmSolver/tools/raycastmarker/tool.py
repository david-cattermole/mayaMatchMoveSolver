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
This is a Ray cast Markers tool.
"""

import maya.cmds
import maya.OpenMaya
import mmSolver.utils.tools as tools_utils
import mmSolver.utils.camera as camera_utils
import mmSolver.utils.viewport as viewport_utils
import mmSolver.utils.time as time_utils
import mmSolver.utils.configmaya as configmaya
import mmSolver.api as mmapi
import mmSolver.logger

import mmSolver.tools.raycastmarker.constant as const
import mmSolver.tools.raycastmarker.lib as lib

LOG = mmSolver.logger.get_logger()


def _get_active_or_selected_camera(cam_node_list):
    active_cam_tfm = None
    active_cam_shp = None
    if len(cam_node_list) > 0:
        cam_node = cam_node_list[0]
        active_cam_tfm, active_cam_shp = camera_utils.get_camera(cam_node)
    else:
        model_editor = viewport_utils.get_active_model_editor()
        if model_editor is not None:
            active_cam_tfm, active_cam_shp = viewport_utils.get_viewport_camera(
                model_editor)
    return active_cam_tfm, active_cam_shp


def _add_unique_markers_to_list(mkr, mkr_list, mkr_uid_list):
    """
    Warning: Modifies the mkr_list and mkr_uid_list lists inside this function.
    """
    mkr_uid = mkr.get_node_uid()
    if mkr_uid not in mkr_uid_list:
        mkr_list.append(mkr)
        mkr_uid_list.add(mkr_uid)


def _get_markers(mkr_node_list, bnd_node_list, active_cam_shp):
    use_camera = False
    mkr_list = []
    mkr_uid_list = set()

    if len(mkr_node_list) > 0:
        for mkr_node in mkr_node_list:
            mkr = mmapi.Marker(node=mkr_node)
            _add_unique_markers_to_list(mkr, mkr_list, mkr_uid_list)

    if len(bnd_node_list) > 0:
        for bnd_node in bnd_node_list:
            bnd = mmapi.Bundle(node=bnd_node)
            bnd_mkr_list = bnd.get_marker_list()
            if len(bnd_mkr_list) == 1:
                # There can only be one possible marker to project from
                mkr = bnd_mkr_list[0]
                cam = mkr.get_camera()
                if cam is None:
                    continue
                _add_unique_markers_to_list(mkr, mkr_list, mkr_uid_list)
            else:
                for mkr in bnd_mkr_list:
                    cam = mkr.get_camera()
                    if cam is None:
                        continue
                    mkr_cam_shp = cam.get_shape_node()
                    if active_cam_shp != mkr_cam_shp:
                        continue
                    use_camera = True
                    _add_unique_markers_to_list(mkr, mkr_list, mkr_uid_list)
    return mkr_list, use_camera


def _get_selected_meshes():
    mesh_nodes = []
    selected_meshes = maya.cmds.ls(
        sl=True,
        type='mesh',
        dagObjects=True,
        noIntermediate=True) or []
    if len(selected_meshes) > 0:
        mesh_nodes = selected_meshes
    else:
        mesh_nodes = maya.cmds.ls(type='mesh', visible=True, long=True) or []
        cache = {}
        mesh_nodes = [n for n in mesh_nodes if lib.is_visible_node(n, cache)]
    return mesh_nodes


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

    node_categories = mmapi.filter_nodes_into_categories(selection)
    mkr_node_list = node_categories['marker']
    bnd_node_list = node_categories['bundle']
    cam_node_list = node_categories['camera']
    if len(mkr_node_list) == 0 and len(bnd_node_list) == 0:
        LOG.warn('Please select markers or bundles to ray-cast.')
        return

    # The camera used to determine where bundles will be projected from.
    active_cam_tfm, active_cam_shp = _get_active_or_selected_camera(
        cam_node_list)

    # Get Markers
    mkr_list, use_camera = _get_markers(
        mkr_node_list, bnd_node_list, active_cam_shp)
    if use_camera and active_cam_shp is None:
        LOG.warn('Please activate a viewport to ray-cast Bundles from.')

    frame_range_mode = configmaya.get_scene_option(
        const.CONFIG_FRAME_RANGE_MODE_KEY,
        default=const.DEFAULT_FRAME_RANGE_MODE)

    frame_start = configmaya.get_scene_option(
        const.CONFIG_FRAME_START_KEY,
        default=const.DEFAULT_FRAME_START)
    frame_end = configmaya.get_scene_option(
        const.CONFIG_FRAME_END_KEY,
        default=const.DEFAULT_FRAME_END)
    if frame_range_mode == const.FRAME_RANGE_MODE_CURRENT_FRAME_VALUE:
        frame_start = int(maya.cmds.currentTime(query=True))
        frame_end = frame_start
    elif frame_range_mode == const.FRAME_RANGE_MODE_TIMELINE_INNER_VALUE:
        frame_start, frame_end = time_utils.get_maya_timeline_range_inner()
    elif frame_range_mode == const.FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE:
        frame_start, frame_end = time_utils.get_maya_timeline_range_outer()
    frame_range = time_utils.FrameRange(frame_start, frame_end)

    use_smooth_mesh = True
    bundle_rotate_mode = configmaya.get_scene_option(
        const.CONFIG_BUNDLE_ROTATE_MODE_KEY,
        default=const.DEFAULT_BUNDLE_ROTATE_MODE)
    bundle_unlock_relock = configmaya.get_scene_option(
        const.CONFIG_BUNDLE_UNLOCK_RELOCK_KEY,
        default=const.DEFAULT_BUNDLE_UNLOCK_RELOCK)

    # Do not disable the viewport if we're only baking a single frame.
    disable_viewport = True
    if frame_range.start == frame_range.end:
        disable_viewport = False

    mesh_nodes = _get_selected_meshes()
    with tools_utils.tool_context(
            use_undo_chunk=True,
            restore_current_frame=True,
            use_dg_evaluation_mode=True,
            disable_viewport=disable_viewport):
        bnd_nodes = lib.raycast_markers_onto_meshes(
            mkr_list, mesh_nodes,
            frame_range=frame_range,
            unlock_bnd_attrs=bundle_unlock_relock,
            relock_bnd_attrs=bundle_unlock_relock,
            use_smooth_mesh=use_smooth_mesh,
            bundle_rotate_mode=bundle_rotate_mode)
        if len(bnd_nodes) > 0:
            maya.cmds.select(bnd_nodes)
        else:
            maya.cmds.select(selection)
    return


def open_window():
    import mmSolver.tools.raycastmarker.ui.raycastmarker_window as window
    window.main()
