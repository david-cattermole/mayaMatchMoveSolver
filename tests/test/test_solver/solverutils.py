"""
Testing Utilities - base class for the test cases.
"""

import os
import math
import time
import unittest

try:
    import maya.standalone
    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds

import test.baseutils as baseUtils


class SolverTestCase(baseUtils.TestBase):

    def setUp(self):
        maya.cmds.file(new=True, force=True)
        self.reload_solver()

        # Start the Profiler
        self._profilerName = self.id().replace('.', '_')
        self._profilerDataName = self._profilerName + '.txt'
        self._profilerPath = None
        if '__file__' in dir():
            self._profilerPath = os.path.join(os.path.dirname(__file__), self._profilerName)
        maya.cmds.profiler(addCategory='mmSolver')
        maya.cmds.profiler(bufferSize=250)
        maya.cmds.profiler(sampling=True)

        super(SolverTestCase, self).setUp()

    def tearDown(self):
        # Stop the Profiler
        maya.cmds.profiler(sampling=False)
        if self._profilerPath is not None:
            maya.cmds.profiler(output=self._profilerPath)

        super(SolverTestCase, self).tearDown()
