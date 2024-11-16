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
Generic data smoothing.

This module is software agnostic and should not rely on any thirdparty
software, however if numpy is available, an numpy-accelerated
code-path will be used.

Smoothing functions supported:

- Average
- Gaussian (blur smoothing)
- Fourier (frequency smoothing)

Example usage::

  import mmSolver.utils.smooth as smooth
  import mmSolver.utils.constant as const
  data = [1.0, 0.0, 2.0, 0.0, 20000.0]
  width = 2.0
  new_data = smooth.smooth(const.SMOOTH_TYPE_AVERAGE, data, width)

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math

import mmSolver.utils.python_compat as pycompat

# FFT module
if pycompat.IS_PYTHON_2:
    import mmSolver.utils._fft_py2 as fft
else:
    import mmSolver.utils._fft_py3 as fft

import mmSolver.utils.constant as const

# NumPy
try:
    import numpy as np
except ImportError:
    np = None


# Optimal 'range' function for Python 2
if pycompat.IS_PYTHON_2:
    range = xrange  # noqa: F821


def smooth(smooth_type, value_array, width):
    """
    Run a Smoothing function, of any type, just pass a 'smooth type' in.

    :param smooth_type: Type of smoothing operation.
    :type smooth_type: SMOOTH_TYPE_*

    :param value_array: Input data to smooth.
    :type value_array: [float, ..]

    :param width: The width to smooth over. Values above 1.0 will
                  perform smoothing. 1.0 or below has no effect.
    :type width: float

    :returns: Smoothed copy of 'value_array', using the 'smooth_type', given.
    :rtype: [float, ..]
    """
    new_array = None
    if smooth_type == const.SMOOTH_TYPE_AVERAGE:
        new_array = average_smooth(value_array, width)
    elif smooth_type == const.SMOOTH_TYPE_GAUSSIAN:
        new_array = gaussian_smooth(value_array, width)
    elif smooth_type == const.SMOOTH_TYPE_FOURIER:
        new_array = fourier_smooth(value_array, width)
    else:
        msg = 'smoothType argument is invalid, ' 'must be SMOOTH_TYPE_* attribute'
        raise ValueError(msg)
    return new_array


def average_smooth(value_array, width):
    """
    Average Smooth Function

    .. note::

        Uses standard python functions only.

    :param value_array: Input data to smooth.
    :type value_array: [float, ..]

    :param width: The width to smooth over. Values above 1.0 will
                  perform smoothing. 1.0 or below has no effect.
    :type width: float

    :returns: Smoothed copy of 'value_array'.
    :rtype: [float, ..]
    """
    sigma_val = width - 1.0
    if sigma_val <= 0.0:
        return value_array

    # Smooth Function
    value_num = len(value_array)
    sum_avg = 0.0
    new_array = [0.0] * value_num
    weights = [1.0] * value_num
    for i in range(value_num):

        # Get Average
        start = int(i - sigma_val)
        end = int(i + sigma_val) + 1
        if start < 0:
            start = 0
        if end >= value_num:
            end = value_num
        for j in range(start, end):
            sum_avg = sum_avg + value_array[j]
        sum_avg = sum_avg / (end - start)

        for k in range(value_num):
            new_array[i] = (sum_avg * weights[i]) + (
                value_array[i] * (1.0 - weights[i])
            )
        sum_avg = 0

    assert len(value_array) == len(new_array)
    return new_array


def _gaussian(sigma, x, mean):
    """
    Gaussian Distribution Function

    :param sigma: Sigma value (the width)
    :type sigma: float

    :param x: input value
    :type x: float

    :param mean: Mean value
    :type mean: float

    :rtype: float
    """
    return math.exp(-(math.pow((x - mean), 2) / (2 * (math.pow(sigma, 2)))))


