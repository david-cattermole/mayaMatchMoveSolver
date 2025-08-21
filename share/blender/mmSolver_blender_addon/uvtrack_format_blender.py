# Copyright (C) 2021 David Cattermole.
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
Convert Blender 2D Tracks to uvtrack format.

See the following files in mmSolver for reference:

   python/mmSolver/tools/loadmarker/lib/formats/uvtrack.py
   3dequalizer/python/uvtrack_format.py

Each 2D Tracker point will store:
    - Point name
    - X, Y position (in UV coordinates, per-frame) as distorted and
      undistorted
    - Point weight (per-frame)
    - Point Set name
    - Point 'Persistent ID'
    - 3D Point X, Y and Z
    - 3D Point X, Y and Z locked status.


The UV Track format v4 contains the following data:
- start_frame
- num_points
- is_undistorted = None
- points
  - name (string)
  - id (string)
  - set_name (string)
  - 3d
    - x (float)
    - y (float)
    - z (float)
    - x_lock (bool)
    - y_lock (bool)
    - z_lock (bool)
  - per_frame (list of frame data)
    - frame (int)
    - pos (float, float) - undistorted
    - weight (float)
    - pos_dist (float, float)
- camera
  - resolution = (int, int)
  - film_back_cm = (float, float)
  - lens_center_offset_cm = (float, float)
  - per_frame
    - frame
    - focal_length_cm



"""

import json

# UV Track format
# This is copied from 'mmSolver.tools.loadmarker.constant' module.
UV_TRACK_FORMAT_VERSION_UNKNOWN = -1
UV_TRACK_FORMAT_VERSION_4 = 4

UV_TRACK_HEADER_VERSION_4 = {
    'version': UV_TRACK_FORMAT_VERSION_4,
}

# Preferred UV Track format version (changes the format
# version used for writing data).
UV_TRACK_FORMAT_VERSION_PREFERRED = UV_TRACK_FORMAT_VERSION_4

# File extension.
FILE_EXT = '.uv'


def get_scene_data(context, clip, tracks, frame_range):
    data = UV_TRACK_HEADER_VERSION_4.copy()
    start_frame = frame_range[0]
    data['start_frame'] = start_frame
    data['num_points'] = len(tracks)
    # This is deprecated in version 4 of the format. We leave it
    # as None, and it will be ignored.
    data['is_undistorted'] = None
    return data


def get_camera_data(context, clip, cam, frame_range):
    """
    - camera
      - resolution = (int, int)
      - film_back_cm = (float, float)
      - lens_center_offset_cm = (float, float)
      - per_frame
        - frame
        - focal_length_cm

    """
    res_width = clip.size[0]
    res_height = clip.size[1]

    pixel_aspect = cam.pixel_aspect
    res_width_real = res_width * pixel_aspect
    res_height_real = res_height
    aspect = res_width_real / res_height_real

    film_back_width = cam.sensor_width * cam.pixel_aspect
    film_back_height = film_back_width / aspect
    # Convert to centimeters.
    film_back_width *= 0.1
    film_back_height *= 0.1

    if hasattr(cam, 'principal_point'):
        # Blender 3.6+ and newer.
        principal_x = (cam.principal_point[0] / res_width) - 0.5
        principal_y = (cam.principal_point[1] / res_height) - 0.5
    elif hasattr(cam, 'principal'):
        # Blender 3.3 and earlier.
        principal_x = (cam.principal[0] / res_width) - 0.5
        principal_y = (cam.principal[1] / res_height) - 0.5
    else:
        principal_x = 0.0
        principal_y = 0.0

    lco_x = principal_x * film_back_width
    lco_y = principal_y * film_back_height

    data = {
        'resolution': (res_width, res_height),
        'film_back_cm': (film_back_width, film_back_height),
        'lens_center_offset_cm': (lco_x, lco_y),
    }

    # Get the focal length
    #
    # Blender does not appear to support having an animated focal
    # length in the Movie Clip Editor. :( Therefore we cannot support
    # it, and this might cause significant issues for people in Maya
    # with mmSolver.
    focal_length = cam.focal_length * 0.1  # convert to centimeters.
    start_frame, end_frame = frame_range
    per_frame_list = []
    for f in range(start_frame, end_frame + 1):
        frame_data = {
            'frame': f,
            'focal_length_cm': focal_length
        }
        per_frame_list.append(frame_data)
    data['per_frame'] = per_frame_list

    return data


def get_track_3d_data(context, track):
    """Get 3D position of the tracking point - the bundle position."""
    pos = track.bundle
    return {
        'x': pos[0],
        'y': pos[1],
        'z': pos[2],
        'x_lock': False,
        'y_lock': False,
        'z_lock': False,
    }


def get_track_data(context, clip, track, frame_range):
    """

    - name (string)
    - id (string)
    - set_name (string)
    - 3d
      - x (float)
      - y (float)
      - z (float)
      - x_lock (bool)
      - y_lock (bool)
      - z_lock (bool)
    - per_frame (list of frame data)
      - frame (int)
      - pos (float, float) - undistorted
      - weight (float)
      - pos_dist (float, float)

    """
    data = {}

    data['name'] = track.name
    data['id'] = None
    data['set_name'] = None
    data['3d'] = get_track_3d_data(context, track)

    weight = track.weight

    per_frame_list = []
    start_frame, end_frame = frame_range
    for f in range(start_frame, end_frame + 1):
        # Blender access the Marker data with the image sequence
        # starting at frame 1, not the "real" frame number of the
        # image sequence loaded.
        blender_frame = 1 + (f - start_frame)
        marker_at_frame = track.markers.find_frame(blender_frame)
        if marker_at_frame is None:
            continue
        if marker_at_frame.mute:
            continue

        # NOTE:
        #  Lower left is (0.0, 0.0) coordinate.
        #  Upper left is (0.0, 1.0) coordinate.
        #  Upper right is (1.0, 1.0) coordinate.
        #  Lower right is (1.0, 0.0) coordinate.
        coords = marker_at_frame.co.xy
        pos_distort_x = coords[0]
        pos_distort_y = coords[1]

        # Currently there is no way to create undistorted 2D tracking
        # position data. Therefore we set a very stupid value so that
        # users know it's wrong.
        pos_x = 0.0
        pos_y = 0.0

        frame_data = {
            'frame': f,
            'pos': (pos_x, pos_y),
            'weight': weight,
            'pos_dist': (pos_distort_x, pos_distort_y),
        }
        per_frame_list.append(frame_data)
    data['per_frame'] = per_frame_list

    return data


def get_data(context, clip, cam, tracks, frame_range):
    data = get_scene_data(context, clip, tracks, frame_range)

    cam_data = get_camera_data(context, clip, cam, frame_range)
    data['camera'] = cam_data

    points_list = []
    for track in tracks:
        track_data = get_track_data(
            context, clip, track,
            frame_range)
        points_list.append(track_data)
    data['points'] = points_list
    return data


def generate(context, clip, camera, tracks, frame_range, fmt=None):
    assert fmt == UV_TRACK_FORMAT_VERSION_4
    assert clip is not None
    assert camera is not None
    assert len(tracks) > 0
    assert len(frame_range) == 2

    data = get_data(context, clip, camera, tracks, frame_range)
    data_str = json.dumps(data)
    return data_str
