"""
Position Bundle under the Marker, in screen-space.
"""

import maya.cmds
import maya.cmds
import maya.OpenMaya

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.node as node_utils
import mmSolver.utils.viewport as viewport_utils
import mmSolver.tools.cameraaim.lib as cameraaim_lib


LOG = mmSolver.logger.get_logger()


def __connect_camera_and_transform(cam_tfm, cam_shp, tfm):
    """
    Create a mmReprojection node, then connect it up as needed.
    """
    try:
        node = maya.cmds.createNode('mmReprojection')
    except RuntimeError:
        # Do not force loading the plug-in each time the tool is
        # run, only if an error happens.
        mmapi.load_plugin()
        try:
            node = maya.cmds.createNode('mmReprojection')
        except RuntimeError:
            raise

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
    return node


def get_marker_frame_list(mkr):
    """
    Get the list of frames that this marker is enabled for.
    """
    frm_list = []
    mkr_node = mkr.get_node()
    curves = maya.cmds.listConnections(mkr_node, type='animCurve') or []

    frm_list = []
    first_time = -99999
    last_time = 99999
    for node in curves:
        times = maya.cmds.keyframe(node, query=True, timeChange=True)
        first_time = max(int(times[0]), first_time)
        last_time = min(int(times[-1]), last_time)

    for t in range(first_time, last_time + 1):
        plug = mkr_node + '.enable'
        value = maya.cmds.getAttr(plug, time=t)
        if value > 0:
            frm = mmapi.Frame(t)
            frm_list.append(frm)
    return frm_list


def triangulate_bundle(bnd, relock=None):
    """
    Triangulate a 3D bundle position.

    :param bnd: Bundle to be triangulated.
    :type bnd: Bundle

    :param relock: If True any bundle translate attributes will be
                   unlocked, changed then relocked.
    :type relock: bool
    """
    if relock is None:
        relock = True
    assert isinstance(relock, bool) is True

    bnd_node = bnd.get_node()

    # Collection
    col = mmapi.Collection()
    col.create_node('triangluatebundle_TEMP')

    # Attributes
    attr_tx = mmapi.Attribute(bnd_node + '.translateX')
    attr_ty = mmapi.Attribute(bnd_node + '.translateY')
    attr_tz = mmapi.Attribute(bnd_node + '.translateZ')

    prev_frame = maya.cmds.currentTime(query=True)

    mkr_list = bnd.get_marker_list()
    for mkr in mkr_list:
        mkr_node = mkr.get_node()
        frm_list = get_marker_frame_list(mkr)
        if len(frm_list) == 0:
            continue

        cam = mkr.get_camera()
        cam_tfm = cam.get_transform_node()
        cam_shp = cam.get_shape_node()

        first_frm = frm_list[0]
        last_frm = frm_list[-1]
        first_frm_num = first_frm.get_number()
        maya.cmds.currentTime(first_frm_num, update=False)

        reproj_node = __connect_camera_and_transform(cam_tfm, cam_shp, mkr_node)
        tmp_node = maya.cmds.createNode('transform')
        pnt = maya.cmds.getAttr(reproj_node + '.outWorldPoint')[0]
        maya.cmds.delete(reproj_node)

        maya.cmds.setAttr(tmp_node + '.translate', *pnt)
        cameraaim_lib.aim_at_target([tmp_node], cam_tfm)
        maya.cmds.parent(bnd_node, tmp_node)

        bnd_node = bnd.get_node()
        maya.cmds.setAttr(bnd_node + '.translateX', 0.0)
        maya.cmds.setAttr(bnd_node + '.translateY', 0.0)
        maya.cmds.setAttr(bnd_node + '.translateZ', 0.0)

        # Solver
        solA = mmapi.Solver()
        solA.set_max_iterations(10)
        solA.set_frame_list([first_frm, last_frm])

        solB = mmapi.Solver()
        solB.set_max_iterations(10)
        solB.set_frame_list(frm_list)

        # Collection (solve depth)
        col.set_solver_list([solA])
        col.set_marker_list([mkr])
        col.set_attribute_list([attr_tx])
        col.execute(refresh=False, verbose=False)

        # Collection (refine)
        maya.cmds.parent(bnd_node, world=True)
        maya.cmds.delete(tmp_node)
        col.set_solver_list([solB])
        col.set_marker_list([mkr])
        col.set_attribute_list([attr_tx, attr_ty, attr_tz])
        col.execute(refresh=False, verbose=False)

    col_node = col.get_node()
    maya.cmds.delete(col_node)

    maya.cmds.currentTime(prev_frame, update=True)
    return
