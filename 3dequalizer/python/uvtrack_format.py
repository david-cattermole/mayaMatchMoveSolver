"""
Generate track data from the given 2D points in 3DEqualizer.

See ./python/mmSolver/tools/loadmarker/formats/uvtrack.py for details
of the '.uv' file format.
"""

import json
import tde4
import mmSolver.tools.loadmarker.constant as const


def generate(point_group, camera, points, fmt=None, **kwargs):
    """
    Return a str, ready to be written to a text file.

    Supported 'kwargs':
    - undistort - True or False - The points should be Undistorted?
    - start_frame - int - Frame '1' 3DE should be mapped to this value.
    """
    if fmt is None:
        fmt = const.UV_TRACK_FORMAT_VERSION_2
    data = ''
    if fmt == const.UV_TRACK_FORMAT_VERSION_1:
        data = _generate_v1(point_group, camera, points, **kwargs)
    elif fmt == const.UV_TRACK_FORMAT_VERSION_2:
        data = _generate_v2(point_group, camera, points, **kwargs)
    return data


def _generate_v1(point_group, camera, points, start_frame=None, undistort=False):
    """
    Generate the UV file format contents, using a basic ASCII format.

    Each point will store:
    - Point name
    - X, Y position (in UV coordinates, per-frame)
    - Point weight (per-frame)
    """
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
            weight = tde4.getPointWeightByFrame(point_group, point, camera, frame)

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


def _generate_v2(point_group, camera, points, start_frame=None, undistort=None):
    """
    Generate the UV file format contents, using JSON format.

    Each point will store:
    - Point name
    - X, Y position (in UV coordinates, per-frame)
    - Point weight (per-frame)
    - Point Set name
    - Point 'Persistent ID'
    """
    if start_frame is None:
        start_frame = 1001
    data = const.UV_TRACK_HEADER_VERSION_2.copy()
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
        uid = tde4.getPointPersistentID(point_group, point)
        point_set = tde4.getPointSet(point_group, point)
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

