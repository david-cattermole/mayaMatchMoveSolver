# -*- mode: python-mode; python-indent-offset: 4 -*-
#
# Copyright (C) 2018, 2019 David Cattermole.
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
# 3DE4.script.version:  v1.6
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
        # retrieve point's parent pgroup (not necessarily being the current one!)...
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
    start_frame = 1
    # Backwards compatibility with 3DE4 Release 2.
    if uvtrack_format.SUPPORT_CAMERA_FRAME_OFFSET is True:
        start_frame = tde4.getCameraFrameOffset(camera)
    pattern = '*' + EXT

    # GUI
    req = tde4.createCustomRequester()
    tde4.addFileWidget(req, 'file_browser_widget', 'Filename...', pattern)
    tde4.addTextFieldWidget(req, 'start_frame_widget', 'Start Frame', str(start_frame))
    ret = tde4.postCustomRequester(req, TITLE, 500, 0, 'Ok', 'Cancel')
    if ret == 1:
        # Query GUI Widgets
        path = tde4.getWidgetValue(req, 'file_browser_widget')
        start_frame = tde4.getWidgetValue(req, 'start_frame_widget')
        start_frame = int(start_frame)

        # Generate file contents
        data_str = uvtrack_format.generate(
            point_group, camera, points,
            start_frame=start_frame,
            fmt=uvtrack_format.UV_TRACK_FORMAT_VERSION_3,
        )

        # Write file.
        if path.find(EXT, len(path)-3) == -1:
            # Ensure the file path ends with the extension, if not add it.
            path += EXT
        f = open(path, 'w')
        if f.closed:
            msg = "Error, couldn't open file.\n"
            msg += repr(path)
            tde4.postQuestionRequester(TITLE, msg, 'Ok')
            return
        f.write(data_str)
        f.close()
    return


if __name__ == '__main__':
    main()
