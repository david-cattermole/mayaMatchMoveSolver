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
# 3DE4.script.name:     Export 2D Tracks (MM Solver)...
#
# 3DE4.script.version:  v1.12
#
# 3DE4.script.gui:      Main Window::3DE4::File::Export
# 3DE4.script.gui:      Object Browser::Context Menu Point
# 3DE4.script.gui:      Object Browser::Context Menu Points
# 3DE4.script.gui:      Object Browser::Context Menu PGroup
#
# 3DE4.script.comment:  Writes 2D tracking curves (including
# 3DE4.script.comment:  frame-by-frame weights) of all selected points
# 3DE4.script.comment:  to a UV Tracks file.
# 3DE4.script.comment:
# 3DE4.script.comment:  To use the file with MM Solver in Maya, open the
# 3DE4.script.comment:  Load Markers UI in Maya to load the .uv file.
# 3DE4.script.comment:
# 3DE4.script.comment:  All 2D Tracks are resolution independent.
# 3DE4.script.comment:
# 3DE4.script.comment:  Files created with this tool will only work with
# 3DE4.script.comment:  MM Solver v0.3.1+.
#
#

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tde4
import uvtrack_format


TITLE = 'Export 2D Tracks to MM Solver...'
EXT = '.uv'


def main():
    camera = tde4.getCurrentCamera()
    point_group = tde4.getCurrentPGroup()
    if camera is None or point_group is None:
        msg = 'There is no current Point Group or Camera.'
        tde4.postQuestionRequester(TITLE, msg, 'Ok')
        return

    # check if context menu has been used, and retrieve point...
    point = tde4.getContextMenuObject()
    if point is not None:
        # retrieve point's parent pgroup (not necessarily being the current
        # one!)...
        point_group = tde4.getContextMenuParentObject()
        points = tde4.getPointList(point_group, 1)
    else:
        # otherwise use regular selection...
        points = tde4.getPointList(point_group, 1)
    if len(points) == 0:
        msg = 'There are no selected points.'
        tde4.postQuestionRequester(TITLE, msg, 'Ok')
        return

    # widget default values
    start, end, step = tde4.getCameraSequenceAttr(camera)
    start_frame = start
    pattern = '*' + EXT

    rs_enabled = False
    rs_distance = None
    # Backwards compatibility with 3DE4 Release 1.
    if uvtrack_format.SUPPORT_RS_ENABLED is True:
        rs_enabled = bool(tde4.getCameraRollingShutterEnabledFlag(camera))

    # GUI
    req = tde4.createCustomRequester()
    tde4.addFileWidget(req, 'file_browser_widget', 'Filename...', pattern)
    tde4.addTextFieldWidget(req, 'start_frame_widget', 'Start Frame', str(start_frame))
    if rs_enabled is True:
        rs_distance = uvtrack_format.get_rs_distance(camera)
        tde4.addTextFieldWidget(
            req,
            'rs_distance_widget',
            'Rolling Shutter Content Distance [cm]',
            str(rs_distance),
        )
    ret = tde4.postCustomRequester(req, TITLE, 900, 0, 'Ok', 'Cancel')
    if ret == 1:
        # Query GUI Widgets
        path = tde4.getWidgetValue(req, 'file_browser_widget')
        start_frame = tde4.getWidgetValue(req, 'start_frame_widget')
        start_frame = int(start_frame)
        if rs_enabled is True:
            rs_distance = tde4.getWidgetValue(req, 'rs_distance_widget')
            rs_distance = float(rs_distance)
            uvtrack_format.set_rs_distance(camera, rs_distance)

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
        if path.find(EXT, len(path) - 3) == -1:
            # Ensure the file path ends with the extension, if not add it.
            path += EXT
        with open(path, 'w') as f:
            if f.closed:
                msg = "Error, couldn't open file.\n"
                msg += repr(path)
                tde4.postQuestionRequester(TITLE, msg, 'Ok')
                return
            f.write(data_str)
    return


if __name__ == '__main__':
    main()
