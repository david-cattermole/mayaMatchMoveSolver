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
#
"""
The Copy/Paste Camera library functions.

The file saved will contain::

- Camera Name

- Image Plane File Path

- Pixel Aspect Ratio (static)

- Camera Translation (animated)

- Camera Rotation (animated - in ZXY rotation order)

- Camera Film Back (animated)

- Camera Film Offsets (animated)

- Camera Focal Length (animated)


This tool does not store Lens Distortion (the Image Plane File Path is
assumed to be undistorted/flattened). A future version of this tool
and file format may support lens distortion, if it were saved in Maya
in a standardized way.


The JSON dictionary format::

    {
        'version': int,
        'data': {
            'name': str,
            'start_frame': int,
            'end_frame': int,
            'image': {
                'file_path': str, # or None
                'width': int,     # or None
                'height': int,    # or None
                'pixel_aspect_ratio': float,  # or None
            },
            'attr': [
                str: [
                    [int, float]
                ]
            ]
        }
    }

"""

import json
import glob
import os
import re
import tempfile

import maya.cmds

import mmSolver.logger

import mmSolver.utils.time as time_utils
import mmSolver.utils.node as node_utils
import mmSolver.utils.camera as camera_utils
import mmSolver.utils.transform as tfm_utils
import mmSolver.tools.copypastecamera.constant as const


LOG = mmSolver.logger.get_logger()


def get_image_path_tokens(file_path):
    """
    """
    data = None
    head, tail = os.path.split(file_path)
    file_frame_ext_prog = re.compile(const.PATTERN_RE_FILE_FRAME_EXT)
    file_frame_ext_match = file_frame_ext_prog.match(tail)
    if file_frame_ext_match:
        grps = file_frame_ext_match.groups()
        frame_num_padding = len(str(grps[2]))
        data = {
            'name': grps[0],
            'frame': grps[2],
            'ext': grps[4],
        }
    return data


def get_image_path_single_frame(file_path, test_disk):
    """
    """
    image_file_path = None
    multi_frame = None
    if test_disk is False:
        head, tail = os.path.split(file_path)
        file_ext_prog = re.compile(const.PATTERN_RE_FILE_EXT)
        file_ext_match = file_ext_prog.match(tail)
        if file_ext_match:
            image_file_path = file_path
            multi_frame = False
    else:
        if os.path.isfile(file_path):
            head, tail = os.path.split(file_path)
            file_ext_prog = re.compile(const.PATTERN_RE_FILE_EXT)
            file_ext_match = file_ext_prog.match(tail)
            if file_ext_match:
                image_file_path = file_path
                multi_frame = False
    return image_file_path, multi_frame


def get_image_path_multi_frame(image_path, test_disk):
    """

    :returns: Image file path and boolean of whether the image path
              represents an image sequence, or not.
              Returns (None, None) if the function cannot determine
              the values accurately.
    :rtype: (str, bool) or (None, None)
    """
    image_file_path = None
    multi_frame = None

    head, tail = os.path.split(image_path)
    file_ext_prog = re.compile(const.PATTERN_RE_FILE_EXT)
    file_ext_match = file_ext_prog.match(tail)
    file_frame_ext_prog = re.compile(const.PATTERN_RE_FILE_FRAME_EXT)
    file_frame_ext_match = file_frame_ext_prog.match(tail)
    if file_ext_match and file_frame_ext_match:
        grps = file_frame_ext_match.groups()
        frame_num_padding = len(str(grps[2]))

        # Check at least one file on disk matches this pattern.
        exists = True
        if test_disk is True:
            pattern_grps = list(grps)
            pattern_grps[2] = '*'
            pattern = ''.join(pattern_grps)
            glob_pattern = os.path.join(head, pattern)
            exists = any(glob.iglob(glob_pattern))

        if exists is True:
            assert frame_num_padding > 0
            pattern_grps = list(grps)
            pattern_grps[2] = '#' * frame_num_padding
            pattern = ''.join(pattern_grps)
            image_file_path = os.path.join(head, pattern)
    else:
        image_file_path, multi_frame = get_image_path_single_frame(image_path, test_disk)
    return image_file_path, multi_frame


def get_image_path_pattern(image_name, use_frame_ext, test_disk=None):
    """
    Compute the image path pattern, for the given Maya imagePlane path.

    Assumptions::

    - '#' character is not used in the image_name string.

    - '?' character is not used in the image_name string.

    - '*' character is not used in the image_name string.

    - An animated image sequence uses the file naming pattern
      'file.####.ext' or 'file.ext', such as 'image.1001.jpg' or 'image.jpg'.

    .. note::

         If test_disk is True, this function will query the file
         path and directory on disk (not just string assumptions).

    :param image_name: Maya imagePlane file (sequence) path.
    :type image_name: str

    :param use_frame_ext: The value of imagePlane node's
                          'useFrameExtension' attribute.
    :type use_frame_ext: bool

    :param test_disk: Is this function allowed to query the file on
                      disk and make calls to the disk? If not we use
                      only string manipulation but do not test
                      (for example) the actual file existence.
    :type test_disk: bool

    :returns: Image file path and boolean of whether the image path
              represents an image sequence, or not.
              Returns (None, None) if the function cannot determine
              the values accurately.
    :rtype: (str, bool) or (None, None)
    """
    assert isinstance(image_name, (str, unicode, basestring))
    assert '#' not in image_name
    assert '?' not in image_name
    assert '*' not in image_name
    if test_disk is None:
        test_disk = False
    assert isinstance(test_disk, bool)

    image_file_path = None
    if use_frame_ext is False:
        image_file_path, multi_frame = get_image_path_single_frame(image_name, test_disk)
    else:
        image_file_path, multi_frame = get_image_path_multi_frame(image_name, test_disk)
    return image_file_path, multi_frame


