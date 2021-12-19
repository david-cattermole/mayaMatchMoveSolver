# -*- mode: python-mode; python-indent-offset: 4 -*-
#
# Copyright (C) 2019, 2021 David Cattermole.
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
# 3DE4.script.name:     Paste Camera (MM Solver)...
#
# 3DE4.script.version:  v1.5
#
# 3DE4.script.gui:      Object Browser::Context Menu Camera
# 3DE4.script.gui:      Object Browser::Context Menu Cameras
# 3DE4.script.gui:      Object Browser::Context Menu PGroup
#
# 3DE4.script.comment:  Paste a .mmcamera file onto the selected camera.
# 3DE4.script.comment:
# 3DE4.script.comment:  In Maya:
# 3DE4.script.comment:  1) Select a camera transform node.
# 3DE4.script.comment:  2) Run the 'Copy Camera' tool (from MM Solver).
# 3DE4.script.comment:  This will save a temporary file and put the file
# 3DE4.script.comment:  path on the copy/paste buffer.
# 3DE4.script.comment:
# 3DE4.script.comment:  In 3DEqualizer:
# 3DE4.script.comment:  3) Select a camera
# 3DE4.script.comment:  4) Right click > Paste Camera (MM Solver)...
# 3DE4.script.comment:  The file path from step 2 will be auto-filled.
# 3DE4.script.comment:  5) Select options for pasting camera.
# 3DE4.script.comment:  6) Press "Paste" button.
# 3DE4.script.comment:
# 3DE4.script.comment:  The tool supports pasting individual components
# 3DE4.script.comment:  of the .mmcamera file.
#
#

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import json

import tde4
import vl_sdv


IS_PYTHON_2 = sys.version_info[0] == 2
if IS_PYTHON_2 is True:
    text_type = basestring
    int_type = (int, long)
else:
    text_type = str
    int_type = int

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

# GUI Constants
TITLE = 'Paste Camera (MM Solver)...'
WIDTH = 900
HEIGHT = 600
EXT = '.mmcamera'

ATTR_FOCAL_LENGTH = 'focalLength'
ATTR_FBK_WIDTH = 'filmBackWidth'
ATTR_FBK_HEIGHT = 'filmBackHeight'
ATTR_FBK_OFFSET_X = 'filmBackOffsetX'
ATTR_FBK_OFFSET_Y = 'filmBackOffsetY'
ATTR_TRANSLATE_X = 'translateX'
ATTR_TRANSLATE_Y = 'translateY'
ATTR_TRANSLATE_Z = 'translateZ'
ATTR_ROTATE_X = 'rotateX'
ATTR_ROTATE_Y = 'rotateY'
ATTR_ROTATE_Z = 'rotateZ'

FILE_BROWSER_WIDGET = 'file_browser_widget'
PLATE_PATH_WIDGET = 'plate_browser_widget'
PLATE_LOAD_WIDGET = 'plate_load_widget'
PLATE_RANGE_WIDGET = 'plate_range_widget'
PIXEL_ASPECT_WIDGET = 'pixel_aspect_widget'
START_FRAME_WIDGET = 'start_frame_widget'
END_FRAME_WIDGET = 'end_frame_widget'
CAMERA_NAME_WIDGET = 'camera_name_widget'

FILE_BROWSER_LABEL = 'File Path...'
PLATE_PATH_LABEL = 'Plate Path'
PLATE_LOAD_LABEL = 'Load Plate?'
PLATE_RANGE_LABEL = 'Plate Frame Range'
PIXEL_ASPECT_LABEL = 'Pixel Aspect Ratio'
START_FRAME_LABEL = 'Load Frame Start'
END_FRAME_LABEL = 'Load Frame End'
CAMERA_NAME_LABEL = 'Set Camera Name'

