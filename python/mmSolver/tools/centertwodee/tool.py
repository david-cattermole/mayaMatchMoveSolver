"""
The Center 2D tool.
"""

import maya.cmds
import mmSolver.logger
import mmSolver.api as mmapi


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
    maya.cmds.connectAttr('defaultResolution.width', node + '.imageWidth')
    maya.cmds.connectAttr('defaultResolution.height', node + '.imageHeight')

    # Connect Pan to camera.pan
    maya.cmds.connectAttr(node + '.outPan', cam_shp + '.pan')
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
    return nodes


def __remove_reprojection(cam_tfm, cam_shp):
    """
    Find the mmReprojection node and delete it.
    """
    nodes = __find_reprojection_nodes(cam_tfm, cam_shp)
    for node in nodes:
        maya.cmds.delete(node)

    attrs = [
        cam_shp + '.horizontalPan',
        cam_shp + '.verticalPan',
    ]
    for attr in attrs:
        maya.cmds.setAttr(attr, lock=False)
        maya.cmds.setAttr(attr, 0.0)
    return


def center_two_dee():
    """
    Center the selected transform onto the camera view.
    """
    mmapi.load_plugin()

    cam_shp = __get_camera()
    if cam_shp is None:
        LOG.warning('Please select an active viewport to get a camera.')
        return
    cam_tfm = maya.cmds.listRelatives(cam_shp, parent=True)[0]

    save_sel = maya.cmds.ls(selection=True, long=True) or []

    # Create centering node network.
    nodes = maya.cmds.ls(
        selection=True,
        long=True,
        type='transform'
    ) or []
    if len(nodes) == 0:
        __remove_reprojection(cam_tfm, cam_shp)
    elif len(nodes) == 1:
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
