"""
The Center 2D tool.
"""

import warnings

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.node as node_utils
import mmSolver.utils.viewport as viewport_utils


LOG = mmSolver.logger.get_logger()


def __connect_camera_and_transform(cam_tfm, cam_shp, tfm):
    """
    Create a mmReprojection node, then connect it up as needed.
    """
    node = maya.cmds.createNode('mmReprojection')

    # Connect transform
    maya.cmds.connectAttr(tfm + '.worldMatrix', node + '.transformWorldMatrix')

    # Connect camera attributes
    maya.cmds.connectAttr(cam_tfm + '.worldMatrix', node + '.cameraWorldMatrix')
    maya.cmds.connectAttr(cam_shp + '.focalLength', node + '.focalLength')
    maya.cmds.connectAttr(cam_shp + '.cameraAperture', node + '.cameraAperture')
    maya.cmds.connectAttr(cam_shp + '.filmOffset', node + '.filmOffset')
    maya.cmds.connectAttr(cam_shp + '.filmFit', node + '.filmFit')
    maya.cmds.connectAttr(cam_shp + '.nearClipPlane', node + '.nearClipPlane')
    maya.cmds.connectAttr(cam_shp + '.farClipPlane', node + '.farClipPlane')
    maya.cmds.connectAttr(cam_shp + '.cameraScale', node + '.cameraScale')

    # Connect render settings attributes
    resolution_factor = 10000.0
    mult_node = maya.cmds.createNode('multiplyDivide')
    maya.cmds.setAttr(mult_node + '.input2X', resolution_factor)
    maya.cmds.setAttr(mult_node + '.input2Y', resolution_factor)
    maya.cmds.connectAttr(cam_shp + '.horizontalFilmAperture', mult_node + '.input1X')
    maya.cmds.connectAttr(cam_shp + '.verticalFilmAperture', mult_node + '.input1Y')
    maya.cmds.connectAttr(mult_node + '.outputX', node + '.imageWidth')
    maya.cmds.connectAttr(mult_node + '.outputY', node + '.imageHeight')

    # Connect Pan to camera.pan
    maya.cmds.connectAttr(node + '.outPan', cam_shp + '.pan')

    # Turn on 'Pan/Zoom'
    plug = cam_shp + '.panZoomEnabled'
    locked = maya.cmds.getAttr(plug, lock=True)
    if locked is False:
        maya.cmds.setAttr(plug, True)
    return node


def __find_reprojection_nodes(cam_tfm, cam_shp):
    """
    Find all the reprojection nodes on the camera.
    """
    nodes = maya.cmds.listConnections(
        cam_shp + '.pan',
        source=True,
        destination=False,
        type='mmReprojection',
        exactType=True,
        skipConversionNodes=True
    ) or []
    # Get connected MultiplyDivide nodes connected.
    for node in list(nodes):
        mult_nodes = maya.cmds.listConnections(
            node + '.imageWidth', 
            node + '.imageHeight',
            source=True,
            destination=False,
            type='multiplyDivide',
            exactType=True,
            skipConversionNodes=True
        ) or []
        nodes += mult_nodes
    return nodes


def __remove_reprojection(cam_tfm, cam_shp):
    """
    Find the mmReprojection node and delete it.
    """
    nodes = __find_reprojection_nodes(cam_tfm, cam_shp)
    for node in reversed(nodes):
        if node.objExists(node) is True:
            maya.cmds.delete(node)
    return


def __reset_pan_zoom(cam_tfm, cam_shp):
    """
    Reset the Pan/Zoom camera settings.

    :param cam_tfm: Camera transform node
    :type cam_tfm: str

    :param cam_shp: Camera shape node.
    :type cam_shp: str

    :rtype: None
    """
    plugs = [
        (cam_shp + '.horizontalPan', 0.0),
        (cam_shp + '.verticalPan', 0.0),
        (cam_shp + '.zoom', 1.0),
        (cam_shp + '.panZoomEnabled', False),
    ]
    for plug, value in plugs:
        node_utils.set_attr(plug, value, relock=True)
    return


def main():
    """
    Center the selected transform onto the camera view.

    .. todo::

        - Allow 2D Center on selected vertices.

        - Support Stereo-camera setups (center both cameras, and ensure
          both have the same zoom).

        - Allow centering on multiple objects at once. We will center
          on the middle of all transforms.

    """
    mmapi.load_plugin()

    model_editor = viewport_utils.get_active_model_editor()
    if model_editor is None:
        msg = 'Please select an active 3D viewport.'
        LOG.warning(msg)
        return

    cam_tfm, cam_shp = viewport_utils.get_viewport_camera(model_editor)
    if cam_shp is None:
        msg = 'Please select an active 3D viewport to get a camera.'
        LOG.warning(msg)
        return

    save_sel = maya.cmds.ls(selection=True, long=True) or []

    # Create centering node network.
    nodes = maya.cmds.ls(
        selection=True,
        long=True,
        type='transform',
    ) or []

    # Filter out selected imagePlanes.
    nodes_tmp = list(nodes)
    nodes = []
    for node in nodes_tmp:
        shps = maya.cmds.listRelatives(
            node,
            shapes=True,
            fullPath=True,
            type='imagePlane') or []
        if len(shps) == 0:
            nodes.append(node)

    if len(nodes) == 0:
        msg = 'No objects selected, removing 2D centering.'
        LOG.warning(msg)
        __remove_reprojection(cam_tfm, cam_shp)
    elif len(nodes) == 1:
        msg = 'Applying 2D centering to %r'
        LOG.warning(msg, nodes)
        reproj_nodes = __find_reprojection_nodes(cam_tfm, cam_shp)
        if len(reproj_nodes) > 0:
            maya.cmds.delete(reproj_nodes)
        __connect_camera_and_transform(cam_tfm, cam_shp, nodes[0])
    elif len(nodes) > 1:
        msg = 'Please select only 1 node to center on.'
        LOG.error(msg)

    if len(save_sel) > 0:
        maya.cmds.select(save_sel, replace=True)
    return


def center_two_dee():
    warnings.warn("Use 'main' function instead.")
    main()
