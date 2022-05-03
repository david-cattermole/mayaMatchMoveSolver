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
Finding and editing nodes connected to cameras.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.logger
import mmSolver.utils.viewport as viewport_utils
import mmSolver.utils.camera as camera_utils
import mmSolver.api as mmapi
import mmSolver.tools.cameracontextmenu.ui as ui

LOG = mmSolver.logger.get_logger()


def _get_active_camera_nodes():
    """
    Get 'active' cameras from the scene.

    This could be the selected cameras, cameras related to the
    selection, or the active viewport's camera. Start-up cameras are
    not counted as cameras.
    """
    sel = maya.cmds.ls(selection=True, long=True) or []
    node_filtered = mmapi.filter_nodes_into_categories(sel)
    camera_nodes = node_filtered['camera']
    # TODO: Should we consider image planes to get cameras from as
    #  well, not just lenses?

    lens_nodes = node_filtered['lens']
    for lens_node in lens_nodes:
        upstream_nodes = maya.cmds.listHistory(
            lens_node,
            allConnections=True,
            future=True,
            allFuture=False,
            breadthFirst=False,
        ) or []
        for upstream_node in upstream_nodes:
            obj_type = mmapi.get_object_type(upstream_node)
            if obj_type == mmapi.OBJECT_TYPE_CAMERA:
                camera_nodes.append(upstream_node)

    # Ensure we only have camera shape nodes.
    camera_nodes = [camera_utils.get_camera(x) for x in camera_nodes]
    camera_nodes = [(tfm, shp) for tfm, shp in camera_nodes
                    if shp is not None]

    camera_nodes = [(tfm, shp) for tfm, shp in camera_nodes
                    if camera_utils.is_not_startup_cam(shp)]
    if len(camera_nodes) > 0:
        return camera_nodes

    # Create a lens in the active viewport camera.
    model_editor = viewport_utils.get_active_model_editor()
    if model_editor is None:
        msg = 'Please select an active 3D viewport.'
        LOG.warn(msg)
        return []
    cam_tfm, cam_shp = viewport_utils.get_viewport_camera(model_editor)
    node = cam_shp
    if node is None:
        msg = 'Please select an active viewport to get a camera.'
        LOG.warn(msg)
        return []
    if camera_utils.is_startup_cam(node) is True:
        return []
    cam_tfm, cam_shp = camera_utils.get_camera(node)

    return [(cam_tfm, cam_shp)]


def create_menu(menu_name):
    LOG.debug('Create Lens Node menu: %r', menu_name)

    # Remove existing menu items.
    maya.cmds.popupMenu(menu_name, edit=True, deleteAllItems=True)

    camera_nodes = _get_active_camera_nodes()
    items = ui.create_camera_menu_items(menu_name, camera_nodes)

    LOG.debug('Created Lens Node menu: %r', items)
    return items
