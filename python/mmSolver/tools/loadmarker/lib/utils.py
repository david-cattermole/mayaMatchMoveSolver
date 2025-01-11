# Copyright (C) 2018, 2020, 2025 David Cattermole.
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
The Load Marker tool - user facing.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import os.path

import maya.cmds
import maya.utils

import mmSolver.logger
import mmSolver.utils.viewport as viewport_utils
import mmSolver.utils.camera as camera_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.api as mmapi
import mmSolver.tools.createcamera.lib as createcamera_lib
import mmSolver.tools.userpreferences.lib as userprefs_lib
import mmSolver.tools.markerbundlerename.lib as markerbundlerename_lib
import mmSolver.tools.markerbundlerename.constant as markerbundlerename_const


LOG = mmSolver.logger.get_logger()


def get_selected_cameras():
    """
    Return the (associated) Camera objects from the selection.

    :returns: Camera objects.
    :rtype: mmSolver.api.Camera
    """
    cams = []
    nodes = maya.cmds.ls(sl=True, long=True) or []

    added_cameras = []
    objects = mmapi.filter_nodes_into_categories(nodes)
    for node in objects[mmapi.OBJECT_TYPE_CAMERA]:
        cam = None
        if maya.cmds.nodeType(node) == 'camera':
            cam = mmapi.Camera(shape=node)
        else:
            cam = mmapi.Camera(transform=node)
        if cam is None:
            continue
        shp_node = cam.get_shape_node()
        if shp_node not in added_cameras:
            cams.append(cam)
            added_cameras.append(shp_node)

    for node in objects[mmapi.OBJECT_TYPE_MARKER]:
        mkr = mmapi.Marker(node=node)
        cam = mkr.get_camera()
        if cam is None:
            continue
        shp_node = cam.get_shape_node()
        if shp_node not in added_cameras:
            cams.append(cam)
            added_cameras.append(shp_node)

    for node in objects[mmapi.OBJECT_TYPE_MARKER_GROUP]:
        mkr_grp = mmapi.MarkerGroup(node=node)
        cam = mkr_grp.get_camera()
        if cam is None:
            continue
        shp_node = cam.get_shape_node()
        if shp_node not in added_cameras:
            cams.append(cam)
            added_cameras.append(shp_node)

    return cams


def get_cameras():
    """
    Get all cameras in the scene file.

    Start-up cameras are ignored ('persp', 'top', 'side', 'front', etc)

    :rtype: list of mmSolver.api.Camera
    """
    nodes = maya.cmds.ls(type='camera', long=True) or []
    cam_nodes = mmapi.filter_camera_nodes(nodes)
    cams = []
    for node in cam_nodes:
        startup = maya.cmds.camera(node, query=True, startupCamera=True)
        if startup is True:
            continue
        cam = mmapi.Camera(shape=node)
        cams.append(cam)
    return cams


def get_marker_groups(cam):
    """
    Get all MarkerGroups for the given camera.

    :rtype: list of mmSolver.api.MarkerGroup
    """
    mkr_grp_list = []
    if cam is None:
        return mkr_grp_list
    assert isinstance(cam, mmapi.Camera)
    if cam.is_valid() is False:
        return mkr_grp_list
    cam_tfm = cam.get_transform_node()
    below_nodes = (
        maya.cmds.ls(cam_tfm, dag=True, long=True, type='mmMarkerGroupTransform') or []
    )
    mkr_grp_list = [
        mmapi.MarkerGroup(node=n)
        for n in below_nodes
        if mmapi.get_object_type(n) == mmapi.OBJECT_TYPE_MARKER_GROUP
    ]
    return mkr_grp_list


def get_selected_markers():
    """
    Get selected Marker object.

    :rtype: list of mmSolver.api.Marker
    """
    nodes = maya.cmds.ls(selection=True, type='transform', long=True) or []
    mkr_nodes = mmapi.filter_marker_nodes(nodes)
    mkr_list = [mmapi.Marker(node=n) for n in mkr_nodes]
    return mkr_list


def set_selected_nodes(nodes):
    if len(nodes) > 0:
        maya.cmds.select(nodes, replace=True)
    return


def get_active_viewport_camera():
    """
    Get the Camera that is attached to the active viewport.

    :return: The Camera object, or None.
    :rtype: Camera or None
    """
    cam = None
    # Get the camera from the active viewport.
    model_editor = viewport_utils.get_active_model_editor()
    if model_editor is None:
        return cam
    cam_tfm, cam_shp = viewport_utils.get_viewport_camera(model_editor)
    if cam_shp is None:
        return cam
    if camera_utils.is_startup_cam(cam_shp) is True:
        return cam
    cam = mmapi.Camera(shape=cam_shp)
    return cam


def get_start_directory(file_path):
    """
    Get a start directory for a file browser window.

    :param file_path: An input
    :return:
    """
    if isinstance(file_path, pycompat.TEXT_TYPE) is False:
        msg = 'file_path must be a string.'
        raise TypeError(msg)
    start_dir = os.getcwd()
    file_path = str(file_path).strip()
    if len(file_path) > 0:
        head, tail = os.path.split(file_path)
        if os.path.isdir(head) is True:
            start_dir = head
    return start_dir


def create_new_camera():
    """
    Create a new camera nodes and object.

    :returns: Camera object.
    :rtype: Camera
    """
    return createcamera_lib.create_camera(name='camera')


def create_new_marker_group(cam):
    """
    Create a new marker group node and object.

    :param cam: The camera to create the Marker Group under.
    :type cam: Camera

    :returns: MarkerGroup object.
    :rtype: MarkerGroup
    """
    assert isinstance(cam, mmapi.Camera)
    mkr_grp = mmapi.MarkerGroup().create_node(cam=cam)
    return mkr_grp


def get_default_image_resolution():
    """
    Get image resolution from Maya Render Settings (Render 'Globals').

    :return: tuple of two ints.
    :rtype: (int, int)
    """
    w = maya.cmds.getAttr('defaultResolution.width')
    h = maya.cmds.getAttr('defaultResolution.height')
    return w, h


def trigger_maya_to_refresh():
    """
    Trigger Maya to refresh.
    """
    frame = maya.cmds.currentTime(query=True)
    maya.cmds.currentTime(frame, update=True)
    maya.cmds.refresh(currentView=True, force=False)


def deferred_revert_of_config_value(config, key, old_value):
    """Set the user preferences to a value, as a deferred fashion."""
    maya.utils.executeDeferred(lambda: userprefs_lib.set_value(config, key, old_value))
    return


def rename_markers_and_bundles(mkr_list, name):
    """
    Rename all markers and bundles with a name.
    """
    bnd_list = [mkr.get_bundle() for mkr in mkr_list]

    mkr_nodes = [mkr.get_node() for mkr in mkr_list]
    bnd_nodes = [bnd.get_node() for bnd in bnd_list]
    mkr_nodes = [mkr for mkr in mkr_nodes if mkr is not None]
    bnd_nodes = [bnd for bnd in bnd_nodes if bnd is not None]

    mkr_name = name
    bnd_name = name

    number_format = markerbundlerename_const.NUMBER_FORMAT
    mkr_suffix = markerbundlerename_const.MARKER_SUFFIX
    bnd_suffix = markerbundlerename_const.BUNDLE_SUFFIX

    changed_nodes = markerbundlerename_lib.rename_markers_and_bundles(
        mkr_nodes,
        bnd_nodes,
        mkr_name,
        bnd_name,
        number_format,
        mkr_suffix,
        bnd_suffix,
    )
    changed_mkr_nodes = mmapi.filter_marker_nodes(changed_nodes)
    return changed_mkr_nodes
