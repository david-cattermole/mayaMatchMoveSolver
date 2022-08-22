# Copyright (C) 2022 David Cattermole.
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
Set Camera to the origin, at a specific frame.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import datetime
import uuid

import maya.cmds

import mmSolver.logger
import mmSolver.utils.camera as camera_utils
import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.node as node_utils
import mmSolver.utils.time as time_utils
import mmSolver.utils.tools as tools_utils
import mmSolver.api as mmapi
import mmSolver.tools.setcameraoriginframe.constant as const
import mmSolver.tools.setcameraoriginframe.lib as lib

LOG = mmSolver.logger.get_logger()
BUNDLE_ATTRS = ['translateX', 'translateY', 'translateZ']


def _get_camera_bundle_lists(cam_list):
    cam_bnd_list_map = collections.defaultdict(list)
    for cam in cam_list:
        mkr_list = cam.get_marker_list()
        for mkr in mkr_list:
            assert isinstance(mkr, mmapi.Marker)
            bnd = mkr.get_bundle()
            if bnd is not None:
                bnd_node = bnd.get_node()
                is_locked = False
                for attr in BUNDLE_ATTRS:
                    node_attr = '{}.{}'.format(bnd_node, attr)
                    locked = maya.cmds.getAttr(node_attr, lock=True)
                    if locked is True:
                        is_locked = True
                        break
                if is_locked is True:
                    LOG.warn("Locked bundle, skipping: %s", bnd_node)
                    continue
                cam_bnd_list_map[cam].append(bnd)
    return cam_bnd_list_map


def main():
    """
    Offset the camera's animation so the current frame is at origin.

    Bundles are moved along with the camera, so that camera-space is maintained.

    Usage:

    1. Select camera nodes.
    2. Run tool
    3. Camera and any connected bundles will be offset to current frame.

    """
    sel = maya.cmds.ls(selection=True, long=True) or []
    cam_shps = set()
    for node in sel:
        cam_tfm, cam_shp = camera_utils.get_camera(node)
        if cam_shp is not None:
            cam_shps.add(cam_shp)

    cam_list = []
    for cam_shp in sorted(cam_shps):
        cam = mmapi.Camera(shape=cam_shp)
        cam_list.append(cam)
    if len(cam_list) == 0:
        LOG.warn('Please select cameras.')
        return

    cam_bnd_list_map = _get_camera_bundle_lists(cam_list)

    current_frame = maya.cmds.currentTime(query=True)
    start_frame, end_frame = time_utils.get_maya_timeline_range_inner()

    scene_scale = configmaya.get_scene_option(
        const.CONFIG_SCENE_SCALE_KEY, default=const.DEFAULT_SCENE_SCALE
    )
    create_group = configmaya.get_scene_option(
        const.CONFIG_CREATE_GROUP_KEY, default=const.DEFAULT_CREATE_GROUP
    )

    undo_id = 'setcameraoriginframe: '
    undo_id += str(datetime.datetime.isoformat(datetime.datetime.now()))
    undo_id += ' '
    undo_id += str(uuid.uuid4())
    with tools_utils.tool_context(
        use_undo_chunk=True,
        undo_chunk_name=undo_id,
        restore_current_frame=True,
        use_dg_evaluation_mode=False,
        disable_viewport=False,
    ):
        for cam, bnd_list in cam_bnd_list_map.items():
            lib.set_camera_origin_frame(
                cam, bnd_list, scene_scale, current_frame, start_frame, end_frame
            )

            if create_group is True:
                group_node = lib.get_origin_group(cam)
                if group_node is None:
                    group_node = lib.create_origin_group(cam)
                lib.parent_under_origin_group(group_node, cam, bnd_list)

    if len(sel) > 0:
        cam_tfm_nodes = [x.get_transform_node() for x in cam_list]
        maya.cmds.select(cam_tfm_nodes, replace=True)
    maya.cmds.currentTime(current_frame, edit=True, update=True)
    return


def open_window():
    import mmSolver.tools.setcameraoriginframe.ui.originframe_window as window

    window.main()
