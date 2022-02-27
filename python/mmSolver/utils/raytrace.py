# Copyright (C) 2019, 2021 David Cattermole.
#
# This file is part of mmSolver.
#
# mmSolver is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# mmSolver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Raytracing functions.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds
import maya.OpenMaya as OpenMaya
import mmSolver.logger
import mmSolver.utils.constant as const

LOG = mmSolver.logger.get_logger()


def _create_smooth_mesh(mesh):
    smooth_mesh = None
    is_smooth = maya.cmds.getAttr(mesh + '.displaySmoothMesh') != 0
    if is_smooth is True:
        parents = maya.cmds.listRelatives(
            mesh, parent=True, fullPath=True) or []
        if len(parents) == 0:
            return smooth_mesh
        tfm_node = parents[0]
        smooth_mesh = maya.cmds.createNode(
            'mesh', name='tempSmoothMeshShape', parent=tfm_node)
        src = mesh + '.outSmoothMesh'
        dst = smooth_mesh + '.inMesh'
        maya.cmds.connectAttr(src, dst)
    return smooth_mesh


def _closest_intersect(source,
                      direction,
                      mesh_nodes,
                      test_both_directions=False,
                      max_dist=None,
                      tolerance=None,
                      use_smooth_mesh=None,
                      get_mesh_normal=None):
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

    :param use_smooth_mesh: Use smooth preview mesh for intersection.
    :type use_smooth_mesh: bool

    :param get_mesh_normal: Get the normal vector for the hit mesh.
    :type get_mesh_normal: bool

    :return: The closest world space intersection, over all mesh nodes
             given, if get_mesh_normal is True, return a tuple of the
             point and normal, or None, or (None, None), if no point was found
    :rtype:
        maya.OpenMaya.MFloatPoint
        or (maya.OpenMaya.MFloatPoint, maya.OpenMaya.MVector)
        or None
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
    hit_normals = []
    for mesh in mesh_nodes:
        # Generate temp smooth mesh, if needed.
        is_smooth_mesh = False
        if use_smooth_mesh is True:
            smooth_mesh = _create_smooth_mesh(mesh)
            if smooth_mesh is not None:
                mesh = smooth_mesh
                is_smooth_mesh = True
        # Do ray-tracing
        try:
            sel = OpenMaya.MSelectionList()
            dag = OpenMaya.MDagPath()
            sel.add(mesh)
            sel.getDagPath(0, dag)
            mesh_fn = OpenMaya.MFnMesh(dag)
            hit_pt = OpenMaya.MFloatPoint()
            hit_normal = OpenMaya.MVector()
            space = OpenMaya.MSpace.kWorld
            hit = mesh_fn.closestIntersection(
                source_pt,
                direction_vec,
                None,   # faceIds
                None,   # triIds
                False,  # idsSorted
                space,
                max_dist,
                test_both_directions,
                None,   # accelParams
                hit_pt,
                None,   # hitRayParam (ray distance)
                None,   # hitFace
                None,   # hitTriangle
                None,   # hitBary1
                None,   # hitBary2
                tolerance)
            if hit is True:
                if get_mesh_normal is True:
                    mesh_fn.getClosestNormal(
                        OpenMaya.MPoint(hit_pt),
                        hit_normal,
                        space
                    )

                hit_points.append(hit_pt)
                hit_normals.append(hit_normal)
        finally:
            if is_smooth_mesh is True:
                # Clean up temp smooth mesh.
                maya.cmds.delete(mesh)

    # Get the closest hit point.
    closest_point = None
    closest_normal = None
    min_dist = max_dist
    for point, normal in zip(hit_points, hit_normals):
        dist = source_pt.distanceTo(point)
        if dist < min_dist:
            min_dist = dist
            closest_point = point
            closest_normal = normal
    assert (closest_point is None
            or isinstance(closest_point, OpenMaya.MFloatPoint))
    assert (closest_normal is None
            or isinstance(closest_normal, OpenMaya.MVector))

    if get_mesh_normal is False:
        return closest_point
    return (closest_point, closest_normal)


def closest_intersect(source,
                      direction,
                      mesh_nodes,
                      test_both_directions=False,
                      max_dist=None,
                      tolerance=None,
                      use_smooth_mesh=None):
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

    :param use_smooth_mesh: Use smooth preview mesh for intersection.
    :type use_smooth_mesh: bool

    :return: The closest world space intersection, over all mesh nodes
             given, or None if no point was found
    :rtype:
        maya.OpenMaya.MFloatPoint or None
    """
    return _closest_intersect(
        source,
        direction,
        mesh_nodes,
        test_both_directions=test_both_directions,
        max_dist=max_dist,
        tolerance=tolerance,
        use_smooth_mesh=use_smooth_mesh,
        get_mesh_normal=False)


def closest_intersect_with_normal(source,
                                  direction,
                                  mesh_nodes,
                                  test_both_directions=False,
                                  max_dist=None,
                                  tolerance=None,
                                  use_smooth_mesh=None):
    """
    Get the closest intersection point and normal on meshes given a
    source point and direction

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

    :param use_smooth_mesh: Use smooth preview mesh for intersection.
    :type use_smooth_mesh: bool

    :return: The closest world space intersection, over all mesh nodes
             given, return a tuple of the
             point and normal, or (None, None), if no point was found.
    :rtype:
        (maya.OpenMaya.MFloatPoint, maya.OpenMaya.MVector) or None
    """
    return _closest_intersect(
        source,
        direction,
        mesh_nodes,
        test_both_directions=test_both_directions,
        max_dist=max_dist,
        tolerance=tolerance,
        use_smooth_mesh=use_smooth_mesh,
        get_mesh_normal=True)
