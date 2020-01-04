# Copyright (C) 2019 David Cattermole.
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
Test functions for transform utilities module.
"""

import unittest

import test.test_utils.utilsutils as test_utils

import maya.cmds
import mmSolver.utils.transform as mod


# @unittest.skip
class TestTransform(test_utils.UtilsTestCase):
    """
    Test transform module.
    """

    def test_set_transform_values(self):
        """
        """
        start_frame = 1001
        end_frame = 1101
        node = maya.cmds.createNode('transform')
        maya.cmds.setKeyframe(node, attribute='translateX', time=start_frame, value=-100.0)
        maya.cmds.setKeyframe(node, attribute='translateX', time=end_frame, value=100.0)
        maya.cmds.setKeyframe(node, attribute='translateY', time=start_frame, value=-10.0)
        maya.cmds.setKeyframe(node, attribute='translateY', time=end_frame, value=10.0)
        maya.cmds.setKeyframe(node, attribute='rotateY', time=start_frame, value=90.0)
        maya.cmds.setKeyframe(node, attribute='rotateY', time=end_frame, value=-90.0)
        frame_range = list(range(start_frame, end_frame + 1))

        tfm_node = mod.TransformNode(node=node)

        tfm_cache = mod.TransformMatrixCache()
        tfm_cache.add_node_attr(tfm_node, 'worldMatrix[0]', frame_range)
        tfm_cache.process()

        dst_node = maya.cmds.createNode('transform')
        dst_tfm_node = mod.TransformNode(node=dst_node)

        mod.set_transform_values(tfm_cache, frame_range,
            tfm_node, dst_tfm_node,
            delete_static_anim_curves=True,
        )

        # save the output scene file
        path = 'test_transform.ma'
        path = self.get_data_path(path)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        return


if __name__ == '__main__':
    prog = unittest.main()
