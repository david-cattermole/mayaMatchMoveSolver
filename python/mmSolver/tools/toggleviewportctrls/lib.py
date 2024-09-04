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
Logic to toggle the NURBS curves, locators and cameras in a viewport.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.logger
import mmSolver.utils.viewport as viewport_utils

LOG = mmSolver.logger.get_logger()


def toggle_ctrls_visibility(model_panel):
    value = viewport_utils.get_locator_visibility(model_panel)
    new_value = not value
    # TODO: Add MM Markers, Bundles and Lines to be disabled/enabled.
    viewport_utils.set_nurbs_curve_visibility(model_panel, new_value)
    viewport_utils.set_locator_visibility(model_panel, new_value)
    viewport_utils.set_joint_visibility(model_panel, new_value)
    viewport_utils.set_ik_handle_visibility(model_panel, new_value)
    viewport_utils.set_dynamic_visibility(model_panel, new_value)
    viewport_utils.set_deformer_visibility(model_panel, new_value)
    viewport_utils.set_light_visibility(model_panel, new_value)
    viewport_utils.set_camera_visibility(model_panel, new_value)
    viewport_utils.set_hair_system_visibility(model_panel, new_value)
    viewport_utils.set_follicle_visibility(model_panel, new_value)
    viewport_utils.set_ncloth_visibility(model_panel, new_value)
    viewport_utils.set_nparticle_visibility(model_panel, new_value)
    viewport_utils.set_nrigid_visibility(model_panel, new_value)
    viewport_utils.set_texture_visibility(model_panel, new_value)
    viewport_utils.set_plane_visibility(model_panel, new_value)
    return
