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
Test functions for mmAnimCurveSimplify command.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import math

import maya.cmds

import test.test_tools.toolsutils as test_tools_utils

DISTRIBUTION_UNIFORM = 'uniform'
DISTRIBUTION_AUTO_KEYPOINTS = 'auto_keypoints'
DISTRIBUTIONS = [
    DISTRIBUTION_UNIFORM,
    DISTRIBUTION_AUTO_KEYPOINTS,
]

INTERPOLATION_LINEAR = 'linear'
INTERPOLATION_CUBIC_NUBS = 'cubic_nubs'
INTERPOLATION_CUBIC_SPLINE = 'cubic_spline'
INTERPOLATIONS = [
    INTERPOLATION_LINEAR,
    INTERPOLATION_CUBIC_NUBS,
    INTERPOLATION_CUBIC_SPLINE,
]

# Statistic type identifiers from the C++ code.
STAT_TYPE_NORMALIZED_ROOT_MEAN_SQUARE_ERROR = 10

# Statistic name
STAT_NAME_NORMALIZED_ROOT_MEAN_SQUARE_ERROR = "normalized_rmse"


def _parse_diff_statistics_result(result):
    """Parse the result array into a dictionary of statistics."""
    stats = {}
    stat_count = int(result[0])

    i = 1
    for j in range(stat_count):
        stat_type = int(result[i])
        stat_value = result[i + 1]

        if stat_type == STAT_TYPE_NORMALIZED_ROOT_MEAN_SQUARE_ERROR:
            stats[STAT_NAME_NORMALIZED_ROOT_MEAN_SQUARE_ERROR] = stat_value

        i += 2

    return stats


def _calc_quality_of_fit(x_values, actual_values, predicted_values):
    """Calculate curve quality of fit metric using normalized RMSE."""
    result = maya.cmds.mmAnimCurveDiffStatistics(
        xValues=x_values,
        yValuesA=actual_values,
        yValuesB=predicted_values,
        normalizedRootMeanSquareError=True,
    )
    stats = _parse_diff_statistics_result(result)

    nrmse = stats[STAT_NAME_NORMALIZED_ROOT_MEAN_SQUARE_ERROR]
    quality = max(0.0, min(100.0, (1.0 - nrmse) * 100.0))

    return quality


def _query_anim_curve_data(anim_curve_node, start_frame, end_frame):
    """Query animation curve data for a given frame range."""
    x_data = list(range(start_frame, end_frame + 1))

    # Query the curve data for the frame range.
    times = [(x,) for x in x_data]
    y_data = (
        maya.cmds.keyframe(anim_curve_node, time=times, query=True, eval=True) or []
    )

    if maya.cmds.nodeType(anim_curve_node) == "animCurveTA":
        scale_factor = math.radians(1)
        y_data = [y * scale_factor for y in y_data]

    assert len(x_data) > 0
    assert len(x_data) == len(y_data)
    return x_data, y_data


def _calculate_and_print_quality_metrics(
    original_curve_data, anim_curves, start_frame, end_frame
):
    """Calculate and print quality metrics for original vs simplified curves."""
    print("Quality Metrics:")
    qualities = []
    for i, anim_curve in enumerate(anim_curves):
        original_x, original_y = original_curve_data[i]
        simplified_x, simplified_y = _query_anim_curve_data(
            anim_curve, start_frame, end_frame
        )
        quality = _calc_quality_of_fit(original_x, original_y, simplified_y)
        qualities.append(quality)
        print("  {}: Quality of Fit = {:.2f}%".format(anim_curve, quality))

    return qualities


# Quality thresholds by control point count
QUALITY_THRESHOLDS = {
    2: 96.35,  # 2 control points: basic approximation
    3: 96.35,  # 3 control points
    4: 97.0,  # 4 control points
    5: 97.20,  # 5 control points
    16: 97.70,  # 16 control points: high fidelity
}


