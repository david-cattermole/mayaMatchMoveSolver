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
Convert a transform into a screen-space transform.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.viewport as viewport_utils
import mmSolver.utils.time as utils_time
import mmSolver.utils.animcurve as anim_utils
import mmSolver.tools.screenspacetransform.lib as lib


LOG = mmSolver.logger.get_logger()


def main():
    """
    Screen-Space Bake.

    Usage:

    1) Select transform nodes.
    2) Activate viewport.
    3) Run tool.
    4) A new locator is created under the active camera
    """
    mmapi.load_plugin()

    editor = viewport_utils.get_active_model_editor()
    if editor is None:
        LOG.error('Please select an active viewport; editor=%r', editor)
        return
    cam_tfm, cam_shp = viewport_utils.get_viewport_camera(editor)
    if cam_tfm is None or cam_shp is None:
        LOG.error('Please select a camera; cam_tfm=%r cam_shp=%r', cam_tfm, cam_shp)
        return
    cam = mmapi.Camera(transform=cam_tfm, shape=cam_shp)
    img_width = maya.cmds.getAttr(cam_shp + '.horizontalFilmAperture') * 100.0
    img_height = maya.cmds.getAttr(cam_shp + '.verticalFilmAperture') * 100.0

    nodes = maya.cmds.ls(selection=True, long=True, type='transform') or []
    if len(nodes) == 0:
        LOG.error('Please select transform nodes; %r', nodes)
        return

    start_frame, end_frame = utils_time.get_maya_timeline_range_inner()
    times = list(range(start_frame, end_frame + 1))

    created_loc_tfms = []
    for node in nodes:
        grp_node, depth_tfm, loc_tfm, loc_shp = lib.create_screen_space_locator(cam)
        created_loc_tfms.append(loc_tfm)

        # BUG: If a camera has 'camera scale' attribute set other than
        # 1.0, the reprojected values will not be correct.
        values = maya.cmds.mmReprojection(
            node,
            camera=(cam_tfm, cam_shp),
            time=times,
            asMarkerCoordinate=True,
            imageResolution=(img_width, img_height),
        )
        stop = len(values)
        step = 3

        plug = loc_tfm + '.translateX'
        values_x = list(values[0:stop:step])
        anim_utils.create_anim_curve_node_apione(times, values_x, node_attr=plug)

        plug = loc_tfm + '.translateY'
        values_y = list(values[1:stop:step])
        anim_utils.create_anim_curve_node_apione(times, values_y, node_attr=plug)

        plug = depth_tfm + '.scaleX'
        values_z = values[2:stop:step]
        anim_utils.create_anim_curve_node_apione(times, values_z, node_attr=plug)

    if len(created_loc_tfms) > 0:
        maya.cmds.select(created_loc_tfms, replace=True)

    # Trigger Maya to refresh.
    maya.cmds.currentTime(update=True)
    maya.cmds.refresh()
    return
