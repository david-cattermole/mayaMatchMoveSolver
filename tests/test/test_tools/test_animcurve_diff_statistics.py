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
STAT_TYPE_RMS_DIFF = 1
STAT_TYPE_POPULATION_STD_DEV = 2
STAT_TYPE_PEAK_TO_PEAK_DIFF = 3
STAT_TYPE_SIGNAL_TO_NOISE_RATIO = 4
STAT_TYPE_POPULATION_VARIANCE = 5
STAT_TYPE_MEAN_DIFF = 6
STAT_TYPE_MEDIAN_DIFF = 7


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
                stats["mean_absolute_diff"] = stat_value
            elif stat_type == STAT_TYPE_RMS_DIFF:
                stats["rms_diff"] = stat_value
            elif stat_type == STAT_TYPE_POPULATION_STD_DEV:
                stats["population_std_dev"] = stat_value
            elif stat_type == STAT_TYPE_PEAK_TO_PEAK_DIFF:
                stats["peak_to_peak_diff"] = stat_value
            elif stat_type == STAT_TYPE_SIGNAL_TO_NOISE_RATIO:
                stats["signal_to_noise_ratio"] = stat_value
            elif stat_type == STAT_TYPE_POPULATION_VARIANCE:
                stats["population_variance"] = stat_value
            elif stat_type == STAT_TYPE_MEAN_DIFF:
                stats["mean_diff"] = stat_value
            elif stat_type == STAT_TYPE_MEDIAN_DIFF:
                stats["median_diff"] = stat_value

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
            variance=True,
            standardDeviation=True,
            peakToPeak=True,
            signalToNoiseRatio=True,
        )

        stats = self._parse_diff_statistics_result(result)

        # Verify all expected statistics are present.
        expected_stats = [
            "mean_absolute_diff",
            "rms_diff",
            "population_std_dev",
            "peak_to_peak_diff",
            "signal_to_noise_ratio",
            "population_variance",
            "mean_diff",
            "median_diff",
        ]

        for stat_name in expected_stats:
            self.assertIn(stat_name, stats)
            self.assertTrue(
                math.isfinite(stats[stat_name]),
                "{} is not finite: {}".format(stat_name, stats[stat_name]),
            )

        # Verify relationships between statistics.
        # Standard deviation should be sqrt(variance).
        expected_std = math.sqrt(stats["population_variance"])
        self.assertAlmostEqual(stats["population_std_dev"], expected_std, places=5)

        # Mean absolute diff should be >= 0.
        self.assertGreaterEqual(stats["mean_absolute_diff"], 0.0)

        # RMS should be >= 0.
        self.assertGreaterEqual(stats["rms_diff"], 0.0)

        # Peak-to-peak should be >= 0.
        self.assertGreaterEqual(stats["peak_to_peak_diff"], 0.0)

    def test_diff_statistics_identical_curves(self):
        """Test statistics when comparing identical curves."""
        maya.cmds.file(new=True, force=True)
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
            variance=True,
            standardDeviation=True,
            peakToPeak=True,
        )

        stats = self._parse_diff_statistics_result(result)

        # For identical curves, all differences should be zero.
        self.assertAlmostEqual(stats["mean_absolute_diff"], 0.0, places=5)
        self.assertAlmostEqual(stats["rms_diff"], 0.0, places=5)
        self.assertAlmostEqual(stats["mean_diff"], 0.0, places=5)
        self.assertAlmostEqual(stats["median_diff"], 0.0, places=5)
        self.assertAlmostEqual(stats["population_variance"], 0.0, places=5)
        self.assertAlmostEqual(stats["population_std_dev"], 0.0, places=5)
        self.assertAlmostEqual(stats["peak_to_peak_diff"], 0.0, places=5)

    def test_diff_statistics_constant_offset(self):
        """Test statistics with curves that have a constant offset."""
        maya.cmds.file(new=True, force=True)
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
            variance=True,
            peakToPeak=True,
        )

        stats = self._parse_diff_statistics_result(result)

        # For constant offset:
        # - Mean diff should equal the offset.
        self.assertAlmostEqual(stats["mean_diff"], -offset, places=5)
        # - Mean absolute diff should equal abs(offset).
        self.assertAlmostEqual(stats["mean_absolute_diff"], abs(offset), places=5)
        # - Median diff should equal the offset.
        self.assertAlmostEqual(stats["median_diff"], -offset, places=5)
        # - Variance should be 0 (no variation in differences).
        self.assertAlmostEqual(stats["population_variance"], 0.0, places=5)
        # - Peak-to-peak should be 0.
        self.assertAlmostEqual(stats["peak_to_peak_diff"], 0.0, places=5)

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
        )
        stats_full = self._parse_diff_statistics_result(result_full)

        # Partial range.
        result_partial = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx,
            animCurve_ty,
            startFrame=50,
            endFrame=150,
            meanAbsoluteDifference=True,
        )
        stats_partial = self._parse_diff_statistics_result(result_partial)

        # Statistics should be different for different ranges.
        self.assertNotAlmostEqual(
            stats_full["mean_absolute_diff"],
            stats_partial["mean_absolute_diff"],
            places=2,
        )

    def test_diff_statistics_noise_detection(self):
        """Test statistics on curves with added noise."""
        maya.cmds.file(new=True, force=True)
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
            standardDeviation=True,
            rootMeanSquareDifference=True,
            meanDifference=True,
        )
        stats = self._parse_diff_statistics_result(result)

        # Verify noise is detected.
        self.assertGreater(stats["population_std_dev"], 0.1)
        self.assertGreater(stats["rms_diff"], 0.1)
        # Mean difference should be close to zero for random noise.
        self.assertLess(abs(stats["mean_diff"]), 0.2)

    def test_diff_statistics_error_handling(self):
        """Test error handling for invalid inputs."""
        maya.cmds.file(new=True, force=True)

        transform = maya.cmds.createNode("transform", name="testTransform")
        maya.cmds.setKeyframe(transform, attribute="translateX", time=1, value=0)
        animCurve = maya.cmds.listConnections(
            "{}.translateX".format(transform), type="animCurve"
        )[0]

        # Test with only one curve (should fail).
        with self.assertRaises(TypeError):
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
        maya.cmds.file(new=True, force=True)
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
        maya.cmds.file(new=True, force=True)
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
        self.assertIn("mean_absolute_diff", parsed)

        # Test RMS only.
        result = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx, animCurve_ty, rootMeanSquareDifference=True
        )
        parsed = self._parse_diff_statistics_result(result)
        self.assertEqual(len(parsed), 1)
        self.assertIn("rms_diff", parsed)

        # Test median difference only.
        result = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx, animCurve_ty, medianDifference=True
        )
        parsed = self._parse_diff_statistics_result(result)
        self.assertEqual(len(parsed), 1)
        self.assertIn("median_diff", parsed)

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
            animCurve_tx, animCurve_ty, meanDifference=True, variance=True
        )
        parsed = self._parse_diff_statistics_result(result)
        self.assertEqual(len(parsed), 2)
        self.assertIn("mean_diff", parsed)
        self.assertIn("population_variance", parsed)

        # Test variance + stddev.
        result = maya.cmds.mmAnimCurveDiffStatistics(
            animCurve_tx, animCurve_ty, variance=True, standardDeviation=True
        )
        parsed = self._parse_diff_statistics_result(result)
        self.assertEqual(len(parsed), 2)
        self.assertIn("population_variance", parsed)
        self.assertIn("population_std_dev", parsed)

        # Verify stddev = sqrt(variance).
        expected_stddev = math.sqrt(parsed["population_variance"])
        self.assertAlmostEqual(parsed["population_std_dev"], expected_stddev, places=5)


if __name__ == "__main__":
    prog = unittest.main()
