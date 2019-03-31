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