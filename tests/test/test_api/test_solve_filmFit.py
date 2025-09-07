# Copyright (C) 2023 David Cattermole.
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
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
import unittest

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import test.test_api.apiutils as test_api_utils


LOG = mmSolver.logger.get_logger()

FILM_FIT_FILL_VALUE = 0
FILM_FIT_HORIZONTAL_VALUE = 1
FILM_FIT_VERTICAL_VALUE = 2
FILM_FIT_OVERSCAN_VALUE = 3
FILM_FIT_VALUES = [
    FILM_FIT_FILL_VALUE,
    FILM_FIT_HORIZONTAL_VALUE,
    FILM_FIT_VERTICAL_VALUE,
    FILM_FIT_OVERSCAN_VALUE,
]
FILM_FIT_LABELS = {
    FILM_FIT_FILL_VALUE: 'Fill',
    FILM_FIT_HORIZONTAL_VALUE: 'Horizontal',
    FILM_FIT_VERTICAL_VALUE: 'Vertical',
    FILM_FIT_OVERSCAN_VALUE: 'Overscan',
}


def create_marker_bundle(cam, mkr_values, bnd_values):
    assert len(mkr_values) == 2
    assert len(bnd_values) == 3
    assert isinstance(cam, mmapi.Camera)

    bnd_name = mmapi.get_new_bundle_name('bundle1')
    bnd = mmapi.Bundle().create_node(name=bnd_name)

    mkr_name = mmapi.get_new_marker_name('marker1')
    mkr = mmapi.Marker().create_node(name=mkr_name, cam=cam, bnd=bnd)

    bnd_node = bnd.get_node()
    bnd_x = bnd_values[0]
    bnd_y = bnd_values[1]
    bnd_z = bnd_values[2]
    maya.cmds.setAttr('{}.tx'.format(bnd_node), bnd_x)
    maya.cmds.setAttr('{}.ty'.format(bnd_node), bnd_y)
    maya.cmds.setAttr('{}.tz'.format(bnd_node), bnd_z)

    mkr_node = mkr.get_node()
    mkr_x = mkr_values[0]
    mkr_y = mkr_values[1]
    maya.cmds.setAttr('{}.tx'.format(mkr_node), mkr_x)
    maya.cmds.setAttr('{}.ty'.format(mkr_node), mkr_y)
    return mkr, bnd


