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


import mmSolver.logger
import mmSolver._api.frame as frame
import mmSolver._api.excep as excep
import mmSolver._api.solverbase as solverbase
import mmSolver._api.solverstep as solverstep
import mmSolver._api.action as api_action


LOG = mmSolver.logger.get_logger()


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

    def __init__(self, *args, **kwargs):
        super(SolverStandard, self).__init__(*args, **kwargs)
        self.use_single_frame = False
        self.only_root_frames = False
        self.global_solve = False
        self.single_frame = None  # frame.Frame(1)
        return

    ############################################################################

    def get_frame_list(self):
        """
        Get frame objects attached to the solver.

        :return: frame objects.
        :rtype: list of frame.Frame
        """
        frame_list_data = self._data.get('frame_list')
        if frame_list_data is None:
            return []
        frm_list = []
        for f in frame_list_data:
            frm = frame.Frame(0)
            frm.set_data(f)  # Override the frame number
            frm_list.append(frm)
        return frm_list

    def get_frame_list_length(self):
        return len(self.get_frame_list())

    def add_frame(self, frm):
        assert isinstance(frm, frame.Frame)
        key = 'frame_list'
        frm_list_data = self._data.get(key)
        if frm_list_data is None:
            frm_list_data = []

        # check we won't get a double up.
        add_frm_data = frm.get_data()
        for frm_data in frm_list_data:
            if frm_data.get('number') == add_frm_data.get('number'):
                msg = 'Frame already added to SolverStep, cannot add again: {0}'
                msg = msg.format(add_frm_data)
                raise excep.NotValid(msg)

        frm_list_data.append(add_frm_data)
        self._data[key] = frm_list_data
        return

    def add_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        for frm in frm_list:
            self.add_frame(frm)
        return

    def remove_frame(self, frm):
        assert isinstance(frm, frame.Frame)
        key = 'frame_list'
        frm_list_data = self._data.get(key)
        if frm_list_data is None:
            # Nothing to remove, initialise the data structure.
            self._data[key] = []
            return
        found_index = -1
        rm_frm_data = frm.get_data()
        for i, frm_data in enumerate(frm_list_data):
            if frm_data.get('number') == rm_frm_data.get('number'):
                found_index = i
                break
        if found_index != -1:
            del frm_list_data[found_index]
        self._data[key] = frm_list_data
        return

    def remove_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        for frm in frm_list:
            self.remove_frame(frm)
        return

    def set_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        self.clear_frame_list()
        self.add_frame_list(frm_list)
        return

    def clear_frame_list(self):
        key = 'frame_list'
        self._data[key] = []
        return

    ############################################################################

    def get_root_frame_list(self):
        """
        Get frame objects attached to the solver.

        :return: frame objects.
        :rtype: list of frame.Frame
        """
        frame_list_data = self._data.get('frame_list')
        if frame_list_data is None:
            return []
        frm_list = []
        for f in frame_list_data:
            frm = frame.Frame(0)
            frm.set_data(f)  # Override the frame number
            frm_list.append(frm)
        return frm_list

    def get_root_frame_list_length(self):
        return len(self.get_root_frame_list())

    def add_root_frame(self, frm):
        assert isinstance(frm, frame.Frame)
        key = 'root_frame_list'
        frm_list_data = self._data.get(key)
        if frm_list_data is None:
            frm_list_data = []

        # check we won't get a double up.
        add_frm_data = frm.get_data()
        for frm_data in frm_list_data:
            if frm_data.get('number') == add_frm_data.get('number'):
                msg = 'Frame already added to SolverStandard, cannot add again: {0}'
                msg = msg.format(add_frm_data)
                raise excep.NotValid(msg)

        frm_list_data.append(add_frm_data)
        self._data[key] = frm_list_data
        return

    def add_root_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        for frm in frm_list:
            self.add_root_frame(frm)
        return

    def remove_root_frame(self, frm):
        assert isinstance(frm, frame.Frame)
        key = 'root_frame_list'
        frm_list_data = self._data.get(key)
        if frm_list_data is None:
            # Nothing to remove, initialise the data structure.
            self._data[key] = []
            return
        found_index = -1
        rm_frm_data = frm.get_data()
        for i, frm_data in enumerate(frm_list_data):
            if frm_data.get('number') == rm_frm_data.get('number'):
                found_index = i
                break
        if found_index != -1:
            del frm_list_data[found_index]
        self._data[key] = frm_list_data
        return

    def remove_root_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        for frm in frm_list:
            self.remove_root_frame(frm)
        return

    def set_root_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        self.clear_frame_list()
        self.add_root_frame_list(frm_list)
        return

    def clear_root_frame_list(self):
        key = 'root_frame_list'
        self._data[key] = []
        return

    ############################################################################

    def compile(self, mkr_list, attr_list):
        actions = []
        # Options to affect how the solve is constructed.
        use_single_frame = self.use_single_frame
        only_root_frames = self.only_root_frames
        global_solve = self.global_solve

        single_frame = self.single_frame
        # root_frame_list = [frame.Frame(x) for x in range(0, 100, 10)]
        # frame_list = [frame.Frame(x) for x in range(100)]
        root_frame_list = self.get_root_frame_list()
        frame_list = self.get_frame_list()

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
            actions_a = solA.compile(mkr_list, attr_list)
            LOG.warn('actions_a: %r', actions_a)
            actions += actions_a

            if only_root_frames is not True:
                # Solver for all other frames.
                solB = solverstep.SolverStep()
                solB.set_frame_list(frame_list)
                solB.set_attributes_use_animated(True)
                solB.set_attributes_use_static(False)
                if global_solve is True:
                    solB.set_attributes_use_static(True)
                actions_b = solB.compile(mkr_list, attr_list)
                LOG.warn('actions_b: %r', actions_b)
                actions += actions_b
        return actions
