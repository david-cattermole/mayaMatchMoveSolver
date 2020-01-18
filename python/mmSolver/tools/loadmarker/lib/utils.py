# Copyright (C) 2018, 2020 David Cattermole.
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

import os
import os.path
import pprint
import math

import maya.cmds

import mmSolver.logger
import mmSolver.utils.node as node_utils
import mmSolver.utils.viewport as viewport_utils
import mmSolver.utils.camera as camera_utils
import mmSolver.tools.loadmarker.lib.formatmanager as formatmanager
import mmSolver.tools.loadmarker.lib.mayareadfile as mayareadfile
import mmSolver.tools.loadmarker.lib.interface as interface
import mmSolver.api as mmapi


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
    for node in objects['camera']:
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

    for node in objects['marker']:
        mkr = mmapi.Marker(node=node)
        cam = mkr.get_camera()
        if cam is None:
            continue
        shp_node = cam.get_shape_node()
        if shp_node not in added_cameras:
            cams.append(cam)
            added_cameras.append(shp_node)

    for node in objects['markergroup']:
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
    below_nodes = maya.cmds.ls(
        cam_tfm, dag=True, long=True,
        type='mmMarkerGroupTransform') or []
    mkr_grp_list = [mmapi.MarkerGroup(node=n) for n in below_nodes
                    if mmapi.get_object_type(n) == mmapi.OBJECT_TYPE_MARKER_GROUP]
    return mkr_grp_list


def get_selected_markers():
    """
    Get selected Marker object.

    :rtype: list of mmSolver.api.Marker
    """
    nodes = maya.cmds.ls(
        selection=True,
        type='transform',
        long=True) or []
    mkr_nodes = mmapi.filter_marker_nodes(nodes)
    mkr_list = [mmapi.Marker(node=n) for n in mkr_nodes]
    return mkr_list


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


def get_file_path_format(text):
    """
    Look up the Format from the file path.

    :param text: File path text.

    :returns: Format for the file path, or None if not found.
    :rtype: None or Format
    """
    format_ = None
    if isinstance(text, (str, unicode)) is False:
        return format_
    if os.path.isfile(text) is False:
        return format_
    fmt_mgr = formatmanager.get_format_manager()
    fmts = fmt_mgr.get_formats()
    ext_to_fmt = {}
    for fmt in fmts:
        for ext in fmt.file_exts:
            ext_to_fmt[ext] = fmt
    for ext, fmt in ext_to_fmt.items():
        if text.endswith(ext):
            format_ = fmt
            break
    return format_


def is_valid_file_path(text):
    """
    Is the given text a file path we can load as a marker?

    :param text: A possible file path string.
    :type text: str

    :returns: File path validity.
    :rtype: bool
    """
    assert isinstance(text, (str, unicode))
    fmt = get_file_path_format(text)
    valid = fmt is not None
    return valid


def get_file_info(file_path):
    """
    Get the file path information.

    :param file_path: The marker file path to get info for.
    :type file_path: str

    :return:
    :rtype: FileInfo
    """
    file_info, _ = mayareadfile.read(file_path)
    return file_info


def get_file_info_strings(file_path):
    """
    Get the file path information, as user-readable strings.

    :param file_path: The marker file path to get info for.
    :type file_path: str

    :return Dictionary of various information about the given
            file path.
    :rtype: dict
    """
    info = {
        'num_points': '?',
        'point_names': '?',
        'frame_range': '?-?',
        'start_frame': '?',
        'end_frame': '?',
        'lens_dist': '?',
        'lens_undist': '?',
        'positions': '?',
        'has_camera_fov': '?',
    }
    file_info, mkr_data_list = mayareadfile.read(file_path)
    if isinstance(mkr_data_list, list) is False:
        return info

    fmt = get_file_path_format(file_path)
    info['fmt'] = fmt
    info['fmt_name'] = str(fmt.name)

    info['num_points'] = str(len(mkr_data_list))
    start_frame = int(999999)
    end_frame = int(-999999)
    point_names = []
    for mkr_data in mkr_data_list:
        name = mkr_data.get_name()
        point_names.append(name)

        # Get start / end frame.
        # We assume that there are X and Y keyframes on each frame,
        # therefore we do not test Y.
        x_keys = mkr_data.get_x()
        x_start = x_keys.get_start_frame()
        x_end = x_keys.get_end_frame()
        if x_start < start_frame:
            start_frame = x_start
        if x_end > end_frame:
            end_frame = x_end

    info['point_names'] = ' '.join(point_names)
    info['start_frame'] = start_frame
    info['end_frame'] = end_frame
    info['frame_range'] = '{0}-{1}'.format(start_frame, end_frame)
    info['lens_dist'] = file_info.marker_distorted
    info['lens_undist'] = file_info.marker_undistorted
    info['positions'] = file_info.bundle_positions
    info['has_camera_fov'] = bool(file_info.camera_field_of_view)
    return info


def get_file_filter():
    """
    Construct a string to be given to QFileDialog as a file filter.

    :return: String of file filters, separated by ';;' characters.
    :rtype: str
    """
    file_fmt_names = []
    file_exts = []
    fmt_mgr = formatmanager.get_format_manager()
    fmts = fmt_mgr.get_formats()
    for fmt in fmts:
        file_fmt_names.append(fmt.name)
        file_exts += fmt.file_exts
    file_fmt_names = sorted(file_fmt_names)
    file_exts = sorted(file_exts)

    extensions_str = ''
    for file_ext in file_exts:
        extensions_str += '*' + file_ext + ' '

    file_filter = 'Marker Files (%s);;' % extensions_str
    for name in file_fmt_names:
        name = name + ';;'
        file_filter += name
    file_filter += 'All Files (*.*);;'
    return file_filter


def get_start_directory(file_path):
    """
    Get a start directory for a file browser window.

    :param file_path: An input
    :return:
    """
    if isinstance(file_path, (str, unicode)) is False:
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
    name = 'camera'
    cam_tfm = maya.cmds.createNode(
        'transform',
        name=name)
    cam_tfm = node_utils.get_long_name(cam_tfm)
    cam_shp = maya.cmds.createNode(
        'camera',
        name=name + 'Shape',
        parent=cam_tfm)
    cam_shp = node_utils.get_long_name(cam_shp)
    cam = mmapi.Camera(transform=cam_tfm, shape=cam_shp)
    return cam


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