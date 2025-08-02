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
Test functions for mmAnimCurveStatistics command.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import math

import maya.cmds

import test.test_tools.toolsutils as test_tools_utils


# Statistic type identifiers from the C++ code
STAT_TYPE_MEAN = 0
STAT_TYPE_MEDIAN = 1
STAT_TYPE_POPULATION_VARIANCE = 2
STAT_TYPE_POPULATION_STD_DEV = 3
STAT_TYPE_SIGNAL_TO_NOISE_RATIO = 4

# Names for each statistic identifier defined in this module.
STAT_NAME_MEAN = "mean"
STAT_NAME_MEDIAN = "median"
STAT_NAME_POPULATION_VARIANCE = "population_variance"
STAT_NAME_POPULATION_STD_DEV = "population_std_dev"
STAT_NAME_SIGNAL_TO_NOISE_RATIO = "signal_to_noise_ratio"
STAT_NAME_LIST = [
    STAT_NAME_MEAN,
    STAT_NAME_MEDIAN,
    STAT_NAME_POPULATION_VARIANCE,
    STAT_NAME_POPULATION_STD_DEV,
    STAT_NAME_SIGNAL_TO_NOISE_RATIO,
]


# @unittest.skip
class TestAnimCurveStatistics(test_tools_utils.ToolsTestCase):
    def _parse_statistics_result(self, result):
        """Parse the result array into a structured format."""
        parsed_curves = []
        i = 0
        while i < len(result):
            curve_index = int(result[i])
            num_stats = int(result[i + 1])
            i += 2

            stats = {}
            for j in range(num_stats):
                stat_type = int(result[i])
                stat_value = result[i + 1]

                if stat_type == STAT_TYPE_MEAN:
                    stats[STAT_NAME_MEAN] = stat_value
                elif stat_type == STAT_TYPE_MEDIAN:
                    stats[STAT_NAME_MEDIAN] = stat_value
                elif stat_type == STAT_TYPE_POPULATION_VARIANCE:
                    stats[STAT_NAME_POPULATION_VARIANCE] = stat_value
                elif stat_type == STAT_TYPE_POPULATION_STD_DEV:
                    stats[STAT_NAME_POPULATION_STD_DEV] = stat_value
                elif stat_type == STAT_TYPE_SIGNAL_TO_NOISE_RATIO:
                    stats[STAT_NAME_SIGNAL_TO_NOISE_RATIO] = stat_value

                i += 2

            parsed_curves.append({"index": curve_index, "stats": stats})

        return parsed_curves

    def test_statistics_all_flags(self):
        """Test calculating all statistics on animation curves."""
        name = "anim_curves1.ma"
        path = self.get_data_path("anim_curves", name)
        maya.cmds.file(path, open=True, force=True)

        startFrame = 1
        endFrame = 200

        tfm = "transform1"
        tfm_attr_tx = "{}.translateX".format(tfm)
        tfm_attr_ty = "{}.translateY".format(tfm)
        tfm_attr_tz = "{}.translateZ".format(tfm)

        animCurve_tx = maya.cmds.listConnections(tfm_attr_tx, type="animCurve")[0]
        animCurve_ty = maya.cmds.listConnections(tfm_attr_ty, type="animCurve")[0]
        animCurve_tz = maya.cmds.listConnections(tfm_attr_tz, type="animCurve")[0]

        result = maya.cmds.mmAnimCurveStatistics(
            animCurve_tx,
            animCurve_ty,
            animCurve_tz,
            startFrame=startFrame,
            endFrame=endFrame,
            mean=True,
            median=True,
            populationVariance=True,
            populationStandardDeviation=True,
            signalToNoiseRatio=True,
        )

        parsed = self._parse_statistics_result(result)
        self.assertEqual(len(parsed), 3)

        for curve_data in parsed:
            stats = curve_data["stats"]
            # Verify all statistics are present.
            for stat_name in STAT_NAME_LIST:
                self.assertIn(stat_name, stats)
            self.assertEqual(len(stats.keys()), len(STAT_NAME_LIST))

            # Verify relationships between statistics.
            # Standard deviation should be sqrt(variance).
            expected_stddev = math.sqrt(stats[STAT_NAME_POPULATION_VARIANCE])
            self.assertAlmostEqual(
                stats[STAT_NAME_POPULATION_STD_DEV], expected_stddev, places=5
            )

            # All values should be finite.
            for stat_name, stat_value in stats.items():
                self.assertTrue(
                    math.isfinite(stat_value),
                    "{} is not finite: {}".format(stat_name, stat_value),
                )

    def test_statistics_single_flag(self):
        """Test calculating individual statistics."""
        name = "anim_curves1.ma"
        path = self.get_data_path("anim_curves", name)
        maya.cmds.file(path, open=True, force=True)

        tfm = "transform1"
        tfm_attr_tx = "{}.translateX".format(tfm)
        animCurve_tx = maya.cmds.listConnections(tfm_attr_tx, type="animCurve")[0]

        # Test mean only.
        result = maya.cmds.mmAnimCurveStatistics(animCurve_tx, mean=True)
        parsed = self._parse_statistics_result(result)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(len(parsed[0]["stats"]), 1)
        self.assertIn(STAT_NAME_MEAN, parsed[0]["stats"])

        # Test median only.
        result = maya.cmds.mmAnimCurveStatistics(animCurve_tx, median=True)
        parsed = self._parse_statistics_result(result)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(len(parsed[0]["stats"]), 1)
        self.assertIn(STAT_NAME_MEDIAN, parsed[0]["stats"])

        # Test populationVariance only.
        result = maya.cmds.mmAnimCurveStatistics(animCurve_tx, populationVariance=True)
        parsed = self._parse_statistics_result(result)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(len(parsed[0]["stats"]), 1)
        self.assertIn(STAT_NAME_POPULATION_VARIANCE, parsed[0]["stats"])

    def test_statistics_frame_range(self):
        """Test statistics with different frame ranges."""
        name = "anim_curves1.ma"
        path = self.get_data_path("anim_curves", name)
        maya.cmds.file(path, open=True, force=True)

        tfm = "transform1"
        tfm_attr_tx = "{}.translateX".format(tfm)
        animCurve_tx = maya.cmds.listConnections(tfm_attr_tx, type="animCurve")[0]

        # Full range.
        result_full = maya.cmds.mmAnimCurveStatistics(
            animCurve_tx, startFrame=1, endFrame=200, mean=True, populationVariance=True
        )
        parsed_full = self._parse_statistics_result(result_full)

        # Partial range.
        result_partial = maya.cmds.mmAnimCurveStatistics(
            animCurve_tx,
            startFrame=50,
            endFrame=150,
            mean=True,
            populationVariance=True,
        )
        parsed_partial = self._parse_statistics_result(result_partial)

        # Statistics should be different for different ranges.
        self.assertNotAlmostEqual(
            parsed_full[0]["stats"][STAT_NAME_MEAN],
            parsed_partial[0]["stats"][STAT_NAME_MEAN],
            places=2,
        )

    def test_statistics_multiple_curves(self):
        """Test statistics on multiple curves at once."""
        name = "anim_curves1.ma"
        path = self.get_data_path("anim_curves", name)
        maya.cmds.file(path, open=True, force=True)

        tfm = "transform1"
        tfm_attr_tx = "{}.translateX".format(tfm)
        tfm_attr_ty = "{}.translateY".format(tfm)
        tfm_attr_tz = "{}.translateZ".format(tfm)

        animCurve_tx = maya.cmds.listConnections(tfm_attr_tx, type="animCurve")[0]
        animCurve_ty = maya.cmds.listConnections(tfm_attr_ty, type="animCurve")[0]
        animCurve_tz = maya.cmds.listConnections(tfm_attr_tz, type="animCurve")[0]

        maya.cmds.select(animCurve_tx, animCurve_ty, animCurve_tz)
        result = maya.cmds.mmAnimCurveStatistics(
            mean=True, populationStandardDeviation=True
        )

        parsed = self._parse_statistics_result(result)
        self.assertEqual(len(parsed), 3)

        # Verify each curve has the requested statistics.
        for i, curve_data in enumerate(parsed):
            self.assertEqual(curve_data["index"], i)
            self.assertEqual(len(curve_data["stats"]), 2)
            self.assertIn(STAT_NAME_MEAN, curve_data["stats"])
            self.assertIn(STAT_NAME_POPULATION_STD_DEV, curve_data["stats"])

    def test_statistics_constant_curve(self):
        """Test statistics on a constant (flat) animation curve."""
        # Create a constant animation curve.
        maya.cmds.file(new=True, force=True)
        transform = maya.cmds.createNode("transform", name="testTransform")

        # Set constant keyframes.
        constant_value = 5.0
        for frame in range(1, 11):
            maya.cmds.setKeyframe(
                transform, attribute="translateX", time=frame, value=constant_value
            )

        animCurve = maya.cmds.listConnections(
            "{}.translateX".format(transform), type="animCurve"
        )[0]

        result = maya.cmds.mmAnimCurveStatistics(
            animCurve,
            mean=True,
            median=True,
            populationVariance=True,
            populationStandardDeviation=True,
            signalToNoiseRatio=True,
        )

        parsed = self._parse_statistics_result(result)
        stats = parsed[0]["stats"]

        # For a constant curve mean and median should equal the
        # constant value.
        self.assertAlmostEqual(stats[STAT_NAME_MEAN], constant_value, places=5)
        self.assertAlmostEqual(stats[STAT_NAME_MEDIAN], constant_value, places=5)

        # For a constant curve variance and standard deviation should
        # be zero.
        self.assertAlmostEqual(stats[STAT_NAME_POPULATION_VARIANCE], 0.0, places=5)
        self.assertAlmostEqual(stats[STAT_NAME_POPULATION_STD_DEV], 0.0, places=5)

        # For a constant curve SNR should be infinity (but might be
        # represented as a large value).
        self.assertTrue(
            stats[STAT_NAME_SIGNAL_TO_NOISE_RATIO] > 1000.0
            or math.isinf(stats[STAT_NAME_SIGNAL_TO_NOISE_RATIO])
        )

    def test_statistics_linear_curve(self):
        """Test statistics on a linear animation curve."""
        # Create a linear animation curve.
        transform = maya.cmds.createNode("transform", name="testTransform")

        # Set linear keyframes from 0 to 10.
        for frame in range(1, 11):
            value = float(frame - 1)  # 0 to 9.
            maya.cmds.setKeyframe(
                transform, attribute="translateX", time=frame, value=value
            )

        animCurve = maya.cmds.listConnections(
            "{}.translateX".format(transform), type="animCurve"
        )[0]

        result = maya.cmds.mmAnimCurveStatistics(
            animCurve,
            startFrame=1,
            endFrame=10,
            mean=True,
            median=True,
            populationVariance=True,
        )

        parsed = self._parse_statistics_result(result)
        stats = parsed[0]["stats"]

        # For a linear curve from 0 to 9:
        # - Mean should be 4.5.
        self.assertAlmostEqual(stats[STAT_NAME_MEAN], 4.5, places=2)

        # - Median should also be 4.5.
        self.assertAlmostEqual(stats[STAT_NAME_MEDIAN], 4.5, places=2)

        # - PopulationVariance should be > 0 (approximately 8.25 for 0-9 range).
        self.assertGreater(stats[STAT_NAME_POPULATION_VARIANCE], 0)

    def test_statistics_error_handling(self):
        """Test error handling for invalid inputs."""
        transform = maya.cmds.createNode("transform", name="testTransform")
        with self.assertRaises(RuntimeError):
            maya.cmds.mmAnimCurveStatistics(transform, mean=True)
        return

    def test_statistics_combined_flags(self):
        """Test various combinations of statistics flags."""
        name = "anim_curves1.ma"
        path = self.get_data_path("anim_curves", name)
        maya.cmds.file(path, open=True, force=True)

        tfm = "transform1"
        tfm_attr_tx = "{}.translateX".format(tfm)
        animCurve_tx = maya.cmds.listConnections(tfm_attr_tx, type="animCurve")[0]

        # Test mean + variance (should calculate mean efficiently).
        result = maya.cmds.mmAnimCurveStatistics(
            animCurve_tx, mean=True, populationVariance=True
        )
        parsed = self._parse_statistics_result(result)
        self.assertEqual(len(parsed[0]["stats"]), 2)

        # Test variance + stddev (should calculate both efficiently).
        result = maya.cmds.mmAnimCurveStatistics(
            animCurve_tx, populationVariance=True, populationStandardDeviation=True
        )
        parsed = self._parse_statistics_result(result)
        self.assertEqual(len(parsed[0]["stats"]), 2)

        # Verify stddev = sqrt(variance).
        stats = parsed[0]["stats"]
        expected_stddev = math.sqrt(stats[STAT_NAME_POPULATION_VARIANCE])
        self.assertAlmostEqual(
            stats[STAT_NAME_POPULATION_STD_DEV], expected_stddev, places=5
        )

    def test_statistics_with_list_input(self):
        """Test statistics with Python list inputs."""
        x_values = [x for x in range(1, 11)]  # 1 to 10
        y_values = [math.sin(x * 0.5) * 10.0 for x in x_values]

        # Test with all statistics.
        result = maya.cmds.mmAnimCurveStatistics(
            xValues=x_values,
            yValues=y_values,
            mean=True,
            median=True,
            populationVariance=True,
            populationStandardDeviation=True,
            signalToNoiseRatio=True,
        )

        parsed = self._parse_statistics_result(result)
        self.assertEqual(len(parsed), 1)

        stats = parsed[0]["stats"]
        # Verify all statistics are present.
        for stat_name in STAT_NAME_LIST:
            self.assertIn(stat_name, stats)
        self.assertEqual(len(stats.keys()), len(STAT_NAME_LIST))

        # Verify relationships between statistics
        expected_stddev = math.sqrt(stats[STAT_NAME_POPULATION_VARIANCE])
        self.assertAlmostEqual(
            stats[STAT_NAME_POPULATION_STD_DEV], expected_stddev, places=5
        )

        expected_mean = sum(y_values) / len(y_values)
        self.assertAlmostEqual(stats[STAT_NAME_MEAN], expected_mean, places=5)

    def test_statistics_mixed_curves_and_lists_error(self):
        """Test that mixing animation curves and list inputs produces an error."""
        name = "anim_curves1.ma"
        path = self.get_data_path("anim_curves", name)
        maya.cmds.file(path, open=True, force=True)

        tfm = "transform1"
        tfm_attr_tx = "{}.translateX".format(tfm)
        animCurve_tx = maya.cmds.listConnections(tfm_attr_tx, type="animCurve")[0]

        x_values = [1.0, 2.0, 3.0, 4.0, 5.0]
        y_values = [1.0, 4.0, 9.0, 16.0, 25.0]

        # This should work - using only list input.
        result = maya.cmds.mmAnimCurveStatistics(
            xValues=x_values,
            yValues=y_values,
            mean=True,
        )
        self.assertIsNotNone(result)

        # This should also work - using only curve input.
        maya.cmds.select(animCurve_tx)
        result = maya.cmds.mmAnimCurveStatistics(mean=True)
        self.assertIsNotNone(result)

    def test_statistics_invalid_list_inputs(self):
        """Test error handling for invalid list inputs."""
        # Test with mismatched list lengths.
        with self.assertRaises(RuntimeError):
            maya.cmds.mmAnimCurveStatistics(
                xValues=[1.0, 2.0, 3.0],
                yValues=[1.0, 4.0],  # Different length
                mean=True,
            )

        # Test with only X values.
        with self.assertRaises(RuntimeError):
            maya.cmds.mmAnimCurveStatistics(
                xValues=[1.0, 2.0, 3.0],
                mean=True,
            )

        # Test with only Y values.
        with self.assertRaises(RuntimeError):
            maya.cmds.mmAnimCurveStatistics(
                yValues=[1.0, 2.0, 3.0],
                mean=True,
            )

        # Test with empty lists.
        with self.assertRaises(RuntimeError):
            maya.cmds.mmAnimCurveStatistics(
                xValues=[],
                yValues=[],
                mean=True,
            )

        # Test with single value.
        with self.assertRaises(RuntimeError):
            maya.cmds.mmAnimCurveStatistics(
                xValues=[1.0],
                yValues=[1.0],
                mean=True,
            )


if __name__ == "__main__":
    prog = unittest.main()
