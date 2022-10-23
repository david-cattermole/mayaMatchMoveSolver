# Copyright (C) 2021 David Cattermole.
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
Contains constant values for the Save Marker File tool.

The .uv format, resolution independent 2D tracking format.

This file supports only the .uv version 4 format.

The UV coordinate (0.0, 0.0) is the lower-left.
The UV coordinate (1.0, 1.0) is the upper-right.

Format version 4::

    {
        'version': int,
        'num_points': int,
        'is_undistorted': None,  # Deprecated
        'points': [
            {
                'name': str,
                'id': int,  # or None
                'set_name': str,
                'per_frame': [
                    {
                        'frame': int,
                        'pos_dist': (float, float),
                        'pos': (float, float),
                        'weight': float
                    },
                ],
               '3d': {
                    'x': float, # or None
                    'y': float, # or None
                    'z': float, # or None
                    'x_lock': bool, # or None
                    'y_lock': bool, # or None
                    'z_lock': bool  # or None
                }
            },
        ],
        'camera': {
            'resolution': (int, int),
            'film_back_cm': (float, float),
            'lens_center_offset_cm': (float, float),
            'per_frame': [
                {
                    'frame': int,
                    'focal_length_cm': float,
                },
            ],
        }
    }

"""

EXT = '.uv'

DEFAULT_DATA_VERSION_4 = {
    'version': 4,
    'num_points': 0,
    'is_undistorted': None,  # Deprecated
    'points': [],
    'camera': {},
}


DEFAULT_POINT_DATA_VERSION_4 = {
    'name': None,
    'id': None,
    'set_name': None,
    'per_frame': [],
    '3d': {
        'x': None,
        'y': None,
        'z': None,
        'x_lock': None,
        'y_lock': None,
        'z_lock': None,
    },
}


DEFAULT_CAMERA_DATA_VERSION_4 = {
    'resolution': (0, 0),
    'film_back_cm': (0.0, 0.0),
    'lens_center_offset_cm': (0.0, 0.0),
    'per_frame': [],
}
