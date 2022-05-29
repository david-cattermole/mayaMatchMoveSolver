# Copyright (C) 2021 David Cattermole.
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
The Save Marker File tool.

This tool will save the selected Markers to a .uv file, for loading in
third-party software (such as 3DEqualizer).
"""

import maya.cmds

import mmSolver.logger

import mmSolver.utils.time as time_utils
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
    data = lib.generate(mkr_list, frame_range)

    # Ask user for file name to write out.
    basic_filter = "*.uv"
    file_path = maya.cmds.fileDialog2(
        caption='Output .uv file',
        okCaption='Save',
        fileMode=0,  # 0="Any file, whether it exists or not."
        fileFilter=basic_filter,
        returnFilter=False,
        dialogStyle=2)
    file_path = file_path[0]

    result = lib.write_file(file_path, data)
    if result:
        LOG.info('Successfully written file: %r', file_path)
    else:
        LOG.warn('Failed to write file: %r', file_path)
    return
