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

import mmSolver.logger
import mmSolver._api.action as api_action
import mmSolver._api.compile as api_compile
import mmSolver._api.solveraffects as solveraffects


LOG = mmSolver.logger.get_logger()


def compile_solver_affects(col, mkr_list, attr_list,
                           precomputed_data,
                           withtest):
    sol = solveraffects.SolverAffects()
    sol.set_precomputed_data(precomputed_data)

    cache = api_compile.create_compile_solver_cache()
    generator = api_compile.compile_solver_with_cache(
        sol, col, mkr_list, attr_list, withtest, cache)
    for action, vaction in generator:
        yield action, vaction
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

        # Don't modify locked attributes.
        locked = attr.is_locked()
        if locked is False:
            continue

        node_name = attr.get_node()
        attr_name = attr.get_attr()
        func = 'mmSolver.utils.animcurve.euler_filter_plug'
        args = [node_name, attr_name]
        kwargs = {}
        action = api_action.Action(
            func=func,
            args=args,
            kwargs=kwargs)
        yield action, None
    return
