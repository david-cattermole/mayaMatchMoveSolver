# Copyright (C) 2019 David Cattermole.
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
The Copy/Paste Camera tool.

This tool will save the a camera and plate to a temporary file, for
loading in third-party software (such as 3DEqualizer).

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

import mmSolver.tools.copypastecamera.constant as const
import mmSolver.tools.copypastecamera.lib as lib


LOG = mmSolver.logger.get_logger()


def main():
    # Get selected camera node.
    sel = maya.cmds.ls(selection=True, long=True, type='transform') or []
    if len(sel) == 0:
        sel += maya.cmds.ls(selection=True, long=True, type='camera') or []
    if len(sel) != 1:
        LOG.warn('Please select one camera: selection=%r', sel)
        return
    cam_tfm, cam_shp = camera_utils.get_camera(sel[0])
    if cam_tfm is None or cam_shp is None:
        LOG.warn('Selected node is not a camera, please select one camera.')
        return

    # Get the connected image planes
    # If more than one image plane exists, print a warning.
    img_pl_shps = camera_utils.get_image_plane_shapes_from_camera(cam_tfm, cam_shp)
    img_pl_shp = None
    if len(img_pl_shps) == 0:
        msg = 'No image plane nodes found.'
        LOG.warn(msg)
    elif len(img_pl_shps) > 1:
        img_pl_shp = img_pl_shps[0]
        msg = 'More than one image plane was found, using first image plane.'
        LOG.warn(msg)
    else:
        # Exactly one image plane node.
        img_pl_shp = img_pl_shps[0]

    # Query plate data from the image plane
    test_disk = const.TEST_DISK
    frame_range = time_utils.get_maya_timeline_range_inner()
    plate_data = {}
    if img_pl_shp is not None:
        plate_data = lib.query_plate_data(cam_tfm, cam_shp, img_pl_shp, test_disk)
        # Calculate the frame range.
        image_file_path = plate_data.get('file_path')
        if image_file_path is not None:
            frame_range = lib.get_frame_range_from_file_pattern(
                image_file_path, fallback_range=frame_range
            )
    assert isinstance(frame_range, (time_utils.FrameRange, tuple))
    frames = list(range(frame_range.start, frame_range.end + 1))
    assert len(frames) > 0

    # Node must be transform and have a camera shape node to be valid.
    rotate_order = const.ROTATE_ORDER

    with tools_utils.tool_context(
        use_undo_chunk=False, use_dg_evaluation_mode=True, disable_viewport=True
    ):
        cam_data = lib.query_camera_data(
            cam_tfm, cam_shp, frames, rotate_order, test_disk
        )

    # Generate file contents.
    data_str = lib.generate(cam_data, plate_data, frame_range)

    # Write out file.
    file_path = lib.write_temp_file(data_str)
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
