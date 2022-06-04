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
The Create Line tool.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.viewport as utils_viewport
import mmSolver.utils.camera as utils_camera


LOG = mmSolver.logger.get_logger()


def main():
    """
    Create a new line under the current viewport camera, or under
    the selected camera, if a camera is selected.
    """
    mmapi.load_plugin()

    sel = maya.cmds.ls(sl=True, long=True)
    node_filtered = mmapi.filter_nodes_into_categories(sel)
    cams = node_filtered['camera']
    cams = list(filter(utils_camera.is_not_startup_cam, cams))
    mkr_grps = node_filtered['markergroup']

    cam = None
    mkr_grp = None
    if len(cams) > 0 and len(mkr_grps) > 0:
        msg = 'Please select a camera or marker group; ' 'both node types are selected.'
        LOG.error(msg)
        return

    elif len(cams) == 0 and len(mkr_grps) == 0:
        # Create a Line under the active viewport camera.
        model_editor = utils_viewport.get_active_model_editor()
        if model_editor is None:
            msg = 'Please select an active 3D viewport.'
            LOG.warning(msg)
            return
        cam_tfm, cam_shp = utils_viewport.get_viewport_camera(model_editor)
        node = cam_shp
        if node is None:
            msg = 'Please select an active viewport to get a camera.'
            LOG.error(msg)
            return
        if utils_camera.is_startup_cam(node) is True:
            msg = "Cannot create Lines in 'persp' camera."
            LOG.error(msg)
            return
        if maya.cmds.nodeType(node) == 'transform':
            cam = mmapi.Camera(transform=node)
        elif maya.cmds.nodeType(node) == 'camera':
            cam = mmapi.Camera(shape=node)
        else:
            LOG.error('Camera node is invalid; %r', node)
            return

    elif len(cams) > 0 and len(mkr_grps) == 0:
        # Create a Line under the selected camera.
        node = cams[0]
        if maya.cmds.nodeType(node) == 'transform':
            cam = mmapi.Camera(transform=node)
        elif maya.cmds.nodeType(node) == 'camera':
            cam = mmapi.Camera(shape=node)
        else:
            LOG.error('Camera node is invalid; %r', node)
            return

    elif len(cams) == 0 and len(mkr_grps) > 0:
        # Create a line under the first selected Marker Group.
        node = mkr_grps[0]
        mkr_grp = mmapi.MarkerGroup(node=node)

    else:
        LOG.error('Should not get here.')
        return

    line_name = mmapi.get_new_line_name('line1')
    line = mmapi.Line().create_node(
        name=line_name,
        cam=cam,
        mkr_grp=mkr_grp,
    )
    mkr_list = line.get_marker_list()
    mkr_nodes = [mkr.get_node() for mkr in mkr_list]

    line_node = line.get_node()
    maya.cmds.select(mkr_nodes, replace=True)
    return
