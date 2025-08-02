# Copyright (C) 2025 David Cattermole.
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
Test functions for mmAnimCurveDiffStatistics command.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import random
import unittest

import maya.cmds

import test.test_tools.toolsutils as test_tools_utils


# Statistic type identifiers from the C++ code.
STAT_TYPE_MEAN_ABSOLUTE_DIFF = 0
STAT_TYPE_ROOT_MEAN_SQUARE_DIFF = 1
STAT_TYPE_POPULATION_STD_DEV = 2
STAT_TYPE_PEAK_TO_PEAK_DIFF = 3
STAT_TYPE_SIGNAL_TO_NOISE_RATIO = 4
STAT_TYPE_POPULATION_VARIANCE = 5
STAT_TYPE_MEAN_DIFF = 6
STAT_TYPE_MEDIAN_DIFF = 7
STAT_TYPE_MEAN_ABSOLUTE_ERROR = 8
STAT_TYPE_ROOT_MEAN_SQUARE_ERROR = 9
STAT_TYPE_NORMALIZED_ROOT_MEAN_SQUARE_ERROR = 10
STAT_TYPE_R_SQUARED = 11


# Names for each statistic identifier defined in this module.
STAT_NAME_MEAN_ABSOLUTE_DIFF = "mean_absolute_diff"
STAT_NAME_MEAN_ABSOLUTE_ERROR = "mean_absolute_error"
STAT_NAME_MEAN_DIFF = "mean_diff"
STAT_NAME_MEDIAN_DIFF = "median_diff"
STAT_NAME_NORMALIZED_ROOT_MEAN_SQUARE_ERROR = "normalized_root_mean_square_error"
STAT_NAME_PEAK_TO_PEAK_DIFF = "peak_to_peak_diff"
STAT_NAME_POPULATION_STD_DEV = "population_std_dev"
STAT_NAME_POPULATION_VARIANCE = "population_variance"
STAT_NAME_ROOT_MEAN_SQUARE_DIFF = "root_mean_square_diff"
STAT_NAME_ROOT_MEAN_SQUARE_ERROR = "root_mean_square_error"
STAT_NAME_R_SQUARED = "r_squared"
STAT_NAME_SIGNAL_TO_NOISE_RATIO = "signal_to_noise_ratio"

STAT_NAME_LIST = [
    STAT_NAME_MEAN_ABSOLUTE_DIFF,
    STAT_NAME_MEAN_ABSOLUTE_ERROR,
    STAT_NAME_MEAN_DIFF,
    STAT_NAME_MEDIAN_DIFF,
    STAT_NAME_NORMALIZED_ROOT_MEAN_SQUARE_ERROR,
    STAT_NAME_PEAK_TO_PEAK_DIFF,
    STAT_NAME_POPULATION_STD_DEV,
    STAT_NAME_POPULATION_VARIANCE,
    STAT_NAME_ROOT_MEAN_SQUARE_DIFF,
    STAT_NAME_ROOT_MEAN_SQUARE_ERROR,
    STAT_NAME_R_SQUARED,
    STAT_NAME_SIGNAL_TO_NOISE_RATIO,
]


