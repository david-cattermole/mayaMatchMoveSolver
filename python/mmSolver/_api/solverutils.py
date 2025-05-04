# Copyright (C) 2020 David Cattermole.
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
Solver utilities.

Below are compilable methods that can be re-used by more than one
solver type.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.logger
import mmSolver._api.attribute as attribute
import mmSolver._api.excep as excep
import mmSolver._api.constant as const
import mmSolver._api.action as api_action
import mmSolver._api.compile as api_compile
import mmSolver._api.solveraffects as solveraffects
import mmSolver._api.solverscenegraph as solverscenegraph


LOG = mmSolver.logger.get_logger()
MIN_NUM_ITERATIONS = 3


def create_attr_blocks(use_attr_blocks, attr_list):
    """
    Splits attributes into blocks that should be solved together.

    :type use_attr_blocks: bool
    :type attr_list: [Attribute, ..]
    :rtype: [([Attribute, ..], float)]
    """
    if use_attr_blocks is False:
        attr_blocks = [(attr_list, 1.0)]
        return attr_blocks

    # The Block types (A to D) define groups of attributes to be solved
    # together, or one after the other - in a specific ordering.
    block_a = []
    block_b = []
    block_c = []
    block_d = []

    for attr in attr_list:
        assert isinstance(attr, attribute.Attribute)

        attr_solver_type = api_compile.get_attribute_solver_type(attr)
        if attr_solver_type == const.ATTR_SOLVER_TYPE_REGULAR:
            block_a.append(attr)
        elif attr_solver_type == const.ATTR_SOLVER_TYPE_BUNDLE_TRANSFORM:
            block_a.append(attr)
        elif attr_solver_type == const.ATTR_SOLVER_TYPE_CAMERA_TRANSLATE:
            block_b.append(attr)
        elif attr_solver_type == const.ATTR_SOLVER_TYPE_CAMERA_ROTATE:
            block_c.append(attr)
        elif attr_solver_type == const.ATTR_SOLVER_TYPE_CAMERA_INTRINSIC:
            block_b.append(attr)
        elif attr_solver_type == const.ATTR_SOLVER_TYPE_LENS_DISTORTION:
            block_d.append(attr)
        else:
            raise excep.NotValid

    num_a = len(block_a)
    num_bc = len(block_b) + len(block_c)
    num_d = len(block_d)

    # The importance ratio and ordering of each block in the set is a
    # heuristic shown to work fairly well, but without rigerious mathematics
    # to describe it.
    #
    # The intuition of splitting the blocks up is that when many attributes
    # are input to the minimization engine, the engine doesn't know what to
    # adjust to find the best global minimum and stops before trying the
    # attributes. Here we ensure that individual groups of attributes are
    # solved together, which helps the solver focus on select groups of
    # attributes to minimize the error.
    attr_blocks = []
    if num_a > 0 and num_bc > 0 and num_d == 0:
        attr_blocks = [
            (block_a, 0.1),
            (block_b + block_c, 0.1),
            (block_a, 0.1),
            (block_b + block_c, 0.1),
            (attr_list, 0.6),
        ]

    elif num_a > 0 and num_bc == 0 and num_d > 0:
        attr_blocks = [
            (block_a, 0.1),
            (block_d, 0.1),
            (block_a, 0.1),
            (block_d, 0.1),
            (attr_list, 0.6),
        ]

    elif num_a > 0 and num_bc > 0 and num_d > 0:
        attr_blocks = [
            (block_a, 0.2),
            (block_b + block_c, 0.1),
            (block_d + block_c, 0.1),
            (block_b + block_c, 0.1),
            (block_d + block_c, 0.1),
            (attr_list, 0.4),
        ]

    else:
        attr_blocks = [(attr_list, 1.0)]

    return attr_blocks


def compile_solver_step_blocks_with_cache(
    sol, col, mkr_list, attr_blocks, withtest, cache
):
    total_iter_num = sol.get_max_iterations()
    for attr_list, solve_ratio in attr_blocks:
        if len(attr_list) == 0:
            continue
        if solve_ratio == 0.0:
            continue

        iter_num = max(MIN_NUM_ITERATIONS, int(total_iter_num * solve_ratio))
        sol.set_max_iterations(iter_num)

        generator = api_compile.compile_solver_with_cache(
            sol, col, mkr_list, attr_list, withtest, cache
        )
        for action, vaction in generator:
            yield action, vaction

    sol.set_max_iterations(total_iter_num)
    return


