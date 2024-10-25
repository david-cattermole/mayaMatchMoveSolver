//
// Copyright (C) 2022 David Cattermole.
//
// This file is part of mmSolver.
//
// mmSolver is free software: you can redistribute it and/or modify it
// under the terms of the GNU Lesser General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// mmSolver is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
// ====================================================================
//
/// Line Regression.
use log::debug;

use crate::constant::Real;

const EPSILON: Real = 1.0e-9;

fn impl_vector2d_normalize(dir_x: &mut Real, dir_y: &mut Real) {
    let dir_magnitude = ((*dir_x) * (*dir_x) + (*dir_y) * (*dir_y)).sqrt();
    if dir_magnitude.abs() > EPSILON {
        *dir_x = *dir_x / dir_magnitude;
        *dir_y = *dir_y / dir_magnitude;
    }
}

fn impl_precompute_line_fit_data(
    x: &[Real],
    y: &[Real],
    out_sum_x: &mut Real,
    out_sum_y: &mut Real,
    out_sum_xy: &mut Real,
    out_sum_x2: &mut Real,
    out_sum_y2: &mut Real,
    out_mean_x: &mut Real,
    out_mean_y: &mut Real,
) -> bool {
    let num = x.len().min(y.len());
    if num < 2 {
        // One point does not define a line, we need at least 2.
        return false;
    }

    *out_sum_x = 0.0;
    *out_sum_y = 0.0;
    *out_sum_xy = 0.0;
    *out_sum_x2 = 0.0;
    *out_sum_y2 = 0.0;
    for (xx, yy) in x.iter().zip(y) {
        *out_sum_x += xx;
        *out_sum_y += yy;
        *out_sum_xy += xx * yy;
        *out_sum_x2 += xx * xx;
        *out_sum_y2 += yy * yy;
    }

    let count = num as Real;
    *out_mean_x = *out_sum_x / count;
    *out_mean_y = *out_sum_y / count;

    true
}

fn impl_fit_line_to_points_type1(
    sum_x: Real,
    sum_xy: Real,
    sum_x2: Real,
    mean_x: Real,
    mean_y: Real,
    out_intercept: &mut Real,
    out_slope: &mut Real,
) -> bool {
    let denominator = sum_x2 - sum_x * mean_x;
    if denominator.abs() < EPSILON {
        // The line is vertical, and so this will fail.
        false
    } else {
        *out_slope = (sum_xy - sum_x * mean_y) / denominator;
        *out_intercept = mean_y - *out_slope * mean_x;
        true
    }
}

fn impl_combine_values_logic(
    ok_a: bool,
    ok_b: bool,
    intercept_a: Real,
    slope_a: Real,
    slope_b: Real,
    mean_x: Real,
    mean_y: Real,
    out_point_x: &mut Real,
    out_point_y: &mut Real,
    out_dir_x: &mut Real,
    out_dir_y: &mut Real,
) -> bool {
    debug!("ok_a={ok_a} ok_b={ok_b}");

    if ok_a && ok_b {
        // Both linear regressions returned.

        // Transpose the values, because of the swapped values given
        // to the impl_fit_line_to_points_type1() function.
        let slope_b = slope_b.recip().min(std::f64::MAX).copysign(slope_a);
        assert_eq!(slope_a.signum(), slope_b.signum());

        *out_point_x = mean_x;
        *out_point_y = mean_y;

        let slope = slope_a.signum() * (slope_a * slope_b).sqrt();
        let angle = slope.atan();
        *out_dir_x = angle.sin();
        *out_dir_y = angle.cos();

        debug!("slope_a={slope_a} slope_b={slope_b}");
        debug!("angle={angle} slope={slope}");

        true
    } else if ok_a && !ok_b {
        // The special case that the line is entirely vertical.
        *out_point_x = intercept_a;
        *out_point_y = mean_y;

        let angle = slope_a.atan();
        *out_dir_x = angle.sin();
        *out_dir_y = angle.cos();

        debug!("slope_a={slope_a} intercept_a={intercept_a}");
        debug!("angle={angle}");

        true
    } else if !ok_a && ok_b {
        // The special case that the line is entirely horizontal.

        // Transpose the values, because of the swapped values given
        // to the impl_fit_line_to_points_type1() function.
        let slope_b = slope_b.recip().min(std::f64::MAX);

        *out_point_x = mean_x;
        *out_point_y = mean_y;

        let angle = (-slope_b).atan();
        *out_dir_x = angle.sin();
        *out_dir_y = angle.cos();

        debug!("slope_b={slope_b}");
        debug!("angle={angle}");

        true
    } else {
        false
    }
}