# @unittest.skip
class TestAnimCurveDiffStatistics(test_tools_utils.ToolsTestCase):
    def _parse_diff_statistics_result(self, result):
        """Parse the result array into a dictionary of statistics."""
        stats = {}
        stat_count = int(result[0])

        i = 1
        for j in range(stat_count):
            stat_type = int(result[i])
            stat_value = result[i + 1]

            if stat_type == STAT_TYPE_MEAN_ABSOLUTE_DIFF:
                stats[STAT_NAME_MEAN_ABSOLUTE_DIFF] = stat_value
            elif stat_type == STAT_TYPE_ROOT_MEAN_SQUARE_DIFF:
                stats[STAT_NAME_ROOT_MEAN_SQUARE_DIFF] = stat_value
            elif stat_type == STAT_TYPE_POPULATION_STD_DEV:
                stats[STAT_NAME_POPULATION_STD_DEV] = stat_value
            elif stat_type == STAT_TYPE_PEAK_TO_PEAK_DIFF:
                stats[STAT_NAME_PEAK_TO_PEAK_DIFF] = stat_value
            elif stat_type == STAT_TYPE_SIGNAL_TO_NOISE_RATIO:
                stats[STAT_NAME_SIGNAL_TO_NOISE_RATIO] = stat_value
            elif stat_type == STAT_TYPE_POPULATION_VARIANCE:
                stats[STAT_NAME_POPULATION_VARIANCE] = stat_value
            elif stat_type == STAT_TYPE_MEAN_DIFF:
                stats[STAT_NAME_MEAN_DIFF] = stat_value
            elif stat_type == STAT_TYPE_MEDIAN_DIFF:
                stats[STAT_NAME_MEDIAN_DIFF] = stat_value
            elif stat_type == STAT_TYPE_MEAN_ABSOLUTE_ERROR:
                stats[STAT_NAME_MEAN_ABSOLUTE_ERROR] = stat_value
            elif stat_type == STAT_TYPE_ROOT_MEAN_SQUARE_ERROR:
                stats[STAT_NAME_ROOT_MEAN_SQUARE_ERROR] = stat_value
            elif stat_type == STAT_TYPE_NORMALIZED_ROOT_MEAN_SQUARE_ERROR:
                stats[STAT_NAME_NORMALIZED_ROOT_MEAN_SQUARE_ERROR] = stat_value
            elif stat_type == STAT_TYPE_R_SQUARED:
                stats[STAT_NAME_R_SQUARED] = stat_value

            i += 2

        return stats

    def test_diff_statistics_basic(self):
        """Test basic diff statistics between two animation curves."""
        name = "anim_curves1.ma"
        path = self.get_data_path("anim_curves", name)
        maya.cmds.file(path, open=True, force=True)

        tfm = "transform1"
        tfm_attr_tx = "{}.translateX".format(tfm)
        tfm_attr_ty = "{}.translateY".format(tfm)

        animCurve_tx = maya.cmds.listConnections(tfm_attr_tx, type="animCurve")[0]
        animCurve_ty = maya.cmds.listConnections(tfm_attr_ty, type="animCurve")[0]

        # Test with all statistics enabled.
        result = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx,
            animCurve_ty,
            startFrame=1,
            endFrame=200,
            meanAbsoluteDifference=True,
            rootMeanSquareDifference=True,
            meanDifference=True,
            medianDifference=True,
            populationVariance=True,
            populationStandardDeviation=True,
            peakToPeak=True,
            signalToNoiseRatio=True,
            meanAbsoluteError=True,
            rootMeanSquareError=True,
            normalizedRootMeanSquareError=True,
            rSquared=True,
        )

        stats = self._parse_diff_statistics_result(result)

        # Verify all expected statistics are present.
        for stat_name in STAT_NAME_LIST:
            self.assertIn(stat_name, stats)
            self.assertTrue(
                math.isfinite(stats[stat_name]),
                "{} is not finite: {}".format(stat_name, stats[stat_name]),
            )
        self.assertEquals(len(stats.keys()), len(STAT_NAME_LIST))

        # Verify relationships between statistics.
        # Standard deviation should be sqrt(variance).
        expected_std = math.sqrt(stats[STAT_NAME_POPULATION_VARIANCE])
        self.assertAlmostEqual(
            stats[STAT_NAME_POPULATION_STD_DEV], expected_std, places=5
        )

        # Mean absolute diff should be >= 0.
        self.assertGreaterEqual(stats[STAT_NAME_MEAN_ABSOLUTE_DIFF], 0.0)

        # RMS should be >= 0.
        self.assertGreaterEqual(stats[STAT_NAME_ROOT_MEAN_SQUARE_DIFF], 0.0)

        # Peak-to-peak should be >= 0.
        self.assertGreaterEqual(stats[STAT_NAME_PEAK_TO_PEAK_DIFF], 0.0)

        # MAE should be >= 0.
        self.assertGreaterEqual(stats[STAT_NAME_MEAN_ABSOLUTE_ERROR], 0.0)

        # RMSE should be >= 0.
        self.assertGreaterEqual(stats[STAT_NAME_ROOT_MEAN_SQUARE_ERROR], 0.0)

        # NRMSE should be >= 0.
        self.assertGreaterEqual(stats[STAT_NAME_NORMALIZED_ROOT_MEAN_SQUARE_ERROR], 0.0)

        # R-squared should be between -infinity and 1.
        self.assertLessEqual(stats[STAT_NAME_R_SQUARED], 1.0)

    def test_diff_statistics_identical_curves(self):
        """Test statistics when comparing identical curves."""
        transform = maya.cmds.createNode("transform", name="testTransform")

        # Create identical animation curves.
        for attr in ["translateX", "translateY"]:
            for frame in range(1, 11):
                value = math.sin(frame * 0.5) * 10.0
                maya.cmds.setKeyframe(
                    transform, attribute=attr, time=frame, value=value
                )

        animCurve_tx = maya.cmds.listConnections(
            "{}.translateX".format(transform), type="animCurve"
        )[0]
        animCurve_ty = maya.cmds.listConnections(
            "{}.translateY".format(transform), type="animCurve"
        )[0]

        # Test with all statistics.
        result = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx,
            animCurve_ty,
            meanAbsoluteDifference=True,
            rootMeanSquareDifference=True,
            meanDifference=True,
            medianDifference=True,
            populationVariance=True,
            populationStandardDeviation=True,
            peakToPeak=True,
            meanAbsoluteError=True,
            rootMeanSquareError=True,
            normalizedRootMeanSquareError=True,
            rSquared=True,
        )

        stats = self._parse_diff_statistics_result(result)

        # For identical curves, all differences should be zero.
        for stat_name in [
            STAT_NAME_MEAN_ABSOLUTE_DIFF,
            STAT_NAME_ROOT_MEAN_SQUARE_DIFF,
            STAT_NAME_POPULATION_STD_DEV,
            STAT_NAME_POPULATION_VARIANCE,
            STAT_NAME_PEAK_TO_PEAK_DIFF,
            STAT_NAME_MEAN_DIFF,
            STAT_NAME_MEDIAN_DIFF,
            STAT_NAME_MEAN_ABSOLUTE_ERROR,
            STAT_NAME_ROOT_MEAN_SQUARE_ERROR,
            STAT_NAME_NORMALIZED_ROOT_MEAN_SQUARE_ERROR,
        ]:
            self.assertAlmostEqual(stats[stat_name], 0.0, places=5)

        # R-squared should be 1.0 for identical curves (perfect correlation).
        self.assertAlmostEqual(stats[STAT_NAME_R_SQUARED], 1.0, places=5)

    def test_diff_statistics_constant_offset(self):
        """Test statistics with curves that have a constant offset."""
        transform = maya.cmds.createNode("transform", name="testTransform")

        # Create two curves with constant offset.
        offset = 5.0
        for frame in range(1, 11):
            base_value = float(frame)
            maya.cmds.setKeyframe(
                transform, attribute="translateX", time=frame, value=base_value
            )
            maya.cmds.setKeyframe(
                transform, attribute="translateY", time=frame, value=base_value + offset
            )

        animCurve_tx = maya.cmds.listConnections(
            "{}.translateX".format(transform), type="animCurve"
        )[0]
        animCurve_ty = maya.cmds.listConnections(
            "{}.translateY".format(transform), type="animCurve"
        )[0]

        result = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx,
            animCurve_ty,
            meanAbsoluteDifference=True,
            meanDifference=True,
            medianDifference=True,
            populationVariance=True,
            peakToPeak=True,
            meanAbsoluteError=True,
            rootMeanSquareError=True,
        )

        stats = self._parse_diff_statistics_result(result)

        # For constant offset:
        # - Mean diff should equal the offset.
        self.assertAlmostEqual(stats[STAT_NAME_MEAN_DIFF], -offset, places=5)
        # - Mean absolute diff should equal abs(offset).
        self.assertAlmostEqual(
            stats[STAT_NAME_MEAN_ABSOLUTE_DIFF], abs(offset), places=5
        )
        # - Median diff should equal the offset.
        self.assertAlmostEqual(stats[STAT_NAME_MEDIAN_DIFF], -offset, places=5)
        # - Variance should be 0 (no variation in differences).
        self.assertAlmostEqual(stats[STAT_NAME_POPULATION_VARIANCE], 0.0, places=5)
        # - Peak-to-peak should be 0.
        self.assertAlmostEqual(stats[STAT_NAME_PEAK_TO_PEAK_DIFF], 0.0, places=5)
        # - MAE should equal abs(offset).
        self.assertAlmostEqual(
            stats[STAT_NAME_MEAN_ABSOLUTE_ERROR], abs(offset), places=5
        )
        # - RMSE should equal abs(offset).
        self.assertAlmostEqual(
            stats[STAT_NAME_ROOT_MEAN_SQUARE_ERROR], abs(offset), places=5
        )

    def test_diff_statistics_frame_range(self):
        """Test statistics with different frame ranges."""
        name = "anim_curves1.ma"
        path = self.get_data_path("anim_curves", name)
        maya.cmds.file(path, open=True, force=True)

        tfm = "transform1"
        tfm_attr_tx = "{}.translateX".format(tfm)
        tfm_attr_ty = "{}.translateY".format(tfm)

        animCurve_tx = maya.cmds.listConnections(tfm_attr_tx, type="animCurve")[0]
        animCurve_ty = maya.cmds.listConnections(tfm_attr_ty, type="animCurve")[0]

        # Full range.
        result_full = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx,
            animCurve_ty,
            startFrame=1,
            endFrame=200,
            meanAbsoluteDifference=True,
            meanAbsoluteError=True,
        )
        stats_full = self._parse_diff_statistics_result(result_full)

        # Partial range.
        result_partial = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx,
            animCurve_ty,
            startFrame=50,
            endFrame=150,
            meanAbsoluteDifference=True,
            meanAbsoluteError=True,
        )
        stats_partial = self._parse_diff_statistics_result(result_partial)

        # Statistics should be different for different ranges.
        self.assertNotAlmostEqual(
            stats_full[STAT_NAME_MEAN_ABSOLUTE_DIFF],
            stats_partial[STAT_NAME_MEAN_ABSOLUTE_DIFF],
            places=2,
        )
        self.assertNotAlmostEqual(
            stats_full[STAT_NAME_MEAN_ABSOLUTE_ERROR],
            stats_partial[STAT_NAME_MEAN_ABSOLUTE_ERROR],
            places=2,
        )

    def test_diff_statistics_noise_detection(self):
        """Test statistics on curves with added noise."""
        transform1 = maya.cmds.createNode("transform", name="testTransform1")
        transform2 = maya.cmds.createNode("transform", name="testTransform2")

        # Create smooth curve and noisy curve.
        random.seed(42)  # For reproducibility.
        for frame in range(1, 51):
            smooth_value = math.sin(frame * 0.1) * 10.0
            noisy_value = smooth_value + random.uniform(-0.5, 0.5)

            maya.cmds.setKeyframe(
                transform1, attribute="translateX", time=frame, value=smooth_value
            )
            maya.cmds.setKeyframe(
                transform2, attribute="translateX", time=frame, value=noisy_value
            )

        animCurve1 = maya.cmds.listConnections(
            "{}.translateX".format(transform1), type="animCurve"
        )[0]
        animCurve2 = maya.cmds.listConnections(
            "{}.translateX".format(transform2), type="animCurve"
        )[0]

        result = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve1,
            animCurve2,
            populationStandardDeviation=True,
            rootMeanSquareDifference=True,
            meanDifference=True,
            meanAbsoluteError=True,
            rootMeanSquareError=True,
            rSquared=True,
        )
        stats = self._parse_diff_statistics_result(result)

        # Verify noise is detected.
        self.assertGreater(stats[STAT_NAME_POPULATION_STD_DEV], 0.1)
        self.assertGreater(stats[STAT_NAME_ROOT_MEAN_SQUARE_DIFF], 0.1)
        self.assertGreater(stats[STAT_NAME_MEAN_ABSOLUTE_ERROR], 0.1)
        self.assertGreater(stats[STAT_NAME_ROOT_MEAN_SQUARE_ERROR], 0.1)
        # Mean difference should be close to zero for random noise.
        self.assertLess(abs(stats[STAT_NAME_MEAN_DIFF]), 0.2)
        # R-squared should be high but not perfect due to noise.
        self.assertGreater(stats[STAT_NAME_R_SQUARED], 0.9)
        self.assertLess(stats[STAT_NAME_R_SQUARED], 1.0)

    def test_diff_statistics_error_handling(self):
        """Test error handling for invalid inputs."""
        transform = maya.cmds.createNode("transform", name="testTransform")
        maya.cmds.setKeyframe(transform, attribute="translateX", time=1, value=0)
        animCurve = maya.cmds.listConnections(
            "{}.translateX".format(transform), type="animCurve"
        )[0]

        # Test with only one curve (should fail).
        with self.assertRaises(RuntimeError):
            maya.cmds.mmAnimCurveDiffStatistics(animCurve, meanDifference=True)

        # Test with non-animation curve nodes.
        with self.assertRaises(RuntimeError):
            maya.cmds.mmAnimCurveDiffStatistics(
                transform, transform, meanDifference=True
            )

        # Test with three curves (should fail).
        maya.cmds.setKeyframe(transform, attribute="translateY", time=1, value=0)
        maya.cmds.setKeyframe(transform, attribute="translateZ", time=1, value=0)
        animCurve_ty = maya.cmds.listConnections(
            "{}.translateY".format(transform), type="animCurve"
        )[0]
        animCurve_tz = maya.cmds.listConnections(
            "{}.translateZ".format(transform), type="animCurve"
        )[0]

        with self.assertRaises(TypeError):
            maya.cmds.mmAnimCurveDiffStatistics(
                animCurve, animCurve_ty, animCurve_tz, meanDifference=True
            )

        # Test with no statistic flags (should fail).
        with self.assertRaises(RuntimeError):
            maya.cmds.mmAnimCurveDiffStatistics(animCurve, animCurve_ty)

    def test_diff_statistics_non_overlapping_ranges(self):
        """Test with curves that have non-overlapping frame ranges."""
        transform = maya.cmds.createNode("transform", name="testTransform")

        # Create curve 1 from frames 1-10.
        for frame in range(1, 11):
            maya.cmds.setKeyframe(
                transform, attribute="translateX", time=frame, value=frame
            )

        # Create curve 2 from frames 20-30.
        for frame in range(20, 31):
            maya.cmds.setKeyframe(
                transform, attribute="translateY", time=frame, value=frame
            )

        animCurve_tx = maya.cmds.listConnections(
            "{}.translateX".format(transform), type="animCurve"
        )[0]
        animCurve_ty = maya.cmds.listConnections(
            "{}.translateY".format(transform), type="animCurve"
        )[0]

        # This should fail due to non-overlapping ranges.
        with self.assertRaises(RuntimeError):
            maya.cmds.mmAnimCurveDiffStatistics(
                animCurve_tx, animCurve_ty, meanDifference=True
            )

    def test_diff_statistics_single_keyframe(self):
        """Test with curves that have only one keyframe."""
        transform = maya.cmds.createNode("transform", name="testTransform")

        # Create curves with single keyframe.
        maya.cmds.setKeyframe(transform, attribute="translateX", time=1, value=5.0)
        maya.cmds.setKeyframe(transform, attribute="translateY", time=1, value=10.0)

        animCurve_tx = maya.cmds.listConnections(
            "{}.translateX".format(transform), type="animCurve"
        )[0]
        animCurve_ty = maya.cmds.listConnections(
            "{}.translateY".format(transform), type="animCurve"
        )[0]

        # This should fail due to insufficient keyframes.
        with self.assertRaises(RuntimeError):
            maya.cmds.mmAnimCurveDiffStatistics(
                animCurve_tx, animCurve_ty, meanDifference=True
            )

    def test_diff_statistics_single_flag(self):
        """Test calculating individual statistics."""
        name = "anim_curves1.ma"
        path = self.get_data_path("anim_curves", name)
        maya.cmds.file(path, open=True, force=True)

        tfm = "transform1"
        tfm_attr_tx = "{}.translateX".format(tfm)
        tfm_attr_ty = "{}.translateY".format(tfm)

        animCurve_tx = maya.cmds.listConnections(tfm_attr_tx, type="animCurve")[0]
        animCurve_ty = maya.cmds.listConnections(tfm_attr_ty, type="animCurve")[0]

        # Test mean absolute difference only.
        result = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx, animCurve_ty, meanAbsoluteDifference=True
        )
        parsed = self._parse_diff_statistics_result(result)
        self.assertEqual(len(parsed), 1)
        self.assertIn(STAT_NAME_MEAN_ABSOLUTE_DIFF, parsed)

        # Test RMS only.
        result = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx, animCurve_ty, rootMeanSquareDifference=True
        )
        parsed = self._parse_diff_statistics_result(result)
        self.assertEqual(len(parsed), 1)
        self.assertIn(STAT_NAME_ROOT_MEAN_SQUARE_DIFF, parsed)

        # Test median difference only.
        result = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx, animCurve_ty, medianDifference=True
        )
        parsed = self._parse_diff_statistics_result(result)
        self.assertEqual(len(parsed), 1)
        self.assertIn(STAT_NAME_MEDIAN_DIFF, parsed)

        # Test MAE only.
        result = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx, animCurve_ty, meanAbsoluteError=True
        )
        parsed = self._parse_diff_statistics_result(result)
        self.assertEqual(len(parsed), 1)
        self.assertIn(STAT_NAME_MEAN_ABSOLUTE_ERROR, parsed)

        # Test RMSE only.
        result = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx, animCurve_ty, rootMeanSquareError=True
        )
        parsed = self._parse_diff_statistics_result(result)
        self.assertEqual(len(parsed), 1)
        self.assertIn(STAT_NAME_ROOT_MEAN_SQUARE_ERROR, parsed)

        # Test NRMSE only.
        result = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx, animCurve_ty, normalizedRootMeanSquareError=True
        )
        parsed = self._parse_diff_statistics_result(result)
        self.assertEqual(len(parsed), 1)
        self.assertIn(STAT_NAME_NORMALIZED_ROOT_MEAN_SQUARE_ERROR, parsed)

        # Test R-squared only.
        result = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx, animCurve_ty, rSquared=True
        )
        parsed = self._parse_diff_statistics_result(result)
        self.assertEqual(len(parsed), 1)
        self.assertIn(STAT_NAME_R_SQUARED, parsed)

    def test_diff_statistics_combined_flags(self):
        """Test various combinations of statistics flags."""
        name = "anim_curves1.ma"
        path = self.get_data_path("anim_curves", name)
        maya.cmds.file(path, open=True, force=True)

        tfm = "transform1"
        tfm_attr_tx = "{}.translateX".format(tfm)
        tfm_attr_ty = "{}.translateY".format(tfm)

        animCurve_tx = maya.cmds.listConnections(tfm_attr_tx, type="animCurve")[0]
        animCurve_ty = maya.cmds.listConnections(tfm_attr_ty, type="animCurve")[0]

        # Test mean + variance.
        result = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx, animCurve_ty, meanDifference=True, populationVariance=True
        )
        parsed = self._parse_diff_statistics_result(result)
        self.assertEqual(len(parsed), 2)
        self.assertIn(STAT_NAME_MEAN_DIFF, parsed)
        self.assertIn(STAT_NAME_POPULATION_VARIANCE, parsed)

        # Test variance + stddev.
        result = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx,
            animCurve_ty,
            populationVariance=True,
            populationStandardDeviation=True,
        )
        parsed = self._parse_diff_statistics_result(result)
        self.assertEqual(len(parsed), 2)
        self.assertIn(STAT_NAME_POPULATION_VARIANCE, parsed)
        self.assertIn(STAT_NAME_POPULATION_STD_DEV, parsed)

        # Verify stddev = sqrt(variance).
        expected_stddev = math.sqrt(parsed[STAT_NAME_POPULATION_VARIANCE])
        self.assertAlmostEqual(
            parsed[STAT_NAME_POPULATION_STD_DEV], expected_stddev, places=5
        )

        result = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx,
            animCurve_ty,
            meanAbsoluteError=True,
            rootMeanSquareError=True,
            normalizedRootMeanSquareError=True,
            rSquared=True,
        )
        parsed = self._parse_diff_statistics_result(result)
        self.assertEqual(len(parsed), 4)
        self.assertIn(STAT_NAME_MEAN_ABSOLUTE_ERROR, parsed)
        self.assertIn(STAT_NAME_ROOT_MEAN_SQUARE_ERROR, parsed)
        self.assertIn(STAT_NAME_NORMALIZED_ROOT_MEAN_SQUARE_ERROR, parsed)
        self.assertIn(STAT_NAME_R_SQUARED, parsed)

    def test_diff_statistics_with_list_inputs(self):
        """Test diff statistics with Python list inputs."""
        x_values = list(range(1, 11))
        y_values1 = [x * 2 for x in x_values]  # Linear.
        y_values2 = [x * 2 + 5 for x in x_values]  # Linear with offset.

        result = maya.cmds.mmAnimCurveDiffStatistics(
            xValues=x_values,
            yValuesA=y_values1,
            yValuesB=y_values2,
            meanAbsoluteDifference=True,
            meanDifference=True,
            populationVariance=True,
            meanAbsoluteError=True,
            rootMeanSquareError=True,
        )

        stats = self._parse_diff_statistics_result(result)

        # For constant offset of 5:
        self.assertAlmostEqual(stats[STAT_NAME_MEAN_DIFF], -5.0, places=5)
        self.assertAlmostEqual(stats[STAT_NAME_MEAN_ABSOLUTE_DIFF], 5.0, places=5)
        self.assertAlmostEqual(stats[STAT_NAME_POPULATION_VARIANCE], 0.0, places=5)
        self.assertAlmostEqual(stats[STAT_NAME_MEAN_ABSOLUTE_ERROR], 5.0, places=5)
        self.assertAlmostEqual(stats[STAT_NAME_ROOT_MEAN_SQUARE_ERROR], 5.0, places=5)

    def test_diff_statistics_invalid_list_inputs(self):
        """Test error handling for invalid list inputs."""
        # Test with incomplete list inputs.
        with self.assertRaises(RuntimeError):
            maya.cmds.mmAnimCurveDiffStatistics(
                xValues=[1, 2, 3],
                yValuesA=[1, 4, 9],
                # Missing yValuesB.
                meanDifference=True,
            )

        with self.assertRaises(RuntimeError):
            maya.cmds.mmAnimCurveDiffStatistics(
                xValues=[1, 2, 3],
                # Missing yValuesA.
                yValuesB=[2, 5, 10],
                meanDifference=True,
            )

        # Test with mismatched lengths, with yValuesA.
        with self.assertRaises(RuntimeError):
            maya.cmds.mmAnimCurveDiffStatistics(
                xValues=[1, 2, 3],
                yValuesA=[1, 4],  # Different length.
                yValuesB=[2, 5, 10],
                meanDifference=True,
            )

        # Test with mismatched lengths, with yValuesA.
        with self.assertRaises(RuntimeError):
            maya.cmds.mmAnimCurveDiffStatistics(
                xValues=[1, 2, 3],
                yValuesA=[1, 4, 9],
                yValuesB=[2, 5],  # Different length.
                meanDifference=True,
            )

        # Test with mismatched lengths, with xValues.
        with self.assertRaises(RuntimeError):
            maya.cmds.mmAnimCurveDiffStatistics(
                xValues=[1, 2],  # Different length.
                yValuesA=[1, 4, 9],
                yValuesB=[2, 5, 10],
                meanDifference=True,
            )

    def test_diff_statistics_noise_with_lists(self):
        """Test noise detection with list inputs."""
        # Create smooth and noisy data
        random.seed(42)
        x_values = list(range(1, 51))
        smooth_values = [math.sin(x * 0.1) * 10.0 for x in x_values]
        noisy_values = [v + random.uniform(-0.5, 0.5) for v in smooth_values]

        result = maya.cmds.mmAnimCurveDiffStatistics(
            xValues=x_values,
            yValuesA=smooth_values,
            yValuesB=noisy_values,
            populationStandardDeviation=True,
            rootMeanSquareDifference=True,
            meanDifference=True,
            meanAbsoluteError=True,
            rootMeanSquareError=True,
            rSquared=True,
        )

        stats = self._parse_diff_statistics_result(result)

        # Verify noise is detected
        self.assertGreater(stats[STAT_NAME_POPULATION_STD_DEV], 0.1)
        self.assertGreater(stats[STAT_NAME_ROOT_MEAN_SQUARE_DIFF], 0.1)
        self.assertGreater(stats[STAT_NAME_MEAN_ABSOLUTE_ERROR], 0.1)
        self.assertGreater(stats[STAT_NAME_ROOT_MEAN_SQUARE_ERROR], 0.1)
        # Mean difference should be close to zero for random noise
        self.assertLess(abs(stats[STAT_NAME_MEAN_DIFF]), 0.2)
        # R-squared should be high but not perfect due to noise
        self.assertGreater(stats[STAT_NAME_R_SQUARED], 0.9)
        self.assertLess(stats[STAT_NAME_R_SQUARED], 1.0)

    def test_diff_statistics_perfect_correlation(self):
        """Test R-squared with perfect correlation (scaled curves)."""
        transform = maya.cmds.createNode("transform", name="testTransform")

        # Create two curves where one is a scaled version of the other.
        scale_factor = 2.0
        for frame in range(1, 21):
            value1 = math.sin(frame * 0.3) * 10.0
            value2 = value1 * scale_factor

            maya.cmds.setKeyframe(
                transform, attribute="translateX", time=frame, value=value1
            )
            maya.cmds.setKeyframe(
                transform, attribute="translateY", time=frame, value=value2
            )

        animCurve_tx = maya.cmds.listConnections(
            "{}.translateX".format(transform), type="animCurve"
        )[0]
        animCurve_ty = maya.cmds.listConnections(
            "{}.translateY".format(transform), type="animCurve"
        )[0]

        result = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx, animCurve_ty, rSquared=True
        )

        stats = self._parse_diff_statistics_result(result)
        self.assertAlmostEqual(stats[STAT_NAME_R_SQUARED], -3.01e-07, places=5)

    def test_diff_statistics_negative_correlation(self):
        """Test R-squared with negative correlation."""
        transform = maya.cmds.createNode("transform", name="testTransform")

        # Create two curves where one is the negative of the other.
        for frame in range(1, 21):
            value1 = math.sin(frame * 0.3) * 10.0
            value2 = -value1  # Negative correlation.

            maya.cmds.setKeyframe(
                transform, attribute="translateX", time=frame, value=value1
            )
            maya.cmds.setKeyframe(
                transform, attribute="translateY", time=frame, value=value2
            )

        animCurve_tx = maya.cmds.listConnections(
            "{}.translateX".format(transform), type="animCurve"
        )[0]
        animCurve_ty = maya.cmds.listConnections(
            "{}.translateY".format(transform), type="animCurve"
        )[0]

        result = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx, animCurve_ty, rSquared=True
        )

        stats = self._parse_diff_statistics_result(result)

        self.assertAlmostEqual(stats[STAT_NAME_R_SQUARED], -3.000001, places=5)


if __name__ == "__main__":
    prog = unittest.main()
