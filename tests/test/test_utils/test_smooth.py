"""
Test functions for API utils module.
"""

import unittest

# import maya.cmds
# import maya.OpenMaya as OpenMaya

import test.test_utils.utilsutils as test_utils
import mmSolver.utils.smooth as smooth_utils


# Some random numbers.
DATA_ONE = [
    0.2540983642613156, 0.7831634753872109, 0.002591692790079203,
    0.41595045018499655, 0.6360617637325738, 0.11174422210135437,
    0.19632980357666963, 0.433340268169374, 0.07028804556375579,
    0.24322363800544966
]


# @unittest.skip
class TestSmooth(test_utils.UtilsTestCase):
    """
    Test smooth module.
    """

    def test_average_smooth(self):
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

    def test_gaussian_smooth(self):
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

    def test_fourier_smooth(self):
        """
        Test the fourier smoothing function.

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


if __name__ == '__main__':
    prog = unittest.main()
