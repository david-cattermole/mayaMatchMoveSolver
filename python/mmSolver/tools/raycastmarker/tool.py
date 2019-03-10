"""
This is a Ray cast Markers tool.
"""

import maya.cmds
import maya.OpenMaya
import mmSolver.utils.raytrace as raytrace_utils
import mmSolver.tools.selection.filternodes as filternodes
import mmSolver.api as mmapi
import mmSolver.logger

LOG = mmSolver.logger.get_logger()


def __get_camera_direction_to_point(camera_node, point_node):
    """
    Get the direction of the camera toward a given point.

    :param camera_node: Camera transform node.
    :type camera_node: str

    :param point_node: Transform node to aim at.
    :type point_node: str

    :return: Direction from camera to point.
    :rtype: (float, float, float)
    """
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
    cam_vec = maya.OpenMaya.MVector(*cam)
    obj_vec = maya.OpenMaya.MVector(*obj)
    distance = cam_vec - obj_vec
    length = maya.OpenMaya.MVector(distance).length()
    direction = distance / length
    x, y, z = direction.x, direction.y, direction.z
    return x, y, z


def main():
    """
    Ray casts selected markers bundles on mesh from the associated camera.

    Select markers and mesh objects to ray cast on, if not mesh
    objects tool will ray cast on all visible mesh objects.

    If a bundle translate attribute is locked, it will be
    unlocked, then projected, and then the lock state will
    be reverted to the original value.

    Example::

        >>> import mmSolver.tools.raycastmarker.tool as tool
        >>> tool.main()
    """
    selection = maya.cmds.ls(selection=True) or []
    if not selection:
        LOG.warning('Please select a marker to rayCast.')
        return

    selected_markers = filternodes.get_marker_nodes(selection)
    if not selected_markers:
        LOG.warning('No markers found in the selection list.')
        return

    meshes = []
    selected_meshes = maya.cmds.ls(
        sl=True,
        type='mesh',
        dagObjects=True,
        noIntermediate=True) or []
    if len(selected_meshes) > 0:
        meshes = selected_meshes
    else:
        meshes = maya.cmds.ls(type='mesh', visible=True) or []

    max_dist = 9999999999.0
    bnd_nodes = []
    for node in selected_markers:
        mkr = mmapi.Marker(node=node)
        bnd = mkr.get_bundle()
        if bnd is None:
            continue
        mkr_node = mkr.get_node()
        camera = mkr.get_camera()
        camera = camera.get_transform_node()
        direction = __get_camera_direction_to_point(camera, mkr_node)
        origin_point = maya.cmds.xform(
            mkr_node, query=True,
            translation=True,
            worldSpace=True
        )

        hit_point = raytrace_utils.closest_intersect(
            origin_point,
            direction,
            meshes,
            test_both_directions=True,
            max_dist=max_dist,
        )
        if hit_point is None:
            LOG.warning('%s didn\'t hit the mesh.' % node)
            continue

        bnd_node = bnd.get_node()
        plugs = [
            '%s.translateX' % bnd_node,
            '%s.translateY' % bnd_node,
            '%s.translateZ' % bnd_node
        ]
        plug_lock_state = {}
        for plug_name in plugs:
            value = maya.cmds.getAttr(plug_name, lock=True)
            plug_lock_state[plug_name] = value
            maya.cmds.setAttr(plug_name, lock=False)
        hit_xyz = (hit_point.x, hit_point.y, hit_point.z)
        maya.cmds.xform(
            bnd_node,
            translation=hit_xyz,
            worldSpace=True,
        )
        for plug_name in plugs:
            value = plug_lock_state.get(plug_name)
            maya.cmds.setAttr(plug_name, lock=value)
        bnd_nodes.append(bnd_node)
        
    if len(bnd_nodes) > 0:
        maya.cmds.select(bnd_nodes)
    else:
        maya.cmds.select(selection)
    return