# @unittest.skip
class TestAnimCurveSimplify(test_tools_utils.ToolsTestCase):
    def _create_scene(self):
        name = 'anim_curves1.ma'
        path = self.get_data_path("anim_curves", name)
        maya.cmds.file(path, open=True, force=True)

        tfm = 'transform1'
        tfm_attr_tx = '{}.translateX'.format(tfm)
        tfm_attr_ty = '{}.translateY'.format(tfm)
        tfm_attr_tz = '{}.translateZ'.format(tfm)
        # print('tfm_attr_tx:', repr(tfm_attr_tx))
        # print('tfm_attr_ty:', repr(tfm_attr_ty))
        # print('tfm_attr_tz:', repr(tfm_attr_tz))
        animCurve_tx = maya.cmds.listConnections(tfm_attr_tx, type='animCurve')[0]
        animCurve_ty = maya.cmds.listConnections(tfm_attr_ty, type='animCurve')[0]
        animCurve_tz = maya.cmds.listConnections(tfm_attr_tz, type='animCurve')[0]

        # print('animCurve_tx:', repr(animCurve_tx))
        # print('animCurve_ty:', repr(animCurve_ty))
        # print('animCurve_ty:', repr(animCurve_ty))
        return (animCurve_tx, animCurve_ty, animCurve_tz)
        # return [animCurve_tx]

    def _save_scene(self, name):
        name = 'animcurve_{}_after.ma'.format(name)
        path = self.get_data_path(name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

    def _test_simplify_with_quality_metrics(
        self,
        control_point_count,
        distributions=None,
        interpolations=None,
        start_frame=None,
        end_frame=None,
    ):
        """Common method to test curve simplification with quality metrics."""
        assert distributions is not None
        assert interpolations is not None
        assert start_frame is not None
        assert end_frame is not None

        min_quality = QUALITY_THRESHOLDS.get(control_point_count, 50.0)

        for distribution in distributions:
            for interpolation in interpolations:
                animCurves = self._create_scene()

                # Store original curve data before simplification
                original_curve_data = []
                for anim_curve in animCurves:
                    x_data, y_data = _query_anim_curve_data(
                        anim_curve, start_frame, end_frame
                    )
                    original_curve_data.append((x_data, y_data))

                maya.cmds.mmAnimCurveSimplify(
                    animCurves,
                    controlPointCount=control_point_count,
                    distribution=distribution,
                    interpolation=interpolation,
                    startFrame=start_frame,
                    endFrame=end_frame,
                )

                # Calculate and print quality metrics
                print(
                    "Test: {} control points, {}, {}".format(
                        control_point_count, distribution, interpolation
                    )
                )
                qualities = _calculate_and_print_quality_metrics(
                    original_curve_data, animCurves, start_frame, end_frame
                )

                # Assert minimum quality
                for quality in qualities:
                    self.assertGreaterEqual(
                        quality,
                        min_quality,
                        "Quality {:.2f}% is below minimum {:.2f}% for {} control points with {} {}".format(
                            quality,
                            min_quality,
                            control_point_count,
                            distribution,
                            interpolation,
                        ),
                    )

                self._save_scene(
                    'simplify_control_points{}_{}_{}'.format(
                        control_point_count, distribution, interpolation
                    )
                )

    def test_simplify_uniform_linear_control_points2(self):
        """Test 2 control points with uniform distribution and linear interpolation."""
        self._test_simplify_with_quality_metrics(
            control_point_count=2,
            distributions=[DISTRIBUTION_UNIFORM],
            interpolations=[INTERPOLATION_LINEAR],
            start_frame=1,
            end_frame=200,
        )

    def test_simplify_control_points3(self):
        """Test 3 control points with various distributions and interpolations."""
        interpolations = [INTERPOLATION_CUBIC_SPLINE, INTERPOLATION_LINEAR]
        self._test_simplify_with_quality_metrics(
            control_point_count=3,
            interpolations=interpolations,
            distributions=DISTRIBUTIONS,
            start_frame=1,
            end_frame=200,
        )

    def test_simplify_control_points4(self):
        """Test 4 control points with all distributions and interpolations."""
        self._test_simplify_with_quality_metrics(
            control_point_count=4,
            distributions=DISTRIBUTIONS,
            interpolations=INTERPOLATIONS,
            start_frame=1,
            end_frame=200,
        )

    def test_simplify_control_points5(self):
        """Test 5 control points with all distributions and interpolations."""
        self._test_simplify_with_quality_metrics(
            control_point_count=5,
            distributions=DISTRIBUTIONS,
            interpolations=INTERPOLATIONS,
            start_frame=1,
            end_frame=200,
        )

    def test_simplify_control_points16(self):
        """Test 16 control points with all distributions and interpolations."""
        self._test_simplify_with_quality_metrics(
            control_point_count=16,
            distributions=DISTRIBUTIONS,
            interpolations=INTERPOLATIONS,
            start_frame=1,
            end_frame=200,
        )


if __name__ == '__main__':
    prog = unittest.main()