pub fn fit_line_to_points_type1(
    x: &[Real],
    y: &[Real],
    out_intercept: &mut Real,
    out_dir_x: &mut Real,
    out_dir_y: &mut Real,
    out_mean_x: &mut Real,
    out_mean_y: &mut Real,
) -> bool {
    let mut sum_x: Real = 0.0;
    let mut sum_y: Real = 0.0;
    let mut sum_xy: Real = 0.0;
    let mut sum_x2: Real = 0.0;
    let mut sum_y2: Real = 0.0;
    let mut mean_x: Real = 0.0;
    let mut mean_y: Real = 0.0;
    let mut slope: Real = 0.0;

    let ok = impl_precompute_line_fit_data(
        &x,
        &y,
        &mut sum_x,
        &mut sum_y,
        &mut sum_xy,
        &mut sum_x2,
        &mut sum_y2,
        &mut mean_x,
        &mut mean_y,
    );
    if !ok {
        return false;
    }

    let ok = impl_fit_line_to_points_type1(
        sum_x,
        sum_xy,
        sum_x2,
        mean_x,
        mean_y,
        out_intercept,
        &mut slope,
    );
    if ok {
        *out_mean_x = mean_x;
        *out_mean_y = mean_y;

        let angle = slope.atan();
        *out_dir_x = angle.sin();
        *out_dir_y = angle.cos();
    }
    ok
}

pub fn curve_fit_linear_regression_type1(
    x: &[Real],
    y: &[Real],
    out_mean_x: &mut Real,
    out_mean_y: &mut Real,
    out_angle: &mut Real,
) -> bool {
    let mut sum_x: Real = 0.0;
    let mut sum_y: Real = 0.0;
    let mut sum_xy: Real = 0.0;
    let mut sum_x2: Real = 0.0;
    let mut sum_y2: Real = 0.0;
    let mut mean_x: Real = 0.0;
    let mut mean_y: Real = 0.0;

    let ok = impl_precompute_line_fit_data(
        &x,
        &y,
        &mut sum_x,
        &mut sum_y,
        &mut sum_xy,
        &mut sum_x2,
        &mut sum_y2,
        &mut mean_x,
        &mut mean_y,
    );
    if !ok {
        return false;
    }

    let mut intercept: Real = 0.0;
    let mut slope: Real = 0.0;
    let ok = impl_fit_line_to_points_type1(
        sum_x,
        sum_xy,
        sum_x2,
        mean_x,
        mean_y,
        &mut intercept,
        &mut slope,
    );
    if ok {
        *out_mean_x = mean_x;
        *out_mean_y = mean_y;

        *out_angle = slope.atan();
        let angle_degree = out_angle.to_degrees();
        println!(
            "fit_line_to_points_type1_curve angle={out_angle} degrees={angle_degree}"
        );
    }
    ok
}

