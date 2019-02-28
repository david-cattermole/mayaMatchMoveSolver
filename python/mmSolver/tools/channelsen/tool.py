"""
The channelsen - user facing.
"""

import mmSolver.logger


LOG = mmSolver.logger.get_logger()


def main():
    """
    Open the Channel Sensitivity window.
    """
    import mmSolver.tools.channelsen.ui.channelsen_window as window
    window.main()