def get_frame_range_from_file_pattern(file_path_pattern, fallback_range=None):
    """
    Given a file pattern with '#' characters representing the frame
    number, get the full frame range on disk.

    :returns: FrameRange
    :rtype: FrameRange or (int, int)
    """
    assert isinstance(file_path_pattern, (str, unicode, basestring))
    assert len(file_path_pattern) > 0
    assert isinstance(fallback_range, (time_utils.FrameRange))
    start = 99999999
    end = -99999999
    glob_pattern = file_path_pattern.replace('#', '?')
    for path in glob.iglob(glob_pattern):
        token_data = get_image_path_tokens(path)
        if token_data is None:
            continue
        frame = int(token_data.get('frame'))
        start = min(start, frame)
        end = max(end, frame)
    frame_range = time_utils.FrameRange(start, end)
    if start > end:
        # frame_range = time_utils.FrameRange(None, None)
        frame_range = fallback_range
    return frame_range


def guess_pixel_aspect_ratio(cam_tfm, cam_shp, img_pl_shp, file_path_pattern):
    ratio = None

    plug = '{0}.fit'.format(img_pl_shp)
    fit = maya.cmds.getAttr(plug)
    if fit == 4:
        # If the image plane is set to 'to size' fit, then calculate
        # the difference between the camera film back and image plane
        # image size.
        plug = '{0}.horizontalFilmAperture'.format(cam_shp)
        fbk_w = maya.cmds.getAttr(plug)
        plug = '{0}.verticalFilmAperture'.format(cam_shp)
        fbk_h = maya.cmds.getAttr(plug)
        fbk_aspect = fbk_w / fbk_h

        # Image size.
        plug = '{0}.coverageX'.format(img_pl_shp)
        img_w = float(maya.cmds.getAttr(plug))
        plug = '{0}.coverageY'.format(img_pl_shp)
        img_h = float(maya.cmds.getAttr(plug))
        if img_w > 0 and img_h > 0:
            img_aspect = img_w / img_h

            # Pixel aspect ratio.
            ratio = fbk_aspect / img_aspect
            ratio = round(ratio, const.PIXEL_ASPECT_RATIO_SIGNIFICANT_DIGITS)
    else:
        # Use Maya's default aspect ratio
        # http://help.autodesk.com/cloudhelp/2016/ENU/Maya-Tech-Docs/Nodes/resolution.html
        device_aspect_ratio = maya.cmds.getAttr('defaultResolution.deviceAspectRatio')
        width = maya.cmds.getAttr('defaultResolution.width')
        height = maya.cmds.getAttr('defaultResolution.height')

        # Pixel aspect ratio.
        ratio = (float(height) / float(width)) * device_aspect_ratio
        ratio = round(ratio, const.PIXEL_ASPECT_RATIO_SIGNIFICANT_DIGITS)

        # # TODO: Guess the Pixel Aspect Ratio by reading the image metadata.
        # glob_pattern = file_path_pattern.replace('#', '?')
        # for path in glob.iglob(glob_pattern):
        #     break
    
    return ratio


def query_plate_data(cam_tfm, cam_shp, img_pl_shp, test_disk):
    """
    Query plate information from the given camera and image plane.

    :param cam_tfm: Camera transform node of given image plane shape.
    :type cam_tfm: str

    :param cam_shp: Camera shape node of given image plane shape.
    :type cam_shp: str

    :param img_pl_shp: Image Plane node shape node to query.
    :type img_pl_shp: str
    """
    assert isinstance(cam_tfm, (str, unicode, basestring))
    assert isinstance(cam_shp, (str, unicode, basestring))
    assert len(cam_tfm) > 0
    assert len(cam_shp) > 0
    assert maya.cmds.objExists(cam_tfm)
    assert maya.cmds.objExists(cam_shp)
    assert isinstance(img_pl_shp, (str, unicode, basestring))
    assert maya.cmds.objExists(img_pl_shp)

    # Query image plane path
    # Parse image plane path and get frame number token.
    # Detect if the image plane is not animated.
    image_file_path = None
    image_width = None
    image_height = None
    image_pixel_aspect = None
    if img_pl_shp is not None:
        plug = '{0}.imageName'.format(img_pl_shp)
        image_name = maya.cmds.getAttr(plug)
        if image_name is not None and len(image_name) > 0:
            if os.path.isabs(image_name) is False:
                image_name = maya.cmds.workspace(expandName=image_name)

        plug = '{0}.useFrameExtension'.format(img_pl_shp)
        use_frame_ext = maya.cmds.getAttr(plug)

        image_file_path, _ = get_image_path_pattern(
            image_name,
            use_frame_ext,
            test_disk=test_disk
        )
        if image_file_path is not None:
            image_wh = maya.cmds.imagePlane(img_pl_shp, query=True, imageSize=True) or None
            if image_wh is not None:
                assert len(image_wh) == 2
                image_width, image_height = image_wh
                image_width = int(image_width)
                image_height = int(image_height)
            image_pixel_aspect = guess_pixel_aspect_ratio(
                cam_tfm,
                cam_shp,
                img_pl_shp,
                image_file_path
            )

    data = {
        'file_path': image_file_path,
        'width': image_width,
        'height': image_height,
        'pixel_aspect': image_pixel_aspect,
    }
    return data


