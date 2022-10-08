# Copyright (C) 2022 David Cattermole.
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
The Save Lens File tool.

This tool will save the selected Lenss to a .uv file, for loading in
third-party software (such as 3DEqualizer).
"""

import maya.cmds

import mmSolver.logger

import mmSolver.utils.time as time_utils
import mmSolver.utils.camera as camera_utils
import mmSolver.tools.savelensfile.lib as lib
import mmSolver.tools.cameracontextmenu.lib.lens as menu_lib_lens
import mmSolver.api as mmapi


LOG = mmSolver.logger.get_logger()


def main():
    nodes = maya.cmds.ls(selection=True, long=True) or []
    if len(nodes) == 0:
        LOG.warn("Please select one camera node.")
        return

    cam_nodes = mmapi.filter_camera_nodes(nodes)
    if len(cam_nodes) != 1:
        LOG.warn("Please select one camera node.")
        return

    cam_tfm, cam_shp = camera_utils.get_camera(cam_nodes[0])
    if cam_tfm is None or cam_shp is None:
        LOG.warn("Please select one camera node.")
        return

    cam = mmapi.Camera(shape=cam_shp)
    lens_nodes = menu_lib_lens.get_camera_lens_nodes(cam_shp)
    if len(lens_nodes) == 0:
        LOG.warn("Please select one camera with a lens.")
        return

    lens_list = [mmapi.Lens(node=lens_node) for lens_node in lens_nodes]
    frame_range = time_utils.get_maya_timeline_range_outer()
    data_list = [lib.generate(cam, lens, frame_range) for lens in lens_list]

    # Ask user for file name to write out.
    basic_filter = "*.nk"
    file_path = maya.cmds.fileDialog2(
        caption='Output .nk file',
        okCaption='Save',
        fileMode=0,  # 0="Any file, whether it exists or not."
        fileFilter=basic_filter,
        returnFilter=False,
        dialogStyle=2,
    )
    if not file_path:
        LOG.info('User cancelled.')
        return

    file_path = file_path[0]
    result = lib.write_nuke_file(file_path, data_list)
    if result:
        LOG.info('Successfully written file: %r', file_path)
    else:
        LOG.warn('Failed to write file: %r', file_path)
    return
