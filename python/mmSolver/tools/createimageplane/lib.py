# Copyright (C) 2020, 2022 David Cattermole.
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
Library functions for creating and modifying image planes.


Idea - Create wrapper image plane node
- The node should adjust either 'live' or 'baked' nodes.


Idea - Allow users to change the image sequence.
- Both 'live' and 'baked' image planes are updated as needed.
- Users can choose to auto-convert to Maya IFF format (for speed).
- Users should have multiple file paths stored on the image plane,
  with the choice to switch between them as needed.


Idea - Bake images into .iff files using Maya 'imgcvt' utility.
- Experiment with .dds files to see if it's faster in the Maya viewport or not.
- Write to local 'sourceimages/mmSolver_temp' directory, by default.


Idea - Apply image processing templates to images.
- Allow the use of OIIO, Natron or Nuke (if installed)
- Features
  - Reformat / down-res plates.
    - Scale (50%)
    - Maximum width (2048)
    - Maximum height (2048)
  - Lens undistort (for baked image planes)
  - Converting to different formats (such as Maya 'iff')


Tool - Set Image Plane File Path


Tool - Toggle the Live/Baked image plane state.


Idea - Create a custom image plane shape node.
- Pipe the deforming polygon plane into the shape node and draw it with
  an image sequence on it.
- This allows us to hide the polygons in a viewport but still show the
  image plane.
- We can control the depth of the image plane with this method.
- When the OCG Image Plane is fully developed we can easily replace this
  shape node with the 'ocgImagePlane'.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from mmSolver.tools.createimageplane._lib.main import (
    set_image_sequence,
    create_image_plane_on_camera,
    convert_image_planes_on_camera,
)

from mmSolver.tools.createimageplane._lib.constant import (
    DEFAULT_IMAGE_SEQUENCE_ATTR_NAME,
)

from mmSolver.tools.createimageplane._lib.utilities import get_default_image_path

from mmSolver.tools.createimageplane._lib.format import (
    format_image_sequence_size,
    format_cache_gpu_used,
    format_cache_cpu_used,
    format_memory_gpu_available,
    format_memory_cpu_available,
)


# Stop users from accessing the internal functions of this sub-module.
__all__ = [
    'create_image_plane_on_camera',
    'convert_image_planes_on_camera',
    'set_image_sequence',
    'get_default_image_path',
    'DEFAULT_IMAGE_SEQUENCE_ATTR_NAME',
    'format_image_sequence_size',
    'format_cache_gpu_used',
    'format_cache_cpu_used',
    'format_memory_gpu_available',
    'format_memory_cpu_available',
]
