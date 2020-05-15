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
Logic to toggle the visible geometry in a viewport.
"""

import mmSolver.logger
import mmSolver.utils.viewport as viewport_utils

LOG = mmSolver.logger.get_logger()


def toggle_geometry_visibility(model_panel):
    value = viewport_utils.get_mesh_visibility(model_panel)
    new_value = not value
    viewport_utils.set_mesh_visibility(model_panel, new_value)
    viewport_utils.set_nurbs_surface_visibility(model_panel, new_value)
    viewport_utils.set_subdiv_visibility(model_panel, new_value)
    viewport_utils.set_fluid_visibility(model_panel, new_value)
    viewport_utils.set_stroke_visibility(model_panel, new_value)
    return
