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
Testing Utilities - base class for the test cases.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pprint
import os
import time
import unittest
import cProfile as profile

try:
    import maya.standalone

    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds

import mmSolver.api as mmapi


class TestBase(unittest.TestCase):
    def setUp(self):
        print('')
        print('-' * 80)
        print('Name:', self.id())
        if self.shortDescription():
            print('Description:', self.shortDescription())

        # Start the timer
        self._start_test_time = time.time()

        # Start the Profiler
        self._pyProfilerName = self.id().replace('.', '_')
        self._pyProfilerDataName = self._pyProfilerName + '.pstat'
        self._pyProfilerPath = self.get_profile_path(self._pyProfilerDataName)
        self._pyProfiler = profile.Profile()
        self._pyProfiler.enable()

    def tearDown(self):
        # Stop the timer
        self._end_test_time = time.time()
        self._test_time = self._end_test_time - self._start_test_time

        # Stop the Profiler
        self._pyProfiler.disable()
        self._pyProfiler.dump_stats(self._pyProfilerPath)
        print('Time: ', '{0: f}'.format(self._test_time))
        print('Python Profiler:', self._pyProfilerPath)

    def reload_solver(self):
        maya.cmds.unloadPlugin('mmSolver', force=True)
        maya.cmds.loadPlugin('mmSolver')

    def quit_maya(self):
        if maya.cmds.about(batch=True):
            maya.cmds.quit(force=True)

    def approx_equal(self, x, y, eps=0.0001):
        return x == y or (x < (y + eps) and x > (y - eps))

    def assertApproxEqual(self, x, y, eps=0.0001):
        if self.approx_equal(x, y, eps=eps) is False:
            raise AssertionError(
                '{x} != {y} (epsilon is {eps})'.format(x=x, y=y, eps=eps)
            )
        return

    def get_data_root(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'data')
        path = os.path.abspath(path)
        return path

    def get_output_root(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'output')
        path = os.path.abspath(path)
        return path

    def get_profile_root(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'profile')
        path = os.path.abspath(path)
        return path

    def get_data_path(self, *args):
        root = self.get_data_root()
        path = os.path.join(root, *args)
        path = os.path.abspath(path)
        return path

    def get_output_path(self, *args):
        root = self.get_output_root()
        path = os.path.join(root, *args)
        path = os.path.abspath(path)
        return path

    def get_profile_path(self, *args):
        root = self.get_profile_root()
        path = os.path.join(root, *args)
        path = os.path.abspath(path)
        return path

    @staticmethod
    def haveSolverType(name=None, index=None):
        has_solver = False
        kwargs = {
            'name': False,
            'index': False,
        }
        if name is not None:
            kwargs['name'] = True
        elif index is not None:
            kwargs['index'] = True
        solverTypes = maya.cmds.mmSolverType(query=True, list=True, **kwargs)
        if name is not None:
            has_solver = name in solverTypes
        if index is not None:
            has_solver = index in solverTypes
        return has_solver

    def checkSolveResults(
        self, solres_list, allow_max_avg_error=None, allow_max_error=None
    ):
        if allow_max_avg_error is None:
            allow_max_avg_error = 1.0
        if allow_max_error is None:
            allow_max_error = max(allow_max_avg_error, 1.0)

        # Ensure the values are correct
        for res in solres_list:
            success = res.get_success()
            err = res.get_final_error()
            print('final error', success, err)
            self.assertTrue(success)
            self.assertTrue(isinstance(err, float))

        # Check the final error values
        frm_err_list = mmapi.merge_frame_error_list(solres_list)
        print('frame error list', pprint.pformat(dict(frm_err_list)))

        avg_err = mmapi.get_average_frame_error_list(frm_err_list)
        print('avg error', avg_err)

        max_err_frm, max_err_val = mmapi.get_max_frame_error(frm_err_list)
        print('max error frame and value:', max_err_frm, max_err_val)
        self.assertLess(avg_err, allow_max_avg_error)
        self.assertGreater(avg_err, 0.0)
        self.assertLess(max_err_val, allow_max_error)
        self.assertGreater(max_err_val, 0.0)
        return
