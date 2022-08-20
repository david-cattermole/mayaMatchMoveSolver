# Copyright (C) 2019 David Cattermole.
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
The 'Convert to Marker' tool.
"""

import warnings

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.camera as utils_camera
import mmSolver.utils.viewport as utils_viewport
import mmSolver.utils.tools as tools_utils
import mmSolver.utils.time as time_utils
import mmSolver.tools.convertmarker.lib as lib
import mmSolver.tools.convertmarker.constant as const


LOG = mmSolver.logger.get_logger()


def main(
    frame_range_mode=None,
    start_frame=None,
    end_frame=None,
    bundle_position_mode=None,
    delete_static_anim_curves=None,
):
    """
    Convert all selected transforms into 2D markers under a camera.

    :param frame_range_mode: The type of frame range to use, see
       'mmSolver.utils.constant.FRAME_RANGE_MODE_*_VALUE' for more
       details.
    :type frame_range_mode: FRAME_RANGE_MODE_*_VALUE

    :param start_frame: The first frame to start converting the
       transform to a Marker.
    :type start_frame: int or None

    :param end_frame: The last frame to end converting the
       transform to a Marker.
    :type end_frame: int or None

    :param bundle_position_mode: The position for the newly created
       Bundle (connected to the Marker).
    :type bundle_position_mode: None or BUNDLE_POSITION_MODE_*

    :param delete_static_anim_curves: When enabled, this will remove
       all keyframes from the bundle, if the bundle is not animated.
    :type delete_static_anim_curves: bool

    """
    if frame_range_mode is None:
        value = configmaya.get_scene_option(
            const.CONFIG_FRAME_RANGE_MODE_KEY, default=const.DEFAULT_FRAME_RANGE_MODE
        )
        assert value in const.FRAME_RANGE_MODE_VALUES
        frame_range_mode = value

    if start_frame is None or end_frame is None:
        start_frame = configmaya.get_scene_option(
            const.CONFIG_FRAME_START_KEY, default=const.DEFAULT_FRAME_START
        )
        end_frame = configmaya.get_scene_option(
            const.CONFIG_FRAME_END_KEY, default=const.DEFAULT_FRAME_END
        )

    if bundle_position_mode is None:
        value = configmaya.get_scene_option(
            const.CONFIG_BUNDLE_POSITION_MODE_KEY,
            default=const.DEFAULT_BUNDLE_POSITION_MODE,
        )
        bundle_position_mode = value

    if delete_static_anim_curves is None:
        value = configmaya.get_scene_option(
            const.CONFIG_DELETE_STATIC_ANIM_CURVES_KEY,
            default=const.DEFAULT_DELETE_STATIC_ANIM_CURVES,
        )
        delete_static_anim_curves = value

    # Frame range
    time_utils.get_frame_range(
        frame_range_mode, start_frame=start_frame, end_frame=end_frame
    )

    # Get camera
    model_editor = utils_viewport.get_active_model_editor()
    if model_editor is None:
        msg = 'Please select an active 3D viewport.'
        LOG.warning(msg)
        return

    cam_tfm, cam_shp = utils_viewport.get_viewport_camera(model_editor)
    if cam_shp is None:
        LOG.error('Please select an active viewport to get a camera.')
        return
    if utils_camera.is_startup_cam(cam_shp) is True:
        LOG.error("Cannot create Markers in 'persp' camera.")
        return

    # Get transforms
    tfm_nodes = (
        maya.cmds.ls(
            selection=True,
            long=True,
            type='transform',
        )
        or []
    )
    if len(tfm_nodes) == 0:
        LOG.warning('Please select one or more transform nodes.')
        return

    # Must ensure the plug-in is loaded, otherwise we won't have all
    # the functionality required.
    mmapi.load_plugin()

    with tools_utils.tool_context(pre_update_frame=True):
        mkr_nodes, bnd_nodes = lib.create_markers_from_transforms(
            cam_tfm,
            cam_shp,
            tfm_nodes,
            start_frame,
            end_frame,
            bundle_position_mode,
            delete_static_anim_curves,
        )

    if len(mkr_nodes) > 0:
        maya.cmds.select(mkr_nodes, replace=True)
    return


def convert_to_marker():
    warnings.warn("Use 'main' function instead.", DeprecationWarning)
    main()


def open_window():
    import mmSolver.tools.convertmarker.ui.convertmarker_window as window

    window.main()
