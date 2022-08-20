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
The triangulation solver, used to solve bundles by triangulating.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

import mmSolver.logger

import mmSolver._api.triangulatebundle as tribnd_utils
import mmSolver._api.constant as const
import mmSolver._api.utils as api_utils
import mmSolver._api.bundle as bundle
import mmSolver._api.frame as frame
import mmSolver._api.solverbase as solverbase
import mmSolver._api.attribute as attribute
import mmSolver._api.action as api_action


LOG = mmSolver.logger.get_logger()

BUNDLE_ATTR_NAMES = ['translateX', 'translateY', 'translateZ']


class SolverTriangulate(solverbase.SolverBase):
    """
    An operation to re-calculate the bundle positions using triangulation.
    """

    def __init__(self, *args, **kwargs):
        super(SolverTriangulate, self).__init__(*args, **kwargs)
        self.root_frame_list = None
        return

    # Method exists to be compatible with
    # 'mmSolver._api.compile.compile_solver_with_cache'.
    def get_frame_list(self):
        return [frame.Frame(1)]

    def compile(self, col, mkr_list, attr_list, withtest=False):
        # TODO: Triangulate the (open) bundles here. We triangulate all
        #  valid bundles after the root frames have solved.
        #
        # NOTE: Bundle triangulation can only happen if the camera
        # is not nodal.
        #
        # NOTE: We currently assume the camera is NOT nodal.

        valid_bnd_node_list = []
        for mkr in mkr_list:
            bnd = mkr.get_bundle()
            bnd_node = bnd.get_node()
            valid_bnd_node_list.append(bnd_node)

        valid_node_list = collections.defaultdict(int)
        for attr in attr_list:
            assert isinstance(attr, attribute.Attribute) is True
            attr_name = attr.get_attr()
            if attr_name not in BUNDLE_ATTR_NAMES:
                continue
            attr_node = attr.get_node()
            if attr_node not in valid_bnd_node_list:
                continue
            obj_type = api_utils.get_object_type(attr_node)
            if obj_type == const.OBJECT_TYPE_BUNDLE:
                valid_node_list[attr_node] += 1

        for node, count in valid_node_list.items():
            if count != 3:
                continue
            bnd = bundle.Bundle(node=node)
            bnd_node = bnd.get_node()
            mkr_node_list = [x.get_node() for x in mkr_list]
            bnd_mkr_list = [
                x for x in bnd.get_marker_list() if x.get_node() in mkr_node_list
            ]
            bnd_mkr_node_list = [x.get_node() for x in bnd_mkr_list]
            bnd_cam_node_list = [
                x.get_camera().get_transform_node() for x in bnd_mkr_list
            ]
            bnd_mkr_frm_list = [
                tribnd_utils._get_marker_first_last_frame_list(x, self.root_frame_list)
                for x in bnd_mkr_node_list
            ]
            bnd_mkr_cam_frm_list = zip(
                bnd_mkr_node_list, bnd_cam_node_list, bnd_mkr_frm_list
            )

            args = [bnd_node, bnd_mkr_cam_frm_list]
            kwargs = {}
            action = api_action.Action(
                tribnd_utils._triangulate_bundle_v2, args=args, kwargs=kwargs
            )
            LOG.debug(
                'adding _triangulate_bundle: func=%r',
                tribnd_utils._triangulate_bundle_v2,
                args,
                kwargs,
            )
            yield action, None
        return
