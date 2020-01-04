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

    def haveSolverType(self, name=None, index=None):
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
