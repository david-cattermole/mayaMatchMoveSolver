"""
The Solver UI tool.
"""

import mmSolver.logger
import mmSolver.tools.solver.ui.solver_window


LOG = mmSolver.logger.get_logger()


def open_window():
    mmSolver.tools.solver.ui.solver_window.main(show=True)
    return
