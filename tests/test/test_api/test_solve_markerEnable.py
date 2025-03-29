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
Testing markers enabling/disabling over time.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pprint
import math
import unittest

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import test.test_api.apiutils as test_api_utils


LOG = mmSolver.logger.get_logger()


# @unittest.skip
class TestSolveMarkerEnable(test_api_utils.APITestCase):
    def do_solve(self, solver_name, solver_type_index, scene_graph_mode):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)
        scene_graph_name = mmapi.SCENE_GRAPH_MODE_NAME_LIST[scene_graph_mode]
        scene_graph_label = mmapi.SCENE_GRAPH_MODE_LABEL_LIST[scene_graph_mode]
        print('Scene Graph:', scene_graph_label)

        start = 1
        end = 5

        # Set Time Range
        maya.cmds.playbackOptions(
            animationStartTime=start, minTime=start, animationEndTime=end, maxTime=end
        )

        # Camera
        cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
        cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)
        cam = mmapi.Camera(shape=cam_shp)

        # Bundle
        bnd = mmapi.Bundle().create_node()
        bundle_tfm = bnd.get_node()
        maya.cmds.setAttr(bundle_tfm + '.tx', 5.5)
        maya.cmds.setAttr(bundle_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundle_tfm + '.tz', -25.0)
        assert mmapi.get_object_type(bundle_tfm) == 'bundle'

        # calculate angle of view (AOV)
        f = maya.cmds.getAttr(cam_shp + '.focalLength')
        fbw = maya.cmds.getAttr(cam_shp + '.horizontalFilmAperture') * 25.4
        aov = math.degrees(2.0 * math.atan(fbw * (0.5 / f)))

        # Set Camera Anim
        maya.cmds.setKeyframe(
            cam_tfm,
            attribute='rotateY',
            time=start,
            value=-(aov / 2),
            inTangentType='linear',
            outTangentType='linear',
        )
        maya.cmds.setKeyframe(
            cam_tfm,
            attribute='rotateY',
            time=end,
            value=(aov / 2),
            inTangentType='linear',
            outTangentType='linear',
        )

        # Marker
        mkr = mmapi.Marker().create_node(cam=cam, bnd=bnd)
        marker_tfm = mkr.get_node()
        assert mmapi.get_object_type(marker_tfm) == 'marker'
        mid_value = 0.23534346
        maya.cmds.setKeyframe(
            marker_tfm,
            attribute='translateX',
            time=start,
            value=-0.5,
            inTangentType='linear',
            outTangentType='linear',
        )
        maya.cmds.setKeyframe(
            marker_tfm,
            attribute='translateX',
            time=start + 1,
            value=-mid_value,
            inTangentType='linear',
            outTangentType='linear',
        )
        maya.cmds.setKeyframe(
            marker_tfm,
            attribute='translateX',
            time=end - 1,
            value=mid_value,
            inTangentType='linear',
            outTangentType='linear',
        )
        maya.cmds.setKeyframe(
            marker_tfm,
            attribute='translateX',
            time=end,
            value=0.5,
            inTangentType='linear',
            outTangentType='linear',
        )
        maya.cmds.setAttr(marker_tfm + '.ty', 0.0)

        maya.cmds.setKeyframe(
            marker_tfm,
            attribute='enable',
            time=1,
            value=1,
            inTangentType='linear',
            outTangentType='linear',
        )
        maya.cmds.setKeyframe(
            marker_tfm,
            attribute='enable',
            time=2,
            value=1,
            inTangentType='linear',
            outTangentType='linear',
        )
        maya.cmds.setKeyframe(
            marker_tfm,
            attribute='enable',
            time=3,
            value=0,
            inTangentType='linear',
            outTangentType='linear',
        )
        maya.cmds.setKeyframe(
            marker_tfm,
            attribute='enable',
            time=4,
            value=1,
            inTangentType='linear',
            outTangentType='linear',
        )
        maya.cmds.setKeyframe(
            marker_tfm,
            attribute='enable',
            time=5,
            value=1,
            inTangentType='linear',
            outTangentType='linear',
        )

        # Create Sphere
        sph_tfm, shp_node = maya.cmds.polySphere()
        maya.cmds.setAttr(sph_tfm + '.tx', -1.0)
        maya.cmds.setAttr(sph_tfm + '.ty', 1.0)
        maya.cmds.setAttr(sph_tfm + '.tz', -25.0)

        # Attributes
        attr_tx = mmapi.Attribute(bundle_tfm + '.tx')
        attr_ty = mmapi.Attribute(bundle_tfm + '.ty')

        # Frames
        frm_list = [
            mmapi.Frame(1, primary=True),
            mmapi.Frame(2, primary=True),
            mmapi.Frame(3, primary=True),
            mmapi.Frame(4, primary=True),
            mmapi.Frame(5, primary=True),
        ]

        # Solver
        sol = mmapi.Solver()
        sol.set_max_iterations(1000)
        sol.set_verbose(True)
        sol.set_frame_list(frm_list)
        sol.set_solver_type(solver_type_index)
        sol.set_scene_graph_mode(scene_graph_mode)

        # Collection
        col = mmapi.Collection()
        col.create_node('mySolveCollection')
        col.add_solver(sol)
        col.add_marker(mkr)
        col.add_attribute(attr_tx)
        col.add_attribute(attr_ty)

        # save the output
        file_name = 'test_solve_marker_enabled_{}_{}_before.ma'.format(
            solver_name, scene_graph_name
        )
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        results = mmapi.execute(col)

        # Ensure the values are correct
        for res in results:
            success = res.get_success()
            res.get_final_error()
            print('error stats: ' + pprint.pformat(res.get_error_stats()))
            print('timer stats: ' + pprint.pformat(res.get_timer_stats()))
            print('solver stats: ' + pprint.pformat(res.get_solver_stats()))
            print(
                'frame error list: ' + pprint.pformat(dict(res.get_frame_error_list()))
            )
            print(
                'marker error list: '
                + pprint.pformat(dict(res.get_marker_error_list()))
            )

            self.assertTrue(success)
            # self.assertGreater(0.001, err)
        # self.assertApproxEqual(maya.cmds.getAttr(bundle_tfm+'.tx'), -6.0)
        # self.assertApproxEqual(maya.cmds.getAttr(bundle_tfm+'.ty'), 3.6)

        # Set Deviation
        mmapi.update_deviation_on_markers([mkr], results)
        mmapi.update_deviation_on_collection(col, results)

        # save the output
        file_name = 'test_solve_marker_enabled_{}_{}_after.ma'.format(
            solver_name, scene_graph_name
        )
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.checkSolveResults(results, allow_max_avg_error=0.02, allow_max_error=0.05)
        return

    def test_ceres_lmder_maya_dag(self):
        self.do_solve(
            'ceres_lmder',
            mmapi.SOLVER_TYPE_CERES_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
        )

    def test_ceres_lmder_mmscenegraph(self):
        self.do_solve(
            'ceres_lmder', mmapi.SOLVER_TYPE_CERES_LMDER, mmapi.SCENE_GRAPH_MODE_AUTO
        )

    def test_ceres_lmdif_maya_dag(self):
        self.do_solve(
            'ceres_lmdif',
            mmapi.SOLVER_TYPE_CERES_LMDIF,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
        )

    def test_ceres_lmdif_mmscenegraph(self):
        self.do_solve(
            'ceres_lmdif', mmapi.SOLVER_TYPE_CERES_LMDIF, mmapi.SCENE_GRAPH_MODE_AUTO
        )

    # def test_cminpack_lmdif_maya_dag(self):
    #     self.do_solve(
    #         'cminpack_lmdif',
    #         mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
    #         mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
    #     )

    # def test_cminpack_lmdif_mmscenegraph(self):
    #     self.do_solve(
    #         'cminpack_lmdif',
    #         mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
    #         mmapi.SCENE_GRAPH_MODE_AUTO,
    #     )

    def test_cminpack_lmder_maya_dag(self):
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
        )

    def test_cminpack_lmder_mmscenegraph(self):
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
        )


if __name__ == '__main__':
    prog = unittest.main()
