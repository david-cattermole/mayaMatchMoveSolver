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
        self._mayaProfilerName = self.id().replace('.', '_')
        self._mayaProfilerDataName = self._mayaProfilerName + '.txt'
        self._mayaProfilerPath = self.get_profile_path(self._mayaProfilerDataName)
        maya.cmds.profiler(addCategory='mmSolver')
        maya.cmds.profiler(bufferSize=20)
        maya.cmds.profiler(sampling=True)

        super(SolverTestCase, self).setUp()

    def tearDown(self):
        # Stop the Profiler
        maya.cmds.profiler(sampling=False)
        if self._mayaProfilerPath is not None:
            maya.cmds.profiler(output=self._mayaProfilerPath)

        super(SolverTestCase, self).tearDown()
