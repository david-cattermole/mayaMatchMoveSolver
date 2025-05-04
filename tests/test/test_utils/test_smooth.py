# Copyright (C) 2018, 2019 David Cattermole.
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
Test functions for API utils module.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import test.test_utils.utilsutils as test_utils
import mmSolver.utils.smooth as smooth_utils


# Some random numbers.
DATA_ONE = [
    0.2540983642613156,
    0.7831634753872109,
    0.002591692790079203,
    0.41595045018499655,
    0.6360617637325738,
    0.11174422210135437,
    0.19632980357666963,
    0.433340268169374,
    0.07028804556375579,
    0.24322363800544966,
]

# A single spike (length 5 - odd)
DATA_TWO = [
    0.0,
    0.0,
    1.0,
    0.0,
    0.0,
]

# A single spike (length 8 - even).
DATA_THREE = [
    0.0,
    0.0,
    0.0,
    1.0,
    1.0,
    0.0,
    0.0,
    0.0,
]


# Some random numbers, same as DATA_ONE, but negative numbers.
DATA_FOUR = [
    -0.2540983642613156,
    -0.7831634753872109,
    -0.002591692790079203,
    -0.41595045018499655,
    -0.6360617637325738,
    -0.11174422210135437,
    -0.19632980357666963,
    -0.433340268169374,
    -0.07028804556375579,
    -0.24322363800544966,
]


# @unittest.skip
class TestSmooth(test_utils.UtilsTestCase):
    """
    Test smooth module.
    """

    def test_average_smooth_one(self):
        """
        Test the average smoothing function.
        """
        # No change should happen with a 'width' of 1.0.
        data = list(DATA_ONE)
        x = smooth_utils.average_smooth(data, 1.0)
        self.assertEqual(data, x)

        # Smooth by two frames.
        data = list(DATA_ONE)
        x = smooth_utils.average_smooth(data, 2.0)
        self.assertNotEqual(data, x)

        # Averaging by the size of the data should average all the data into
        # a single flat line.
        data = list(DATA_ONE)
        size = len(data)
        x = smooth_utils.average_smooth(data, float(size))
        x1 = x[0]
        for i in x:
            self.assertEqual(i, x1)
        return

    def test_gaussian_smooth_one(self):
        """
        Test the gaussian smoothing function.
        """
        # No change should happen with a 'width' of 1.0.
        data = list(DATA_ONE)
        x = smooth_utils.gaussian_smooth(data, 1.0)
        assert data == x

        # Smooth by two frames.
        data = list(DATA_ONE)
        x = smooth_utils.gaussian_smooth(data, 2.0)
        self.assertNotEqual(data, x)
        return

    def test_fourier_smooth_one(self):
        """
        Test the fourier smoothing function, with data one input.

        .. todo::

            Test with and without Numpy in the same interpreter
              session; We must get the exact same result!

        """
        # No change should happen with a 'width' of 1.0.
        data = list(DATA_ONE)
        x = smooth_utils.fourier_smooth(data, 1.0)
        self.assertEqual(data, x)

        # Smooth by two frames.
        data = list(DATA_ONE)
        x = smooth_utils.fourier_smooth(data, 2.0)
        same_value = True
        for i, v in enumerate(x):
            if data[i] != v:
                same_value = False
                break
        self.assertIs(same_value, False)
        return

    def test_fourier_smooth_two(self):
        """
        Test the fourier smoothing function, with data input two
        """
        # No change should happen with a 'width' of 1.0.
        data = list(DATA_TWO)
        x = smooth_utils.fourier_smooth(data, 1.0, filtr='box')
        self.assertEqual(data, x)

        data = list(DATA_TWO)
        x = smooth_utils.fourier_smooth(data, 1.0, filtr='triangle')
        self.assertEqual(data, x)

        data = list(DATA_TWO)
        x = smooth_utils.fourier_smooth(data, 1.0, filtr='fourier')
        self.assertEqual(data, x)

        # Smooth by two frames.
        data = list(DATA_TWO)
        x = smooth_utils.fourier_smooth(data, 2.0, filtr='box')
        data = [
            0.0,
            0.3333333333333333,
            0.3333333333333333,
            0.3333333333333333,
            0.0,
        ]
        for a, b in zip(list(x), data):
            self.assertAlmostEqual(a, b)

        data = list(DATA_TWO)
        x = smooth_utils.fourier_smooth(data, 2.0, filtr='triangle')
        data = [
            0.0,
            0.2,
            0.6,
            0.2,
            0.0,
        ]
        for a, b in zip(list(x), data):
            self.assertAlmostEqual(a, b)

        data = list(DATA_TWO)
        x = smooth_utils.fourier_smooth(data, 2.0, filtr='gaussian')
        data = [
            0.0,
            0.27406862,
            0.45186276,
            0.27406862,
            0.0,
        ]
        for a, b in zip(list(x), data):
            self.assertAlmostEqual(a, b)
        return

    def test_fourier_smooth_three(self):
        """
        Test the fourier smoothing function, with data input three
        """
        # No change should happen with a 'width' of 1.0.
        data = list(DATA_THREE)
        x = smooth_utils.fourier_smooth(data, 1.0, filtr='box')
        self.assertEqual(data, x)

        data = list(DATA_THREE)
        x = smooth_utils.fourier_smooth(data, 1.0, filtr='triangle')
        self.assertEqual(data, x)

        data = list(DATA_THREE)
        x = smooth_utils.fourier_smooth(data, 1.0, filtr='gaussian')
        self.assertEqual(data, x)

        # Smooth by two frames.
        data = list(DATA_THREE)
        x = smooth_utils.fourier_smooth(data, 2.0, filtr='box')
        data = [
            0.0,
            0.0,
            0.3333333333333,
            0.66666666666666,
            0.66666666666666,
            0.3333333333333,
            0.0,
            0.0,
        ]
        for a, b in zip(list(x), data):
            self.assertAlmostEqual(a, b)

        data = list(DATA_THREE)
        x = smooth_utils.fourier_smooth(data, 2.0, filtr='triangle')
        data = [
            0.0,
            0.0,
            0.2,
            0.8,
            0.8,
            0.2,
            0.0,
            0.0,
        ]
        for a, b in zip(list(x), data):
            self.assertAlmostEqual(a, b)

        data = list(DATA_THREE)
        x = smooth_utils.fourier_smooth(data, 2.0, filtr='gaussian')
        data = [
            0.0,
            0.0,
            0.27406862,
            0.72593138,
            0.72593138,
            0.27406862,
            0.0,
            0.0,
        ]
        for a, b in zip(list(x), data):
            self.assertAlmostEqual(a, b)
        return

    def test_fourier_smooth_four(self):
        """
        Test the fourier smoothing function, with data four input.

        .. todo::

            Test with and without Numpy in the same interpreter
              session; We must get the exact same result!

        """
        # Smooth and negate DATA_ONE.
        data = list(DATA_ONE)
        x = smooth_utils.fourier_smooth(data, 2.0)
        x_neg = [n * -1.0 for n in x]

        # Smooth DATA_FOUR by two frames, it must match DATA_ONE after
        # it was smoothed and negated.
        data = list(DATA_FOUR)
        y = smooth_utils.fourier_smooth(data, 2.0)
        self.assertEqual(len(x_neg), len(y))
        for i, v in enumerate(y):
            self.assertApproxEqual(x_neg[i], v)
        return


if __name__ == '__main__':
    prog = unittest.main()
