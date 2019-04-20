"""
Raytracing functions.
"""

import maya.OpenMaya as OpenMaya
import mmSolver.logger
import mmSolver.utils.constant as const

LOG = mmSolver.logger.get_logger()


def closest_intersect(source,
                      direction,
                      mesh_nodes,
                      test_both_directions=False,
                      max_dist=None,
                      tolerance=None):
    """
    Get the closest intersection point on meshes given a source point
    and direction

    :param source: Origin point of the ray projection.
    :type source: [float, float, float]

    :param direction: The direction the ray will travel.
    :type direction: [float, float, float]

    :param mesh_nodes: Mesh nodes
    :type mesh_nodes: [str, ..]

    :param test_both_directions: testing ray direction both sides;
                                 default is False.
    :type test_both_directions: bool

    :param max_dist: The maximum distance the ray will travel before
                     stopping; default is RAYTRACE_MAX_DIST.
    :type max_dist: float

    :param tolerance: The minimum ray trace tolerance; default is
                      RAYTRACE_EPSILON.
    :type tolerance: float

    :return: The closest world space intersection, over all mesh nodes
             given, or None if no point was found.
    :rtype: maya.OpenMaya.MFloatPoint or None
    """
    assert isinstance(mesh_nodes, (list, tuple))
    assert len(source) >= 3
    assert len(direction) >= 3
    if max_dist is None:
        max_dist = const.RAYTRACE_MAX_DIST
    if tolerance is None:
        tolerance = const.RAYTRACE_EPSILON
    if len(mesh_nodes) == 0:
        LOG.warning('No mesh objects found in the scene')
        return

    source_pt = OpenMaya.MFloatPoint(source[0], source[1], source[2])
    direction_vec = OpenMaya.MFloatVector(*direction)

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
    assert closest_point is None or isinstance(closest_point,
                                               OpenMaya.MFloatPoint)
    return closest_point
