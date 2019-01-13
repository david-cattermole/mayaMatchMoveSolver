"""
The Convert to Marker tool.
"""

import maya.cmds
import maya.mel
import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.loadmarker.mayareadfile as mayareadfile
import mmSolver.tools.loadmarker.interface as loadmkr_interface


LOG = mmSolver.logger.get_logger()


def __get_model_editor():
    """
    Get the active model editor.
    """
    the_panel = maya.cmds.getPanel(withFocus=1)
    panel_type = maya.cmds.getPanel(typeOf=the_panel)

    if panel_type != 'modelPanel':
        return None

    model_ed = maya.cmds.modelPanel(the_panel, modelEditor=1, query=1)
    return model_ed


def __get_camera():
    """
    Get the camera from the active model editor

    :returns: Camera shape node name or None.
    :rtype: None or basestring
    """
    model_ed = __get_model_editor()
    cam = None
    cam_shp = None
    if model_ed is not None:
        cam = maya.cmds.modelEditor(model_ed, query=True, camera=True)
    if maya.cmds.nodeType(cam) == 'transform':
        shps = maya.cmds.listRelatives(
            cam,
            children=True,
            shapes=True,
            fullPath=True
        ) or []
        if len(shps) > 0:
            cam_shp = shps[0]
    elif maya.cmds.nodeType(cam) == 'camera':
        cam_shp = maya.cmds.ls(cam, long=True)[0]
    else:
        LOG.error('Should not get here: cam=%r' % cam)
    return cam_shp


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
    maya.cmds.connectAttr(cam_shp + '.horizontalFilmAperture', mult_node + '.input1X')
    maya.cmds.connectAttr(cam_shp + '.verticalFilmAperture', mult_node + '.input1Y')
    maya.cmds.setAttr(mult_node + '.input2X', 10000.0)
    maya.cmds.setAttr(mult_node + '.input2Y', 10000.0)
    maya.cmds.connectAttr(mult_node + '.outputX', node + '.imageWidth')
    maya.cmds.connectAttr(mult_node + '.outputY', node + '.imageHeight')
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


def __get_timeline_range_inner():
    s = maya.cmds.playbackOptions(query=True, minTime=True)
    e = maya.cmds.playbackOptions(query=True, maxTime=True)
    return int(s), int(e)


def convert_to_marker():
    """
    Center the selected transform onto the camera view.
    """
    # Get camera
    cam_shp = __get_camera()
    if cam_shp is None:
        LOG.warning('Please select an active viewport to get a camera.')
        return
    cam_tfm = maya.cmds.listRelatives(cam_shp, parent=True)[0]

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
        start_frame, end_frame = __get_timeline_range_inner()
        mkr_data_list = __convert_nodes_to_marker_data_list(
            cam_tfm,
            cam_shp,
            nodes,
            start_frame,
            end_frame
        )

        cam = mmapi.Camera(shape=cam_shp)
        mayareadfile.create_nodes(
            mkr_data_list,
            cam=cam,
            mkr_grp=None,
            with_bundles=False,
        )
    except:
        raise
    finally:
        maya.mel.eval('paneLayout -e -manage true $gMainPane')  # turn on Maya UI
    return
