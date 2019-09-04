"""
Position Bundle under the Marker.
"""

import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver.logger
import mmSolver.utils.lineintersect as tri_utils


LOG = mmSolver.logger.get_logger()


def get_marker_frame_list(mkr_node):
    """
    Get the list of frames that this marker is enabled for.
    """
    frm_list = []
    curves = maya.cmds.listConnections(mkr_node, type='animCurve') or []
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
            frm_list.append(t)
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
        relock = False
    assert isinstance(relock, bool) is True

    prev_frame = maya.cmds.currentTime(query=True)
    try:
        mkr_list = bnd.get_marker_list()
        for mkr in mkr_list:
            mkr_node = mkr.get_node()
            frm_list = get_marker_frame_list(mkr_node)
            if len(frm_list) == 0:
                continue

            bnd_node = bnd.get_node()
            cam = mkr.get_camera()
            cam_tfm = cam.get_transform_node()

            first_frm = frm_list[0]
            last_frm = frm_list[-1]
            first_pnt, first_dir = tri_utils.get_point_and_direction(
                cam_tfm,
                mkr_node,
                first_frm
            )
            last_pnt, last_dir = tri_utils.get_point_and_direction(
                cam_tfm,
                mkr_node,
                last_frm
            )

            a_pnt, b_pnt = tri_utils.calculate_approx_intersection_point_between_two_3d_lines(
                first_pnt, first_dir,
                last_pnt, last_dir
            )
            pnt = OpenMaya.MPoint(
                (a_pnt.x + b_pnt.x) * 0.5,
                (a_pnt.y + b_pnt.y) * 0.5,
                (a_pnt.z + b_pnt.z) * 0.5
            )

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
                bnd_node,
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
