# Copyright (C) 2020 David Cattermole.
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
Logic to toggle the visible image planes in a viewport.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.logger
import mmSolver.utils.viewport as viewport_utils

LOG = mmSolver.logger.get_logger()


def toggle_image_plane_visibility(model_panel):
    value = viewport_utils.get_image_plane_visibility(model_panel)
    new_value = not value
    viewport_utils.set_image_plane_visibility(model_panel, new_value)
    viewport_utils.set_mm_image_plane_v2_visibility(model_panel, new_value)
    return