def gaussian_smooth(value_array, width):
    """
    Gaussian Smooth Function.

    .. note::

        Uses standard python functions only.

    :param value_array: Input data to smooth.
    :type value_array: [float, ..]

    :param width: The width to smooth over. Values above 1.0 will perform
                  smoothing. 1.0 or below has no effect.
    :type width: float

    :returns: Smoothed copy of 'value_array'.
    :rtype: [float, ..]
    """
    sigma_val = (width - 1.0) * 0.5
    if sigma_val <= 0.0:
        return value_array

    value_num = len(value_array)

    # Smooth Function
    sum_gaussian = 0.0
    tmp_gaussian = [None] * value_num
    new_array = [0.0] * value_num
    for i in range(value_num):

        for j in range(value_num):
            tmp_gaussian[j] = _gaussian(sigma_val, i, j)
            sum_gaussian = sum_gaussian + tmp_gaussian[j]
        for k in range(value_num):
            new_array[i] = new_array[i] + (
                value_array[k] * (tmp_gaussian[k] / sum_gaussian)
            )

        sum_gaussian = 0

    assert len(value_array) == len(new_array)
    return new_array


def _generate_window_raw(n, filtr=None):
    """
    Create a "window" array used for convolving.

    Uses standard python functions only.

    :param n: Number of 'frames' to smooth by.
    :type n: int

    :param filtr: Type of frequency-space smoothing filter, 'gaussian',
                  'triangle' or 'box'. Default filter is 'gaussian'.
    :type filtr: str

    :returns: A [float, ..] numbers, list is length 'n'.
    """
    if filtr is None:
        filtr = 'gaussian'

    mean = 1.0
    std = float(n - 1) / 2.0
    window = [0] * n

    if filtr == 'gaussian':
        for i in range(n):
            window[i] = _gaussian(mean, i, std)

    elif filtr == 'triangle':
        half_n = (n - 1) // 2
        # Middle index number
        window[half_n] = n

        # First half of window
        for i in range(half_n):
            window[i] = half_n - i

        # Second (rear) half of window.
        # We must reverse the index
        for i in range(half_n):
            index = n - i - 1
            window[index] = half_n - i

    elif filtr == 'box':
        for i in range(n):
            window[i] = 1

    else:
        msg = 'filtr argument is incorrect: {0}'
        raise ValueError(msg.format(repr(filtr)))

    window_sum = sum(window)
    if window_sum > 0.0:
        window_sum = 1.0 / window_sum
    for i in range(n):
        window[i] *= window_sum
    return window


def _fft_convolve_raw(signal, window):
    """
    Perform convolution.

    Uses standard python functions only.

    :param signal: The input signal to be convolved
    :type signal: [float, ..]

    :param window: The window to be multiplied over each value in 'signal'.
    :type window: [float, ..]

    :returns: Modified copy of 'signal'.
    """
    m = len(signal)
    n = len(window)
    length = max(m, n) - min(m, n) + 1  # 'valid' mode

    # zero pad the window
    tmp = [0.0] * len(signal)
    tmp[: len(window)] = window
    window = tmp

    r = fft.convolve(signal, window)  # , realoutput=True
    r = r[(min(m, n) - 1) :]
    return r


