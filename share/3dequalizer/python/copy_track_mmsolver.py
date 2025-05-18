# -*- mode: python-mode; python-indent-offset: 4 -*-
#
# Copyright (C) 2018, 2019, 2020, 2021, 2025 David Cattermole.
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
# ----------------------------------------------------------------------
#
# 3DE4.script.name:     Copy 2D Tracks (MM Solver)
#
# 3DE4.script.version:  v1.12
#
# 3DE4.script.gui:      Object Browser::Context Menu Point
# 3DE4.script.gui:      Object Browser::Context Menu Points
# 3DE4.script.gui:      Object Browser::Context Menu PGroup
#
# 3DE4.script.comment:  Copies the selected 2D track points to a temporary
# 3DE4.script.comment:  file and puts the file path on the Operating
# 3DE4.script.comment:  System's clipboard.
# 3DE4.script.comment:
# 3DE4.script.comment:  The 2D Tracks are stored distorted and undistorted.
# 3DE4.script.comment:
# 3DE4.script.comment:  Rolling Shutter (RS) is supported and exported
# 3DE4.script.comment:  as undistortion. In 3DE4 r6 the content distance
# 3DE4.script.comment:  comes from the Camera's Content Distance
# 3DE4.script.comment:  parameter. In 3DE4 r5 and below the Content
# 3DE4.script.comment:  Distance defaults to 100.0 cm unless overridden
# 3DE4.script.comment:  by adding "RS Content Distance = 100.0" or
# 3DE4.script.comment:  into the Attribute Editor "Project Notes".
# 3DE4.script.comment:
# 3DE4.script.comment:  To use the file with MM Solver in Maya, open the
# 3DE4.script.comment:  Load Markers UI in Maya, the UI will
# 3DE4.script.comment:  automatically read the Operating System's
# 3DE4.script.comment:  clipboard and add it into the file path field.
# 3DE4.script.comment:
# 3DE4.script.comment:  All 2D Tracks are resolution independent.
# 3DE4.script.comment:
# 3DE4.script.comment:  Files created with this tool will only work with
# 3DE4.script.comment:  MM Solver v0.3.1+.
#

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tempfile
import time

import tde4

import uvtrack_format  # GENERATE_FILTER_LINE
# INCLUDE_FILE uvtrack_format.py


TITLE = 'Copy 2D Tracks to MM Solver...'
EXT = '.uv'


def main():
    point_group = tde4.getCurrentPGroup()
    if point_group is None:
        msg = 'Please activate a Point Group.'
        tde4.postQuestionRequester(TITLE, msg, 'Ok')
        return

    camera = tde4.getCurrentCamera()
    if camera is None:
        msg = 'Please activate a Camera.'
        tde4.postQuestionRequester(TITLE, msg, 'Ok')
        return

    # check if context menu has been used, and retrieve point...
    point = tde4.getContextMenuObject()
    if point is not None:
        # retrieve point's parent pgroup (not necessarily being the current
        # one!)...
        point_group = tde4.getContextMenuParentObject()
        if point_group is None:
            msg = 'Please select some points.'
            tde4.postQuestionRequester(TITLE, msg, 'Ok')
            return
        points = tde4.getPointList(point_group, 1)
    else:
        # otherwise use regular selection...
        points = tde4.getPointList(point_group, 1)
    if len(points) == 0:
        msg = 'Please select some points.'
        tde4.postQuestionRequester(TITLE, msg, 'Ok')
        return

    start, end, step = tde4.getCameraSequenceAttr(camera)
    start_frame = start

    rs_enabled = False
    rs_distance = None
    # Backwards compatibility with 3DE4 Release 1.
    if uvtrack_format.SUPPORT_RS_ENABLED is True:
        rs_enabled = bool(tde4.getCameraRollingShutterEnabledFlag(camera))
    if rs_enabled is True:
        rs_distance = uvtrack_format.get_rs_distance(camera)
        if (
            uvtrack_format.SUPPORT_PROJECT_NOTES is True
            and uvtrack_format.SUPPORT_RS_DISTANCE is False
        ):
            uvtrack_format.set_rs_distance_into_project_notes(rs_distance)

    # Generate file contents
    data_str = uvtrack_format.generate(
        point_group,
        camera,
        points,
        start_frame=start_frame,
        rs_distance=rs_distance,
        fmt=uvtrack_format.UV_TRACK_FORMAT_VERSION_PREFERRED,
    )

    # Write file.
    file_ext = EXT
    # Prefix with the current time 'YYYY-MM-DD_HH_MM', for example
    # '2020-12-04_14_26'.
    now_str = time.strftime('%Y-%m-%d_%H_%M')
    prefix = 'tmp_{0}_'.format(now_str)
    with tempfile.NamedTemporaryFile(
        mode='w', prefix=prefix, suffix=file_ext, delete=False
    ) as f:
        if f.closed:
            msg = "Error: Couldn't open file.\n"
            msg += repr(f.name)
            tde4.postQuestionRequester(TITLE, msg, 'Ok')
            return
        f.write(data_str)

    # Override the user's clipboard with the temporary file path.
    if uvtrack_format.SUPPORT_CLIPBOARD is True:
        tde4.setClipboardString(f.name)
    else:
        # Cannot set the clipboard, so we'll print to the Python Console
        # and the user can copy it. Pretty bad workaround.
        print(f.name)
    return


if __name__ == '__main__':
    main()
