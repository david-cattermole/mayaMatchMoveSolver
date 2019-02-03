"""
This is a Ray cast Markers tool.
"""

import maya.cmds
import maya.OpenMaya as OpenMaya
# import mmSolver.tools.raycastmarker.lib as raycast_lib
import mmSolver.tools.selection.filternodes as filternodes
import mmSolver.api as mmapi
import mmSolver.logger

LOG = mmSolver.logger.get_logger()

MAX_DIST = 9999999999.0


def __get_camera_direction_to_point(camera_node, point_node):
    """
    Get the direction of the camera from a given point.

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


def intersect(source,
              direction,
              mesh_nodes,
              test_both_directions=False,
              max_dist=None,
              tolerance=None):
    """
    Get the intersection point on meshes given a source point and direction

    :param source: Origin point of the ray projection.
    :type source: [float, float, float]

    :param direction: The direction the ray will travel.

    :param mesh_nodes: Mesh nodes

    :param test_both_directions: testing ray direction both sides;
                                 default is False.
    :type test_both_directions: bool

    :param max_dist: The maximum distance the ray will travel before
                     stopping; default is 99999999999.0.
    :type max_dist: float

    :param tolerance: The minimum ray trace tolerance; default is 0.0001.
    :type tolerance: float

    :return: The closest world space intersection, over all mesh nodes
             given, or None if no point was found.
    :rtype: maya.OpenMaya.MFloatPoint or None
    """
    assert isinstance(mesh_nodes, (list, tuple))
    if max_dist is None:
        max_dist = 99999999999.0
    if tolerance is None:
        tolerance = 0.0001
    if len(mesh_nodes) == 0:
        LOG.warning('No mesh objects found in the scene')
        return

    source_pt = OpenMaya.MFloatPoint(source[0], source[1], source[2])
    direction_vec = OpenMaya.MFloatVector(direction[0], direction[1], direction[2])

    hit_points = []
    for mesh in mesh_nodes:
        sel = OpenMaya.MSelectionList()
        dag = OpenMaya.MDagPath()
        sel.add(mesh)
        sel.getDagPath(0, dag)
        mesh_fn = OpenMaya.MFnMesh(dag)
        hit_pt = OpenMaya.MFloatPoint()
        hit = mesh_fn.closestIntersection(
            source_pt,
            direction_vec,
            None,
            None,
            False,
            OpenMaya.MSpace.kWorld,
            max_dist,
            test_both_directions,
            None,
            hit_pt,
            None,
            None,
            None,
            None,
            None,
            tolerance)
        if hit is True:
            hit_points.append(hit_pt)

    # Get the closest hit point.
    closest_point = None
    min_dist = max_dist
    for point in hit_points:
        dist = source_pt.distanceTo(point)
        if dist < min_dist:
            min_dist = dist
            closest_point = point
    assert closest_point is None or isinstance(closest_point, OpenMaya.MFloatPoint)
    return closest_point


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
        LOG.warning('Please select a marker to rayCast')
        return

    selected_markers = filternodes.get_marker_nodes(selection)
    if not selected_markers:
        LOG.warning('No markers found in the selection list')
        return

    meshes = []
    selected_meshes = maya.cmds.ls(
        sl=True,
        type='mesh',
        dagObjects=True,
        noIntermediate=True) or []
    if selected_meshes:
        meshes = selected_meshes
    else:
        meshes = maya.cmds.ls(type='mesh', visible=True) or []

    for node in selected_markers:
        mkr = mmapi.Marker(name=node)
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

        hit_point = intersect(
            origin_point,
            direction,
            meshes,
            test_both_directions=True,
            max_dist=MAX_DIST,
        )
        if hit_point is None:
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
    return
