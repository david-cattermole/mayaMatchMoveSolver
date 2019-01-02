# -*- mode: python-mode; python-indent-offset: 4 -*-
#
# 3DE4.script.name:     Export 2D Tracks (MM Solver)...
#
# 3DE4.script.version:  v1.3
#
# 3DE4.script.gui:      Main Window::3DE4::File::Export
# 3DE4.script.gui:      Object Browser::Context Menu Point
# 3DE4.script.gui:      Object Browser::Context Menu Points
# 3DE4.script.gui:      Object Browser::Context Menu PGroup
#
# 3DE4.script.comment:  Writes 2D tracking curves (including
# 3DE4.script.comment:  frame-by-frame weights) of all selected points
# 3DE4.script.comment:  to a UV Tracks file.
# 3DE4.script.comment:  All 2D Tracks are resolution independent.
#
#

import json
import tde4


TITLE = 'Export 2D Tracks to MM Solver...'
EXT = '.uv'


# UV Track format
# This is copied from 'mmSolver.tools.loadmarker.constant module',
UV_TRACK_FORMAT_VERSION_UNKNOWN = -1
UV_TRACK_FORMAT_VERSION_1 = 1
UV_TRACK_FORMAT_VERSION_2 = 2
UV_TRACK_HEADER_VERSION_2 = {
    'version': UV_TRACK_FORMAT_VERSION_2,
}

# Preferred UV Track format version (changes the format
# version used for writing data).
UV_TRACK_FORMAT_VERSION_PREFERRED = UV_TRACK_FORMAT_VERSION_2

