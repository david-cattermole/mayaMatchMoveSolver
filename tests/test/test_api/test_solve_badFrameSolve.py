# Copyright (C) 2018, 2019 David Cattermole.
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
This file solves wildly, with each frame good, then next bad. The
animCurves created are very spikey, but we expect to solve a smooth
curve.

When opening the scene file manually using the GUI, and running the
solver, the undo-ing the (bad) result, the timeline is traversed
slowly. This shows issue #45.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
import pprint
import math
import unittest

import maya.cmds

import mmSolver.logger
import mmSolver.utils.time as time_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.api as mmapi
import mmSolver.tools.solver.lib.collection as lib_col
import mmSolver.tools.loadmarker.lib.mayareadfile as marker_read
import test.test_api.apiutils as test_api_utils


LOG = mmSolver.logger.get_logger()


# @unittest.skip
class TestSolveBadPerFrameSolve(test_api_utils.APITestCase):

    def test_badPerFrameSolve(self):
        s = time.time()

        # Open the Maya file
        file_name = 'mmSolverBasicSolveA_badSolve01.ma'
        path = self.get_data_path('scenes', file_name)
        maya.cmds.file(path, open=True, force=True, ignoreVersion=True)

        col = mmapi.Collection(node='collection1')
        lib_col.compile_collection(col)
        e = time.time()
        print('pre-solve time:', e - s)

        # Run solver!
        s = time.time()
        solres_list = mmapi.execute(col)
        e = time.time()
        print('total time:', e - s)

        # Set Deviation
        mkr_list = col.get_marker_list()
        mmapi.update_deviation_on_markers(mkr_list, solres_list)
        mmapi.update_deviation_on_collection(col, solres_list)

        # save the output
        path = self.get_data_path('test_solve_badPerFrameSolve_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.checkSolveResults(solres_list)
        return

    def test_badPerFrameSolve_solverstandard(self):
        """
        The same test as 'test_badPerFrameSolve', but using the SolverStandard class.
        """
        s = time.time()
        # Open the Maya file
        file_name = 'mmSolverBasicSolveA_badSolve01.ma'
        path = self.get_data_path('scenes', file_name)
        maya.cmds.file(path, open=True, force=True, ignoreVersion=True)
        print('File opened:', path)

        # Frames
        start_frame = 1
        end_frame = 120
        root_frames = [1, 30, 60, 90, 120]
        root_frm_list = []
        for f in root_frames:
            frm = mmapi.Frame(f)
            root_frm_list.append(frm)
        print('root frames:', root_frm_list)

        frm_list = []
        for f in range(start_frame, end_frame):
            frm = mmapi.Frame(f)
            frm_list.append(frm)
        print('frames:', frm_list)

        # Solver
        sol = mmapi.SolverStandard()
        sol.set_root_frame_list(root_frm_list)
        sol.set_frame_list(frm_list)
        sol.set_use_single_frame(False)
        sol.set_global_solve(False)
        sol.set_only_root_frames(False)
        sol_list = [sol]
        print('Solver:', sol)
        e = time.time()
        print('pre-solve time:', e - s)

        # Run solver!
        s = time.time()
        col = mmapi.Collection(node='collection1')
        col.set_solver_list(sol_list)
        solres_list = mmapi.execute(col)
        e = time.time()
        print('total time:', e - s)

        # Set Deviation
        mkr_list = col.get_marker_list()
        mmapi.update_deviation_on_markers(mkr_list, solres_list)
        mmapi.update_deviation_on_collection(col, solres_list)

        # save the output
        path = self.get_data_path('test_solve_badPerFrameSolve_solverstandard_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.checkSolveResults(solres_list)
        return


if __name__ == '__main__':
    prog = unittest.main()
