# -*- mode: python-mode; python-indent-offset: 4 -*-
#
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
# ----------------------------------------------------------------------
"""
mmSolver Camera Format, to store cameras and plates.
"""
# 3DE4.script.hide:     true


import sys
import collections
import json

import tde4
import vl_sdv


# MM Camera format
# This is copied from 'mmSolver.tools.copypastecamera.constant module',
MM_CAMERA_FORMAT_VERSION_UNKNOWN = -1
MM_CAMERA_FORMAT_VERSION_1 = 1
MM_CAMERA_HEADER_VERSION_1 = {
    'version': MM_CAMERA_FORMAT_VERSION_1,
}

# Preferred MM Camera format version (changes the format version used
# for writing data).
MM_CAMERA_FORMAT_VERSION_PREFERRED = MM_CAMERA_FORMAT_VERSION_1

# Do we have support for new features of 3DE tde4 module?
SUPPORT_CAMERA_FRAME_OFFSET = 'getCameraFrameOffset' in dir(tde4)
SUPPORT_CLIPBOARD = 'setClipboardString' in dir(tde4)

# Conversion constants
MILLIMETERS_TO_CENTIMETRES = 0.1
PI = 3.141592654


def _float_is_equal(x, y):
    """
    Using an epsilon for approximate floating point equality.

    :returns: True or False, if float is equal or not.
    :rtype: bool
    """
    if x == y:
        return True
    eps = sys.float_info.epsilon * 100.0
    if x < (y + eps) and x > (y - eps):
        return True
    return False


def parse(file_path):
    """
    Parse a .mmcamera file path into a Python dictionary.
    """
    data = {}
    with open(file_path, 'rb') as f:
        data = json.load(f)
    return data


def _get_frame_list_to_set_values(cam_id, samples_list,
                                  file_start_frame, file_end_frame,
                                  chosen_start_frame, chosen_end_frame):
    """
    Calculate the frame numbers that are valid to set values with.

    :param cam_id: The 3DE Camera ID to apply data to.
    :type cam_id: str

    :param samples_list: List of list of frame/value tuples.
    :type samples_list: [[(int, float), ..], .. ]

    :param file_start_frame: The start frame available from the parsed file.
    :type file_start_frame: int

    :param file_end_frame: The end frame available from the parsed file.
    :type file_end_frame: int

    :param chosen_start_frame: The start frame that the user want's to limit to.
    :type chosen_start_frame: int

    :param chosen_end_frame: The end frame that the user want's to limit to.
    :type chosen_end_frame: int

    :returns: List of integer frame numbers.
    :rtype: [int, ..]
    """
    assert isinstance(file_start_frame, (int, long))
    assert isinstance(file_end_frame, (int, long))
    assert isinstance(chosen_start_frame, (int, long))
    assert isinstance(chosen_end_frame, (int, long))
    user_requested_frames = set(range(chosen_start_frame, chosen_end_frame + 1))

    cam_start, cam_end, _ = tde4.getCameraSequenceAttr(cam_id)
    cam_frames = set(range(cam_start, cam_end + 1))

    file_frames = set(range(file_start_frame, file_end_frame + 1))

    sample_frames = set()
    for samples in samples_list:
        sample_frames |= set([int(f) for f, _ in samples])

    frames = sample_frames & file_frames & user_requested_frames & cam_frames
    frames = list(sorted(list(frames)))
    return frames


def detect_samples_are_static(samples):
    """
    Given a set of samples (frame and value tuple), determine if the
    values are animated or static.

    :param samples: The list of Attribute samples to test.
    :type samples: [(int, float), ..]

    :rtype bool
    """
    is_static = True
    previous_value = None
    for _, value in samples:
        if previous_value is None:
            previous_value = value
        is_equal = _float_is_equal(previous_value, value)
        previous_value = value
        if is_equal is False:
            is_static = False
            break
    return is_static


