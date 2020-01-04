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

import json
import tde4


TITLE = 'Export 2D Tracks to MM Solver...'
EXT = '.uv'

# UV Track format
# This is copied from 'mmSolver.tools.loadmarker.constant module',
UV_TRACK_FORMAT_VERSION_UNKNOWN = -1
UV_TRACK_FORMAT_VERSION_1 = 1
UV_TRACK_FORMAT_VERSION_2 = 2
UV_TRACK_FORMAT_VERSION_3 = 3

UV_TRACK_HEADER_VERSION_2 = {
    'version': UV_TRACK_FORMAT_VERSION_2,
}

UV_TRACK_HEADER_VERSION_3 = {
    'version': UV_TRACK_FORMAT_VERSION_3,
}

# Preferred UV Track format version (changes the format
# version used for writing data).
UV_TRACK_FORMAT_VERSION_PREFERRED = UV_TRACK_FORMAT_VERSION_3

# Do we have support for new features of 3DE tde4 module?
SUPPORT_PERSISTENT_ID = 'getPointPersistentID' in dir(tde4)
SUPPORT_CAMERA_FRAME_OFFSET = 'getCameraFrameOffset' in dir(tde4)
SUPPORT_POINT_WEIGHT_BY_FRAME = 'getPointWeightByFrame' in dir(tde4)
SUPPORT_CLIPBOARD = 'setClipboardString' in dir(tde4)
SUPPORT_POINT_VALID_MODE = 'getPointValidMode' in dir(tde4)
SUPPORT_POINT_SURVEY_XYZ_ENABLED = 'getPointSurveyXYZEnabledFlags' in dir(tde4)


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
        data_str = generate(
            point_group, camera, points,
            start_frame=start_frame,
            fmt=UV_TRACK_FORMAT_VERSION_3,
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


def _get_point_valid_mode(point_group, point):
    """
    Is the point valid in various positions?

    This function has backwards compatibility built-in, so older
    versions of 3DE can use it reliably and get consistent results.

    :param point_group: The 3DE Point Group containing 'point'
    :type point_group: str

    :param point: 3DE Point to check.
    :type point: str

    :returns: A 'point_valid_mode', 1 of 3 strings;
              'POINT_VALID_INSIDE_FOV',
              'POINT_VALID_INSIDE_FRAME', or
              'POINT_VALID_ALWAYS'.
    :rtype: str
    """
    valid_mode = 'POINT_VALID_INSIDE_FRAME'
    if SUPPORT_POINT_VALID_MODE is True:
        valid_mode = tde4.getPointValidMode(point_group, point)
    else:
        valid_outside = tde4.getPointValidOutsideFOVFlag(point_group, point)
        if valid_outside == 1:
            valid_mode = 'POINT_VALID_ALWAYS'
    return valid_mode


def _is_valid_position(pos_2d, camera_fov, valid_mode):
    """
    Is the 2D position is valid for the point 'valid_mode' and camera FOV?

    :param pos_2d: 2D point position to check.
    :type pos_2d: [float, float]

    :param camera_fov: The Camera FOV as given by 'tde4.getCameraFOV' command.
    :type camera_fov: [float, float, float, float]

    :param valid_mode: The point valid mode, as given by
                       'tde4.getPointValidMode' command.
    :type valid_mode: str

    :returns: If the 2D position given is valid, based on the 'valid_mode'.
    :rtype: bool
    """
    value = True
    if valid_mode == 'POINT_VALID_ALWAYS':
        pass
    elif valid_mode == 'POINT_VALID_INSIDE_FRAME':
        if ((pos_2d[0] < 0.0)
            or (pos_2d[0] > 1.0)
            or (pos_2d[1] < 0.0)
            or (pos_2d[1] > 1.0)):
            value = False
    elif valid_mode == 'POINT_VALID_INSIDE_FOV':
        left, right, bottom, top = camera_fov
        if ((pos_2d[0] < left)
            or (pos_2d[0] > right)
            or (pos_2d[1] < bottom)
            or (pos_2d[1] > top)):
            value = False
    return value


def _get_point_weight(point_group, point, camera, frame):
    """
    Get the 2D point weight.

    This function has backwards compatibility built-in, so older
    versions of 3DE can use it reliably and get consistent results.

    :param point_group: The 3DE Point Group containing 'point'
    :type point_group: str

    :param point: 3DE Point to query.
    :type point: str

    :param camera: The 3DE Camera containing the 3DE 'point'.
    :type camera: str

    :param frame: 3DE Frame number (1-based) to get weight from.
    :type frame: float

    :returns: A floating-point weight value.
    :rtype: float
    """
    weight = 1.0
    if SUPPORT_POINT_WEIGHT_BY_FRAME is True:
        weight = tde4.getPointWeightByFrame(
            point_group,
            point,
            camera,
            frame
        )
    return weight


def _get_3d_data_from_point(point_group, point):
    """
    Get 3D data structure from 3DE point.

    :param point_group: 3DE point group id.
    :type point_group: str

    :param point: 3DE point id.
    :type point: str

    :returns: Dictionary of the point 3d.
    :rtype: dict
    """
    has_pos = tde4.isPointCalculated3D(point_group, point)
    pos_3d = (None, None, None)
    if has_pos:
        pos_3d = tde4.getPointCalcPosition3D(point_group, point)

    x_lock = False
    y_lock = False
    z_lock = False
    survey_mode = tde4.getPointSurveyMode(point_group, point)
    if survey_mode not in ['SURVEY_FREE']:
        x_lock = True
        y_lock = True
        z_lock = True
        if SUPPORT_POINT_SURVEY_XYZ_ENABLED is True:
            xyz_lock = tde4.getPointSurveyXYZEnabledFlags(point_group, point)
            x_lock, y_lock, z_lock = xyz_lock

    point_3d_data = {
        'x': pos_3d[0],
        'y': pos_3d[1],
        'z': pos_3d[2],
        'x_lock': bool(x_lock),
        'y_lock': bool(y_lock),
        'z_lock': bool(z_lock),
    }
    return point_3d_data


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
                UV_TRACK_FORMAT_VERSION_1, UV_TRACK_FORMAT_VERSION_2
                or UV_TRACK_FORMAT_VERSION_3.
    :type fmt: None or UV_TRACK_FORMAT_VERSION_*

    Supported 'kwargs':
    - undistort (True or False) - Should points be undistorted?
                                  (Format v1 and v2)
    - start_frame - (int) - Frame '1' 3DE should be mapped to this value.
                    (Format v1, v2 and v3)
    """
    if fmt is None:
        fmt = UV_TRACK_FORMAT_VERSION_PREFERRED
    data = ''
    if fmt == UV_TRACK_FORMAT_VERSION_1:
        data = _generate_v1(point_group, camera, points, **kwargs)
    elif fmt == UV_TRACK_FORMAT_VERSION_2:
        data = _generate_v2(point_group, camera, points, **kwargs)
    elif fmt == UV_TRACK_FORMAT_VERSION_3:
        data = _generate_v3(point_group, camera, points, **kwargs)
    return data


def _generate_v1(point_group, camera, points, start_frame=None, undistort=False):
    """
    Generate the UV file format contents, using a basic ASCII format.

    Each point will store:
    - Point name
    - X, Y position (in UV coordinates, per-frame)
    - Point weight (per-frame)

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

    :returns: A ASCII format string, with the UV Track data in it.
    :rtype: str
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
    camera_fov = tde4.getCameraFOV(camera)

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
        valid_mode = _get_point_valid_mode(point_group, point)

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

            # Does the 2D point go outside the camera FOV? Is that ok?
            valid = tde4.isPointPos2DValid(
                point_group,
                point,
                camera,
                frame
            )
            if valid == 0:
                # No valid data here.
                frame += 1
                continue

            # Check if we're inside the FOV / Frame or not.
            valid_pos = _is_valid_position(v, camera_fov, valid_mode)
            if valid_pos is False:
                frame += 1
                continue

            # Number of points with valid positions
            num_valid_frame += 1

            f = frame + frame0
            if undistort is True:
                v = tde4.removeDistortion2D(camera, frame,  v)
            weight = _get_point_weight(point_group, point, camera, frame)

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


def _generate_v2_and_v3(point_group, camera, points,
                        version=None,
                        **kwargs):
    """
    Generate the UV file format contents, using JSON format.

    Set the individual _generate_v2 or _generate_v3 functions for
    details of what is stored.

    :param point_group: The 3DE Point Group containing 'points'
    :type point_group: str

    :param camera: The 3DE Camera containing 2D 'points' data.
    :type camera: str

    :param points: The list of 3DE Points representing 2D data to
                   save.
    :type points: list of str

    :param version: The version of file to generate,
                    UV_TRACK_FORMAT_VERSION_2 or
                    UV_TRACK_FORMAT_VERSION_3.
    :type version: int

    :param start_frame: Format v2 and v3; The frame number to be
                        considered at 'first frame'.
                        Defaults to 1001 if set to None.
    :type start_frame: None or int

    :param undistort: Format v2; Should we apply undistortion to the 2D
                      points data? Yes or no.
    :type undistort: bool

    :returns: A JSON format string, with the UV Track data in it.
    :rtype: str
    """
    assert isinstance(point_group, basestring)
    assert isinstance(camera, basestring)
    assert isinstance(points, (list, tuple))
    assert isinstance(version, (int, long))
    assert version in [UV_TRACK_FORMAT_VERSION_2,
                       UV_TRACK_FORMAT_VERSION_3]

    start_frame = kwargs.get('start_frame')
    assert start_frame is None or isinstance(start_frame, int)
    if start_frame is None:
        start_frame = 1001

    undistort = None
    if version == UV_TRACK_FORMAT_VERSION_2:
        undistort = kwargs.get('undistort')
        assert isinstance(undistort, bool)

    data = None
    if version == UV_TRACK_FORMAT_VERSION_2:
        data = UV_TRACK_HEADER_VERSION_2.copy()
    else:
        data = UV_TRACK_HEADER_VERSION_3.copy()
    cam_num_frames = tde4.getCameraNoFrames(camera)
    camera_fov = tde4.getCameraFOV(camera)

    if len(points) == 0:
        return ''

    frame0 = int(start_frame)
    frame0 -= 1

    data['num_points'] = len(points)
    data['is_undistorted'] = None
    if version == UV_TRACK_FORMAT_VERSION_2:
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
        valid_mode = _get_point_valid_mode(point_group, point)

        # Get the 3D point position
        if version == UV_TRACK_FORMAT_VERSION_3:
            point_data['3d'] = _get_3d_data_from_point(point_group, point)

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

            # Is the 2D point obscured?
            valid = tde4.isPointPos2DValid(
                point_group,
                point,
                camera,
                frame
            )
            if valid == 0:
                # No valid data here.
                frame += 1
                continue

            # Check if we're inside the FOV / Frame or not.
            valid_pos = _is_valid_position(pos, camera_fov, valid_mode)
            if valid_pos is False:
                frame += 1
                continue

            pos_undist = pos
            if undistort is True or undistort is None:
                pos_undist = tde4.removeDistortion2D(camera, frame,  pos)
            weight = _get_point_weight(point_group, point, camera, frame)

            f = frame + frame0
            frame_data = {
                'frame': f,
                'pos': pos_undist,
                'weight': weight
            }
            if version == UV_TRACK_FORMAT_VERSION_3:
                frame_data['pos_dist'] = pos
            point_data['per_frame'].append(frame_data)
            frame += 1

        data['points'].append(point_data)

    data_str = json.dumps(data)
    return data_str


def _generate_v2(point_group, camera, points,
                 start_frame=None,
                 undistort=False):
    """
    Generate the UV file format contents, using JSON format.

    Each point will store:
    - Point name
    - X, Y position (in UV coordinates, per-frame)
    - Point weight (per-frame)
    - Point Set name
    - Point 'Persistent ID'

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

    :returns: A JSON format string, with the UV Track data in it.
    :rtype: str
    """
    return _generate_v2_and_v3(
        point_group,
        camera,
        points,
        version=UV_TRACK_FORMAT_VERSION_2,
        start_frame=start_frame,
        undistort=undistort
    )


def _generate_v3(point_group, camera, points,
                 start_frame=None):
    """
    Generate the UV file format contents, using JSON format.

    Each point will store:
    - Point name
    - X, Y position (in UV coordinates, per-frame) as distorted and
      undistorted
    - Point weight (per-frame)
    - Point Set name
    - Point 'Persistent ID'
    - 3D Point X, Y and Z
    - 3D Point X, Y and Z locked status.

    :param point_group: The 3DE Point Group containing 'points'
    :type point_group: str

    :param camera: The 3DE Camera containing 2D 'points' data.
    :type camera: str

    :param points: The list of 3DE Points representing 2D data to
                   save.
    :type points: list of str

    :param start_frame: The frame number to be considered at
                        'first frame'. Defaults to 1001 if set to None.
    :type start_frame: None or int

    :returns: A JSON format string, with the UV Track data in it.
    :rtype: str
    """
    return _generate_v2_and_v3(
        point_group,
        camera,
        points,
        version=UV_TRACK_FORMAT_VERSION_3,
        start_frame=start_frame
    )


if __name__ == '__main__':
    main()
