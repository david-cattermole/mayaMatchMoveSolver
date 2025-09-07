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
Load pre-tracked Markers for the 'opera house' image sequence,
then solve it.

http://danielwedge.com/fmatrix/operahouse.html
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.loadmarker.lib.mayareadfile as marker_read
import mmSolver.tools.createlens.lib as createlens_lib
import test.test_api.apiutils as test_api_utils


LOG = mmSolver.logger.get_logger()


# @unittest.skip
class TestSolveOperaHouse(test_api_utils.APITestCase):
    def do_solve(self, solver_name, solver_type_index, scene_graph_mode):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)
        scene_graph_name = mmapi.SCENE_GRAPH_MODE_NAME_LIST[scene_graph_mode]
        scene_graph_label = mmapi.SCENE_GRAPH_MODE_LABEL_LIST[scene_graph_mode]
        print('Scene Graph:', scene_graph_label)

        # Time Range
        start = 0
        end = 41
        maya.cmds.playbackOptions(
            animationStartTime=start, minTime=start, animationEndTime=end, maxTime=end
        )

        # Camera
        cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
        cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
        maya.cmds.setAttr(cam_tfm + '.rotateOrder', 2)  # zxy
        maya.cmds.setAttr(cam_shp + '.focalLength', 14)
        maya.cmds.setAttr(cam_shp + '.horizontalFilmAperture', 5.4187 / 25.4)
        maya.cmds.setAttr(cam_shp + '.verticalFilmAperture', 4.0640 / 25.4)
        cam = mmapi.Camera(shape=cam_shp)

        # Set Camera Keyframes
        cam_data = {
            '0': (
                -0.19889791581420663,
                0.5591321634949238,
                7.258789219735233,
                -1.9999507874015703,
                -0.3999999999999992,
                0.0,
            ),
            '22': (
                -4.840404384215566,
                0.7543627646977502,
                6.3465857678271425,
                -3.0709513272069815,
                -36.91024116734281,
                0.0,
            ),
            '41': (
                -8.584368967987194,
                0.6990718939718145,
                5.508167213044364,
                -1.4738793091011815,
                -54.30997787050599,
                0.0,
            ),
        }
        for key in sorted(cam_data.keys()):
            frame = int(key)
            for i, attr in enumerate(['tx', 'ty', 'tz', 'rx', 'ry', 'rz']):
                value = cam_data[key][i]
                maya.cmds.setKeyframe(cam_tfm, attribute=attr, time=frame, value=value)
        maya.cmds.setKeyframe(cam_shp, attribute='focalLength', time=start, value=14.0)
        maya.cmds.setKeyframe(cam_shp, attribute='focalLength', time=end, value=14.0)

        # Create lens
        lens = createlens_lib.create_lens_on_camera(cam, force_create_new=None)
        lens_node = lens.get_node()

        # Create image plane
        path = self.get_data_path('operahouse', 'frame00.jpg')
        imgpl = maya.cmds.imagePlane(camera=cam_shp, fileName=path)
        maya.cmds.setAttr(imgpl[1] + '.useFrameExtension', 1)
        maya.cmds.setAttr(imgpl[1] + '.depth', 2000)
        maya.cmds.setAttr(imgpl[1] + '.frameCache', 0)
        maya.cmds.setAttr(imgpl[1] + '.coverageX', 3072)
        maya.cmds.setAttr(imgpl[1] + '.coverageY', 2304)

        # Create Horizon Line
        cir = maya.cmds.circle(name='horizon', nrx=0, nry=1, nrz=0)
        maya.cmds.setAttr(cir[1] + ".radius", 3000)

        # Create Cube for Opera House
        cube = maya.cmds.polyCube()
        maya.cmds.setAttr(cube[0] + ".ty", 0.5)
        maya.cmds.setAttr(cube[0] + ".sx", 2.68)
        maya.cmds.setAttr(cube[0] + ".sy", 0.91625416)
        maya.cmds.setAttr(cube[0] + ".sz", 1.68658365)

        # Marker Group
        mkr_grp = mmapi.MarkerGroup().create_node(cam=cam)
        mkr_grp_node = mkr_grp.get_node()

        # Bundle Group
        bnd_grp = maya.cmds.createNode('transform', name='bundleGroup')
        bnd_fg_grp = maya.cmds.createNode(
            'transform', name='bundles_fg', parent=bnd_grp
        )
        bnd_bg_grp = maya.cmds.createNode(
            'transform', name='bundles_bg', parent=bnd_grp
        )

        # Load Markers
        fg_points = [
            'Track_01',
            'Track_02',
            'Track_05',
            'Track_06',
            'Track_08',
            'Track_09',
            'Track_10',
            'Track_11',
            'Track_19',
            'Track_20',
            'Track_21',
            'Track_22',
            'Track_23',
            'Track_23',
            'Track_24',
            'Track_25',
            'Track_26',
            'Track_27',
        ]
        bg_points = [
            'Track_03',
            'Track_04',
            'Track_07',
            'Track_12',
            'Track_13',
            'Track_14',
            'Track_15',
            'Track_16',
            'Track_17',
            'Track_18',
            'Track_28',
            'Track_29',
            'Track_30',
            'Track_31',
        ]
        bnd_positions = {
            'Track_23': (-0.7669678476654883, 0.704741253611808, 0.11480582185051777),
            'Track_14': (-6.096859889443822, 2.0552736121532478, -64.25806442305448),
            'Track_12': (45.11056705173852, 2.602519222901666, -43.16772737415769),
            'Track_13': (-11.331222134074189, -0.9161249928992397, -63.60343691220178),
            'Track_28': (12.97847320083373, 0.4908757961951475, -6.558878377403925),
            'Track_24': (
                -0.9577362080844809,
                0.11947272894636578,
                -0.29860515939718035,
            ),
            'Track_25': (-0.3816240705349317, 0.09511793539283707, 0.5968218516602972),
            'Track_05': (-0.5497538933513093, 0.9121450956455763, 0.0689419211208016),
            'Track_06': (0.6442115545215732, 0.09146863102772763, 0.2698159600733472),
            'Track_02': (-1.1928085448379213, 0.06849164070024401, 0.741609523996595),
            'Track_17': (4.101733117764308, 0.4416977194116366, -20.775735845844235),
            'Track_16': (10.499779696104385, 2.4959245952203037, -61.65315035391216),
            'Track_21': (0.4422885021421483, 0.15594114410956195, -0.4586671394741284),
            'Track_18': (13.426726902476766, 2.208127581689255, -62.440721369338476),
            'Track_27': (-1.203371663768503, 0.07727436882970459, -0.34432924439358475),
            'Track_07': (24.82344439444535, 3.8981611004590917, -62.57148439047777),
            'Track_26': (-1.036542158437551, 0.1301250303434169, 0.6183349238312523),
            'Track_11': (-1.2868698932117608, 0.07508027422294668, -0.6923287330737453),
            'Track_09': (
                -1.1210978513200678,
                -0.0009538700668097195,
                -0.7481409812887209,
            ),
            'Track_20': (0.5370453995103619, 0.32144750391315535, 0.10037404391850258),
            'Track_08': (-0.35711469535141427, 0.8134673956410489, -0.8873816770491396),
            'Track_19': (-1.0708190128497155, 0.5849715587489718, 0.22909459498373133),
            'Track_10': (-0.8256010837265352, 0.04548785302325305, -0.6865934949556973),
            'Track_30': (12.219883964568602, 1.6676763053004873, -63.511794156133575),
            'Track_22': (-0.42435005852350927, 0.6386843510112235, -1.0271747982989685),
            'Track_31': (14.4768210901898, 1.5761955139450978, -40.10088917167338),
            'Track_15': (-0.17540615158899264, 2.5048877383268424, -64.10912011449136),
            'Track_29': (15.264518808431728, 1.8337698745022983, -62.076762425418536),
            'Track_03': (311.42375656555913, 16.402469194090923, -179.38329132993437),
            'Track_01': (-1.0890118590423876, 0.5109764471108498, -0.707187214616633),
            'Track_04': (209.73939576288353, 12.878819985707446, -150.30617721944793),
        }
        mkr_fg_grp = maya.cmds.createNode('transform', name='fg', parent=mkr_grp_node)
        mkr_bg_grp = maya.cmds.createNode('transform', name='bg', parent=mkr_grp_node)
        path = self.get_data_path('match_mover', 'loadmarker.rz2')
        _, mkr_data_list = marker_read.read(path)
        mkr_list = marker_read.create_nodes(mkr_data_list, cam=cam, mkr_grp=mkr_grp)
        mkr_fg_list = []
        mkr_bg_list = []
        for mkr in mkr_list:
            mkr_node = mkr.get_node()
            mgrp = mkr_grp_node
            bgrp = bnd_grp
            pos = None
            for name in fg_points:
                if name in mkr_node:
                    if name in bnd_positions:
                        pos = bnd_positions[name]
                    mgrp = mkr_fg_grp
                    bgrp = bnd_fg_grp
                    mkr_fg_list.append(mkr)
                    break
            for name in bg_points:
                if name in mkr_node:
                    if name in bnd_positions:
                        pos = bnd_positions[name]
                    mgrp = mkr_bg_grp
                    bgrp = bnd_bg_grp
                    mkr_bg_list.append(mkr)
                    break
            maya.cmds.parent(mkr_node, mgrp, relative=True)

            bnd = mkr.get_bundle()
            bnd_node = bnd.get_node()
            plug_tx = bnd_node + '.tx'
            plug_ty = bnd_node + '.ty'
            plug_tz = bnd_node + '.tz'
            maya.cmds.setAttr(plug_tx, pos[0])
            maya.cmds.setAttr(plug_ty, pos[1])
            maya.cmds.setAttr(plug_tz, pos[2])
            maya.cmds.parent(bnd_node, bgrp, relative=True)

            # bnd_node = bnd.get_node()
            # plug_tx = bnd_node + '.tx'
            # plug_ty = bnd_node + '.ty'
            # plug_tz = bnd_node + '.tz'
            # maya.cmds.setAttr(plug_tx, lock=True)
            # maya.cmds.setAttr(plug_ty, lock=True)
            # maya.cmds.setAttr(plug_tz, lock=True)

        # Frames
        #
        # Root Frames are automatically calculated from the markers.
        root_frm_list = []
        not_root_frm_list = []
        min_frames_per_marker = 3
        frame_nums = mmapi.get_root_frames_from_markers(
            mkr_list, min_frames_per_marker, start, end
        )
        frame_nums = mmapi.root_frames_list_combine(frame_nums, [start, end])
        max_frame_span = 5
        frame_nums = mmapi.root_frames_subdivide(frame_nums, max_frame_span)
        for f in frame_nums:
            frm = mmapi.Frame(f)
            root_frm_list.append(frm)
        for f in range(start, end + 1):
            frm = mmapi.Frame(f)
            not_root_frm_list.append(frm)

        sol_list = []
        sol = mmapi.SolverStandard()
        sol.set_single_frame(False)
        sol.set_root_frame_list(root_frm_list)
        sol.set_frame_list(not_root_frm_list)
        sol.set_only_root_frames(False)
        sol.set_global_solve(True)
        sol.set_solver_type(solver_type_index)
        sol.set_scene_graph_mode(scene_graph_mode)
        sol.set_use_attr_blocks(False)
        sol.set_triangulate_bundles(False)
        sol.set_solve_focal_length(True)
        sol.set_solve_lens_distortion(True)
        sol_list.append(sol)

        # Collection
        col = mmapi.Collection()
        col.create_node('mySolverCollection')
        col.add_solver_list(sol_list)

        # Add markers
        col.add_marker_list(mkr_fg_list)
        col.add_marker_list(mkr_bg_list)

        # Attributes
        attr_cam_tx = mmapi.Attribute(cam_tfm + '.tx')
        attr_cam_ty = mmapi.Attribute(cam_tfm + '.ty')
        attr_cam_tz = mmapi.Attribute(cam_tfm + '.tz')
        attr_cam_rx = mmapi.Attribute(cam_tfm + '.rx')
        attr_cam_ry = mmapi.Attribute(cam_tfm + '.ry')
        attr_cam_rz = mmapi.Attribute(cam_tfm + '.rz')
        attr_cam_focal = mmapi.Attribute(cam_shp + '.focalLength')
        col.add_attribute(attr_cam_tx)
        col.add_attribute(attr_cam_ty)
        col.add_attribute(attr_cam_tz)
        col.add_attribute(attr_cam_rx)
        col.add_attribute(attr_cam_ry)
        col.add_attribute(attr_cam_rz)
        col.add_attribute(attr_cam_focal)

        attr_lens_k1 = mmapi.Attribute(lens_node + '.tdeClassic_distortion')
        attr_lens_k2 = mmapi.Attribute(lens_node + '.tdeClassic_quarticDistortion')
        col.add_attribute(attr_lens_k1)
        col.add_attribute(attr_lens_k2)

        mkr_list = col.get_marker_list()
        for mkr in mkr_list:
            bnd = mkr.get_bundle()
            bnd_node = bnd.get_node()
            attr_tx = mmapi.Attribute(bnd_node + '.tx')
            attr_ty = mmapi.Attribute(bnd_node + '.ty')
            attr_tz = mmapi.Attribute(bnd_node + '.tz')
            col.add_attribute(attr_tx)
            col.add_attribute(attr_ty)
            col.add_attribute(attr_tz)

        # save the output
        file_name = 'test_solve_operahouse_{}_{}_before.ma'.format(
            solver_name, scene_graph_name
        )
        path = self.get_output_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        results = mmapi.execute(col)

        # Ensure the values are correct
        for res in results:
            success = res.get_success()
            err = res.get_final_error()
            print('err', err, 'success', success)

        # Set Deviation
        mmapi.update_deviation_on_markers(mkr_list, results)
        mmapi.update_deviation_on_collection(col, results)

        # save the output
        file_name = 'test_solve_operahouse_{}_{}_after.ma'.format(
            solver_name, scene_graph_name
        )
        path = self.get_output_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.checkSolveResults(results, allow_max_avg_error=4.1, allow_max_error=9.0)
        return

    # # NOTE: Commented out because it takes too long to compute.
    # def test_ceres_lmder_maya_dag(self):
    #     self.do_solve(
    #         'ceres_lmder',
    #         mmapi.SOLVER_TYPE_CERES_LMDER,
    #         mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
    #     )

    def test_ceres_lmder_mmscenegraph(self):
        self.do_solve(
            'ceres_lmder', mmapi.SOLVER_TYPE_CERES_LMDER, mmapi.SCENE_GRAPH_MODE_AUTO
        )

    # # NOTE: Commented out because it takes too long to compute.
    # def test_ceres_lmdif_maya_dag(self):
    #     self.do_solve(
    #         'ceres_lmdif',
    #         mmapi.SOLVER_TYPE_CERES_LMDIF,
    #         mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
    #     )

    # # NOTE: Commented out because the results aren't good enough.
    # def test_ceres_lmdif_mmscenegraph(self):
    #     self.do_solve(
    #         'ceres_lmdif', mmapi.SOLVER_TYPE_CERES_LMDIF, mmapi.SCENE_GRAPH_MODE_AUTO
    #     )

    # # NOTE: Commented out because the results aren't good enough.
    # def test_cminpack_lmdif_maya_dag(self):
    #     self.do_solve(
    #         'cminpack_lmdif',
    #         mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
    #         mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
    #     )

    # # NOTE: Commented out because the results aren't good enough.
    # def test_cminpack_lmdif_mmscenegraph(self):
    #     self.do_solve(
    #         'cminpack_lmdif',
    #         mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
    #         mmapi.SCENE_GRAPH_MODE_AUTO,
    #     )

    # # NOTE: Commented out because it takes too long to compute.
    # def test_cminpack_lmder_maya_dag(self):
    #     self.do_solve(
    #         'cminpack_lmder',
    #         mmapi.SOLVER_TYPE_CMINPACK_LMDER,
    #         mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
    #     )

    def test_cminpack_lmder_mmscenegraph(self):
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_AUTO,
        )


if __name__ == '__main__':
    prog = unittest.main()
