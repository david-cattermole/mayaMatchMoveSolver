"""
The 'Convert to Marker' tool.
"""

import warnings

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.camera as utils_camera
import mmSolver.utils.viewport as utils_viewport
import mmSolver.utils.time as utils_time
import mmSolver.tools.loadmarker.mayareadfile as mayareadfile
import mmSolver.tools.loadmarker.interface as loadmkr_interface


LOG = mmSolver.logger.get_logger()


def __connect_transform_to_reprojection(tfm, reproj):
    src = tfm + '.worldMatrix'
    dst = reproj + '.transformWorldMatrix'
    maya.cmds.connectAttr(src, dst)
    return


def __create_reprojection_node(cam_tfm, cam_shp):
    """
    Create a mmReprojection node, then connect it up as needed.
    """
    node = maya.cmds.createNode('mmReprojection')

    # Connect camera attributes
    maya.cmds.connectAttr(cam_tfm + '.worldMatrix', node + '.cameraWorldMatrix')
    maya.cmds.connectAttr(cam_shp + '.focalLength', node + '.focalLength')
    maya.cmds.connectAttr(cam_shp + '.cameraAperture', node + '.cameraAperture')
    maya.cmds.connectAttr(cam_shp + '.filmOffset', node + '.filmOffset')
    maya.cmds.connectAttr(cam_shp + '.filmFit', node + '.filmFit')
    maya.cmds.connectAttr(cam_shp + '.nearClipPlane', node + '.nearClipPlane')
    maya.cmds.connectAttr(cam_shp + '.farClipPlane', node + '.farClipPlane')
    maya.cmds.connectAttr(cam_shp + '.cameraScale', node + '.cameraScale')

    # Force the image width and height to be the same aspect as the
    # film back.
    mult_node = maya.cmds.createNode('multiplyDivide')

    src = cam_shp + '.horizontalFilmAperture'
    dst = mult_node + '.input1X'
    maya.cmds.connectAttr(src, dst)

    src = cam_shp + '.verticalFilmAperture'
    dst = mult_node + '.input1Y'
    maya.cmds.connectAttr(src, dst)

    maya.cmds.setAttr(mult_node + '.input2X', 10000.0)
    maya.cmds.setAttr(mult_node + '.input2Y', 10000.0)

    src = mult_node + '.outputX'
    dst = node + '.imageWidth'
    maya.cmds.connectAttr(src, dst)

    src = mult_node + '.outputY'
    dst = node + '.imageHeight'
    maya.cmds.connectAttr(src, dst)
    return node


def __convert_nodes_to_marker_data_list(cam_tfm, cam_shp,
                                        nodes,
                                        start_frame, end_frame):
    # Create nodes and objects for loop.
    node_pairs = []
    reproj_nodes = []
    mkr_data_list = []
    for node in nodes:
        reproj = __create_reprojection_node(cam_tfm, cam_shp)
        __connect_transform_to_reprojection(node, reproj)
        reproj_nodes.append(reproj)

        mkr_data = loadmkr_interface.MarkerData()
        mkr_data.set_name(node)
        mkr_data_list.append(mkr_data)

        node_pairs.append((node, reproj, mkr_data))

    # Query Screen-space coordinates across time for all nodes
    cur_time = maya.cmds.currentTime(query=True)
    for f in xrange(start_frame, end_frame + 1):
        maya.cmds.currentTime(f, edit=True, update=True)
        for node, reproj, mkr_data in node_pairs:
            node_attr = reproj + '.outNormCoord'
            mkr_u = maya.cmds.getAttr(node_attr + 'X')
            mkr_v = maya.cmds.getAttr(node_attr + 'Y')
            mkr_enable = True
            mkr_weight = 1.0

            mkr_data.weight.set_value(f, mkr_weight)
            mkr_data.enable.set_value(f, mkr_enable)
            mkr_data.x.set_value(f, mkr_u)
            mkr_data.y.set_value(f, mkr_v)

    if len(reproj_nodes) > 0:
        maya.cmds.delete(reproj_nodes)

    maya.cmds.currentTime(cur_time, edit=True, update=True)
    return mkr_data_list


def main():
    """
    Convert all selected transforms into 2D markers under a camera.
    """
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
    nodes = maya.cmds.ls(
        selection=True,
        long=True,
        type='transform',
    ) or []
    if len(nodes) == 0:
        LOG.warning('Please select one or more transform nodes.')
        return

    mmapi.load_plugin()
    try:
        # Turn off Maya UI
        maya.mel.eval('paneLayout -e -manage false $gMainPane')

        # Compute the Marker Data.
        start_frame, end_frame = utils_time.get_maya_timeline_range_outer()
        mkr_data_list = __convert_nodes_to_marker_data_list(
            cam_tfm,
            cam_shp,
            nodes,
            start_frame,
            end_frame,
        )

        cam = mmapi.Camera(shape=cam_shp)
        mkr_list = mayareadfile.create_nodes(
            mkr_data_list,
            cam=cam,
            mkr_grp=None,
            with_bundles=True,
        )
        mkr_nodes = [mkr.get_node() for mkr in mkr_list]
    except:
        raise
    finally:
        # Turn on Maya UI
        maya.mel.eval('paneLayout -e -manage true $gMainPane')
    if len(mkr_nodes) > 0:
        maya.cmds.select(mkr_nodes, replace=True)
    return


def convert_to_marker():
    warnings.warn("Use 'main' function instead.")
    main()