def filter_attr_list(attr_list, use_camera_intrinsics=None, use_lens_distortion=None):
    if use_camera_intrinsics is None:
        use_camera_intrinsics = True
    if use_lens_distortion is None:
        use_lens_distortion = True

    tmp_attr_list = list(attr_list)
    attr_list = []
    for attr in tmp_attr_list:
        attr_solver_type = api_compile.get_attribute_solver_type(attr)
        is_cam_intrinsic = attr_solver_type == const.ATTR_SOLVER_TYPE_CAMERA_INTRINSIC
        is_lens_dist = attr_solver_type == const.ATTR_SOLVER_TYPE_LENS_DISTORTION

        if is_cam_intrinsic and use_camera_intrinsics is False:
            continue
        if is_lens_dist and use_lens_distortion is False:
            continue
        attr_list.append(attr)
    return attr_list


def compile_solver_affects(col, mkr_list, attr_list, frame_list, precomputed_data, withtest):
    # Reset the used hints to 'unknown' before setting 'used' or
    # 'unused' flags.
    generator = compile_reset_used_hints(col, mkr_list, attr_list)
    for action, vaction in generator:
        yield action, vaction

    sol = solveraffects.SolverAffects()
    sol.set_frame_list(frame_list)
    sol.set_precomputed_data(precomputed_data)

    cache = api_compile.create_compile_solver_cache()
    generator = api_compile.compile_solver_with_cache(
        sol, col, mkr_list, attr_list, withtest, cache
    )
    for action, vaction in generator:
        yield action, vaction
    return


def compile_solver_scene_graph(
    col,
    mkr_list,
    attr_list,
    use_animated_attrs,
    use_static_attrs,
    scene_graph_mode,
    precomputed_data,
    withtest,
):
    sol = solverscenegraph.SolverSceneGraph()
    sol.set_attributes_use_animated(use_animated_attrs)
    sol.set_attributes_use_static(use_static_attrs)
    sol.set_scene_graph_mode(scene_graph_mode)
    sol.set_precomputed_data(precomputed_data)

    cache = api_compile.create_compile_solver_cache()
    generator = api_compile.compile_solver_with_cache(
        sol, col, mkr_list, attr_list, withtest, cache
    )
    for action, vaction in generator:
        yield action, vaction
    return


def compile_reset_used_hints(col, mkr_list, attr_list):
    func = 'mmSolver._api.solveraffects.reset_marker_used_hints'
    mkr_nodes = [mkr.get_node() for mkr in mkr_list]
    args = [mkr_nodes]
    kwargs = {}
    action = api_action.Action(func=func, args=args, kwargs=kwargs)
    yield action, None

    func = 'mmSolver._api.solveraffects.reset_attr_used_hints'
    node_attr_list = [attr.get_name() for attr in attr_list]
    args = [col.get_node(), node_attr_list]
    kwargs = {}
    action = api_action.Action(func=func, args=args, kwargs=kwargs)
    yield action, None
    return


def compile_euler_filter(attr_list, withtest):
    """
    Compile a Euler filter to run on all rotation attributes, for
    *all* frames.

    :param attr_list:
        List of Attributes.
    :type attr_list: [Attribute, ..]

    :param withtest:
        Compile the test/validation Action, as well as the solve Action?
    :type withtest: bool

    :return:
        Yields an Action and None, at each iteration.
    :rtype: (Action, None)
    """
    for attr in attr_list:
        attr_type = attr.get_attribute_type()
        if attr_type is None:
            continue
        if attr_type.endswith('Angle') is False:
            continue

        # Don't modify non-animated attributes (this includes
        # locked attributes).
        animated = attr.is_animated()
        if animated is False:
            continue

        node_name = attr.get_node()
        attr_name = attr.get_attr()
        func = 'mmSolver.utils.animcurve.euler_filter_plug'
        args = [node_name, attr_name]
        kwargs = {}
        action = api_action.Action(func=func, args=args, kwargs=kwargs)
        yield action, None
    return
