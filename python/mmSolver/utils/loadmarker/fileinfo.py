# Copyright (C) 2018 David Cattermole.
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
Provides a base interface for marker import plug-ins.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections


FileInfo = collections.namedtuple(
    'FileInfo',
    [
        'marker_distorted',
        'marker_undistorted',
        'bundle_positions',
        'scene_transform',
        'point_group_transform',
        'camera_field_of_view',
    ],
)


def create_file_info(
    marker_distorted=None,
    marker_undistorted=None,
    bundle_positions=None,
    scene_transform=None,
    point_group_transform=None,
    camera_field_of_view=None,
):
    """
    Create the type of contents available in the file format.
    """
    if marker_distorted is None:
        marker_distorted = False
    if marker_undistorted is None:
        marker_undistorted = False
    if bundle_positions is None:
        bundle_positions = False
    if scene_transform is None:
        scene_transform = False
    if point_group_transform is None:
        point_group_transform = False
    if camera_field_of_view is None:
        camera_field_of_view = []
    file_info = FileInfo(
        marker_distorted=marker_distorted,
        marker_undistorted=marker_undistorted,
        bundle_positions=bundle_positions,
        scene_transform=scene_transform,
        point_group_transform=point_group_transform,
        camera_field_of_view=camera_field_of_view,
    )
    return file_info
