# Copyright (C) 2019, 2021 David Cattermole.
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
The Copy/Paste Marker tool.

This tool will save the a marker to a temporary file, for loading in
third-party software (such as 3DEqualizer).
"""

import os

import maya.cmds

import mmSolver.logger

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtGui as QtGui

import mmSolver.utils.time as time_utils
import mmSolver.utils.camera as camera_utils
import mmSolver.utils.tools as tools_utils
import mmSolver.tools.savemarkerfile.lib as lib
import mmSolver.api as mmapi


LOG = mmSolver.logger.get_logger()


def main():
    nodes = maya.cmds.ls(
        selection=True,
        long=True,
        type='transform') or []
    if len(nodes) == 0:
        LOG.warn("Please select some Marker nodes.")
        return
    mkr_list = [mmapi.Marker(node=node) for node in nodes]
    mkr_list = [mkr for mkr in mkr_list if mkr.get_node()]
    if len(mkr_list) == 0:
        LOG.warn("Please select some Marker nodes.")
        return
    frame_range = time_utils.get_maya_timeline_range_outer()

    data = None
    with tools_utils.tool_context(use_undo_chunk=False,
                                  use_dg_evaluation_mode=True,
                                  disable_viewport=True):
        data = lib.generate(mkr_list, frame_range)
    if data is None:
        return None

    # Write out file.
    file_path = lib.write_temp_file(data)
    if not os.path.isfile(file_path):
        msg = 'Failed to write temp file. path=%r'
        LOG.error(msg, file_path)
        return
    msg = 'Successfully wrote to temporary file. path=%r'
    LOG.info(msg, file_path)

    # Set Copy/Paste Clipboard buffer.
    try:
        clippy = QtGui.QClipboard()
        clippy.setText(file_path)
    except Exception as e:
        msg = 'Could not set file path on clipboard. path=%r'
        LOG.warn(msg, file_path)
        LOG.info(str(e))
    return file_path
