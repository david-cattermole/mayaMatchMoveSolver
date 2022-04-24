# Copyright (C) 2022 David Cattermole.
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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .camera import (
    create_camera,
    camera_lens_distortion_enabled,
    toggle_camera_lens_distortion_enabled,
)

from .imageplane import (
    create_image_plane,
    get_camera_image_planes,
    get_image_plane_type_name_label,
)

from .lens import (
    create_lens,
    get_camera_lens_nodes,
    lens_node_enabled,
    toggle_lens_enabled
)

from .utilities import (
    open_node_in_attribute_editor,
    open_node_in_node_editor,
)

__all__ = [
    # Camera
    'create_camera',
    'camera_lens_distortion_enabled',
    'toggle_camera_lens_distortion_enabled',

    # Image Plane
    'create_image_plane',
    'get_camera_image_planes',
    'get_image_plane_type_name_label',

    # Lens
    'create_lens',
    'get_camera_lens_nodes',
    'lens_node_enabled',
    'toggle_lens_enabled',

    # Utilities
    'open_node_in_attribute_editor',
    'open_node_in_node_editor',
]