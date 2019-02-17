"""
The channelsen - user facing.
"""

import mmSolver.logger


LOG = mmSolver.logger.get_logger()


def main():
    import mmSolver.tools.channelsen.ui.channelsen_window as window
    window.main()
