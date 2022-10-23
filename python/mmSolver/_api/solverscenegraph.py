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
Solver to construct the scene graph, to detect failure before a
proper solve.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.logger
import mmSolver._api.constant as const
import mmSolver._api.frame as frame
import mmSolver._api.action as api_action
import mmSolver._api.solverbase as solverbase
import mmSolver._api.compile as api_compile

LOG = mmSolver.logger.get_logger()


class SolverSceneGraph(solverbase.SolverBase):
    """
    SolverSceneGraph is a metadata calculation solver. SolverSceneGraph
    does not directly adjust attributes.

    The SolverSceneGraph contains no properties, other than the base
    Markers, and Attributes lists.
    """

    def __init__(self, *args, **kwargs):
        """
        Create a SolverSceneGraph class with default values.

        :param args: Not used.
        :param kwargs: Not used.
        """
        super(SolverSceneGraph, self).__init__(*args, **kwargs)
        self._use_animated_attributes = True
        self._use_static_attributes = True
        return

    def get_frame_list(self):
        return [frame.Frame(1)]

    ############################################################################

    def get_attributes_use_animated(self):
        return self._use_animated_attributes

    def set_attributes_use_animated(self, value):
        assert isinstance(value, (bool, int))
        self._use_animated_attributes = bool(value)

    def get_attributes_use_static(self):
        return self._use_static_attributes

    def set_attributes_use_static(self, value):
        assert isinstance(value, (bool, int))
        self._use_static_attributes = bool(value)

    ############################################################################

    def get_scene_graph_mode(self):
        """
        :rtype: int
        """
        return self._data.get(
            'scene_graph_mode', const.SOLVER_STD_SCENE_GRAPH_MODE_DEFAULT_VALUE
        )

    def set_scene_graph_mode(self, value):
        """
        :param value: Value to be set.
        :type value: int
        """
        assert isinstance(value, int)
        self._data['scene_graph_mode'] = value

    ############################################################################

    def compile(self, col, mkr_list, attr_list, withtest=False):
        """
        Compiles data given into flags for a single run of 'mmSolver'.

        :param self: The solver to compile
        :type self: Solver

        :param col: The collection to compile.
        :type col: Collection

        :param mkr_list: Markers to measure
        :type mkr_list: list of Marker

        :param attr_list: Attributes to solve for
        :type attr_list: list of Attribute

        :return:
            Yields a tuple of two Actions at each iteration. First
            action is the solver action, second action is for
            validation of the solve.
        :rtype: (Action, Action)
        """
        assert isinstance(self, solverbase.SolverBase)
        assert isinstance(self, SolverSceneGraph)
        assert isinstance(mkr_list, list)
        assert isinstance(attr_list, list)

        if withtest is not True:
            return

        func = 'maya.cmds.mmSolverSceneGraph'
        args = []
        kwargs = dict()
        kwargs['camera'] = []
        kwargs['marker'] = []
        kwargs['attr'] = []
        kwargs['frame'] = []
        kwargs['sceneGraphMode'] = self.get_scene_graph_mode()
        kwargs['mode'] = 'debugConstruct'

        # Get precomputed data to reduce re-querying Maya for data.
        precomputed_data = self.get_precomputed_data()
        mkr_state_values = precomputed_data.get(solverbase.MARKER_STATIC_VALUES_KEY)
        attr_state_values = precomputed_data.get(solverbase.ATTR_STATIC_VALUES_KEY)

        # Get Markers and Cameras
        markers, cameras = api_compile.markersAndCameras_compile_flags(
            mkr_list, mkr_static_values=mkr_state_values
        )
        if len(markers) == 0 and len(cameras) == 0:
            LOG.warning('No Markers or Cameras found!')
            return
        elif len(markers) == 0:
            LOG.warning('No Markers found!')
            return
        elif len(cameras) == 0:
            LOG.warning('No Cameras found!')
            return

        # Get Attributes
        use_animated = self._use_animated_attributes
        use_static = self._use_static_attributes
        attrs = api_compile.attributes_compile_flags(
            col,
            attr_list,
            use_animated,
            use_static,
            attr_static_values=attr_state_values,
        )
        if len(attrs) == 0:
            LOG.warning('No Attributes found!')
            return

        # Get Frames
        # TODO: Make the user set the correct frame list.
        frm_list = self.get_frame_list()
        frame_use_tags = ['normal']
        frames = api_compile.frames_compile_flags(frm_list, frame_use_tags)
        if len(frames) == 0:
            LOG.warning('No Frames found!')
            return

        kwargs['marker'] = markers
        kwargs['camera'] = cameras
        kwargs['attr'] = attrs
        kwargs['frame'] = frames

        action = api_action.Action(func=func, args=args, kwargs=kwargs)
        yield action, action
