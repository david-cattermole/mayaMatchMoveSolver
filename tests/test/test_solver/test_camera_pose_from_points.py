# Copyright (C) 2022 David Cattermole.
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
Calculate the camera and bundle poses from 2D marker positions only
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pprint
import time
import unittest

try:
    import maya.standalone

    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds

import mmSolver.utils.python_compat as pycompat
import mmSolver.api as mmapi

import test.test_solver.solverutils as solverUtils


# @unittest.skip
class TestCameraPoseResection(solverUtils.SolverTestCase):
    def test_six_point_pose_resection1(self):
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
        mkr_bnd_list = []
        mkr_nodes = (
            maya.cmds.listRelatives(mkr_grp_node, children=True, shapes=False) or []
        )
        for node in mkr_nodes:
            if node.endswith('_MKR') is False:
                continue
            assert mmapi.get_object_type(node) == 'marker'
            mkr = mmapi.Marker(node=node)
            bnd = mkr.get_bundle()
            if bnd is None:
                continue
            mkr_node = mkr.get_node()
            bnd_node = bnd.get_node()
            if bnd_node is None:
                continue
            if mkr_node is None:
                continue
            mkr_bnd = (mkr_node, bnd_node)
            mkr_bnd_list.append(mkr_bnd)
        assert len(mkr_bnd_list) > 0

        frames = list(range(start_frame, end_frame + 1))

        # Remove animation.
        attrs = [
            'translateX',
            'translateY',
            'translateZ',
            'rotateX',
            'rotateY',
            'rotateZ',
            'focalLength',
        ]
        maya.cmds.cutKey(
            [cam_tfm_node, cam_shp_node],
            attribute=attrs,
            time=(
                frames[1],
                frames[-1],
            ),
        )
        maya.cmds.setKeyframe(cam_tfm_node, attribute=attrs, time=frames[0], value=0.0)
        maya.cmds.setKeyframe(
            cam_shp_node, attribute='focalLength', time=frames[0], value=27.0
        )

        kwargs = {
            'setValues': True,
            'frame': frames,
            'camera': cam_tfm_node,
            'marker': mkr_bnd_list,
        }

        # save the input
        file_name = 'solver_camera_pose_from_points_six_point_pose1_before.ma'
        path = self.get_output_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        assert 'mmCameraPoseFromPoints' in dir(maya.cmds)
        s = time.time()
        result = maya.cmds.mmCameraPoseFromPoints(**kwargs)
        print('result:', pprint.pformat(result))
        e = time.time()
        print('total time:', e - s)

        # save the output
        file_name = 'solver_camera_pose_from_points_six_point_pose1_after.ma'
        path = self.get_output_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)


if __name__ == '__main__':
    prog = unittest.main()