def _set_camera_translation(pgroup_id, cam_id,
                            tx_samples, ty_samples, tz_samples,
                            file_start_frame, file_end_frame,
                            chosen_start_frame, chosen_end_frame):
    """
    Set the camera translation values on the given 3DE camera ids.

    :param pgroup_id: The Point Group ID with the active camera in it.
    :type pgroup_id: str

    :param cam_id: The Camera ID to apply data to.
    :type cam_id: str

    :param lens_id: The Lens ID to apply data to.
    :type lens_id: str

    :param tx_samples: Frame/value pairs for Translate X, representing
                       a curve of values.
    :type tx_samples: [(int, float), ..]

    :param ty_samples: Frame/value pairs for Translate Y, representing
                       a curve of values.
    :type ty_samples: [(int, float), ..]

    :param tz_samples: Frame/value pairs for Translate Z, representing
                       a curve of values.
    :type tz_samples: [(int, float), ..]

    :param file_start_frame: The start frame available from the parsed file.
    :type file_start_frame: int

    :param file_end_frame: The end frame available from the parsed file.
    :type file_end_frame: int

    :param chosen_start_frame: The start frame that the user want's to limit to.
    :type chosen_start_frame: int

    :param chosen_end_frame: The end frame that the user want's to limit to.
    :type chosen_end_frame: int

    :returns: Were the translation values changed?
    :rtype: bool
    """
    values_were_set = False
    assert isinstance(file_start_frame, (int, long))
    assert isinstance(file_end_frame, (int, long))
    assert isinstance(chosen_start_frame, (int, long))
    assert isinstance(chosen_end_frame, (int, long))
    assert tx_samples
    assert ty_samples
    assert tz_samples

    samples_list = (tx_samples, ty_samples, tz_samples)
    frames = _get_frame_list_to_set_values(
        cam_id, samples_list,
        file_start_frame, file_end_frame,
        chosen_start_frame, chosen_end_frame
    )

    translate_data = dict()
    for component_index, samples in [(0, tx_samples),
                                     (1, ty_samples),
                                     (2, tz_samples)]:
        for frame, value in samples:
            frame = int(frame)
            if frame not in translate_data:
                translate_data[frame] = [None, None, None]
            translate_data[frame][component_index] = value

    for global_frame in frames:
        pos_value = translate_data.get(global_frame)
        if pos_value is None:
            continue
        # Internally, 3DE always starts at frame 1.
        raw_frame = 1 + (global_frame - file_start_frame)
        tde4.setPGroupPosition3D(pgroup_id, cam_id, raw_frame, pos_value)
        values_were_set = True
    return values_were_set


def _set_camera_rotation(pgroup_id, cam_id,
                         rx_samples, ry_samples, rz_samples,
                         file_start_frame, file_end_frame,
                         chosen_start_frame, chosen_end_frame):
    """
    Set the camera rotation values on the given 3DE camera ids.

    :param pgroup_id: The Point Group ID with the active camera in it.
    :type pgroup_id: str

    :param cam_id: The Camera ID to apply data to.
    :type cam_id: str

    :param lens_id: The Lens ID to apply data to.
    :type lens_id: str

    :param rx_samples: Frame/value pairs for Rotate X, representing
                       a curve of values.
    :type rx_samples: [(int, float), ..]

    :param ry_samples: Frame/value pairs for Rotate Y, representing
                       a curve of values.
    :type ry_samples: [(int, float), ..]

    :param rz_samples: Frame/value pairs for Rotate Z, representing
                       a curve of values.
    :type rz_samples: [(int, float), ..]

    :param file_start_frame: The start frame available from the parsed file.
    :type file_start_frame: int

    :param file_end_frame: The end frame available from the parsed file.
    :type file_end_frame: int

    :param chosen_start_frame: The start frame that the user want's to limit to.
    :type chosen_start_frame: int

    :param chosen_end_frame: The end frame that the user want's to limit to.
    :type chosen_end_frame: int

    :returns: Were the rotation values changed?
    :rtype: bool
    """
    values_were_set = False
    assert isinstance(file_start_frame, (int, long))
    assert isinstance(file_end_frame, (int, long))
    assert isinstance(chosen_start_frame, (int, long))
    assert isinstance(chosen_end_frame, (int, long))
    assert rx_samples
    assert ry_samples
    assert rz_samples

    samples_list = (rx_samples, ry_samples, rz_samples)
    frames = _get_frame_list_to_set_values(
        cam_id, samples_list,
        file_start_frame, file_end_frame,
        chosen_start_frame, chosen_end_frame
    )

    rotate_data = dict()
    for component_index, samples in [(0, rx_samples),
                                     (1, ry_samples),
                                     (2, rz_samples)]:
        for frame, value in samples:
            frame = int(frame)
            if frame not in rotate_data:
                rotate_data[frame] = [None, None, None]
            rotate_data[frame][component_index] = (value * PI) / 180.0

    for global_frame in frames:
        rot_value = rotate_data.get(global_frame)
        if rot_value is None:
            continue
        rot_x, rot_y, rot_z = rot_value
        r3d = vl_sdv.rot3d(rot_x, rot_y, rot_z, vl_sdv.VL_APPLY_ZXY)
        r3d = vl_sdv.mat3d(r3d)
        r3d0 = [
            [r3d[0][0], r3d[0][1], r3d[0][2]],
            [r3d[1][0], r3d[1][1], r3d[1][2]],
            [r3d[2][0], r3d[2][1], r3d[2][2]]
        ]
        # Internally, 3DE always starts at frame 1.
        raw_frame = 1 + (global_frame - file_start_frame)
        tde4.setPGroupRotation3D(pgroup_id, cam_id, raw_frame, r3d0)
        values_were_set = True
    return values_were_set


