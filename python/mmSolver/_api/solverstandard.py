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
The standard solver.
"""

import mmSolver._api.frame as frame
import mmSolver._api.solverbase as solverbase
import mmSolver._api.solverstep as solverstep
import mmSolver._api.action as api_action


# class SolverOpTriangulateBundles(SolverBase):
#     """
#     An operation to re-calculate the bundle positions using triangulation.
#     """
#     pass


# class SolverOpSmoothCameraTranslate(SolverBase):
#     """
#     An operation to smooth the translations of a camera.
#     """
#     pass


class SolverStandard(solverbase.SolverBase):
    # TODO: Write a 'meta-solver' class to hold attributes for solving.
    #  Issue #57 - Maya Tool - Solver UI - Add Simplified Solver Settings
    #  Issue #72 - Python API - Re-Design Collection Compiling
    #
    # Parameters for 'meta solver':
    # - Frame Range - with options:
    #   - "Single Frame"
    #   - "Time Slider (Inner)"
    #   - "Time Slider (Outer)"
    #   - "Custom"
    # - Root Frames - A list of integer frame numbers.
    # - Solver Method
    #   - "Solve Everything at Once" option - On or Off
    #   - "Solve Root Frames Only" option - On or Off
    #
    # If a Solver is 'Single Frame' (current frame), then we solve both
    # animated and static attributes on the current frame, in a single step
    # and return.
    #
    # If the 'Solver Root Frames Only' option is On, then we only solve the
    # root frames, with both animated and static attributes.
    #
    # If the 'Solver Root Frames Only' is Off, then we first solve the root
    # frames with both animated and static attributes, then secondly we solve
    # only animated attributes for the entire frame range.
    #
    # If the 'Solve Everything at Once' option is On, then the second solve
    # step contains static and animated attributes (not just animated),
    # and all frames are solved as one big crunch.
    #
    # TODO: Before solving root frames we should query the current
    #  animated attribute values at each root frame, store it,
    #  then remove all keyframes between the first and last frames to
    #  solve. Lastly we should re-keyframe the values at the animated
    #  frames, and ensure the keyframe tangents are linear. This will
    #  ensure that animated keyframe values do not affect a re-solve.
    #  Only the root frames need to be initialized with good values.
    #
    # TODO: Add get/set 'use_single_frame' - bool
    # TODO: Add get/set 'only_root_frames' - bool
    # TODO: Add get/set 'global_solve' - bool
    # TODO: Add get/set 'single_frame' - Frame or None
    # TODO: Add get/set 'root_frame_list' - list of Frame
    # TODO: Add get/set 'frame_list' - list of Frame

    def compile(self, mkr_list, attr_list):
        actions = []
        # Options to affect how the solve is constructed.
        use_single_frame = False
        only_root_frames = False
        global_solve = False

        single_frame = frame.Frame(1)
        root_frame_list = [frame.Frame(x) for x in range(0, 100, 10)]
        frame_list = [frame.Frame(x) for x in range(100)]

        if use_single_frame is True:
            # Single frame solve
            solA = solverstep.SolverStep()
            solA.set_frame_list([single_frame])
            solA.set_attributes_use_animated(True)
            solA.set_attributes_use_static(True)
            actions += solA.compile(mkr_list, attr_list)
        else:
            # Solver for root frames.
            solA = solverstep.SolverStep()
            solA.set_frame_list(root_frame_list)
            solA.set_attributes_use_animated(True)
            solA.set_attributes_use_static(True)
            actions += solA.compile(mkr_list, attr_list)

            if only_root_frames is not True:
                # Solver for all other frames.
                solB = solverstep.SolverStep()
                solB.set_frame_list(frame_list)
                solB.set_attributes_use_animated(True)
                solB.set_attributes_use_static(False)
                if global_solve is True:
                    solB.set_attributes_use_static(True)
                actions += solB.compile(mkr_list, attr_list)
        return actions
