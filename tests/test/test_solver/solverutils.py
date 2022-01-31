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

import time

try:
    import maya.standalone
    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds

import mmSolver.utils.node as node_utils

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

    @staticmethod
    def runSolverAffects(affects_mode, **kwargs):
        assert 'mmSolverAffects' in dir(maya.cmds)
        s = time.time()
        result = maya.cmds.mmSolverAffects(
            mode=affects_mode,
            **kwargs)
        e = time.time()
        print('mmSolverAffects time:', e - s)
        return result

    @staticmethod
    def create_camera(name):
        tfm_name = name + '_tfm'
        shp_name = name + '_shp'

        tfm = maya.cmds.createNode('transform', name=tfm_name)
        shp = maya.cmds.createNode('camera', name=shp_name, parent=tfm)

        tfm = node_utils.get_long_name(tfm)
        shp = node_utils.get_long_name(shp)
        return tfm, shp

    @staticmethod
    def create_bundle(name, parent=None):
        tfm_name = name + '_tfm'
        shp_name = name + '_shp'

        tfm = maya.cmds.createNode('transform', name=tfm_name, parent=parent)
        shp = maya.cmds.createNode('locator', name=shp_name, parent=tfm)

        tfm = node_utils.get_long_name(tfm)
        shp = node_utils.get_long_name(shp)
        return tfm, shp

    @staticmethod
    def create_marker(name, cam_tfm, bnd_tfm=None):
        tfm_name = name + '_tfm'
        shp_name = name + '_shp'

        tfm = maya.cmds.createNode('transform', name=tfm_name, parent=cam_tfm)
        tfm = node_utils.get_long_name(tfm)

        shp = maya.cmds.createNode('locator', name=shp_name, parent=tfm)
        shp = node_utils.get_long_name(shp)

        maya.cmds.addAttr(
            tfm,
            longName='enable',
            at='short',
            minValue=0,
            maxValue=1,
            defaultValue=True
        )
        maya.cmds.addAttr(
            tfm,
            longName='weight',
            at='double',
            minValue=0.0,
            defaultValue=1.0)
        maya.cmds.setAttr(tfm + '.enable', keyable=True, channelBox=True)
        maya.cmds.setAttr(tfm + '.weight', keyable=True, channelBox=True)

        maya.cmds.addAttr(
            tfm,
            longName='bundle',
            at='message')

        if bnd_tfm is not None:
            src = bnd_tfm + '.message'
            dst = tfm + '.bundle'
            if not maya.cmds.isConnected(src, dst):
                maya.cmds.connectAttr(src, dst)
        return tfm, shp