def _set_camera_focal_length(cam_id, lens_id,
                             samples,
                             file_start_frame, file_end_frame,
                             chosen_start_frame, chosen_end_frame):
    """
    Set the focal length on the given camera/lens.

    :returns: Return True if the focal length was set, False otherwise.
    :rtype: bool
    """
    values_were_set = False
    assert isinstance(file_start_frame, (int, long))
    assert isinstance(file_end_frame, (int, long))
    assert isinstance(chosen_start_frame, (int, long))
    assert isinstance(chosen_end_frame, (int, long))
    assert samples

    samples_list = (samples, )
    frames = _get_frame_list_to_set_values(
        cam_id, samples_list,
        file_start_frame, file_end_frame,
        chosen_start_frame, chosen_end_frame
    )

    focal_length_is_static = detect_samples_are_static(samples)
    if focal_length_is_static is True:
        fl_mode = 'FOCAL_USE_FROM_LENS'
        tde4.setCameraFocalLengthMode(cam_id, fl_mode)
        value = samples[0][-1] * MILLIMETERS_TO_CENTIMETRES
        tde4.setLensFocalLength(lens_id, value)
        values_were_set = True

    else:
        fl_mode = 'FOCAL_DYNAMIC'
        tde4.setCameraFocalLengthMode(cam_id, fl_mode)
        curve_id = tde4.getCameraZoomCurve(cam_id)

        # Clean keyframes inside start/end frame range.
        remove_key_ids = []
        key_ids = tde4.getCurveKeyList(curve_id, 0)
        for key_id in key_ids:
            frame, value = tde4.getCurveKeyPosition(curve_id, key_id)
            if frame not in frames:
                continue
            remove_key_ids.append(key_id)
        for key_id in remove_key_ids:
            tde4.deleteCurveKey(curve_id, key_id)
            values_were_set = True

        # Set new keyframes in the range
        for global_frame, value in samples:
            if global_frame not in frames:
                continue
            value *= MILLIMETERS_TO_CENTIMETRES
            raw_frame = 1 + (global_frame - file_start_frame)
            vec = [raw_frame, value]
            key_id = tde4.createCurveKey(curve_id, vec)
            tde4.setCurveKeyMode(curve_id, key_id, 'LINEAR')
            values_were_set = True
    return values_were_set


