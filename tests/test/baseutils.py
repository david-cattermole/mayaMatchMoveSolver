"""
Testing Utilities - base class for the test cases.
"""

import os
import math
import time
import unittest
import cProfile as profile

try:
    import maya.standalone
    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds


class TestBase(unittest.TestCase):

    def setUp(self):
        print ''
        print '-' * 80
        print 'Name:', self.id()
        if self.shortDescription():
            print 'Description:', self.shortDescription()

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
        print 'Time: ', '{0: f}'.format(self._test_time)
        print 'Python Profiler:', self._pyProfilerPath

    def reload_solver(self):
        maya.cmds.unloadPlugin('mmSolver')
        maya.cmds.loadPlugin('mmSolver')

    def quit_maya(self):
        if maya.cmds.about(batch=True):
            maya.cmds.quit(force=True)

    def approx_equal(self, x, y, eps=0.0001):
        return x == y or (x < (y + eps) and x > (y - eps))

    def get_data_root(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'data')
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

    def get_profile_path(self, *args):
        root = self.get_profile_root()
        path = os.path.join(root, *args)
        path = os.path.abspath(path)
        return path
