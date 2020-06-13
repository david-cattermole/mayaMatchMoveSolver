# Copyright (C) 2019 David Cattermole.
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
Utility functions for 3D line intersection (for triangulating 3D points).

.. code::

    # Example usage
    import mmSolver.utils.lineintersect as tri_utils
    cam_tfm = '|camera1'
    mkr_node = '|camera1|markerGroup1|marker1_MKR'
    first_frm_num = 1001
    last_frm_num = 1101
    first_pnt, first_dir = tri_utils.get_point_and_direction(
        cam_tfm,
        mkr_node,
        first_frm_num
    )
    last_pnt, last_dir = tri_utils.get_point_and_direction(
        cam_tfm,
        mkr_node,
        last_frm_num
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
    # Use 'pnt' as the 'intersection' point of the two lines.

"""

import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver.logger

LOG = mmSolver.logger.get_logger()


def get_point_and_direction(camera_node, point_node, frame):
    """
    Get the direction of the camera toward a given point.

    .. note:: This function changes the current maya scene time to the
        frame argument. It is the user's responsibility to ensure the
        frame is maintained before/after the tool using this function
        is finished.

    :param camera_node: Camera transform node.
    :type camera_node: str

    :param point_node: Transform node to aim at.
    :type point_node: str

    :param frame: The frame to query at.
    :type frame: int

    :return: Point and direction from camera to point.
    :rtype: (OpenMaya.MPoint, OpenMaya.MVector)
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

    :param eps: Direction B.
    :type eps: float

    :return: Two points to define the closest line intersection.
    :rtype: (MPoint, MPoint)
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
