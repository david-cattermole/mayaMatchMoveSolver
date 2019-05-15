"""
Position Bundle under the Marker.
"""

import maya.cmds
import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver.logger
import mmSolver.api as mmapi


LOG = mmSolver.logger.get_logger()


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


def get_point_and_direction(camera_node, point_node, frame):
    """
    Get the direction of the camera toward a given point.

    :param camera_node: Camera transform node.
    :type camera_node: str

    :param point_node: Transform node to aim at.
    :type point_node: str

    :return: Point and direction from camera to point.
    :rtype:
    """
    maya.cmds.currentTime(frame, update=True)
    obj = maya.cmds.xform(
        point_node,
        query=True,
        worldSpace=True,
        translation=True)
    cam = maya.cmds.xform(
        camera_node,
        query=True,
        worldSpace=True,
        translation=True)
    cam_vec = OpenMaya.MVector(*cam)
    obj_vec = OpenMaya.MVector(*obj)
    direction = obj_vec - cam_vec
    direction.normalize()

    pnt = OpenMaya.MPoint(*obj)
    return pnt, direction


def calculate_approx_intersection_point_between_two_3d_lines(a_pnt, a_dir,
                                                             b_pnt, b_dir,
                                                             eps=None):
    """
    Calculate approximate intersection between two lines in 3D.

    http://paulbourke.net/geometry/pointlineplane/
    http://paulbourke.net/geometry/pointlineplane/lineline.c

    :param a_pnt: Point A.
    :type a_pnt: MPoint

    :param a_dir: Direction A.
    :type a_dir: MVector

    :param b_pnt: Point B
    :type b_pnt: MPoint

    :param b_dir: Direction B.
    :type b_dir: MVector

    :return: Two points to define the closest line intersection.
    :rtype (MPoint, MPoint)
    """
    if eps is None:
        eps = 0.0000

    # Define the lines using points and directions.
    p1 = a_pnt
    p2 = OpenMaya.MPoint(a_pnt + a_dir)
    p3 = b_pnt
    p4 = OpenMaya.MPoint(b_pnt + b_dir)

    p13 = OpenMaya.MVector(p1.x - p3.x, p1.y - p3.y, p1.z - p3.z)

    p43 = OpenMaya.MVector(p4.x - p3.x, p4.y - p3.y, p4.z - p3.z)
    if abs(p43.x) < eps and abs(p43.x) < eps and abs(p43.x) < eps:
        return OpenMaya.MPoint()

    p21 = OpenMaya.MVector(p2.x - p1.x, p2.y - p1.y, p2.z - p1.z)
    if abs(p21.x) < eps and abs(p21.x) < eps and abs(p21.x) < eps:
        return OpenMaya.MPoint()

    d1343 = p13.x * p43.x + p13.y * p43.y + p13.z * p43.z
    d4321 = p43.x * p21.x + p43.y * p21.y + p43.z * p21.z
    d1321 = p13.x * p21.x + p13.y * p21.y + p13.z * p21.z
    d4343 = p43.x * p43.x + p43.y * p43.y + p43.z * p43.z
    d2121 = p21.x * p21.x + p21.y * p21.y + p21.z * p21.z

    denom = d2121 * d4343 - d4321 * d4321
    if abs(denom) < eps:
        return OpenMaya.MVector()
    numer = d1343 * d4321 - d1321 * d4343

    mua = numer / denom
    mub = (d1343 + d4321 * mua) / d4343

    pa = OpenMaya.MPoint(p1.x + mua * p21.x,
                         p1.y + mua * p21.y,
                         p1.z + mua * p21.z)
    pb = OpenMaya.MPoint(p3.x + mub * p43.x,
                         p3.y + mub * p43.y,
                         p3.z + mub * p43.z)
    return pa, pb


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

    prev_frame = maya.cmds.currentTime(query=True)
    try:
        mkr_list = bnd.get_marker_list()
        for mkr in mkr_list:
            mkr_node = mkr.get_node()
            frm_list = get_marker_frame_list(mkr)
            if len(frm_list) == 0:
                continue

            cam = mkr.get_camera()
            cam_tfm = cam.get_transform_node()

            first_frm = frm_list[0]
            last_frm = frm_list[-1]
            first_frm_num = first_frm.get_number()
            last_frm_num = last_frm.get_number()
            first_pnt, first_dir = get_point_and_direction(cam_tfm, mkr_node, first_frm_num)
            last_pnt, last_dir = get_point_and_direction(cam_tfm, mkr_node, last_frm_num)

            pnt = calculate_approx_intersection_point_between_two_3d_lines(
                first_pnt, first_dir,
                last_pnt, last_dir
            )
            bnd_node = bnd.get_node()

            plugs = [
                '%s.translateX' % bnd_node,
                '%s.translateY' % bnd_node,
                '%s.translateZ' % bnd_node
            ]
            lock_state = {}
            for plug in plugs:
                value = maya.cmds.getAttr(plug, lock=True)
                lock_state[plug] = value
                maya.cmds.setAttr(plug, lock=False)

            maya.cmds.xform(
                translation=(pnt.x, pnt.y, pnt.z),
                worldSpace=True
            )

            if relock is True:
                for plug in plugs:
                    value = lock_state.get(plug)
                    maya.cmds.setAttr(plug, lock=value)
    finally:
        maya.cmds.currentTime(prev_frame, update=False)
    return
