# -*- mode: python-mode; python-indent-offset: 4 -*-
#
# 3DE4.script.name:     Copy Undistorted 2D Tracks (Maya MM Solver)...
#
# 3DE4.script.version:  v1.2
#
# 3DE4.script.gui:      Object Browser::Context Menu Point
# 3DE4.script.gui:      Object Browser::Context Menu Points
# 3DE4.script.gui:      Object Browser::Context Menu PGroup
#
# 3DE4.script.comment:  Copies the selected 2D track points to a temporary
# 3DE4.script.comment:  file and puts the file path on the Operating
# 3DE4.script.comment:  System's clipboard.
# 3DE4.script.comment:  2D track points are undistorted!
#
#


import tempfile
import tde4
import uvtrack_format


TITLE = 'Copy Undistorted 2D Tracks to Maya MM Solver...'
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

    # Generate file contents
    undistort = 1
    start_frame = 1
    # Backwards compatibility with 3DE4 Release 2.
    if uvtrack_format.SUPPORT_CAMERA_FRAME_OFFSET is True:
        start_frame = tde4.getCameraFrameOffset(camera)
    data_str = uvtrack_format.generate(
        point_group, camera, points,
        start_frame=start_frame,
        undistort=undistort
    )

    # Write file.
    file_ext = EXT
    f = tempfile.NamedTemporaryFile(
        mode='w+b', 
        bufsize=-1, 
        suffix=file_ext, 
        delete=False
    )
    if f.closed:
        msg = "Error: Couldn't open file.\n%r"
        msg = msg % f.name
        tde4.postQuestionRequester(TITLE, msg, 'Ok')
        return
    f.write(data_str)
    f.close()
    
    # Override the user's clipboard with the temporary file path.
    if uvtrack_format.SUPPORT_CLIPBOARD is True:
        tde4.setClipboardString(f.name)
    else:
        # Cannot set the clipboard, so we'll print to the Python Console
        # and the user can copy it. Pretty bad workaround.
        print f.name
    return


if __name__ == '__main__':
    main()