ATTR_FOCAL_LENGTH_WIDGET = 'focal_length_widget'
ATTR_FBK_SIZE_WIDGET = 'film_back_size_widget'
ATTR_FBK_OFFSET_WIDGET = 'film_back_offset_widget'
ATTR_TRANSLATE_WIDGET = 'translate_widget'
ATTR_ROTATE_WIDGET = 'rotate_widget'

ATTR_FOCAL_LENGTH_LABEL = 'Focal Length'
ATTR_FBK_SIZE_LABEL = 'Film Back Size'
ATTR_FBK_OFFSET_LABEL = 'Film Back Offset'
ATTR_TRANSLATE_LABEL = 'Translate'
ATTR_ROTATE_LABEL = 'Rotate'

SEP_01_WIDGET = 'separator_01_widget'
SEP_03_WIDGET = 'separator_03_widget'
SEP_04_WIDGET = 'separator_04_widget'
SEP_05_WIDGET = 'separator_05_widget'

BUILD_WIDGET_LIST = [
    PLATE_LOAD_WIDGET,
    PLATE_PATH_WIDGET,
    PLATE_RANGE_WIDGET,

    CAMERA_NAME_WIDGET,

    START_FRAME_WIDGET,
    END_FRAME_WIDGET,

    ATTR_FBK_SIZE_WIDGET,
    ATTR_FBK_OFFSET_WIDGET,
    PIXEL_ASPECT_WIDGET,
    ATTR_FOCAL_LENGTH_WIDGET,
    ATTR_TRANSLATE_WIDGET,
    ATTR_ROTATE_WIDGET,

    SEP_01_WIDGET,
    SEP_03_WIDGET,
    SEP_04_WIDGET,
    SEP_05_WIDGET,
]


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

    :param chosen_start_frame: The start frame that the user wants to limit to.
    :type chosen_start_frame: int

    :param chosen_end_frame: The end frame that the user wants to limit to.
    :type chosen_end_frame: int

    :returns: List of integer frame numbers.
    :rtype: [int, ..]
    """
    assert isinstance(file_start_frame, int_type)
    assert isinstance(file_end_frame, int_type)
    assert isinstance(chosen_start_frame, int_type)
    assert isinstance(chosen_end_frame, int_type)
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

    :param chosen_start_frame: The start frame that the user wants to limit to.
    :type chosen_start_frame: int

    :param chosen_end_frame: The end frame that the user wants to limit to.
    :type chosen_end_frame: int

    :returns: Were the translation values changed?
    :rtype: bool
    """
    values_were_set = False
    assert isinstance(file_start_frame, int_type)
    assert isinstance(file_end_frame, int_type)
    assert isinstance(chosen_start_frame, int_type)
    assert isinstance(chosen_end_frame, int_type)
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

    :param chosen_start_frame: The start frame that the user wants to limit to.
    :type chosen_start_frame: int

    :param chosen_end_frame: The end frame that the user wants to limit to.
    :type chosen_end_frame: int

    :returns: Were the rotation values changed?
    :rtype: bool
    """
    values_were_set = False
    assert isinstance(file_start_frame, int_type)
    assert isinstance(file_end_frame, int_type)
    assert isinstance(chosen_start_frame, int_type)
    assert isinstance(chosen_end_frame, int_type)
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

    :param cam_id: The Camera ID to apply data to.
    :type cam_id: str

    :param lens_id: The Lens ID to apply data to.
    :type lens_id: str

    :param samples: Frame/value pairs for Focal Length attribute,
                    representing a curve of values.
    :type samples: [(int, float), ..]

    :param file_start_frame: The start frame available from the parsed file.
    :type file_start_frame: int

    :param file_end_frame: The end frame available from the parsed file.
    :type file_end_frame: int

    :param chosen_start_frame: The start frame that the user wants to limit to.
    :type chosen_start_frame: int

    :param chosen_end_frame: The end frame that the user wants to limit to.
    :type chosen_end_frame: int

    :returns: Return True if the focal length was set, False otherwise.
    :rtype: bool
    """
    values_were_set = False
    assert isinstance(file_start_frame, int_type)
    assert isinstance(file_end_frame, int_type)
    assert isinstance(chosen_start_frame, int_type)
    assert isinstance(chosen_end_frame, int_type)
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
            # Internally, 3DE always starts at frame 1.
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
        # Set plate frame range
        file_start = int(file_start_frame)
        file_end = int(file_end_frame)
        tde4.setCameraSequenceAttr(cam_id, file_start, file_end, 1)
        if SUPPORT_CAMERA_FRAME_OFFSET is True:
            tde4.setCameraFrameOffset(cam_id, file_start)

        # Note: It is important to set the file path after the sequence
        # attributes, otherwise the camera will not show the image.
        plate_path = os.path.normpath(plate_path)
        tde4.setCameraPath(cam_id, plate_path)

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
            and isinstance(file_start_frame, int_type)
            and isinstance(file_end_frame, int_type)
            and isinstance(chosen_start_frame, text_type)
            and isinstance(chosen_end_frame, text_type)):
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
    if (isinstance(file_start_frame, int_type)
            and isinstance(file_end_frame, int_type)
            and isinstance(chosen_start_frame, text_type)
            and isinstance(chosen_end_frame, text_type)):
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


