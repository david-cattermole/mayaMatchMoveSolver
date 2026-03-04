# Copyright (C) 2026 David Cattermole.
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
Library functions for Camera Solver.
"""

from mmSolver.tools.camerasolver.lib.save_data import (
    INCHES_TO_MM,
    construct_output_file_path,
    save_markers_to_file,
    save_camera_to_file,
    save_nuke_lens_to_file,
    save_solver_settings_to_file,
)

from mmSolver.tools.camerasolver.lib.load_data import (
    load_solved_camera_from_file,
    load_camera_outputs,
    load_nuke_lens_file,
    load_solved_bundles_from_file,
    load_bundle_outputs,
)

from mmSolver.tools.camerasolver.lib.types import (
    AdjustmentSolver,
    AdjustmentAttributes,
)

from mmSolver.tools.camerasolver.lib.execute import (
    find_executable_file_path,
    SolveProcess,
    launch_solve,
    launch_solve_async,
)
