"""
The Load Marker tool - user facing.
"""

import maya.cmds
import mmSolver.api as mmapi
import mmSolver.logger
import mmSolver.tools.selection.filternodes as filternodes
import mmSolver.tools.loadmarker.formatmanager as formatmanager
# import mmSolver.tools.loadmarker.lib as lib


LOG = mmSolver.logger.get_logger()


def main(file_path, cam=None, **kwargs):
    raise NotImplementedError