# @unittest.skip
class TestSolveFilmFit(test_api_utils.APITestCase):

    # @unittest.skip
    def do_solve(
        self,
        solver_name,
        solver_type_index,
        scene_graph_mode,
        film_fit,
        use_standard_solver,
    ):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)
        scene_graph_name = mmapi.SCENE_GRAPH_MODE_NAME_LIST[scene_graph_mode]
        scene_graph_label = mmapi.SCENE_GRAPH_MODE_LABEL_LIST[scene_graph_mode]
        print('Scene Graph:', scene_graph_label)

        film_fit_name = FILM_FIT_LABELS[film_fit]
        print('Film Fit:', film_fit, 'Name:', film_fit_name)

        # Scene constants
        start_frame = 0
        end_frame = 71
        maya.cmds.playbackOptions(
            animationStartTime=start_frame,
            minTime=start_frame,
            animationEndTime=end_frame,
            maxTime=end_frame,
        )

        s = time.time()

        # Import the MEL script from 3DEqualizer.
        file_name = 'trackboy_slim_mel_export.mel'
        path = self.get_data_path('3de_v4', file_name)
        maya.cmds.file(path, i=True, force=True)

        # Cube geometry
        cube_tfm, poly_shp = maya.cmds.polyCube()
        maya.cmds.setAttr(cube_tfm + '.tx', 77.9)
        maya.cmds.setAttr(cube_tfm + '.ty', 128.3)
        maya.cmds.setAttr(cube_tfm + '.tz', 0.0)
        maya.cmds.setAttr(cube_tfm + '.rx', 33.7)
        maya.cmds.setAttr(cube_tfm + '.ry', -7.1)
        maya.cmds.setAttr(cube_tfm + '.rz', -57.7)
        maya.cmds.setAttr(cube_tfm + '.sx', 26.0)
        maya.cmds.setAttr(cube_tfm + '.sy', 26.0)
        maya.cmds.setAttr(cube_tfm + '.sz', 26.0)

        if use_standard_solver is False:
            # Attributes must be keyed to be adjusted by the "Basic"
            # solver.
            attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
            for attr in attrs:
                maya.cmds.setKeyframe('{}.{}'.format(cube_tfm, attr))

        # Camera attributes
        cam_tfm = 'trackboy_1_1'
        cam = mmapi.Camera(cam_tfm)
        cam_shp = cam.get_shape_node()
        maya.cmds.setAttr('{}.filmFit'.format(cam_shp), film_fit)

        # Remove overscan values on camera film back, and set to
        # same values as in 3DE.
        film_back_width_mm = 28.029668
        film_back_height_mm = 18.647837
        film_back_width_inch = film_back_width_mm / 25.4
        film_back_height_inch = film_back_height_mm / 25.4
        maya.cmds.setAttr(
            '{}.horizontalFilmAperture'.format(cam_shp), film_back_width_inch
        )
        maya.cmds.setAttr(
            '{}.verticalFilmAperture'.format(cam_shp), film_back_height_inch
        )

        # Collection to solve.
        col = mmapi.Collection()
        col.create_node('myCollection')

        # Set Markers and Bundles
        marker_values = [
            (-0.024518048, 0.086120737),
            (0.098380867, 0.124784005),
            (0.134181899, 0.037203894),
            (0.00967453, -0.009284776),
            (-0.035734883, 0.05381131),
            (-0.001395078, -0.04001695),
            (0.120727048, 0.006345424),
        ]
        bundle_values = [
            (-0.5, 0.5, 0.5),
            (-0.5, 0.5, -0.5),
            (0.5, 0.5, -0.5),
            (0.5, 0.5, 0.5),
            (-0.5, -0.5, 0.5),
            (0.5, -0.5, 0.5),
            (0.5, -0.5, -0.5),
        ]
        mkr_list = []
        for mkr_values, bnd_values in zip(marker_values, bundle_values):
            mkr, bnd = create_marker_bundle(cam, mkr_values, bnd_values)
            mkr_list.append(mkr)

            # Parent the bundle under the cube.
            bnd_node = bnd.get_node()
            maya.cmds.parent(bnd_node, cube_tfm, relative=True)

        # Frames
        frm = mmapi.Frame(0)
        frm_list = [frm]

        # Run solver!
        sol_list = []
        if use_standard_solver is True:
            sol = mmapi.SolverStandard()
            sol.set_only_root_frames(False)
            sol.set_root_frame_list(frm_list)
            sol.set_use_single_frame(True)
            sol.set_single_frame(frm)
        else:
            sol = mmapi.SolverBasic()
            sol.set_use_single_frame(True)
            sol.set_single_frame(frm)
        sol.set_solver_type(solver_type_index)
        sol.set_scene_graph_mode(scene_graph_mode)
        sol_list.append(sol)

        # Note that TZ is not solved, because if it is solved there is
        # an infinite number of possible solve results, because any
        # scale is valid. By locking TZ to a specific value, only one
        # screen-depth and one scale is valid.
        attr_list = [
            mmapi.Attribute(node=cube_tfm, attr='translateX'),
            mmapi.Attribute(node=cube_tfm, attr='translateY'),
            mmapi.Attribute(node=cube_tfm, attr='rotateX'),
            mmapi.Attribute(node=cube_tfm, attr='rotateY'),
            mmapi.Attribute(node=cube_tfm, attr='rotateZ'),
            mmapi.Attribute(node=cube_tfm, attr='scaleX'),
            mmapi.Attribute(node=cube_tfm, attr='scaleY'),
            mmapi.Attribute(node=cube_tfm, attr='scaleZ'),
        ]
        col.set_marker_list(mkr_list)
        col.set_attribute_list(attr_list)
        col.set_solver_list(sol_list)

        e = time.time()
        print('pre-solve time:', e - s)

        # save the output, before.
        file_name = 'test_solve_filmFit_{}_{}_filmFit{}_before.ma'.format(
            solver_name, scene_graph_name, film_fit_name
        )
        path = self.get_output_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        s = time.time()
        solres_list = mmapi.execute(col)
        e = time.time()
        print('total time:', e - s)

        # Set Deviation
        mkr_list = col.get_marker_list()
        mmapi.update_deviation_on_markers(mkr_list, solres_list)
        mmapi.update_deviation_on_collection(col, solres_list)

        # save the output
        file_name = 'test_solve_filmFit_{}_{}_filmFit{}_after.ma'.format(
            solver_name, scene_graph_name, film_fit_name
        )
        path = self.get_output_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.checkSolveResults(
            solres_list, allow_max_avg_error=0.8, allow_max_error=0.8
        )
        return

    def test_cminpack_lmder_maya_dag_film_fit_fill_solver_basic(self):
        use_standard_solver = False
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
            FILM_FIT_FILL_VALUE,
            use_standard_solver,
        )

    def test_cminpack_lmder_maya_dag_film_fit_fill_solver_standard(self):
        use_standard_solver = True
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
            FILM_FIT_FILL_VALUE,
            use_standard_solver,
        )

    def test_cminpack_lmder_maya_dag_film_fit_horizontal_solver_basic(self):
        use_standard_solver = False
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
            FILM_FIT_HORIZONTAL_VALUE,
            use_standard_solver,
        )

    def test_cminpack_lmder_maya_dag_film_fit_horizontal_solver_standard(self):
        use_standard_solver = True
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
            FILM_FIT_HORIZONTAL_VALUE,
            use_standard_solver,
        )

    def test_cminpack_lmder_maya_dag_film_fit_vertical_solver_basic(self):
        use_standard_solver = False
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
            FILM_FIT_VERTICAL_VALUE,
            use_standard_solver,
        )

    def test_cminpack_lmder_maya_dag_film_fit_vertical_solver_standard(self):
        use_standard_solver = True
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
            FILM_FIT_VERTICAL_VALUE,
            use_standard_solver,
        )

    def test_cminpack_lmder_maya_dag_film_fit_overscan_solver_basic(self):
        use_standard_solver = False
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
            FILM_FIT_OVERSCAN_VALUE,
            use_standard_solver,
        )

    def test_cminpack_lmder_maya_dag_film_fit_overscan_solver_standard(self):
        use_standard_solver = True
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
            FILM_FIT_OVERSCAN_VALUE,
            use_standard_solver,
        )

    def test_cminpack_lmder_mmscenegraph_film_fit_fill_solver_basic(self):
        use_standard_solver = False
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
            FILM_FIT_FILL_VALUE,
            use_standard_solver,
        )

    def test_cminpack_lmder_mmscenegraph_film_fit_fill_solver_standard(self):
        use_standard_solver = True
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
            FILM_FIT_FILL_VALUE,
            use_standard_solver,
        )

    def test_cminpack_lmder_mmscenegraph_film_fit_horizontal_solver_basic(self):
        use_standard_solver = False
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
            FILM_FIT_HORIZONTAL_VALUE,
            use_standard_solver,
        )

    def test_cminpack_lmder_mmscenegraph_film_fit_horizontal_solver_standard(self):
        use_standard_solver = True
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
            FILM_FIT_HORIZONTAL_VALUE,
            use_standard_solver,
        )

    def test_cminpack_lmder_mmscenegraph_film_fit_vertical_solver_basic(self):
        use_standard_solver = False
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
            FILM_FIT_VERTICAL_VALUE,
            use_standard_solver,
        )

    def test_cminpack_lmder_mmscenegraph_film_fit_vertical_solver_standard(self):
        use_standard_solver = True
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
            FILM_FIT_VERTICAL_VALUE,
            use_standard_solver,
        )

    def test_cminpack_lmder_mmscenegraph_film_fit_overscan_solver_basic(self):
        use_standard_solver = False
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
            FILM_FIT_OVERSCAN_VALUE,
            use_standard_solver,
        )

    def test_cminpack_lmder_mmscenegraph_film_fit_overscan_solver_standard(self):
        use_standard_solver = True
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
            FILM_FIT_OVERSCAN_VALUE,
            use_standard_solver,
        )


if __name__ == '__main__':
    prog = unittest.main()
