"""
Position Bundle under the Marker, in screen-space.
"""

import maya.cmds
import maya.OpenMaya

import mmSolver.logger

LOG = mmSolver.logger.get_logger()


def current_frame(mkr_list, relock=None):
    """
    Re-project Marker's Bundle underneath the Marker in screen-space,
    on the current-frame.

    :param mkr_list: Markers to have Bundles triangulated.
    :type mkr_list: [Marker, ..]

    :param relock: If True any bundle translate attributes will be
                   unlocked, changed then relocked.  then relocked.
    :type relock: bool

    :returns: List of Bundle
    :rtype: [Bundle, ..]
    """
    if relock is None:
        relock = True
    assert isinstance(relock, bool) is True

    attrs = ['translateX', 'translateY', 'translateZ']
    bnd_moved_list = []
    for mkr in mkr_list:
        bnd = mkr.get_bundle()
        if bnd is None:
            continue
        cam = mkr.get_camera()
        cam_tfm_node = cam.get_transform_node()
        mkr_node = mkr.get_node()
        bnd_node = bnd.get_node()

        # Get distance vector between camera and marker.
        mkr_trans = maya.cmds.xform(
            mkr_node,
            query=True,
            worldSpace=True,
            translation=True)
        cam_trans = maya.cmds.xform(
            cam_tfm_node,
            query=True,
            worldSpace=True,
            translation=True)
        assert len(mkr_trans) == 3
        assert len(cam_trans) == 3
        cam_pnt = maya.OpenMaya.MPoint(*cam_trans)
        cam_vec = maya.OpenMaya.MVector(*cam_trans)
        mkr_vec = maya.OpenMaya.MVector(*mkr_trans)
        distance_vec = maya.OpenMaya.MVector(cam_vec - mkr_vec)

        # Get new world position for bundle.
        pnt = cam_pnt + (-distance_vec * 10.0)
        value = (pnt.x, pnt.y, pnt.z)

        # Unlock Attributes
        lock_values = {}
        if relock is True:
            for attr in attrs:
                plug = bnd_node + '.' + attr
                locked = maya.cmds.getAttr(plug, lock=True)
                lock_values[plug] = locked
                maya.cmds.setAttr(plug, lock=False)

        # Set value.
        maya.cmds.xform(
            bnd_node,
            worldSpace=True,
            translation=value)

        # Set keyframe (on animated attributes only)
        for attr in attrs:
            plug = bnd_node + '.' + attr
            anim_curves = maya.cmds.listConnections(
                plug,
                source=True,
                destination=False,
                type='animCurve'
            ) or []
            if len(anim_curves) > 0:
                maya.cmds.setKeyframe(bnd_node, attribute=attr)

        # Re-lock attributes
        if relock is True:
            for k, v in lock_values.items():
                print k, v
                maya.cmds.setAttr(k, lock=v)

        bnd_moved_list.append(bnd)
    return bnd_moved_list