def _parse_data(file_path):
    """
    Parses the given file path into a data structure.

    :param file_path: The full file path to read.
    :type file_path: str

    :returns: The data structure contained in the file path.
    :rtype: dict or None
    """
    assert file_path is not None
    assert isinstance(file_path, text_type)
    assert len(file_path) > 0
    try:
        file_data = parse(file_path)
    except Exception as e:
        file_data = None
    return file_data


def _file_path_is_valid(file_path):
    """
    Test if the given file path is valid.

    :param file_path: File path string to test.
    :type file_path: str

    :rtype: bool
    """
    if file_path is None:
        return False
    if not isinstance(file_path, text_type):
        return False
    if len(file_path) == 0:
        return False
    if not os.path.isfile(file_path):
        return False
    return True


def _file_data_has_valid_data(file_data):
    """
    Does the file data structure have valid data for using as .mmcamera format?

    :param file_data: A data structure of from a JSON .mmcamera format file.
    :type file_data: dict

    :rtype: bool
    """
    if not isinstance(file_data, dict):
        return False
    data = file_data.get('data')
    if data is None:
        return False
    return True


def _remove_all_dynamic_widgets(req, widget, action):
    """
    Remove all dynamically generated widgets. A clean up function to
    prepare for all the widgets being created again.
    """
    for widget_name in BUILD_WIDGET_LIST:
        exists = tde4.widgetExists(req, widget_name)
        if not exists:
            continue
        tde4.removeWidget(req, widget_name)
    return


def _run_gui(req, pgroup_id, cam_id, lens_id):
    """
    Run when the user presses the 'ok' button in the window.

    :param req: The 3DEqualizer window requester id.
    :type req: str

    :param pgroup_id: The Point Group ID with the active camera in it.
    :type pgroup_id: str

    :param cam_id: The Camera ID to apply data to.
    :type cam_id: str

    :param lens_id: The Lens ID to apply data to.
    :type lens_id: str
    """
    # Query all widgets.
    options = dict()
    names_and_widgets = [
        ('file_path', FILE_BROWSER_WIDGET),
        ('plate_load', PLATE_LOAD_WIDGET),
        ('plate_path', PLATE_PATH_WIDGET),
        ('set_cam_name', CAMERA_NAME_WIDGET),
        ('start_frame', START_FRAME_WIDGET),
        ('end_frame', END_FRAME_WIDGET),
        ('fl', ATTR_FOCAL_LENGTH_WIDGET),
        ('fbk_size', ATTR_FBK_SIZE_WIDGET),
        ('fbk_offset', ATTR_FBK_OFFSET_WIDGET),
        ('par', PIXEL_ASPECT_WIDGET),
        ('translate', ATTR_TRANSLATE_WIDGET),
        ('rotate', ATTR_ROTATE_WIDGET),
    ]
    for name, widget in names_and_widgets:
        if tde4.widgetExists(req, widget):
            options[name] = tde4.getWidgetValue(req, widget)

    file_path = options.get('file_path')
    is_valid_file_path = _file_path_is_valid(file_path)
    if is_valid_file_path is False:
        print 'Error: File path is not valid.'
        return
    file_data = _parse_data(file_path)
    has_valid_data = _file_data_has_valid_data(file_data)
    if has_valid_data is False:
        print 'Error: File data is not valid.'
        return

    # Pass widget values to run function.
    file_data = _parse_data(file_path)
    apply_to_camera(
        pgroup_id,
        cam_id,
        lens_id,
        options,
        file_data,
    )
    return