# Do we have support for new features of 3DE tde4 module?
SUPPORT_PERSISTENT_ID = 'getPointPersistentID' in dir(tde4)
SUPPORT_CAMERA_FRAME_OFFSET = 'getCameraFrameOffset' in dir(tde4)
SUPPORT_POINT_WEIGHT_BY_FRAME = 'getPointWeightByFrame' in dir(tde4)
SUPPORT_CLIPBOARD = 'setClipboardString' in dir(tde4)


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
    if SUPPORT_CAMERA_FRAME_OFFSET is True:
        start_frame = tde4.getCameraFrameOffset(camera)
    pattern = '*' + EXT
    # Undistortion default is 'On'.
    undistort = 1

    # GUI
    req = tde4.createCustomRequester()
    tde4.addFileWidget(req, 'file_browser_widget', 'Filename...', pattern)
    tde4.addTextFieldWidget(req, 'start_frame_widget', 'Start Frame', str(start_frame))
    tde4.addToggleWidget(req, 'undistort_widget', 'Apply Undistortion', undistort)
    ret = tde4.postCustomRequester(req, TITLE, 500, 0, 'Ok', 'Cancel')
    if ret == 1:
        # Query GUI Widgets
        path = tde4.getWidgetValue(req, 'file_browser_widget')
        start_frame = tde4.getWidgetValue(req, 'start_frame_widget')
        start_frame = int(start_frame)
        undistort = tde4.getWidgetValue(req, 'undistort_widget')
        undistort = bool(undistort)

        # Generate file contents
        data_str = generate(
            point_group, camera, points,
            start_frame=start_frame,
            undistort=undistort
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


def generate(point_group, camera, points, fmt=None, **kwargs):
    """
    Return a str, ready to be written to a text file.

    :param point_group: The 3DE Point Group containing 'points'
    :type point_group: str

    :param camera: The 3DE Camera containing 2D 'points' data.
    :type camera: str

    :param points: The list of 3DE Points representing 2D data to
                   save.
    :type points: list of str

    :param fmt: The format to generate, either
                UV_TRACK_FORMAT_VERSION_1 or UV_TRACK_FORMAT_VERSION_2.
    :type fmt: None or UV_TRACK_FORMAT_VERSION_*

    Supported 'kwargs':
    - undistort (True or False) - Should points be undistorted?
    - start_frame - (int) - Frame '1' 3DE should be mapped to this value.
    """
    if fmt is None:
        fmt = UV_TRACK_FORMAT_VERSION_PREFERRED
    data = ''
    if fmt == UV_TRACK_FORMAT_VERSION_1:
        data = _generate_v1(point_group, camera, points, **kwargs)
    elif fmt == UV_TRACK_FORMAT_VERSION_2:
        data = _generate_v2(point_group, camera, points, **kwargs)
    return data


def _generate_v1(point_group, camera, points, start_frame=None, undistort=False):
    """
    Generate the UV file format contents, using a basic ASCII format.

    :param point_group: The 3DE Point Group containing 'points'
    :type point_group: str

    :param camera: The 3DE Camera containing 2D 'points' data.
    :type camera: str

    :param points: The list of 3DE Points representing 2D data to
                   save.
    :type points: list of str

    :param start_frame: The frame number to be considered at
                       'first frame'. Defaults to 1001 if
                       set to None.
    :type start_frame: None or int

    :param undistort: Should we apply undistortion to the 2D points
                      data? Yes or no.
    :type undistort: bool

    Each point will store:
    - Point name
    - X, Y position (in UV coordinates, per-frame)
    - Point weight (per-frame)
    """
    assert isinstance(point_group, basestring)
    assert isinstance(camera, basestring)
    assert isinstance(points, (list, tuple))
    assert start_frame is None or isinstance(start_frame, int)
    assert isinstance(undistort, bool)
    if start_frame is None:
        start_frame = 1001
    data_str = ''
    cam_num_frames = tde4.getCameraNoFrames(camera)

    if len(points) == 0:
        return data_str

    frame0 = int(start_frame)
    frame0 -= 1

    data_str += '{0:d}\n'.format(len(points))

    for point in points:
        name = tde4.getPointName(point_group, point)
        c2d = tde4.getPointPosition2DBlock(
            point_group, point, camera,
            1, cam_num_frames
        )

        # Write per-frame position data
        num_valid_frame = 0
        pos_list = []
        weight_list = []
        frame = 1  # 3DE starts at frame '1' regardless of the 'start-frame'.
        for v in c2d:
            if v[0] == -1.0 or v[1] == -1.0:
                # No valid data here.
                frame += 1
                continue
            num_valid_frame += 1  # number of points with valid positions

            f = frame + frame0
            if undistort is True:
                v = tde4.removeDistortion2D(camera, frame,  v)
            weight = 1.0
            if SUPPORT_POINT_WEIGHT_BY_FRAME is True:
                weight = tde4.getPointWeightByFrame(
                    point_group,
                    point,
                    camera,
                    frame
                )

            pos_list.append((f, v))
            weight_list.append((f, weight))
            frame += 1

        # add data
        data_str += name + '\n'
        data_str += '{0:d}\n'.format(num_valid_frame)
        for pos_data, weight_data in zip(pos_list, weight_list):
            f = pos_data[0]
            v = pos_data[1]
            w = weight_data[1]
            assert f == weight_data[0]
            data_str += '%d %.15f %.15f %.8f\n' % (f, v[0], v[1], w)

    return data_str


def _generate_v2(point_group, camera, points, start_frame=None, undistort=False):
    """
    Generate the UV file format contents, using JSON format.

    :param point_group: The 3DE Point Group containing 'points'
    :type point_group: str

    :param camera: The 3DE Camera containing 2D 'points' data.
    :type camera: str

    :param points: The list of 3DE Points representing 2D data to
                   save.
    :type points: list of str

    :param start_frame: The frame number to be considered at
                       'first frame'. Defaults to 1001 if
                       set to None.
    :type start_frame: None or int

    :param undistort: Should we apply undistortion to the 2D points
                      data? Yes or no.
    :type undistort: bool

    Each point will store:
    - Point name
    - X, Y position (in UV coordinates, per-frame)
    - Point weight (per-frame)
    - Point Set name
    - Point 'Persistent ID'
    """
    assert isinstance(point_group, basestring)
    assert isinstance(camera, basestring)
    assert isinstance(points, (list, tuple))
    assert start_frame is None or isinstance(start_frame, int)
    assert isinstance(undistort, bool)
    if start_frame is None:
        start_frame = 1001
    data = UV_TRACK_HEADER_VERSION_2.copy()
    cam_num_frames = tde4.getCameraNoFrames(camera)

    if len(points) == 0:
        return ''

    frame0 = int(start_frame)
    frame0 -= 1

    data['num_points'] = len(points)
    data['is_undistorted'] = bool(undistort)

    data['points'] = []
    for point in points:
        point_data = {}

        # Query point information
        name = tde4.getPointName(point_group, point)
        uid = None
        if SUPPORT_PERSISTENT_ID is True:
            uid = tde4.getPointPersistentID(point_group, point)
        point_set = tde4.getPointSet(point_group, point)
        point_set_name = None
        if point_set is not None:
            point_set_name = tde4.getSetName(point_group, point_set)
        point_data['name'] = name
        point_data['id'] = uid
        point_data['set_name'] = point_set_name

        # Write per-frame position data
        frame = 1  # 3DE starts at frame '1' regardless of the 'start frame'.
        point_data['per_frame'] = []
        pos_block = tde4.getPointPosition2DBlock(
            point_group, point, camera,
            1, cam_num_frames
        )
        for pos in pos_block:
            if pos[0] == -1.0 or pos[1] == -1.0:
                # No valid data here.
                frame += 1
                continue

            f = frame + frame0
            if undistort is True:
                pos = tde4.removeDistortion2D(camera, frame,  pos)
            weight = 1.0
            if SUPPORT_POINT_WEIGHT_BY_FRAME is True:
                weight = tde4.getPointWeightByFrame(
                    point_group,
                    point,
                    camera,
                    frame
                )
            frame_data = {
                'frame': f,
                'pos': pos,
                'weight': weight
            }
            point_data['per_frame'].append(frame_data)
            frame += 1

        data['points'].append(point_data)

    data_str = json.dumps(data)
    return data_str


if __name__ == '__main__':
    main()