/// Fits a Line to X and Y data, using "Linear Regression Type II".
///
/// This function will correctly fit a data set regardless if the line
/// is (almost) perfectly vertical or horizontal.
///
/// For a brief understanding of the differences between Type/Model I
/// and II, see this:
/// https://www.mbari.org/introduction-to-model-i-and-model-ii-linear-regressions/
pub fn fit_line_to_points_type2(
    x: &[Real],
    y: &[Real],
    out_point_x: &mut Real,
    out_point_y: &mut Real,
    out_dir_x: &mut Real,
    out_dir_y: &mut Real,
) -> bool {
    assert_eq!(x.len(), y.len());

    let mut sum_x: Real = 0.0;
    let mut sum_y: Real = 0.0;
    let mut sum_xy: Real = 0.0;
    let mut sum_x2: Real = 0.0;
    let mut sum_y2: Real = 0.0;
    let mut mean_x: Real = 0.0;
    let mut mean_y: Real = 0.0;

    let ok = impl_precompute_line_fit_data(
        &x,
        &y,
        &mut sum_x,
        &mut sum_y,
        &mut sum_xy,
        &mut sum_x2,
        &mut sum_y2,
        &mut mean_x,
        &mut mean_y,
    );
    if !ok {
        return false;
    }

    // Swap the X and Y coordinates.
    let mut intercept_a = 0.0;
    let mut slope_a = 0.0;
    let ok_a = impl_fit_line_to_points_type1(
        sum_y,
        sum_xy,
        sum_y2,
        mean_y,
        mean_x,
        &mut intercept_a,
        &mut slope_a,
    );

    let mut intercept_b = 0.0;
    let mut slope_b = 0.0;
    let ok_b = impl_fit_line_to_points_type1(
        sum_x,
        sum_xy,
        sum_x2,
        mean_x,
        mean_y,
        &mut intercept_b,
        &mut slope_b,
    );

    impl_combine_values_logic(
        ok_a,
        ok_b,
        intercept_a,
        slope_a,
        slope_b,
        mean_x,
        mean_y,
        out_point_x,
        out_point_y,
        out_dir_x,
        out_dir_y,
    )
}