def _build_widgets(req, widget, action):
    """
    Build the bottom half of the window, using the data of the file
    path in the UI.

    :param req: The 3DEqualizer window requester id.
    :type req: str

    :param widget: The widget name that called this function.
    :type widget: str

    :param action: The state of the widget that called this function;
                   what was the widget's action?
    :type action: str
    """
    pgroup_id, cam_id, lens_id = _query_selection_state()
    if not pgroup_id or not cam_id or not lens_id:
        return
    _remove_all_dynamic_widgets(req, widget, action)
    file_path = tde4.getWidgetValue(req, FILE_BROWSER_WIDGET)
    has_vaild_file_path = _file_path_is_valid(file_path)
    if has_vaild_file_path is not True:
        return
    file_data = _parse_data(file_path)
    has_vaild_data = _file_data_has_valid_data(file_data)
    if has_vaild_data is not True:
        return
    _build_widgets_with_data(req, pgroup_id, cam_id, lens_id, file_data)
    return


def _build_widgets_with_data(req, pgroup_id, cam_id, lens_id, file_data):
    """
    Build the bottom half of the window, using the data from
    the mmcamera file.

    :param req: The 3DEqualizer window requester id.
    :type req: str

    :param pgroup_id: The Point Group ID with the active camera in it.
    :type pgroup_id: str

    :param cam_id: The Camera ID to apply data to.
    :type cam_id: str

    :param lens_id: The Lens ID to apply data to.
    :type lens_id: str

    :param file_data: Valid file data from a .mmcamera file.
    :type file_data: dict
    """
    assert isinstance(file_data, dict)
    assert 'data' in file_data
    data = file_data.get('data')
    assert data is not None

    image_data = data.get('image', dict())
    plate_path = image_data.get('file_path')
    pixel_aspect = image_data.get('pixel_aspect_ratio')

    camera_name = str(data.get('name'))
    start_frame = str(data.get('start_frame'))
    end_frame = str(data.get('end_frame'))

    attrs_data = data.get('attr', dict())
    attr_names = list(attrs_data.keys())

    if not start_frame or not end_frame:
        msg = (
            'File contains invalid frame range: {file_start}-{file_end}'
        )
        msg = msg.format(
            file_start=start_frame,
            file_end=end_frame,
        )
        tde4.postQuestionRequester(TITLE, msg, 'Ok')
        return
    start_frame = int(start_frame)
    end_frame = int(end_frame)

    # Detect if the parsed file data does not have any frame
    # information in common with the selected camera.
    if not plate_path:
        has_common_frames = False
        cam_start, cam_end, _ = tde4.getCameraSequenceAttr(cam_id)
        if str(start_frame) and str(end_frame) and str(cam_start) and str(cam_end):
            cam_start = int(cam_start)
            cam_end = int(cam_end)
            cam_frames = set(range(cam_start, cam_end + 1))
            file_frames = set(range(start_frame, end_frame + 1))
            has_common_frames = not file_frames.isdisjoint(cam_frames)
        if has_common_frames is False:
            msg = (
                'The file path does not contain animated'
                ' data in the camera\'s frame range.\n'
                'File Frame Range: {file_start}-{file_end}\n'
                'Camera Frame Range: {cam_start}-{cam_end}\n'
            )
            msg = msg.format(
                file_start=start_frame,
                file_end=end_frame,
                cam_start=cam_start,
                cam_end=cam_end
            )
            tde4.postQuestionRequester(TITLE, msg, 'Ok')
            return

    tde4.addSeparatorWidget(req, SEP_01_WIDGET)

    if plate_path:
        plate_path = os.path.normpath(plate_path)
        tde4.addToggleWidget(req, PLATE_LOAD_WIDGET, PLATE_LOAD_LABEL, True)
        tde4.addTextFieldWidget(req, PLATE_PATH_WIDGET, PLATE_PATH_LABEL, plate_path)

        plate_range = '{0}-{1}'.format(start_frame, end_frame)
        tde4.addTextFieldWidget(req, PLATE_RANGE_WIDGET, PLATE_RANGE_LABEL, plate_range)

        tde4.addSeparatorWidget(req, SEP_03_WIDGET)

    if camera_name:
        tde4.addToggleWidget(req, CAMERA_NAME_WIDGET, CAMERA_NAME_LABEL, True)

    tde4.addTextFieldWidget(req, START_FRAME_WIDGET, START_FRAME_LABEL, str(start_frame))
    tde4.addTextFieldWidget(req, END_FRAME_WIDGET, END_FRAME_LABEL, str(end_frame))

    has_fbk_w = ATTR_FBK_WIDTH in attr_names
    has_fbk_h = ATTR_FBK_HEIGHT in attr_names
    if has_fbk_w or has_fbk_h:
        tde4.addToggleWidget(req, ATTR_FBK_SIZE_WIDGET, ATTR_FBK_SIZE_LABEL, True)

    has_fbk_x = ATTR_FBK_OFFSET_X in attr_names
    has_fbk_y = ATTR_FBK_OFFSET_Y in attr_names
    if has_fbk_x or has_fbk_y:
        tde4.addToggleWidget(req, ATTR_FBK_OFFSET_WIDGET, ATTR_FBK_OFFSET_LABEL, True)

    if pixel_aspect:
        label = '{0} ({1})'.format(PIXEL_ASPECT_LABEL, str(pixel_aspect))
        tde4.addToggleWidget(req, PIXEL_ASPECT_WIDGET, label, True)

    has_fl = ATTR_FOCAL_LENGTH in attr_names
    if has_fl:
        samples = attrs_data.get(ATTR_FOCAL_LENGTH)
        is_static = detect_samples_are_static(samples)
        static_mode = 'static'
        if is_static is not True:
            static_mode = 'animated'
        label = '{0} ({1})'.format(ATTR_FOCAL_LENGTH_LABEL, static_mode)
        tde4.addToggleWidget(req, ATTR_FOCAL_LENGTH_WIDGET, label, True)

    has_tx = ATTR_TRANSLATE_X in attr_names
    has_ty = ATTR_TRANSLATE_Y in attr_names
    has_tz = ATTR_TRANSLATE_Z in attr_names
    if has_tx or has_ty or has_tz:
        label = ATTR_TRANSLATE_LABEL + ' '
        label += 'X' * has_tx
        label += 'Y' * has_ty
        label += 'Z' * has_tz
        tde4.addToggleWidget(req, ATTR_TRANSLATE_WIDGET, label, True)

    has_rx = ATTR_ROTATE_X in attr_names
    has_ry = ATTR_ROTATE_Y in attr_names
    has_rz = ATTR_ROTATE_Z in attr_names
    if has_rx or has_ry or has_rz:
        label = ATTR_ROTATE_LABEL + ' '
        label += 'X' * has_rx
        label += 'Y' * has_ry
        label += 'Z' * has_rz
        tde4.addToggleWidget(req, ATTR_ROTATE_WIDGET, label, True)
    return


