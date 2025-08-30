"""This file is intended to be run in the Maya Script Editor, with the
'example_camera_curves_01.ma' Maya Scene open.
"""

import os
import maya.cmds


def _sample_attr(start_frame, end_frame, node_attr):
    data = []
    for f in range(start_frame, end_frame + 1):
        v = maya.cmds.getAttr(node_attr, time=f)
        data.append((f, v))
    return data


def _write_data(name, data, output_directory):
    output_dir = os.path.expanduser(output_directory)
    file_path = os.path.join(output_dir, name + '.chan')
    print('file_path:', file_path)
    with open(file_path, 'w') as f:
        for sample in data:
            frame, value = sample
            line = '{} {}\n'.format(frame, value)
            f.write(line)
    return


def _set_sample_attr(node_attr, data):
    for f, v in data:
        maya.cmds.setKeyframe(node_attr, value=v, time=f)
    return


output_directory = (
    '~/dev/mayaMatchMoveSolver/lib/rust/mmscenegraph/tests/data'
)

start_frame = 0
end_frame = 94

raw_data_translateX = _sample_attr(start_frame, end_frame, 'camera.translateX')
raw_data_translateY = _sample_attr(start_frame, end_frame, 'camera.translateY')
raw_data_translateZ = _sample_attr(start_frame, end_frame, 'camera.translateZ')

raw_data_rotateX = _sample_attr(start_frame, end_frame, 'camera.rotateX')
raw_data_rotateY = _sample_attr(start_frame, end_frame, 'camera.rotateY')
raw_data_rotateZ = _sample_attr(start_frame, end_frame, 'camera.rotateZ')

raw_data_focalLength = _sample_attr(start_frame, end_frame, 'cameraShape.focalLength')

_write_data('camera_curve_01_translateX_raw', raw_data_translateX, output_directory)
_write_data('camera_curve_01_translateY_raw', raw_data_translateY, output_directory)
_write_data('camera_curve_01_translateZ_raw', raw_data_translateZ, output_directory)

_write_data('camera_curve_01_rotateX_raw', raw_data_rotateX, output_directory)
_write_data('camera_curve_01_rotateY_raw', raw_data_rotateY, output_directory)
_write_data('camera_curve_01_rotateZ_raw', raw_data_rotateZ, output_directory)

_write_data('camera_curve_01_focalLength_raw', raw_data_focalLength, output_directory)
