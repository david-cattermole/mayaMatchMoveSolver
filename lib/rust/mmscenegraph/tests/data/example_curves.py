"""This file is intended to be run in the Maya Script Editor, with
the 'example_curves.ma' Maya Scene open.
"""

import os
import random

import maya.cmds


def _sample_attr(start_frame, end_frame, node_attr):
    data = []
    for f in range(start_frame, end_frame + 1):
        v = maya.cmds.getAttr(node_attr, time=f)
        data.append((f, v))
    return data


def _write_data(name, data, output_directory):
    output_dir = os.path.expandvars(output_directory)
    file_path = os.path.join(output_dir, name + '.chan')
    with open(file_path, 'w') as f:
        for sample in data:
            frame, value = sample
            line = '{} {}\n'.format(frame, value)
            f.write(line)
    return


def _generate_variance_data(raw_data, variance):
    data = [(f, (random.uniform(v - variance, v + variance))) for f, v in raw_data]
    assert len(raw_data) == len(data)
    return data


def _generate_spike_data(raw_data, variance, spike_probability):
    data = []
    temp_data = [(f, random.uniform(v - variance, v + variance)) for f, v in raw_data]
    for (raw_f, raw_v), (spike_f, spike_v) in zip(raw_data, temp_data):
        if random.random() < spike_probability:
            data.append((spike_f, spike_v))
        else:
            data.append((raw_f, raw_v))
    assert len(raw_data) == len(data)
    return data


output_directory = (
    '${USERPROFILE}/dev/mayaMatchMoveSolver/lib/rust/mmscenegraph/tests/data'
)

start_frame = 1001
end_frame = 1101

variance_low = 0.01
variance_medium = 0.1
variance_high = 1.0
variance_very_high = 10.0

spike_probability_low = 0.01
spike_probability_medium = 0.1
spike_probability_high = 0.25

# Identity (all zero values)
raw_data = _sample_attr(start_frame, end_frame, 'identity.translateY')
_write_data('identity_raw', raw_data, output_directory)

variance = variance_low
data = _generate_variance_data(raw_data, variance)
_write_data('identity_variance1', data, output_directory)

variance = variance_medium
data = _generate_variance_data(raw_data, variance)
_write_data('identity_variance2', data, output_directory)

variance = variance_high
data = _generate_variance_data(raw_data, variance)
_write_data('identity_variance3', data, output_directory)

variance = variance_very_high
data = _generate_variance_data(raw_data, variance)
_write_data('identity_variance4', data, output_directory)

variance = variance_low
spike_probability = spike_probability_medium
data = _generate_spike_data(raw_data, variance, spike_probability)
_write_data('identity_spike1', data, output_directory)

variance = variance_medium
data = _generate_spike_data(raw_data, variance, spike_probability)
_write_data('identity_spike2', data, output_directory)

variance = variance_high
data = _generate_spike_data(raw_data, variance, spike_probability)
_write_data('identity_spike3', data, output_directory)

variance = variance_very_high
data = _generate_spike_data(raw_data, variance, spike_probability)
_write_data('identity_spike4', data, output_directory)


# Degrees 45 - Up
raw_data = _sample_attr(start_frame, end_frame, 'degree_45_up.translateY')
_write_data('degree_45_up_raw', raw_data, output_directory)

variance = variance_low
data = _generate_variance_data(raw_data, variance)
_write_data('degree_45_up_variance1', data, output_directory)

variance = variance_medium
data = _generate_variance_data(raw_data, variance)
_write_data('degree_45_up_variance2', data, output_directory)

variance = variance_high
data = _generate_variance_data(raw_data, variance)
_write_data('degree_45_up_variance3', data, output_directory)

variance = variance_very_high
data = _generate_variance_data(raw_data, variance)
_write_data('degree_45_up_variance4', data, output_directory)

variance = variance_low
spike_probability = spike_probability_medium
data = _generate_spike_data(raw_data, variance, spike_probability)
_write_data('degree_45_up_spike1', data, output_directory)

variance = variance_medium
data = _generate_spike_data(raw_data, variance, spike_probability)
_write_data('degree_45_up_spike2', data, output_directory)

variance = variance_high
data = _generate_spike_data(raw_data, variance, spike_probability)
_write_data('degree_45_up_spike3', data, output_directory)

variance = variance_very_high
data = _generate_spike_data(raw_data, variance, spike_probability)
_write_data('degree_45_up_spike4', data, output_directory)


# Degrees 45 - Down
raw_data = _sample_attr(start_frame, end_frame, 'degree_45_down.translateY')
_write_data('degree_45_down_raw', raw_data, output_directory)

variance = variance_low
data = _generate_variance_data(raw_data, variance)
_write_data('degree_45_down_variance1', data, output_directory)

variance = variance_medium
data = _generate_variance_data(raw_data, variance)
_write_data('degree_45_down_variance2', data, output_directory)

variance = variance_high
data = _generate_variance_data(raw_data, variance)
_write_data('degree_45_down_variance3', data, output_directory)

variance = variance_very_high
data = _generate_variance_data(raw_data, variance)
_write_data('degree_45_down_variance4', data, output_directory)


# Linear (2-point)
raw_data = _sample_attr(start_frame, end_frame, 'linear_2_point.translateY')
_write_data('linear_2_point_raw', raw_data, output_directory)