def _build_gui(file_path):
    """
    Build the widgets at the top of the window.

    :param file_path: The initial file path to parse.
    :type file_path: text_type or None

    :returns: 3DEqualizer UI request id.
    """
    # Get the clipboard value and test if it's a valid .mmcamera file,
    #  if so use it as the default.  If not, use the current 3DE file
    #  path as a directory to search.
    cwd_path = os.getcwd()
    proj_path = tde4.getProjectPath()
    if SUPPORT_CLIPBOARD is True:
        file_path = tde4.getClipboardString()

    file_data = None
    if file_path:
        file_data = _parse_data(file_path)
    has_vaild_data = _file_data_has_valid_data(file_data)
    if has_vaild_data is not True:
        file_path = proj_path or cwd_path

    window_requester = tde4.createCustomRequester()

    file_pattern = '*' + EXT
    tde4.addFileWidget(
        window_requester,
        FILE_BROWSER_WIDGET,
        FILE_BROWSER_LABEL,
        file_pattern,
        file_path,
    )
    tde4.setWidgetCallbackFunction(
        window_requester,
        FILE_BROWSER_WIDGET,
        '_build_widgets'
    )

    pgroup_id, cam_id, lens_id = _query_selection_state()
    has_vaild_data = _file_data_has_valid_data(file_data)
    if has_vaild_data is not True or not pgroup_id or not cam_id or not lens_id:
        _build_widgets(window_requester, FILE_BROWSER_WIDGET, 0)
    else:
        _build_widgets_with_data(window_requester, pgroup_id, cam_id, lens_id, file_data)
    return window_requester


