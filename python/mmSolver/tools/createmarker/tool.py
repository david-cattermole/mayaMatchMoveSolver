"""
The Create Marker tool.
"""

import warnings

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.viewport as utils_viewport
import mmSolver.utils.camera as utils_camera
import mmSolver.tools.selection.filternodes as filter_nodes


LOG = mmSolver.logger.get_logger()


def main():
    """
    Create a new marker under the current viewport camera, or under
    the selected camera, if a camera is selected.
    """
    mmapi.load_plugin()

    sel = maya.cmds.ls(sl=True, long=True)
    node_filtered = filter_nodes.get_nodes(sel)
    cams = node_filtered['camera']
    cams = filter(utils_camera.is_not_startup_cam, cams)
    mkr_grps = node_filtered['markergroup']

    cam = None
    mkr_grp = None
    if len(cams) > 0 and len(mkr_grps) > 0:
        msg = (
            'Please select a camera or marker group; '
            'both node types are selected.'
        )
        LOG.error(msg)

    elif len(cams) == 0 and len(mkr_grps) == 0:
        # Create a Marker under the active viewport camera.
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
            msg = "Cannot create Markers in 'persp' camera."
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
        # Create a Marker under the selected camera.
        node = cams[0]
        if maya.cmds.nodeType(node) == 'transform':
            cam = mmapi.Camera(transform=node)
        elif maya.cmds.nodeType(node) == 'camera':
            cam = mmapi.Camera(shape=node)
        else:
            LOG.error('Camera node is invalid; %r', node)
            return

    elif len(cams) == 0 and len(mkr_grps) > 0:
        # Create a marker under the first selected Marker Group.
        node = mkr_grps[0]
        mkr_grp = mmapi.MarkerGroup(name=node)

    else:
        LOG.error('Should not get here.')

    bnd_name = mmapi.get_bundle_name('bundle1')
    bnd = mmapi.Bundle().create_node(
        name=bnd_name
    )

    mkr_name = mmapi.get_marker_name('marker1')
    mkr = mmapi.Marker().create_node(
        name=mkr_name,
        cam=cam,
        mkr_grp=mkr_grp,
        bnd=bnd
    )

    maya.cmds.select(mkr.get_node(), replace=True)
    return


def create_marker():
    warnings.warn("Use 'main' function instead.")
    main()
