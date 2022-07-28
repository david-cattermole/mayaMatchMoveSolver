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
# 3DE4.script.version:  v1.6
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

import sys
import os
import tde4
import mmcamera_format


IS_PYTHON_2 = sys.version_info[0] == 2
if IS_PYTHON_2 is True:
    TEXT_TYPE = basestring  # noqa: F821
    INT_TYPES = (int, long)  # noqa: F821
else:
    TEXT_TYPE = str
    INT_TYPES = (int,)

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


def _parse_data(file_path):
    """
    Parses the given file path into a data structure.

    :param file_path: The full file path to read.
    :type file_path: str

    :returns: The data structure contained in the file path.
    :rtype: dict or None
    """
    assert file_path is not None
    assert isinstance(file_path, TEXT_TYPE)
    assert len(file_path) > 0
    try:
        file_data = mmcamera_format.parse(file_path)
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
    if not isinstance(file_path, TEXT_TYPE):
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
        print('Error: File path is not valid.')
        return
    file_data = _parse_data(file_path)
    has_valid_data = _file_data_has_valid_data(file_data)
    if has_valid_data is False:
        print('Error: File data is not valid.')
        return

    # Pass widget values to run function.
    file_data = _parse_data(file_path)
    mmcamera_format.apply_to_camera(
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
        msg = 'File contains invalid frame range: {file_start}-{file_end}'
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
                cam_end=cam_end,
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

    tde4.addTextFieldWidget(
        req, START_FRAME_WIDGET, START_FRAME_LABEL, str(start_frame)
    )
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
        is_static = mmcamera_format.detect_samples_are_static(samples)
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
    if mmcamera_format.SUPPORT_CLIPBOARD is True:
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
        window_requester, FILE_BROWSER_WIDGET, '_build_widgets'
    )

    pgroup_id, cam_id, lens_id = _query_selection_state()
    has_vaild_data = _file_data_has_valid_data(file_data)
    if has_vaild_data is not True or not pgroup_id or not cam_id or not lens_id:
        _build_widgets(window_requester, FILE_BROWSER_WIDGET, 0)
    else:
        _build_widgets_with_data(
            window_requester, pgroup_id, cam_id, lens_id, file_data
        )
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
        _paste_camera_mmsolver_requester, TITLE, WIDTH, HEIGHT, 'Paste', 'Cancel'
    )
    if button_pressed == 1:
        # Button index pressed is 1-based; 1=='Paste', 2='Cancel'.
        _run_gui(_paste_camera_mmsolver_requester, pgroup_id, cam_id, lens_id)