variance = variance_low
data = _generate_variance_data(raw_data, variance)
_write_data('linear_2_point_variance1', data, output_directory)

variance = variance_medium
data = _generate_variance_data(raw_data, variance)
_write_data('linear_2_point_variance2', data, output_directory)

variance = variance_high
data = _generate_variance_data(raw_data, variance)
_write_data('linear_2_point_variance3', data, output_directory)

variance = variance_very_high
data = _generate_variance_data(raw_data, variance)
_write_data('linear_2_point_variance4', data, output_directory)


# Linear (3-point)
raw_data = _sample_attr(start_frame, end_frame, 'linear_3_point.translateY')
_write_data('linear_3_point_raw', raw_data, output_directory)

variance = variance_low
data = _generate_variance_data(raw_data, variance)
_write_data('linear_3_point_variance1', data, output_directory)

variance = variance_medium
data = _generate_variance_data(raw_data, variance)
_write_data('linear_3_point_variance2', data, output_directory)

variance = variance_high
data = _generate_variance_data(raw_data, variance)
_write_data('linear_3_point_variance3', data, output_directory)

variance = variance_very_high
data = _generate_variance_data(raw_data, variance)
_write_data('linear_3_point_variance4', data, output_directory)

variance = variance_low
spike_probability = spike_probability_medium
data = _generate_spike_data(raw_data, variance, spike_probability)
_write_data('linear_3_point_spike1', data, output_directory)

variance = variance_medium
data = _generate_spike_data(raw_data, variance, spike_probability)
_write_data('linear_3_point_spike2', data, output_directory)

variance = variance_high
data = _generate_spike_data(raw_data, variance, spike_probability)
_write_data('linear_3_point_spike3', data, output_directory)

variance = variance_very_high
_generate_spike_data(raw_data, variance, spike_probability)
data = _write_data('linear_3_point_spike4', data, output_directory)


# Linear (4-point)
raw_data = _sample_attr(start_frame, end_frame, 'linear_4_point.translateY')
_write_data('linear_4_point_raw', raw_data, output_directory)

variance = variance_low
data = _generate_variance_data(raw_data, variance)
_write_data('linear_4_point_variance1', data, output_directory)

variance = variance_medium
data = _generate_variance_data(raw_data, variance)
_write_data('linear_4_point_variance2', data, output_directory)

variance = variance_high
data = _generate_variance_data(raw_data, variance)
_write_data('linear_4_point_variance3', data, output_directory)

variance = variance_very_high
data = _generate_variance_data(raw_data, variance)
_write_data('linear_4_point_variance4', data, output_directory)


# Up-Down-Up
raw_data = _sample_attr(start_frame, end_frame, 'up_down_up.translateY')
_write_data('up_down_up_raw', raw_data, output_directory)

variance = variance_low
data = _generate_variance_data(raw_data, variance)
_write_data('up_down_up_variance1', data, output_directory)

variance = variance_medium
data = _generate_variance_data(raw_data, variance)
_write_data('up_down_up_variance2', data, output_directory)

variance = variance_high
data = _generate_variance_data(raw_data, variance)
_write_data('up_down_up_variance3', data, output_directory)

variance = variance_very_high
data = _generate_variance_data(raw_data, variance)
_write_data('up_down_up_variance4', data, output_directory)


# Down-Up-Down
raw_data = _sample_attr(start_frame, end_frame, 'down_up_down.translateY')
_write_data('down_up_down_raw', raw_data, output_directory)

variance = variance_low
data = _generate_variance_data(raw_data, variance)
_write_data('down_up_down_variance1', data, output_directory)

variance = variance_medium
data = _generate_variance_data(raw_data, variance)
_write_data('down_up_down_variance2', data, output_directory)

variance = variance_high
data = _generate_variance_data(raw_data, variance)
_write_data('down_up_down_variance3', data, output_directory)

variance = variance_very_high
data = _generate_variance_data(raw_data, variance)
_write_data('down_up_down_variance4', data, output_directory)


# Bounce 5 - Up-Down
raw_data = _sample_attr(start_frame, end_frame, 'bounce_5_up_down.translateY')
_write_data('bounce_5_up_down_raw', raw_data, output_directory)

variance = variance_low
data = _generate_variance_data(raw_data, variance)
_write_data('bounce_5_up_down_variance1', data, output_directory)

variance = variance_medium
data = _generate_variance_data(raw_data, variance)
_write_data('bounce_5_up_down_variance2', data, output_directory)

variance = variance_high
data = _generate_variance_data(raw_data, variance)
_write_data('bounce_5_up_down_variance3', data, output_directory)

variance = variance_very_high
data = _generate_variance_data(raw_data, variance)
_write_data('bounce_5_up_down_variance4', data, output_directory)

variance = variance_low
spike_probability = spike_probability_medium
data = _generate_spike_data(raw_data, variance, spike_probability)
_write_data('bounce_5_up_down_spike1', data, output_directory)

variance = variance_medium
data = _generate_spike_data(raw_data, variance, spike_probability)
_write_data('bounce_5_up_down_spike2', data, output_directory)

variance = variance_high
data = _generate_spike_data(raw_data, variance, spike_probability)
_write_data('bounce_5_up_down_spike3', data, output_directory)

variance = variance_very_high
data = _generate_spike_data(raw_data, variance, spike_probability)
_write_data('bounce_5_up_down_spike4', data, output_directory)
