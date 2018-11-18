"""
The Load Marker tool - user facing.
"""

import maya.cmds
import mmSolver.api as mmapi
import mmSolver.logger
import mmSolver.tools.selection.filternodes as filternodes
import mmSolver.tools.loadmarker.formatmanager as formatmanager

LOG = mmSolver.logger.get_logger(level='DEBUG')


def main(file_path, cam=None, **kwargs):
    pass


def get_selected_cameras():
    cams = []
    nodes = maya.cmds.ls(sl=True, long=True) or []

    added_cameras = []
    objects = filternodes.get_nodes(nodes)
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
        mkr = mmapi.Marker(name=node)
        cam = mkr.get_camera()
        if cam is None:
            continue
        shp_node = cam.get_shape_node()
        if shp_node not in added_cameras:
            cams.append(cam)
            added_cameras.append(shp_node)

    for node in objects['markergroup']:
        mkr_grp = mmapi.MarkerGroup(name=node)
        cam = mkr_grp.get_camera()
        if cam is None:
            continue
        shp_node = cam.get_shape_node()
        if shp_node not in added_cameras:
            cams.append(cam)
            added_cameras.append(shp_node)

    return cams


def get_cameras():
    nodes = maya.cmds.ls(type='camera', long=True) or []
    cam_nodes = filternodes.get_camera_nodes(nodes)
    cams = []
    for node in cam_nodes:
        startup = maya.cmds.camera(node, query=True, startupCamera=True)
        if startup is True:
            continue
        cam = mmapi.Camera(shape=node)
        cams.append(cam)
    return cams


def is_valid_file_path(text):
    valid = False
    file_exts = []
    fmt_mgr = formatmanager.get_format_manager()
    fmts = fmt_mgr.get_formats()
    for fmt in fmts:
        LOG.debug('format: %r', fmt)
        LOG.debug('name: %r', fmt.name)
        LOG.debug('ext: %r', fmt.file_exts)
        file_exts += list(fmt.file_exts)
    for ext in file_exts:
        if text.endswith(ext):
            valid = True
            break
    return valid


def create_new_camera():
    name = 'camera'
    cam_tfm = maya.cmds.createNode(
        'transform',
        name=name)
    cam_tfm = mmapi.get_long_name(cam_tfm)
    cam_shp = maya.cmds.createNode(
        'camera',
        name=name + 'Shape',
        parent=cam_tfm)
    cam_shp = mmapi.get_long_name(cam_shp)
    cam = mmapi.Camera(transform=cam_tfm, shape=cam_shp)
    return cam
