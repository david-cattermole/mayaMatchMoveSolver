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
Functions for saving camera solver input data to files.
"""

import json
import os

import maya.cmds

import mmSolver.api as mmapi
import mmSolver.utils.time as time_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.tools.savemarkerfile.lib as savemarkerfile_lib
import mmSolver.tools.savelensfile.lib as savelensfile_lib

import mmSolver.tools.camerasolver.constant as const

from mmSolver.tools.camerasolver.lib.types import AdjustmentSolver, AdjustmentAttributes

# Maya stores film aperture in inches; camera solver expects mm.
INCHES_TO_MM = 25.4


def construct_output_file_path(output_dir, file_prefix, file_suffix, file_ext):
    # type: (...) -> str
    assert isinstance(output_dir, pycompat.TEXT_TYPE)
    assert isinstance(file_prefix, pycompat.TEXT_TYPE)
    assert isinstance(file_suffix, pycompat.TEXT_TYPE)
    assert isinstance(file_ext, pycompat.TEXT_TYPE)
    file_name = file_prefix + file_suffix + file_ext
    return os.path.join(output_dir, file_name)


def save_markers_to_file(mkr_list, frame_range, file_prefix, output_dir):
    # type: (...) -> str
    assert isinstance(mkr_list, list)
    assert isinstance(frame_range, time_utils.FrameRange)
    assert isinstance(file_prefix, pycompat.TEXT_TYPE)
    assert isinstance(output_dir, pycompat.TEXT_TYPE)
    data = savemarkerfile_lib.generate(mkr_list, frame_range)
    file_suffix = ''
    file_path = construct_output_file_path(output_dir, file_prefix, file_suffix, '.uv')
    savemarkerfile_lib.write_file(file_path, data)
    return file_path


def _query_sample_attr_over_frames(node, attr_name, frames):
    # type: (...) -> list[list]
    assert isinstance(node, pycompat.TEXT_TYPE)
    assert isinstance(attr_name, pycompat.TEXT_TYPE)
    assert isinstance(frames, list)
    result = []
    for frame in frames:
        value = maya.cmds.getAttr(node + '.' + attr_name, time=frame)
        result.append([frame, value])
    return result


def save_camera_to_file(cam, frame_range, file_prefix, output_dir):
    # type: (...) -> str
    assert isinstance(cam, mmapi.Camera)
    assert isinstance(frame_range, time_utils.FrameRange)
    file_suffix = ''
    file_path = construct_output_file_path(
        output_dir, file_prefix, file_suffix, '.mmcamera'
    )

    cam_tfm = cam.get_transform_node()
    cam_shp = cam.get_shape_node()
    assert cam_tfm is not None
    assert cam_shp is not None

    frames = list(range(frame_range.start, frame_range.end + 1))

    def _sample_mm(node, attr):
        raw = _query_sample_attr_over_frames(node, attr, frames)
        return [[f, v * INCHES_TO_MM] for f, v in raw]

    attr_data = {
        'translateX': _query_sample_attr_over_frames(cam_tfm, 'translateX', frames),
        'translateY': _query_sample_attr_over_frames(cam_tfm, 'translateY', frames),
        'translateZ': _query_sample_attr_over_frames(cam_tfm, 'translateZ', frames),
        'rotateX': _query_sample_attr_over_frames(cam_tfm, 'rotateX', frames),
        'rotateY': _query_sample_attr_over_frames(cam_tfm, 'rotateY', frames),
        'rotateZ': _query_sample_attr_over_frames(cam_tfm, 'rotateZ', frames),
        'focalLength': _query_sample_attr_over_frames(cam_shp, 'focalLength', frames),
        'filmBackWidth': _sample_mm(cam_shp, 'horizontalFilmAperture'),
        'filmBackHeight': _sample_mm(cam_shp, 'verticalFilmAperture'),
        'filmBackOffsetX': _sample_mm(cam_shp, 'horizontalFilmOffset'),
        'filmBackOffsetY': _sample_mm(cam_shp, 'verticalFilmOffset'),
    }

    image_width, image_height = cam.get_plate_resolution()
    pixel_aspect = None

    cam_name = cam_tfm.split('|')[-1]

    doc = {
        'version': 1,
        'data': {
            'name': cam_name,
            'start_frame': frame_range.start,
            'end_frame': frame_range.end,
            'image': {
                'width': image_width,
                'height': image_height,
                'pixel_aspect_ratio': pixel_aspect,
                'file_path': None,
            },
            'attr': attr_data,
        },
    }

    with open(file_path, 'w') as fh:
        json.dump(doc, fh)
    return file_path


def save_nuke_lens_to_file(cam, lens, frame_range, file_prefix, output_dir):
    # type: (...) -> str
    assert isinstance(cam, mmapi.Camera)
    assert isinstance(lens, mmapi.Lens)
    assert isinstance(frame_range, time_utils.FrameRange)
    assert isinstance(file_prefix, pycompat.TEXT_TYPE)
    assert isinstance(output_dir, pycompat.TEXT_TYPE)
    file_suffix = ''
    data_list = [savelensfile_lib.generate(cam, lens, frame_range)]
    file_path = construct_output_file_path(output_dir, file_prefix, file_suffix, '.nk')
    savelensfile_lib.write_nuke_file(file_path, data_list)
    return file_path


def save_solver_settings_to_file(
    frame_range,
    adjustment_solver,
    adjustment_attrs,
    file_prefix,
    output_dir,
):
    # type: (...) -> str
    assert isinstance(frame_range, time_utils.FrameRange)
    assert isinstance(adjustment_solver, AdjustmentSolver)
    assert isinstance(adjustment_attrs, AdjustmentAttributes)
    assert isinstance(file_prefix, pycompat.TEXT_TYPE)
    assert isinstance(output_dir, pycompat.TEXT_TYPE)

    file_suffix = ''
    file_path = construct_output_file_path(
        output_dir, file_prefix, file_suffix, '.mmsettings'
    )

    solver_type_map = {
        const.ADJUSTMENT_SOLVER_TYPE_EVOLUTION_REFINE: 'evolution_refine',
        const.ADJUSTMENT_SOLVER_TYPE_EVOLUTION_UNKNOWN: 'evolution_unknown',
        const.ADJUSTMENT_SOLVER_TYPE_UNIFORM_GRID: 'uniform_grid',
    }
    adj_type = adjustment_solver.get_adjustment_solver_type()
    adj_type_str = None
    if adj_type is not None:
        adj_type_str = solver_type_map.get(adj_type)

    adj_solver_data = None
    if adj_type_str is not None:
        thread_count = adjustment_solver.get_thread_count()
        value_range_estimate = adjustment_solver.get_evolution_value_range_estimate()
        if value_range_estimate is None:
            value_range_estimate = True

        gen_count = adjustment_solver.get_evolution_generation_count()
        pop_count = adjustment_solver.get_evolution_population_count()
        adj_solver_data = {
            'type': adj_type_str,
            'thread_count': thread_count,
            'evolution_value_range_estimate': value_range_estimate,
            'evolution_generation_count': gen_count,
            'evolution_population_count': pop_count,
        }

    attr_list = []
    for attr_name in adjustment_attrs.get_attribute_names():
        bounds = adjustment_attrs.get_attribute_bounds(attr_name)
        sample_count = adjustment_attrs.get_attribute_sample_count(attr_name)
        if bounds:
            value_min = bounds[0]
            value_max = bounds[1]
        else:
            value_min = 0.0
            value_max = 200.0
        entry = {
            'name': attr_name,
            'value_min': value_min,
            'value_max': value_max,
            'sample_count': sample_count,
        }
        attr_list.append(entry)

    data_section = {
        'origin_frame': frame_range.start,
        'frames': {
            'start_frame': frame_range.start,
            'end_frame': frame_range.end,
        },
        'adjustment_attributes': attr_list,
    }
    if adj_solver_data is not None:
        data_section['adjustment_solver'] = adj_solver_data

    doc = {'version': 1, 'data': data_section}

    with open(file_path, 'w') as fh:
        json.dump(doc, fh, indent=4)
    return file_path