def _query_selection_state():
    """
    Query the current selection state.

    Get the active point group, selected camera and connected lens.

    :returns: A tuple of Point Group ID, Camera ID and Lens ID. Any of
             the tuple members may be None if it could not be found.
    :rtype: (str or None, str or None, str or None)
    """
    cam_id = None
    lens_id = None
    msg = None
    pgroup_id = tde4.getCurrentPGroup()
    if not pgroup_id:
        msg = 'Error: Could not get active Point Group for camera.'
    else:
        with_selection = 1
        cam_ids = tde4.getCameraList(with_selection)
        if len(cam_ids) == 1:
            cam_id = cam_ids[0]
            lens_id = tde4.getCameraLens(cam_id)
            if not lens_id:
                msg = 'Error: Selected camera does not have a connected lens.'
        else:
            if len(cam_ids) == 0:
                msg = 'Error: Please select a camera.'
            elif len(cam_ids) > 1:
                msg = 'Error: Please select only one camera.'
            tde4.postQuestionRequester(TITLE, msg, 'Ok')
        if msg is not None:
            tde4.postQuestionRequester(TITLE, msg, 'Ok')
    return pgroup_id, cam_id, lens_id


# Launch GUI when this script is run.
pgroup_id, cam_id, lens_id = _query_selection_state()
if pgroup_id and cam_id and lens_id:
    try:
        requester = _paste_camera_mmsolver_requester
        _remove_all_dynamic_widgets(requester, '', 0)
        file_path = tde4.getWidgetValue(requester, FILE_BROWSER_WIDGET) or None
    except (ValueError, NameError, TypeError):
        file_path = None

    requester = _build_gui(file_path)
    _paste_camera_mmsolver_requester = requester

    button_pressed = tde4.postCustomRequester(
        _paste_camera_mmsolver_requester,
        TITLE, WIDTH, HEIGHT,
        'Paste', 'Cancel'
    )
    if button_pressed == 1:
        # Button index pressed is 1-based; 1=='Paste', 2='Cancel'.
        _run_gui(
            _paste_camera_mmsolver_requester,
            pgroup_id,
            cam_id,
            lens_id
        )
