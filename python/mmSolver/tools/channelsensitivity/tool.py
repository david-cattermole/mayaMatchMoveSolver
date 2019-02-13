"""
The Load Marker tool - user facing.
"""

import maya.cmds
import mmSolver.api as mmapi
import mmSolver.logger
# import mmSolver.tools.selection.filternodes as filternodes
# import mmSolver.tools.loadmarker.formatmanager as formatmanager


LOG = mmSolver.logger.get_logger()


def main():
    import mmSolver.tools.channelsensitivity.ui.channelsensitivity_window as window
    window.main()