def _fourier_smooth_raw(data, width, filtr=None):
    """
    Fourier smoothing.

    Uses standard python functions only.

    :param data: Input data to smooth.
    :type data: [float, ..]

    :param width: The width to smooth over. Values above 1.0 will perform
                  smoothing. 1.0 or below has no effect.
    :type width: float

    :param filtr: Type of frequency-space smoothing filter, 'gaussian',
                  'triangle' or 'box'. Default filter is 'gaussian'.
    :type filtr: str

    :returns: Smoothed copy of 'data'.
    """
    sigma_val = (width - 1.0) * 0.5
    if sigma_val <= 0.0:
        return data

    # Value must always be odd number.
    # 1 = 0
    # 2 = 3
    # 3 = 5
    n = ((int(width) - 1) * 2) + 1  # number of 'frames' to smooth by.

    # Convert to frequency space.
    x = fft.transform(data, inverse=False)
    assert len(x) == len(data)

    # Generate Smoothing Window
    window = _generate_window_raw(n, filtr=filtr)

    # Custom Convolve ('valid')
    s = data[n - 1 : 0 : -1]
    s += data
    s += data[-2 : -n - 1 : -1]
    x = _fft_convolve_raw(s, window)
    if n % 2 == 1:
        # n is odd
        x = x[n // 2 : -(n // 2)]
    else:
        # n is even
        x = x[(n // 2) - 1 : -(n // 2)]

    assert len(x) == len(data)
    return x


def _generate_window_numpy(n, filtr=None):
    """
    Create a "window" array used for convolving.

    Uses the numpy module.

    :param n: Number of 'frames' to smooth by.
    :type n: int

    :param filtr: Type of frequency-space smoothing filter, 'gaussian',
                  'triangle' or 'box'. Default filter is 'gaussian'.
    :type filtr: str

    :returns: Numpy array of length 'n'.
    """
    assert np is not None
    if filtr is None:
        filtr = 'gaussian'

    mean = 1.0
    std = float(n - 1) / 2.0
    window = np.zeros(n)

    if filtr == 'gaussian':
        for i in range(n):
            window[i] = _gaussian(mean, i, std)

    elif filtr == 'triangle':
        half_n = (n - 1) // 2
        # Middle index number
        window[half_n] = n

        # First half of window
        for i in range(half_n):
            window[i] = half_n - i

        # Second (rear) half of window.
        # We must reverse the index
        for i in range(half_n):
            index = n - i - 1
            window[index] = half_n - i

    elif filtr == 'box':
        for i in range(n):
            window[i] = 1

    window /= window.sum()
    return window


def _fourier_smooth_numpy(data, width, filtr=None):
    """
    Fourier smooth function.

    Uses the numpy module.

    :param data: Input data to smooth.
    :type data: [float, ..]

    :param width: The width to smooth over. Values above 1.0 will perform
                  smoothing. 1.0 or below has no effect.
    :type width: float

    :param filtr: Type of frequency-space smoothing filter, 'gaussian',
                  'triangle' or 'box'. Default filter is 'gaussian'.
    :type filtr: str

    :returns: Smoothed copy of 'data'.
    """
    assert np is not None

    sigma_val = (width - 1.0) * 0.5
    if sigma_val <= 0.0:
        return data

    # Value must always be odd number.
    # 1 = 0
    # 2 = 3
    # 3 = 5
    n = ((int(width) - 1) * 2) + 1  # number of 'frames' to smooth by.

    # Convert to frequency space.
    data = np.array(data)
    x = np.fft.fft(data)
    assert len(x) == len(data)

    # Generate Smoothing Window
    window = _generate_window_numpy(n, filtr=filtr)

    # NumPy Convolve (with 'valid' mode)
    s = np.r_[data[n - 1 : 0 : -1], data, data[-2 : -n - 1 : -1]]
    x = np.convolve(s, window, mode='valid')
    if n % 2 == 1:
        # n is odd
        x = x[n // 2 : -(n // 2)]
    else:
        # n is even
        x = x[(n // 2) - 1 : -(n // 2)]

    assert len(x) == len(data)
    return x


def fourier_smooth(value_array, width, filtr=None):
    """
    Fourier Smooth Function.

    :param value_array: Input data to smooth.
    :type value_array: [float, ..]

    :param width: The width to smooth over. Values above 1.0 will perform
                  smoothing. 1.0 or below has no effect.
    :type width: float

    :param filtr: Type of frequency-space smoothing filter, 'gaussian',
                  'triangle' or 'box'. Default filter is 'gaussian'.
    :type filtr: str

    :returns: Smoothed copy of 'value_array'.
    """
    if np is not None:
        return _fourier_smooth_numpy(value_array, width, filtr=filtr)
    else:
        return _fourier_smooth_raw(value_array, width, filtr=filtr)


############################################################################
# Split out complex numbers into frequency, phase and amplitude.
# These functions are used for visualising and debug.
#
# Article:
# https://betterexplained.com/articles/an-interactive-guide-to-the-fourier-transform/
#
# Code:
# https://gist.github.com/kazad/8bb682da198db597558c
#
def __convert_into_cycles_from_signal(data):
    """
    Decompose complex numbers into frequency, phase, amplitude; stored as dict.
    """
    result = []
    for i, d in enumerate(data):
        phase = 0.0
        if d.imag != 0 and d.real != 0:
            phase = math.atan(d.imag / d.real)
        x = {
            'freq': i,
            'phase': math.degrees(phase),
            'amp': abs(d) / len(data),
        }
        result.append(x)
    return result


def __convert_into_cycle_strs_from_signal(data):
    """
    Decompose complex numbers into frequency, phase, amplitude; stored as str.
    """
    cycles = __convert_into_cycles_from_signal(data)
    result = []
    for cycle in cycles:
        x = '{amp:.3g}:{phase:.4g}'.format(**cycle)
        result.append(x)
    return result