/// Approximates a perfectly straight line from a set of (ordered) line
/// points from a (mostly) straight line.
///
/// Assumes the data points are ordered. That is, the data is a
/// sequence of points that define line segments and connect together
/// to create a line.
///
/// points_coord_x: X position coordiates for points. Must have same length as 'points_coord_y'.
/// points_coord_y: Y position coordiates for points. Must have same length as 'points_coord_x'.
/// out_point_x: Center X coordinate of the computed line.
/// out_point_y: Center Y coordinate of the computed line.
/// out_dir_x: Direction X of the computed line.
/// out_dir_y: Direction Y of the computed line.
///
/// out_dir_x and out_dir_y are normalized if they were a 2D direction
/// vector.
pub fn fit_straight_line_to_ordered_points<'a>(
    points_coord_x: &'a [Real],
    points_coord_y: &'a [Real],
    out_point_x: &mut Real,
    out_point_y: &mut Real,
    out_dir_x: &mut Real,
    out_dir_y: &mut Real,
) -> bool {
    assert_eq!(points_coord_x.len(), points_coord_y.len());

    let points_count = points_coord_x.len();

    let mut mean_x = 0.0 as Real;
    let mut mean_y = 0.0 as Real;
    for v in points_coord_x.iter() {
        mean_x += v;
    }
    for v in points_coord_y.iter() {
        mean_y += v;
    }
    mean_x = mean_x / (points_count as Real);
    mean_y = mean_y / (points_count as Real);
    *out_point_x = mean_x;
    *out_point_y = mean_y;

    let mut dir_x = 0.0;
    let mut dir_y = 0.0;
    let mut previous_x = points_coord_x[0];
    let mut previous_y = points_coord_y[0];
    for (x, y) in points_coord_x[1..].iter().zip(points_coord_y[1..].iter()) {
        dir_x += x - previous_x;
        dir_y += y - previous_y;
        previous_x = *x;
        previous_y = *y;
    }

    impl_vector2d_normalize(&mut dir_x, &mut dir_y);
    *out_dir_x = dir_x;
    *out_dir_y = dir_y;

    true
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;

    const EPSILON: Real = 1.0e-5;

    #[test]
    fn test_fit_line_to_points_type1_1() {
        let x = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let y = vec![3.0, 4.0, 5.0, 6.0, 8.0];

        let mut intercept: Real = 0.0;
        let mut dir_x: Real = 0.0;
        let mut dir_y: Real = 0.0;
        let mut mean_x: Real = 0.0;
        let mut mean_y: Real = 0.0;
        let ok = fit_line_to_points_type1(
            &x,
            &y,
            &mut intercept,
            &mut dir_x,
            &mut dir_y,
            &mut mean_x,
            &mut mean_y,
        );
        assert_eq!(ok, true);

        let slope: Real = dir_x / dir_y;
        println!("intercept: {}", intercept);
        println!("slope: {}", slope);
        println!("dir_x: {}", dir_x);
        println!("dir_y: {}", dir_y);
        println!("mean_x: {}", mean_x);
        println!("mean_y: {}", mean_y);

        assert_relative_eq!(intercept, 1.6, epsilon = EPSILON);
        assert_relative_eq!(slope, 1.2, epsilon = EPSILON);
        assert_relative_eq!(mean_x, 3.0, epsilon = EPSILON);
        assert_relative_eq!(mean_y, 5.2, epsilon = EPSILON);
        assert_relative_eq!(dir_x, 0.7682212795973759, epsilon = EPSILON);
        assert_relative_eq!(dir_y, 0.6401843996644798, epsilon = EPSILON);
    }

    #[test]
    fn test_fit_line_to_points_type1_2() {
        let x = vec![
            1714.0, 1664.0, 1760.0, 1685.0, 1693.0, 1670.0, 1764.0, 1764.0,
            1792.0, 1850.0, 1735.0, 1775.0, 1735.0, 1712.0, 1773.0, 1872.0,
            1755.0, 1674.0, 1842.0, 1786.0, 1761.0, 1722.0, 1663.0, 1687.0,
            1974.0, 1826.0, 1787.0, 1821.0, 2020.0, 1794.0, 1769.0, 1934.0,
            1775.0, 1855.0, 1880.0, 1849.0, 1808.0, 1954.0, 1777.0, 1831.0,
            1865.0, 1850.0, 1966.0, 1702.0, 1990.0, 1925.0, 1824.0, 1956.0,
            1857.0, 1979.0, 1802.0, 1855.0, 1907.0, 1634.0, 1879.0, 1887.0,
            1730.0, 1953.0, 1781.0, 1891.0, 1964.0, 1808.0, 1893.0, 2041.0,
            1893.0, 1832.0, 1850.0, 1934.0, 1861.0, 1931.0, 1933.0, 1778.0,
            1975.0, 1934.0, 2021.0, 2015.0, 1997.0, 2020.0, 1843.0, 1936.0,
            1810.0, 1987.0, 1962.0, 2050.0,
        ];
        let y = vec![
            2.4, 2.52, 2.54, 2.74, 2.83, 2.91, 3.0, 3.0, 3.01, 3.01, 3.02,
            3.07, 3.08, 3.08, 3.12, 3.17, 3.17, 3.17, 3.17, 3.19, 3.19, 3.19,
            3.2, 3.21, 3.24, 3.28, 3.28, 3.28, 3.28, 3.28, 3.28, 3.28, 3.29,
            3.29, 3.29, 3.31, 3.32, 3.34, 3.37, 3.37, 3.37, 3.38, 3.38, 3.39,
            3.39, 3.4, 3.4, 3.4, 3.41, 3.41, 3.41, 3.42, 3.42, 3.42, 3.44,
            3.47, 3.47, 3.47, 3.47, 3.48, 3.49, 3.49, 3.5, 3.51, 3.51, 3.52,
            3.52, 3.54, 3.58, 3.58, 3.59, 3.59, 3.6, 3.6, 3.61, 3.62, 3.64,
            3.65, 3.71, 3.71, 3.71, 3.73, 3.76, 3.81,
        ];

        let mut intercept: Real = 0.0;
        let mut dir_x: Real = 0.0;
        let mut dir_y: Real = 0.0;
        let mut mean_x: Real = 0.0;
        let mut mean_y: Real = 0.0;
        let ok = fit_line_to_points_type1(
            &x,
            &y,
            &mut intercept,
            &mut dir_x,
            &mut dir_y,
            &mut mean_x,
            &mut mean_y,
        );

        assert_eq!(ok, true);

        let slope: Real = dir_x / dir_y;
        println!("intercept: {}", intercept);
        println!("slope: {}", slope);
        println!("dir_x: {}", dir_x);
        println!("dir_y: {}", dir_y);
        println!("mean_x: {}", mean_x);
        println!("mean_y: {}", mean_y);

        assert_relative_eq!(intercept, 0.27504, epsilon = EPSILON);
        assert_relative_eq!(slope, 0.00165565, epsilon = EPSILON);
        assert_relative_eq!(mean_x, 1845.2738, epsilon = EPSILON);
        assert_relative_eq!(mean_y, 3.330238, epsilon = EPSILON);
        assert_relative_eq!(dir_x, 0.001655685780726433, epsilon = EPSILON);
        assert_relative_eq!(dir_y, 0.9999986293513584, epsilon = EPSILON);
    }

    #[test]
    fn test_fit_line_to_points_type1_3() {
        let x = vec![
            83.0, 71.0, 64.0, 69.0, 69.0, 64.0, 68.0, 59.0, 81.0, 91.0, 57.0,
            65.0, 58.0, 62.0,
        ];

        let y = vec![
            183.0, 168.0, 171.0, 178.0, 176.0, 172.0, 165.0, 158.0, 183.0,
            182.0, 163.0, 175.0, 164.0, 175.0,
        ];

        let mut intercept: Real = 0.0;
        let mut dir_x: Real = 0.0;
        let mut dir_y: Real = 0.0;
        let mut mean_x: Real = 0.0;
        let mut mean_y: Real = 0.0;
        let ok = fit_line_to_points_type1(
            &x,
            &y,
            &mut intercept,
            &mut dir_x,
            &mut dir_y,
            &mut mean_x,
            &mut mean_y,
        );

        assert_eq!(ok, true);

        let slope: Real = dir_x / dir_y;
        println!("intercept: {}", intercept);
        println!("slope: {}", slope);
        println!("dir_x: {}", dir_x);
        println!("dir_y: {}", dir_y);
        println!("mean_x: {}", mean_x);
        println!("mean_y: {}", mean_y);

        assert_relative_eq!(intercept, 129.5721, epsilon = EPSILON);
        assert_relative_eq!(slope, 0.62329927, epsilon = EPSILON);
        assert_relative_eq!(mean_x, 68.64285714, epsilon = EPSILON);
        assert_relative_eq!(mean_y, 172.3571429, epsilon = EPSILON);
        assert_relative_eq!(dir_x, 0.5289606532087621, epsilon = EPSILON);
        assert_relative_eq!(dir_y, 0.8486463499933053, epsilon = EPSILON);
    }

    #[test]
    fn test_fit_line_to_points_type1_4() {
        let x = vec![1.5, 2.4, 3.2, 4.8, 5.0, 7.0, 8.43];
        let y = vec![3.5, 5.3, 7.7, 6.2, 11.0, 9.5, 10.27];

        let mut intercept: Real = 0.0;
        let mut dir_x: Real = 0.0;
        let mut dir_y: Real = 0.0;
        let mut mean_x: Real = 0.0;
        let mut mean_y: Real = 0.0;
        let ok = fit_line_to_points_type1(
            &x,
            &y,
            &mut intercept,
            &mut dir_x,
            &mut dir_y,
            &mut mean_x,
            &mut mean_y,
        );
        assert_eq!(ok, true);

        let slope: Real = dir_x / dir_y;
        println!("intercept: {}", intercept);
        println!("slope: {}", slope);
        println!("dir_x: {}", dir_x);
        println!("dir_y: {}", dir_y);
        println!("mean_x: {}", mean_x);
        println!("mean_y: {}", mean_y);

        assert_relative_eq!(intercept, 3.46212, epsilon = EPSILON);
        assert_relative_eq!(slope, 0.904273, epsilon = EPSILON);
        assert_relative_eq!(mean_x, 4.61857, epsilon = EPSILON);
        assert_relative_eq!(mean_y, 7.63857, epsilon = EPSILON);
        assert_relative_eq!(dir_x, 0.6707138074200799, epsilon = EPSILON);
        assert_relative_eq!(dir_y, 0.7417162452960431, epsilon = EPSILON);
    }

    #[test]
    fn test_fit_line_to_points_type2_1() {
        let x = vec![
            -0.3688522990709718,
            -0.36980964203725525,
            -0.3700151319901966,
            -0.36988012681264837,
            -0.3680363719268923,
        ];
        let y = vec![
            -0.42468134270856445,
            -0.2084985089326494,
            0.007684324843265656,
            0.2212148852763163,
            0.3931911714326893,
        ];

        let mut point_x: Real = 0.0;
        let mut point_y: Real = 0.0;
        let mut dir_x: Real = 0.0;
        let mut dir_y: Real = 0.0;
        let ok = fit_line_to_points_type2(
            &x,
            &y,
            &mut point_x,
            &mut point_y,
            &mut dir_x,
            &mut dir_y,
        );
        assert_eq!(ok, true);

        let slope: Real = dir_x / dir_y;
        println!("point_x: {}", point_x);
        println!("point_y: {}", point_y);
        println!("dir_x: {}", dir_x);
        println!("dir_y: {}", dir_y);
        println!("slope: {}", slope);

        assert_relative_eq!(point_x, -0.3693187143675929, epsilon = EPSILON);
        assert_relative_eq!(point_y, -0.0022178940177885243, epsilon = EPSILON);
        assert_relative_eq!(slope, 0.002606265777458439, epsilon = EPSILON);
        assert_relative_eq!(dir_x, 0.0026062569258153137, epsilon = EPSILON);
        assert_relative_eq!(dir_y, 0.999996603706651, epsilon = EPSILON);
    }

    #[test]
    fn test_fit_line_to_points_type2_2() {
        // All X values are perfectly flat, this will cause the linear
        // regression to fail in this axis.
        //
        // The line should aim directly up-wards (vertical).
        let x = vec![-0.3, -0.3, -0.3, -0.3, -0.3];
        let y = vec![-0.4, -0.2, 0.00, 0.2, 0.4];

        let mut point_x: Real = 0.0;
        let mut point_y: Real = 0.0;
        let mut dir_x: Real = 0.0;
        let mut dir_y: Real = 0.0;
        let ok = fit_line_to_points_type2(
            &x,
            &y,
            &mut point_x,
            &mut point_y,
            &mut dir_x,
            &mut dir_y,
        );
        assert_eq!(ok, true);

        let slope: Real = dir_y / dir_x;
        println!("point_x: {}", point_x);
        println!("point_y: {}", point_y);
        println!("dir_x: {}", dir_x);
        println!("dir_y: {}", dir_y);
        println!("slope: {}", slope);

        assert_relative_eq!(point_x, -0.3, epsilon = EPSILON);
        assert_relative_eq!(point_y, 0.0, epsilon = EPSILON);
        assert_relative_eq!(slope, -2.4019198012642652e16, epsilon = EPSILON);
        assert_relative_eq!(dir_x, 0.0, epsilon = EPSILON);
        assert_relative_eq!(dir_y, 1.0, epsilon = EPSILON);
    }

    #[test]
    fn test_fit_line_to_points_type2_3() {
        // All Y values are perfectly flat, this will cause the linear
        // regression to fail in this axis.
        //
        // The line should aim directly sideways (horizontal).
        let x = vec![-0.4, -0.2, 0.00, 0.2, 0.4];
        let y = vec![-0.3, -0.3, -0.3, -0.3, -0.3];

        let mut point_x: Real = 0.0;
        let mut point_y: Real = 0.0;
        let mut dir_x: Real = 0.0;
        let mut dir_y: Real = 0.0;
        let ok = fit_line_to_points_type2(
            &x,
            &y,
            &mut point_x,
            &mut point_y,
            &mut dir_x,
            &mut dir_y,
        );
        assert_eq!(ok, true);

        let slope: Real = dir_y / dir_x;
        println!("point_x: {}", point_x);
        println!("point_y: {}", point_y);
        println!("dir_x: {}", dir_x);
        println!("dir_y: {}", dir_y);
        println!("slope: {}", slope);

        assert_relative_eq!(point_x, 0.0, epsilon = EPSILON);
        assert_relative_eq!(point_y, -0.3, epsilon = EPSILON);
        assert_relative_eq!(slope, 0.0, epsilon = EPSILON);
        assert_relative_eq!(dir_x, 1.0, epsilon = EPSILON);
        assert_relative_eq!(dir_y, 0.0, epsilon = EPSILON);
    }

    #[test]
    fn test_fit_line_to_points_type2_4() {
        let x = vec![-0.2, 0.0, 0.2];
        let y = vec![-0.2, 0.2, -0.2];

        let mut point_x: Real = 0.0;
        let mut point_y: Real = 0.0;
        let mut dir_x: Real = 0.0;
        let mut dir_y: Real = 0.0;
        let ok = fit_line_to_points_type2(
            &x,
            &y,
            &mut point_x,
            &mut point_y,
            &mut dir_x,
            &mut dir_y,
        );
        assert_eq!(ok, true);

        let slope: Real = dir_y / dir_x;
        println!("point_x: {}", point_x);
        println!("point_y: {}", point_y);
        println!("dir_x: {}", dir_x);
        println!("dir_y: {}", dir_y);
        println!("slope: {}", slope);

        assert_relative_eq!(point_x, 0.0, epsilon = EPSILON);
        assert_relative_eq!(point_y, -0.06666666666666667, epsilon = EPSILON);
        assert_relative_eq!(slope, Real::INFINITY, epsilon = EPSILON);
        assert_relative_eq!(dir_x, 0.0, epsilon = EPSILON);
        assert_relative_eq!(dir_y, 1.0, epsilon = EPSILON);
    }

    #[test]
    fn test_fit_straight_line_to_ordered_points_1() {
        let x = vec![-0.3, 0.0, 0.3];
        let y = vec![3.60239e-16, 0.3, -1.41612e-15];

        let mut point_x: Real = 0.0;
        let mut point_y: Real = 0.0;
        let mut dir_x: Real = 0.0;
        let mut dir_y: Real = 0.0;
        let ok = fit_straight_line_to_ordered_points(
            &x,
            &y,
            &mut point_x,
            &mut point_y,
            &mut dir_x,
            &mut dir_y,
        );
        assert_eq!(ok, true);

        let slope: Real = dir_y / dir_x;
        println!("point_x: {}", point_x);
        println!("point_y: {}", point_y);
        println!("dir_x: {}", dir_x);
        println!("dir_y: {}", dir_y);
        println!("slope: {}", slope);

        assert_relative_eq!(point_x, 0.0, epsilon = EPSILON);
        assert_relative_eq!(point_y, 0.1, epsilon = EPSILON);
        assert_relative_eq!(dir_x, 1.0, epsilon = EPSILON);
        assert_relative_eq!(dir_y, 0.0, epsilon = EPSILON);
        assert_relative_eq!(slope, 0.0, epsilon = EPSILON);
        assert_relative_eq!(dir_x, 1.0, epsilon = EPSILON);
        assert_relative_eq!(dir_y, 0.0, epsilon = EPSILON);
    }

    #[test]
    fn test_fit_straight_line_to_ordered_points_2() {
        let x = vec![-0.3, -0.15, 0.0, 0.15, 0.3];
        let y = vec![3.60239e-16, 0.15, 0.3, 0.15, -1.41612e-15];

        let mut point_x: Real = 0.0;
        let mut point_y: Real = 0.0;
        let mut dir_x: Real = 0.0;
        let mut dir_y: Real = 0.0;
        let ok = fit_straight_line_to_ordered_points(
            &x,
            &y,
            &mut point_x,
            &mut point_y,
            &mut dir_x,
            &mut dir_y,
        );
        assert_eq!(ok, true);

        let slope: Real = dir_y / dir_x;
        println!("point_x: {}", point_x);
        println!("point_y: {}", point_y);
        println!("dir_x: {}", dir_x);
        println!("dir_y: {}", dir_y);
        println!("slope: {}", slope);

        assert_relative_eq!(point_x, 0.0, epsilon = EPSILON);
        assert_relative_eq!(point_y, 0.12, epsilon = EPSILON);
        assert_relative_eq!(dir_x, 1.0, epsilon = EPSILON);
        assert_relative_eq!(dir_y, 0.0, epsilon = EPSILON);
        assert_relative_eq!(slope, 0.0, epsilon = EPSILON);
        assert_relative_eq!(dir_x, 1.0, epsilon = EPSILON);
        assert_relative_eq!(dir_y, 0.0, epsilon = EPSILON);
    }
}
