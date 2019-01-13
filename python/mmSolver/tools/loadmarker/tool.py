"""
The Load Marker tool - user facing.
"""

import maya.cmds
import mmSolver.api as mmapi
import mmSolver.logger
# import mmSolver.tools.selection.filternodes as filternodes
# import mmSolver.tools.loadmarker.formatmanager as formatmanager


LOG = mmSolver.logger.get_logger()


# def main(file_path, cam=None, **kwargs):
#     raise NotImplementedError


def open_window():
    mmapi.load_plugin()
    import mmSolver.tools.loadmarker.ui.loadmarker_window as loadmarker_window
    loadmarker_window.main()