def query_camera_data(cam_tfm,
                      cam_shp,
                      frames,
                      rotate_order,
                      test_disk):
    """
    Get the camera information from the given cameras
    """
    assert isinstance(cam_tfm, (str, unicode, basestring))
    assert isinstance(cam_shp, (str, unicode, basestring))
    assert len(cam_tfm) > 0
    assert len(cam_shp) > 0
    assert maya.cmds.objExists(cam_tfm)
    assert maya.cmds.objExists(cam_shp)
    assert isinstance(frames, (list, tuple))

    cam_data = {}
    attr_data = {}

    # Get the camera name, by parsing node name.
    name = cam_tfm.rpartition('|')[-1]
    cam_data['name'] = name

    # Add 'translate' and 'rotate' attributes to list to evaluate.
    tfm_node = tfm_utils.TransformNode(cam_tfm)
    tfm_cache = tfm_utils.TransformMatrixCache()
    tfm_cache.add_node(tfm_node, frames)
    tfm_cache.process()
    tfm_mat_list = tfm_utils.get_transform_matrix_list(
        tfm_cache, frames, tfm_node,
        rotate_order=rotate_order
    )
    assert len(tfm_mat_list) == len(frames)
    tx_values = []
    ty_values = []
    tz_values = []
    rx_values = []
    ry_values = []
    rz_values = []
    prv_rot = None
    for f, mat in zip(frames, tfm_mat_list):
        tx, ty, tz, rx, ry, rz, _, _, _ = tfm_utils.decompose_matrix(mat, prv_rot)
        tx_values.append((f, tx))
        ty_values.append((f, ty))
        tz_values.append((f, tz))
        rx_values.append((f, rx))
        ry_values.append((f, ry))
        rz_values.append((f, rz))
    attr_data['translateX'] = tx_values
    attr_data['translateY'] = ty_values
    attr_data['translateZ'] = tz_values
    attr_data['rotateX'] = rx_values
    attr_data['rotateY'] = ry_values
    attr_data['rotateZ'] = rz_values

    # Get the camera shape node attributes:
    # - focal length
    # - film back
    # - film back offset
    #
    # The values are stored in millimetres (mm).
    attrs = [
        ('focalLength', 'focalLength', lambda x: x),
        ('horizontalFilmAperture', 'filmBackWidth', lambda x: x * 25.4),
        ('verticalFilmAperture', 'filmBackHeight', lambda x: x * 25.4),
        ('horizontalFilmOffset', 'filmBackOffsetX', lambda x: x * 25.4),
        ('verticalFilmOffset', 'filmBackOffsetY', lambda x: x * 25.4),
    ]
    for attr, attr_name, convert_func in attrs:
        plug = '{0}.{1}'.format(cam_tfm, attr)
        attr_values = []
        for f in frames:
            v = maya.cmds.getAttr(plug, time=f)
            v = convert_func(v)
            attr_values.append((f, v))
        attr_data[attr_name] = attr_values

    cam_data['attr'] = attr_data
    return cam_data


def generate(cam_data, plate_data, frame_range):
    """
    """
    data = const.MM_CAMERA_HEADER_VERSION_1.copy()
    data.update(
        {
            'data': {
                'name': cam_data.get('name'),
                'start_frame': frame_range.start,
                'end_frame': frame_range.end,
                'image': {
                    'file_path': plate_data.get('file_path'),
                    'width': plate_data.get('width'),
                    'height': plate_data.get('height'),
                    'pixel_aspect_ratio': plate_data.get('pixel_aspect'),
                },
                'attr': cam_data.get('attr'),
            },
        }
    )
    data_str = json.dumps(data)
    return data_str


def write_temp_file(data_str):
    """
    Write file.
    """
    file_ext = const.EXT
    f = tempfile.NamedTemporaryFile(
        mode='w+b',
        bufsize=-1,
        suffix=file_ext,
        delete=False
    )
    if f.closed:
        msg = "Error: Couldn't open file.\n%r"
        msg = msg % f.name
        return False
    f.write(data_str)
    f.close()
    return f.name
