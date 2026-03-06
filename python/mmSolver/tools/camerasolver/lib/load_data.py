# Copyright (C) 2026 David Cattermole.
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
Functions for loading camera solver output data from files.
"""

import json
import os

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.python_compat as pycompat

from mmSolver.tools.camerasolver.lib.save_data import INCHES_TO_MM

LOG = mmSolver.logger.get_logger()


def load_solved_camera_from_file(cam, file_path):
    # type: (...) -> bool
    """Apply solved camera data from a .mmcamera file to a Maya camera.

    Keyframes are set on the camera transform and shape for every frame
    stored in the file.  Film-back attributes are converted from mm
    (file units) back to inches (Maya units).

    Returns True on success, False if the file could not be loaded.
    """
    assert isinstance(cam, mmapi.Camera)
    assert isinstance(file_path, pycompat.TEXT_TYPE)

    if not os.path.isfile(file_path):
        LOG.error('Solved camera file not found: %r', file_path)
        return False

    with open(file_path, 'r') as fh:
        doc = json.load(fh)

    attr_data = doc.get('data', {}).get('attr', {})
    if not attr_data:
        LOG.error('No attribute data found in: %r', file_path)
        return False

    cam_tfm = cam.get_transform_node()
    cam_shp = cam.get_shape_node()

    # Map from mmcamera attribute name -> (node, maya_attr, mm_to_inches)
    MM_TO_INCHES = 1.0 / INCHES_TO_MM
    attr_map = {
        'translateX': (cam_tfm, 'translateX', False),
        'translateY': (cam_tfm, 'translateY', False),
        'translateZ': (cam_tfm, 'translateZ', False),
        'rotateX': (cam_tfm, 'rotateX', False),
        'rotateY': (cam_tfm, 'rotateY', False),
        'rotateZ': (cam_tfm, 'rotateZ', False),
        'focalLength': (cam_shp, 'focalLength', False),
        'filmBackWidth': (cam_shp, 'horizontalFilmAperture', True),
        'filmBackHeight': (cam_shp, 'verticalFilmAperture', True),
        'filmBackOffsetX': (cam_shp, 'horizontalFilmOffset', True),
        'filmBackOffsetY': (cam_shp, 'verticalFilmOffset', True),
    }

    for file_attr, (node, maya_attr, convert_to_inches) in attr_map.items():
        samples = attr_data.get(file_attr)
        if not samples:
            continue
        scale = MM_TO_INCHES if convert_to_inches else 1.0
        for frame, value in samples:
            maya.cmds.setKeyframe(
                node, attribute=maya_attr, time=frame, value=value * scale
            )

    return True


def load_camera_outputs(cam, prefix_name, output_dir):
    # type: (...) -> bool
    """Load the solved camera from the output directory into Maya.

    The solver writes ``{prefix_name}_camera.mmcamera`` to *output_dir*.
    This function reads that file and keyframes the supplied *cam*.

    Returns True on success.
    """
    assert isinstance(cam, mmapi.Camera)
    assert isinstance(prefix_name, pycompat.TEXT_TYPE)
    assert output_dir and os.path.isdir(output_dir)
    file_name = prefix_name + '_camera.mmcamera'
    file_path = os.path.join(output_dir, file_name)
    return load_solved_camera_from_file(cam, file_path)


def load_nuke_lens_file():
    # type: () -> None
    # TODO: Read nuke lens file.
    raise NotImplementedError


def load_residuals_file(mkr_list, file_path):
    # type: (...) -> bool
    """Apply per-frame deviation values from a .mmresiduals file to markers.

    Returns True on success, False on failure.
    """
    assert isinstance(mkr_list, list)
    assert isinstance(file_path, pycompat.TEXT_TYPE)

    if not os.path.isfile(file_path):
        LOG.error('Residuals file not found: %r', file_path)
        return False

    with open(file_path, 'r') as fh:
        doc = json.load(fh)

    assert isinstance(doc, dict)
    version = doc.get('version')
    if version != 1:
        LOG.error('Unsupported residuals version %r in: %r', version, file_path)
        return False
    assert version == 1

    data = doc.get('data', {})
    assert isinstance(data, dict)
    marker_names = data.get('marker_names', [])
    per_frame = data.get('per_frame_per_marker', [])
    assert isinstance(marker_names, list)
    assert isinstance(per_frame, list)

    if not marker_names or not per_frame:
        LOG.error('No marker data in residuals file: %r', file_path)
        return False

    name_to_mkr = {}
    for mkr in mkr_list:
        assert isinstance(mkr, mmapi.Marker)
        mkr_node = mkr.get_node()
        if mkr_node is None:
            continue
        mkr_name = mkr_node.split('|')[-1]
        name_to_mkr[mkr_name] = mkr

    # Every marker name in the file must have a corresponding Marker
    # in the scene. The file is produced by the solver from the same
    # markers we passed in, so a mismatch indicates a pipeline error.
    for name in marker_names:
        assert isinstance(name, pycompat.TEXT_TYPE)
        if name not in name_to_mkr:
            LOG.error(
                'Marker %r from residuals file not found in scene.'
                ' file marker_names=%r, scene marker names=%r',
                name,
                marker_names,
                list(name_to_mkr.keys()),
            )
            return False

    # Collect per-marker frame/error lists. After this loop each
    # marker has exactly len(per_frame) entries.
    marker_count = len(marker_names)
    frame_lists = [[] for _ in range(marker_count)]
    dev_lists = [[] for _ in range(marker_count)]

    for frame_entry in per_frame:
        assert isinstance(frame_entry, dict)
        frame = frame_entry.get('frame')
        assert isinstance(frame, (int, float))
        errors = frame_entry.get('errors', [])
        assert isinstance(errors, list)
        # The solver writes exactly one error per marker per frame.
        assert len(errors) == marker_count
        for i, error in enumerate(errors):
            frame_lists[i].append(frame)
            if error is None:
                error = 0.0
            assert isinstance(error, (int, float))
            dev_lists[i].append(error)

    for i, name in enumerate(marker_names):
        mkr = name_to_mkr[name]
        assert isinstance(mkr, mmapi.Marker)
        frames = frame_lists[i]
        devs = dev_lists[i]
        assert len(frames) == len(devs)

        mkr.set_deviation(frames, devs)
        avg_dev = mmapi.calculate_average_deviation(devs)
        assert isinstance(avg_dev, float)
        mkr.set_average_deviation(avg_dev)
        max_dev, max_frm = mmapi.calculate_maximum_deviation(frames, devs)
        assert isinstance(max_dev, float)
        mkr.set_maximum_deviation(max_dev, max_frm)

    LOG.debug('Applied residuals for %d markers from %r', marker_count, file_path)
    return True


def load_residuals_outputs(mkr_list, prefix_name, output_dir):
    # type: (...) -> bool
    """Load residuals from the output directory into Maya markers.

    Returns True on success.
    """
    assert isinstance(mkr_list, list)
    assert isinstance(prefix_name, pycompat.TEXT_TYPE)
    assert output_dir and os.path.isdir(output_dir)
    file_name = prefix_name + '_residuals.mmresiduals'
    file_path = os.path.join(output_dir, file_name)
    return load_residuals_file(mkr_list, file_path)


def load_solved_bundles_from_file(mkr_list, file_path):
    # type: (...) -> bool
    """Apply solved bundle positions from a .mmbundles file to Maya bundles.

    Matches each entry in the file by name to a marker in *mkr_list*,
    then sets translateX/Y/Z on the linked bundle.

    Returns True on success, False if the file could not be loaded.
    """
    assert isinstance(mkr_list, list)
    assert isinstance(file_path, pycompat.TEXT_TYPE)

    if not os.path.isfile(file_path):
        LOG.error('Solved bundle file not found: %r', file_path)
        return False

    with open(file_path, 'r') as fh:
        lines = fh.read().splitlines()

    if not lines:
        LOG.error('Bundle file is empty: %r', file_path)
        return False

    try:
        count = int(lines[0].strip())
    except ValueError:
        LOG.error('Invalid bundle count in: %r', file_path)
        return False

    # Build name -> bundle node map from the marker list.
    name_to_bnd_node = {}
    for mkr in mkr_list:
        mkr_node = mkr.get_node()
        if mkr_node is None:
            continue
        mkr_name = mkr_node.split('|')[-1]
        bnd = mkr.get_bundle()
        if bnd is None:
            continue
        bnd_node = bnd.get_node()
        if bnd_node is None:
            continue
        name_to_bnd_node[mkr_name] = bnd_node

    line_idx = 1
    applied = 0
    for _ in range(count):
        if line_idx + 1 >= len(lines):
            break
        name = lines[line_idx]
        pos_line = lines[line_idx + 1]
        line_idx += 2

        bnd_node = name_to_bnd_node.get(name)
        if bnd_node is None:
            LOG.warning('No bundle found for marker name %r, skipping.', name)
            continue

        parts = pos_line.split()
        if len(parts) < 3:
            LOG.warning('Invalid position line for %r: %r', name, pos_line)
            continue

        x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
        maya.cmds.setAttr(bnd_node + '.translateX', x)
        maya.cmds.setAttr(bnd_node + '.translateY', y)
        maya.cmds.setAttr(bnd_node + '.translateZ', z)
        applied += 1

    LOG.debug('Applied %d bundle positions from %r', applied, file_path)
    return True


def load_bundle_outputs(mkr_list, prefix_name, output_dir):
    # type: (...) -> bool
    """Load the solved bundle positions from the output directory into Maya.

    The solver writes ``{prefix_name}_bundles.mmbundles`` to *output_dir*.

    Returns True on success.
    """
    assert isinstance(mkr_list, list)
    assert isinstance(prefix_name, pycompat.TEXT_TYPE)
    assert output_dir and os.path.isdir(output_dir)
    file_name = prefix_name + '_bundles.mmbundles'
    file_path = os.path.join(output_dir, file_name)
    return load_solved_bundles_from_file(mkr_list, file_path)
