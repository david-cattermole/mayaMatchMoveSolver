"""
The .uv format has two versions; v1 ASCII format and v2 JSON format.

The v1 ASCII format is derived from the 3DEqualizer 2D Points exporter.

The UV coordinate (0.0, 0.0) is the lower-left.
The UV coordinate (1.0, 1.0) is the upper-right.

The ASCII file format looks like this::

    int     # Number of track points in the file
    string  # Name of point
    int     # Number of frames
    int float float float  # Frame, U coord, V coord, Point Weight

Simple ASCII v1 file with 1 2D track and 1 frame of data::

    1
    My Point Name
    1
    1 0.0 1.0 1.0

The JSON format takes the shape of a dictionary.
The dictionary looks like this::

    {
        'version': int,
        'num_points': int,
        'is_undistorted': bool,
        'points': {
            'name': str,
            'id': int,
            'set_name': str,
            'per_frame': [
                {
                    'frame': int,
                    'pos': (float, float),
                    'weight': float
                },
            ],
        },
    }

"""

import json
import mmSolver.tools.loadmarker.interface as interface
import mmSolver.tools.loadmarker.formatmanager as fmtmgr
import mmSolver.tools.loadmarker.constant as const


def determine_format_version(file_path):
    f = open(file_path)
    try:
        data = json.load(f)
    except ValueError:
        data = {}
    f.close()
    if len(data) == 0:
        return const.UV_TRACK_FORMAT_VERSION_1
    version = data.get('version', const.UV_TRACK_FORMAT_VERSION_UNKNOWN)
    return version


def parse_v1(file_path):
    """
    Parse the UV file format or 3DEqualizer .txt format.

    :param file_path:
    :return:
    """
    f = open(file_path, 'r')
    lines = f.readlines()
    f.close()
    if len(lines) == 0:
        raise OSError('No contents in the file: %s' % file_path)
    mkr_data_list = []

    num_points = int(lines[0])
    if num_points < 1:
        raise interface.ParserException('No points exist.')

    idx = 1  # Skip the first line
    for i in xrange(num_points):
        mkr_name = lines[idx]
        mkr_name = mkr_name.strip()

        # Create marker
        mkr_data = interface.MarkerData()
        mkr_data.set_name(mkr_name)

        idx += 1
        num_frames = int(lines[idx])
        if num_frames <= 0:
            msg = 'point has no data: %r'
            print(msg % mkr_name)
            continue

        # Frame data parsing
        frames = []
        j = num_frames
        while j > 0:
            idx += 1
            line = lines[idx]
            if len(line) == 0:
                # Have we reached the end of the file?
                break
            j = j - 1
            split = line.split()
            if len(split) != 4:
                # We should not get here
                msg = 'File invalid, there must be 4 numbers in line: %r'
                raise interface.ParserError(msg % line)
            frame = int(split[0])
            mkr_u = float(split[1])
            mkr_v = float(split[2])
            mkr_weight = 1.0
            mkr_weight = float(split[3])

            mkr_data.weight.set_value(frame, mkr_weight)
            mkr_data.x.set_value(frame, mkr_u)
            mkr_data.y.set_value(frame, mkr_v)
            frames.append(frame)

        # Fill in occluded point frames
        all_frames = list(range(min(frames), max(frames)+1))
        for frame in all_frames:
            mkr_enable = int(frame in frames)
            mkr_data.enable.set_value(frame, mkr_enable)
            if mkr_enable is False:
                mkr_data.weight.set_value(frame, 0.0)

        mkr_data_list.append(mkr_data)
        idx += 1

    return mkr_data_list


def parse_v2(file_path):
    """
    Parse the UV file format, using JSON.

    :param file_path:
    :return:
    """
    mkr_data_list = []
    f = open(file_path)
    data = json.load(f)
    f.close()

    points = data.get('points', [])
    for point_data in points:
        mkr_data = interface.MarkerData()

        # Static point information.
        name = point_data.get('name')
        set_name = point_data.get('set_name')
        id = point_data.get('id')
        assert isinstance(name, basestring)
        assert isinstance(set_name, basestring)
        assert isinstance(id, int)
        mkr_data.set_name(name)
        mkr_data.set_group_name(set_name)
        mkr_data.set_id(name)

        # Create marker
        frames = []
        per_frame = point_data.get('per_frame', [])
        for frame_data in per_frame:
            frame_num = frame_data.get('frame')
            assert frame_num is not None
            frames.append(frame_num)

            pos = frame_data.get('pos')
            assert pos is not None
            mkr_u, mkr_v = pos

            mkr_weight = frame_data.get('weight')

            # Set Marker Data
            mkr_data.x.set_value(frame_num, mkr_u)
            mkr_data.y.set_value(frame_num, mkr_v)
            mkr_data.weight.set_value(frame_num, mkr_weight)
            mkr_data.enable.set_value(frame_num, True)

        # Fill in occluded point frames
        all_frames = list(range(min(frames), max(frames)+1))
        for frame in all_frames:
            mkr_enable = int(frame in frames)
            mkr_data.enable.set_value(frame, mkr_enable)
            if mkr_enable is False:
                mkr_data.weight.set_value(frame, 0.0)

        mkr_data_list.append(mkr_data)
    return mkr_data_list


class LoaderUVTrack(interface.LoaderBase):

    name = 'UV Track Points (.uv)'
    file_exts = ['.uv']
    args = []

    def parse(self, file_path, **kwargs):
        """
        Decodes a file path into a list of MarkerData.

        kwargs is not used.

        :param file_path: The file path to parse.
        :type file_path: str

        :param kwargs: There are no custom keyword arguments used.

        :return: List of MarkerData
        """
        version = determine_format_version(file_path)
        if version == const.UV_TRACK_FORMAT_VERSION_1:
            mkr_data_list = parse_v1(file_path)
        elif version == const.UV_TRACK_FORMAT_VERSION_2:
            mkr_data_list = parse_v2(file_path)
        else:
            msg = 'Could not determine format version for UV Track file.'
            raise interface.ParserError(msg)
        return mkr_data_list


# Register the File Format
mgr = fmtmgr.get_format_manager()
mgr.register_format(LoaderUVTrack)