def apply_to_camera(pgroup_id, cam_id, lens_id, options, file_data):
    """
    Replace the camera and lens with the given options.
    """
    camera_data = file_data.get('data', dict())

    # Set image file path
    file_start_frame = camera_data.get('start_frame')
    file_end_frame = camera_data.get('end_frame')
    plate_load = options.get('plate_load')
    plate_path = options.get('plate_path')
    if (plate_load
            and file_start_frame is not None
            and file_end_frame is not None
            and plate_path):
        tde4.setCameraPath(cam_id, plate_path)

        # Set plate frame range
        file_start = int(file_start_frame)
        file_end = int(file_end_frame)
        tde4.setCameraSequenceAttr(cam_id, file_start, file_end, 1)
        if SUPPORT_CAMERA_FRAME_OFFSET is True:
            tde4.setCameraFrameOffset(cam_id, file_start)

    # Set pixel aspect ratio
    par = options.get('par')
    if par:
        par = float(par)
        tde4.setLensPixelAspect(lens_id, par)

    # Set Camera name
    set_name = options.get('set_cam_name')
    if set_name:
        cam_name = camera_data.get('name', '')
        if cam_name:
            tde4.setCameraName(cam_id, cam_name)
        lens_name = cam_name + '_lens'
        if lens_name:
            tde4.setLensName(lens_id, lens_name)

    attr_data = camera_data.get('attr', dict())

    # Set film back
    #
    # Note: These values cannot be animated in 3DE, even if in Maya
    # they were animated. We only take the first value in the list and
    # assume the film back value is constant.
    fbk_size = options.get('fbk_size')
    filmBackWidthSamples = attr_data.get('filmBackWidth')
    filmBackHeightSamples = attr_data.get('filmBackHeight')
    if fbk_size and filmBackWidthSamples and filmBackHeightSamples:
        value_x = filmBackWidthSamples[0][-1] * MILLIMETERS_TO_CENTIMETRES
        value_y = filmBackHeightSamples[0][-1] * MILLIMETERS_TO_CENTIMETRES
        tde4.setLensFBackWidth(lens_id, value_x)
        tde4.setLensFBackHeight(lens_id, value_y)

    fbk_offset = options.get('fbk_offset')
    filmBackOffsetXSamples = attr_data.get('filmBackOffsetX')
    filmBackOffsetYSamples = attr_data.get('filmBackOffsetY')
    if fbk_offset and filmBackOffsetXSamples and filmBackOffsetYSamples:
        value_x = filmBackOffsetXSamples[0][-1] * MILLIMETERS_TO_CENTIMETRES
        value_y = filmBackOffsetYSamples[0][-1] * MILLIMETERS_TO_CENTIMETRES
        tde4.setLensLensCenterX(lens_id, value_x)
        tde4.setLensLensCenterY(lens_id, value_y)

    # Set focal length
    file_start_frame = camera_data.get('start_frame')
    file_end_frame = camera_data.get('end_frame')
    chosen_start_frame = options.get('start_frame')
    chosen_end_frame = options.get('end_frame')
    fl = options.get('fl')
    focalLengthSamples = attr_data.get('focalLength')
    if (fl and focalLengthSamples
            and isinstance(file_start_frame, (int, long))
            and isinstance(file_end_frame, (int, long))
            and isinstance(chosen_start_frame, basestring)
            and isinstance(chosen_end_frame, basestring)):
        file_start = int(file_start_frame)
        file_end = int(file_end_frame)
        chosen_start = int(chosen_start_frame)
        chosen_end = int(chosen_end_frame)
        focal_length_set = _set_camera_focal_length(
            cam_id, lens_id,
            focalLengthSamples,
            file_start, file_end,
            chosen_start, chosen_end,
        )

    # Set translation and rotation
    file_start_frame = camera_data.get('start_frame')
    file_end_frame = camera_data.get('end_frame')
    chosen_start_frame = options.get('start_frame')
    chosen_end_frame = options.get('end_frame')
    if (isinstance(file_start_frame, (int, long))
            and isinstance(file_end_frame, (int, long))
            and isinstance(chosen_start_frame, basestring)
            and isinstance(chosen_end_frame, basestring)):
        file_start = int(file_start_frame)
        file_end = int(file_end_frame)
        chosen_start = int(chosen_start_frame)
        chosen_end = int(chosen_end_frame)

        # Set Translation
        translate_set = False
        translate = options.get('translate')
        tx_samples = attr_data.get('translateX')
        ty_samples = attr_data.get('translateY')
        tz_samples = attr_data.get('translateZ')
        if translate and tx_samples and ty_samples and tz_samples:
            translate_set = _set_camera_translation(
                pgroup_id, cam_id,
                tx_samples, ty_samples, tz_samples,
                file_start, file_end,
                chosen_start, chosen_end
            )

        # Set Rotation
        rotate_set = False
        rotate = options.get('rotate')
        rx_samples = attr_data.get('rotateX')
        ry_samples = attr_data.get('rotateY')
        rz_samples = attr_data.get('rotateZ')
        if rotate and rx_samples and ry_samples and rz_samples:
            rotate_set = _set_camera_rotation(
                pgroup_id, cam_id,
                rx_samples, ry_samples, rz_samples,
                file_start, file_end,
                chosen_start, chosen_end
            )

        if translate_set or rotate_set:
            tde4.setPGroupPostfilterMode(pgroup_id, 'POSTFILTER_OFF')
            tde4.filterPGroup(pgroup_id, cam_id)
    return
