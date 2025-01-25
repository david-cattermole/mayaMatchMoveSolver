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
Test file based on 3DEqualizer 'stA' image sequence.

The Maya file loaded contains a good 3DEqualizer solve.  This
test tests the solver to ensure it produces good results,
given an already good solution.

The 'stA' image sequence has a frame range of 0 to 94.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import maya.cmds

import mmSolver.logger
import mmSolver.utils.python_compat as pycompat
import mmSolver.api as mmapi
import test.test_api.apiutils as test_api_utils


LOG = mmSolver.logger.get_logger()


# @unittest.skip
class TestSolveRefineGoodSolveStA(test_api_utils.APITestCase):
    def do_solve(self, solver_name, solver_type_index, scene_graph_mode):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)
        scene_graph_name = mmapi.SCENE_GRAPH_MODE_NAME_LIST[scene_graph_mode]
        scene_graph_label = mmapi.SCENE_GRAPH_MODE_LABEL_LIST[scene_graph_mode]
        print('Scene Graph:', scene_graph_label)

        start_frame = 0
        end_frame = 94

        path = self.get_data_path('scenes', 'stA_v001.ma')
        ok = maya.cmds.file(path, open=True, ignoreVersion=True, force=True)
        assert isinstance(ok, pycompat.TEXT_TYPE)

        # Camera
        cam_name = 'stA_1_1Shape1'
        cam = mmapi.Camera(shape=cam_name)
        cam_tfm_node = cam.get_transform_node()
        cam_shp_node = cam.get_shape_node()

        # Marker Group
        mkr_grp_name = 'markerGroup1'
        mkr_grp = mmapi.MarkerGroup(node=mkr_grp_name)
        mkr_grp_node = mkr_grp.get_node()

        # Markers
        mkr_list = []
        bnd_list = []
        mkr_nodes = (
            maya.cmds.listRelatives(mkr_grp_node, children=True, shapes=False) or []
        )
        for node in mkr_nodes:
            if node.endswith('_MKR') is False:
                continue
            assert mmapi.get_object_type(node) == 'marker'
            mkr = mmapi.Marker(node=node)
            bnd = mkr.get_bundle()
            mkr_list.append(mkr)
            bnd_list.append(bnd)
        assert len(mkr_list) > 0
        assert len(bnd_list) > 0

        # Attributes
        attr_list = []
        for bnd in bnd_list:
            bnd_node = bnd.get_node()
            attr_tx = mmapi.Attribute(node=bnd_node, attr='tx')
            attr_ty = mmapi.Attribute(node=bnd_node, attr='ty')
            attr_tz = mmapi.Attribute(node=bnd_node, attr='tz')
            attr_list.append(attr_tx)
            attr_list.append(attr_ty)
            attr_list.append(attr_tz)
        attr_tx = mmapi.Attribute(node=cam_tfm_node, attr='tx')
        attr_ty = mmapi.Attribute(node=cam_tfm_node, attr='ty')
        attr_tz = mmapi.Attribute(node=cam_tfm_node, attr='tz')
        attr_rx = mmapi.Attribute(node=cam_tfm_node, attr='rx')
        attr_ry = mmapi.Attribute(node=cam_tfm_node, attr='ry')
        attr_rz = mmapi.Attribute(node=cam_tfm_node, attr='rz')
        attr_fl = mmapi.Attribute(node=cam_shp_node, attr='focalLength')
        attr_list.append(attr_tx)
        attr_list.append(attr_ty)
        attr_list.append(attr_tz)
        attr_list.append(attr_rx)
        attr_list.append(attr_ry)
        attr_list.append(attr_rz)
        attr_list.append(attr_fl)

        # Frames
        #
        # Root Frames are automatically calculated from the markers.
        root_frm_list = []
        not_root_frm_list = []
        min_frames_per_marker = 2
        frame_nums = mmapi.get_root_frames_from_markers(
            mkr_list, min_frames_per_marker, start_frame, end_frame
        )
        for f in frame_nums:
            frm = mmapi.Frame(f)
            root_frm_list.append(frm)
        for f in range(start_frame, end_frame + 1):
            frm = mmapi.Frame(f)
            not_root_frm_list.append(frm)

        # Solvers
        sol_list = []
        sol = mmapi.SolverStandard()
        sol.set_root_frame_list(root_frm_list)
        sol.set_frame_list(not_root_frm_list)
        sol.set_only_root_frames(False)
        sol.set_global_solve(False)
        sol.set_use_single_frame(False)
        sol.set_solver_type(solver_type_index)
        sol.set_scene_graph_mode(scene_graph_mode)
        sol_list.append(sol)

        # Collection
        col = mmapi.Collection()
        col.create_node('mySolveCollection')
        col.set_solver_list(sol_list)
        col.add_marker_list(mkr_list)
        col.add_attribute_list(attr_list)

        # save the output
        file_name = 'test_solve_stA_refine_{}_{}_before.ma'.format(
            solver_name, scene_graph_name
        )
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        LOG.warning('Running Solver Test... (it may take some time to finish).')
        results = mmapi.execute(col)

        # Set Deviation
        mmapi.update_deviation_on_markers(mkr_list, results)
        mmapi.update_deviation_on_collection(col, results)

        # save the output
        file_name = 'test_solve_stA_refine_{}_{}_after.ma'.format(
            solver_name, scene_graph_name
        )
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.checkSolveResults(results, allow_max_avg_error=1.7, allow_max_error=3.0)
        return

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
            mmapi.SCENE_GRAPH_MODE_AUTO,
        )


if __name__ == '__main__':
    prog = unittest.main()
