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
Manipulate solvers.
"""

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.time as utils_time


LOG = mmSolver.logger.get_logger()


def create_solver():
    sol = mmapi.Solver()
    sol.set_max_iterations(10)
    sol.set_verbose(True)
    start, end = utils_time.get_maya_timeline_range_inner()
    for f in xrange(start, end + 1):
        frm = mmapi.Frame(f)
        sol.add_frame(frm)
    return sol


def get_solvers_from_collection(col):
    sol_list = col.get_solver_list()
    return sol_list


def add_solver_to_collection(sol, col):
    return col.add_solver(sol)


def remove_solver_from_collection(sol, col):
    return col.remove_solver(sol)
