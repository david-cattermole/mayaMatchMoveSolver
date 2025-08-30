//
// Copyright (C) 2024 David Cattermole.
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

use plotters::prelude::*;

#[allow(unused_imports)]
use log::debug;

use anyhow::Result;
use std::ffi::OsStr;

use mmscenegraph_rust::constant::FrameTime;
use mmscenegraph_rust::constant::Real;
use mmscenegraph_rust::math::curve_fit::AngleRadian;
use mmscenegraph_rust::math::curve_fit::Point2;
use mmscenegraph_rust::math::interpolate::Interpolation;

use crate::common::chart_utils::{
    calculate_bounds, calculate_bounds_vec, configure_chart_legend,
    draw_line_series, ChartCoord, DrawingBackendResult,
};
use crate::common::curve_generation::{
    create_control_points_from_point_and_dir,
    create_control_points_from_points, create_control_points_line,
    create_interpolated_curve_from_3_points,
    create_interpolated_curve_from_control_points, generate_fitted_line_values,
};
use crate::common::data_utils::calculate_quality_of_fit;

#[allow(dead_code)]
pub fn save_chart_linear_regression(
    data_raw: &[(FrameTime, Real)],
    data: &[(FrameTime, Real)],
    point: Point2,
    angle: AngleRadian,
    chart_title: &str,
    chart_file_path: &OsStr,
    chart_resolution: (u32, u32),
) -> Result<()> {
    let root_area = BitMapBackend::new(
        chart_file_path,
        (chart_resolution.0, chart_resolution.1),
    )
    .into_drawing_area();
    root_area.fill(&WHITE)?;

    let root_area = root_area.titled(chart_title, ("sans-serif", 60))?;

    let x_first = data[0].0;
    let y_first = data[0].1;
    let x_last = data[data.len() - 1].0;
    let y_last = data[data.len() - 1].1;
    let x_diff = (x_last - x_first) as Real / 2.0;
    let y_diff = (y_last - y_first) as Real / 2.0;
    debug!("x_first={x_first}");
    debug!("y_first={y_first}");
    debug!("x_last={x_last}");
    debug!("y_last={y_last}");
    debug!("x_diff={x_diff}");
    debug!("y_diff={y_diff}");

    let x_line_coords = vec![x_first, x_last];
    let y_line_values =
        generate_fitted_line_values(&x_line_coords, point, angle);
    let line: Vec<(f64, Real)> = x_line_coords
        .iter()
        .zip(y_line_values.iter())
        .map(|(&x, &y)| (x, y))
        .collect();
    debug!("line: {:#?}", line);

    let bounds = calculate_bounds(&[data_raw, data, &line], None);
    let x_pad = 0.1;
    let y_pad = 0.1;
    let chart_min_value_x = bounds.x_min - x_pad;
    let chart_max_value_x = bounds.x_max + x_pad;
    let chart_min_value_y = bounds.y_min - y_pad;
    let chart_max_value_y = bounds.y_max + y_pad;

    // Calculate quality of fit by comparing raw data to actual fitted line.
    let raw_x_values: Vec<FrameTime> =
        data_raw.iter().map(|(x, _)| *x).collect();
    let raw_y_values: Vec<f64> =
        data_raw.iter().map(|(_, y)| *y as f64).collect();
    let fitted_line_y_values =
        generate_fitted_line_values(&raw_x_values, point, angle);
    let fitted_y_values: Vec<f64> =
        fitted_line_y_values.iter().map(|&y| y as f64).collect();
    let quality = calculate_quality_of_fit(&raw_y_values, &fitted_y_values)
        .unwrap_or(0.0);

    let chart_caption = format!("Quality: {:.2}%", quality);

    let mut cc = ChartBuilder::on(&root_area)
        .margin(5)
        .set_all_label_area_size(50)
        .caption(&chart_caption, ("sans-serif", 40))
        .build_cartesian_2d(
            chart_min_value_x..chart_max_value_x,
            chart_min_value_y..chart_max_value_y,
        )?;

    cc.configure_mesh()
        .x_labels(20)
        .y_labels(10)
        .disable_mesh()
        .x_label_formatter(&|v| format!("{:.1}", v))
        .y_label_formatter(&|v| format!("{:.1}", v))
        .draw()?;

    draw_line_series(&mut cc, data_raw, &RED, 2, Some("Raw Data"))?;
    draw_line_series(&mut cc, data, &BLUE, 2, Some("Input Data"))?;
    draw_line_series(&mut cc, &line, &GREEN, 2, Some("Fitted Line"))?;

    configure_chart_legend(&mut cc)?;

    // To avoid the IO failure being ignored silently, we manually
    // call the present function.
    root_area.present()?;
    debug!("Chart saved to: {:?}", chart_file_path);

    Ok(())
}

#[allow(dead_code)]
pub fn save_chart_linear_regression_pop(
    data_raw: &[(FrameTime, Real)],
    data_pop: &[(FrameTime, Real)],
    data_filtered: &[(FrameTime, Real)],
    point: Point2,
    angle: AngleRadian,
    chart_title: &str,
    chart_file_path: &OsStr,
    chart_resolution: (u32, u32),
) -> Result<()> {
    let root_area = BitMapBackend::new(
        chart_file_path,
        (chart_resolution.0, chart_resolution.1),
    )
    .into_drawing_area();
    root_area.fill(&WHITE)?;

    let root_area = root_area.titled(chart_title, ("sans-serif", 60))?;
    let bounds = calculate_bounds(&[data_raw, data_pop, data_filtered], None);

    let x_first = data_pop[0].0;
    let y_first = data_pop[0].1;
    let x_last = data_pop[data_pop.len() - 1].0;
    let y_last = data_pop[data_pop.len() - 1].1;
    let x_diff = (x_last - x_first) as Real / 2.0;
    let y_diff = (y_last - y_first) as Real / 2.0;
    debug!("x_first={x_first}");
    debug!("y_first={y_first}");
    debug!("x_last={x_last}");
    debug!("y_last={y_last}");
    debug!("x_diff={x_diff}");
    debug!("y_diff={y_diff}");

    let x_line_coords = vec![x_first, x_last];
    let y_line_values =
        generate_fitted_line_values(&x_line_coords, point, angle);
    let line: Vec<(f64, Real)> = x_line_coords
        .iter()
        .zip(y_line_values.iter())
        .map(|(&x, &y)| (x, y))
        .collect();
    debug!("line: {:#?}", line);

    let x_pad = 0.1;
    let y_pad = 0.1;
    let chart_min_value_x = bounds.x_min - x_pad;
    let chart_max_value_x = bounds.x_max + x_pad;
    let chart_min_value_y = bounds.y_min - y_pad;
    let chart_max_value_y = bounds.y_max + y_pad;

    // Calculate quality of fit by comparing raw data to pop data.
    let raw_y_values: Vec<f64> =
        data_raw.iter().map(|(_, y)| *y as f64).collect();
    let pop_y_values: Vec<f64> =
        data_pop.iter().map(|(_, y)| *y as f64).collect();
    let quality =
        calculate_quality_of_fit(&raw_y_values, &pop_y_values).unwrap_or(0.0);

    let chart_caption = format!("Quality: {:.2}%", quality);

    let mut cc = ChartBuilder::on(&root_area)
        .margin(5)
        .set_all_label_area_size(50)
        .caption(&chart_caption, ("sans-serif", 40))
        .build_cartesian_2d(
            chart_min_value_x..chart_max_value_x,
            chart_min_value_y..chart_max_value_y,
        )?;

    cc.configure_mesh()
        .x_labels(20)
        .y_labels(10)
        .disable_mesh()
        .x_label_formatter(&|v| format!("{:.1}", v))
        .y_label_formatter(&|v| format!("{:.1}", v))
        .draw()?;

    draw_line_series(&mut cc, data_raw, &RED, 2, Some("Raw Data"))?;
    draw_line_series(&mut cc, data_pop, &BLUE, 2, Some("Pop Data"))?;
    draw_line_series(&mut cc, data_filtered, &CYAN, 2, Some("Filtered Data"))?;
    draw_line_series(&mut cc, &line, &GREEN, 2, Some("Fitted Line"))?;

    configure_chart_legend(&mut cc)?;

    // To avoid the IO failure being ignored silently, we manually
    // call the present function.
    root_area.present()?;
    debug!("Chart saved to: {:?}", chart_file_path);

    Ok(())
}

#[allow(dead_code)]
pub fn save_chart_n3_regression(
    data_raw: &[(FrameTime, Real)],
    data: &[(FrameTime, Real)],
    point_a: Point2,
    point_b: Point2,
    point_c: Point2,
    interpolation_method: Interpolation,
    chart_title: &str,
    chart_file_path: &OsStr,
    chart_resolution: (u32, u32),
) -> Result<()> {
    let root_area = BitMapBackend::new(
        chart_file_path,
        (chart_resolution.0, chart_resolution.1),
    )
    .into_drawing_area();
    root_area.fill(&WHITE)?;

    let root_area = root_area.titled(chart_title, ("sans-serif", 60))?;

    let x_sample_values: Vec<f64> = data.iter().map(|(x, _)| *x).collect();
    let control_points_line =
        create_control_points_from_points(point_a, point_b, point_c);
    debug!("control points line: {:#?}", control_points_line);

    let interpolated_line = create_interpolated_curve_from_3_points(
        &x_sample_values,
        point_a,
        point_b,
        point_c,
        interpolation_method,
    );
    debug!("interpolated line: {:#?}", interpolated_line);

    let bounds = calculate_bounds(
        &[data_raw, data, &control_points_line, &interpolated_line],
        None,
    );

    let x_pad = 0.1;
    let y_pad = 0.1;
    let chart_min_value_x = bounds.x_min - x_pad;
    let chart_max_value_x = bounds.x_max + x_pad;
    let chart_min_value_y = bounds.y_min - y_pad;
    let chart_max_value_y = bounds.y_max + y_pad;

    // Calculate quality of fit by comparing raw data to interpolated
    // curve.
    let raw_y_values: Vec<f64> =
        data_raw.iter().map(|(_, y)| *y as f64).collect();
    let fitted_y_values: Vec<f64> =
        interpolated_line.iter().map(|(_, y)| *y as f64).collect();
    let quality = calculate_quality_of_fit(&raw_y_values, &fitted_y_values)
        .unwrap_or(0.0);

    let chart_caption = format!("Quality: {:.2}%", quality);

    let mut cc = ChartBuilder::on(&root_area)
        .margin(5)
        .set_all_label_area_size(50)
        .caption(&chart_caption, ("sans-serif", 40))
        .build_cartesian_2d(
            chart_min_value_x..chart_max_value_x,
            chart_min_value_y..chart_max_value_y,
        )?;

    cc.configure_mesh()
        .x_labels(20)
        .y_labels(10)
        .disable_mesh()
        .x_label_formatter(&|v| format!("{:.0}", v))
        .y_label_formatter(&|v| format!("{:.1}", v))
        .draw()?;

    draw_line_series(&mut cc, data_raw, &RED, 2, Some("Raw Data"))?;
    draw_line_series(&mut cc, data, &BLUE, 2, Some("Input Data"))?;
    draw_line_series(
        &mut cc,
        &control_points_line,
        &GREEN,
        2,
        Some("Control Points"),
    )?;
    draw_line_series(
        &mut cc,
        &interpolated_line,
        &MAGENTA,
        2,
        Some("Interpolated Curve"),
    )?;

    configure_chart_legend(&mut cc)?;

    // To avoid the IO failure being ignored silently, we manually
    // call the present function.
    root_area.present()?;
    debug!("Chart saved to: {:?}", chart_file_path);

    Ok(())
}

#[allow(dead_code)]
pub fn save_chart_linear_n3_regression_pop(
    data_raw: &[(FrameTime, Real)],
    data_pop: &[(FrameTime, Real)],
    data_filtered: &[(FrameTime, Real)],
    point_a: Point2,
    point_b: Point2,
    point_c: Point2,
    chart_title: &str,
    chart_file_path: &OsStr,
    chart_resolution: (u32, u32),
) -> Result<()> {
    let root_area = BitMapBackend::new(
        chart_file_path,
        (chart_resolution.0, chart_resolution.1),
    )
    .into_drawing_area();
    root_area.fill(&WHITE)?;

    let root_area = root_area.titled(chart_title, ("sans-serif", 60))?;

    let line = create_control_points_from_points(point_a, point_b, point_c);
    debug!("line: {:#?}", line);

    let bounds =
        calculate_bounds(&[data_raw, data_pop, data_filtered, &line], None);
    let x_pad = 0.1;
    let y_pad = 0.1;
    let chart_min_value_x = bounds.x_min - x_pad;
    let chart_max_value_x = bounds.x_max + x_pad;
    let chart_min_value_y = bounds.y_min - y_pad;
    let chart_max_value_y = bounds.y_max + y_pad;

    // Calculate quality of fit by comparing raw data to pop data.
    let raw_y_values: Vec<f64> =
        data_raw.iter().map(|(_, y)| *y as f64).collect();
    let pop_y_values: Vec<f64> =
        data_pop.iter().map(|(_, y)| *y as f64).collect();
    let quality =
        calculate_quality_of_fit(&raw_y_values, &pop_y_values).unwrap_or(0.0);

    let chart_caption = format!("Quality: {:.2}%", quality);

    let mut cc = ChartBuilder::on(&root_area)
        .margin(5)
        .set_all_label_area_size(50)
        .caption(&chart_caption, ("sans-serif", 40))
        .build_cartesian_2d(
            chart_min_value_x..chart_max_value_x,
            chart_min_value_y..chart_max_value_y,
        )?;

    cc.configure_mesh()
        .x_labels(20)
        .y_labels(10)
        .disable_mesh()
        .x_label_formatter(&|v| format!("{:.0}", v))
        .y_label_formatter(&|v| format!("{:.1}", v))
        .draw()?;

    draw_line_series(&mut cc, data_raw, &RED, 2, Some("Raw Data"))?;
    draw_line_series(&mut cc, data_pop, &BLUE, 2, Some("Pop Data"))?;
    draw_line_series(&mut cc, data_filtered, &CYAN, 2, Some("Filtered Data"))?;
    draw_line_series(&mut cc, &line, &GREEN, 2, Some("Control Points"))?;

    configure_chart_legend(&mut cc)?;

    // To avoid the IO failure being ignored silently, we manually
    // call the present function.
    root_area.present()?;
    debug!("Chart saved to: {:?}", chart_file_path);

    Ok(())
}

#[allow(dead_code)]
pub fn save_chart_n_points_regression(
    data_raw: &[(FrameTime, Real)],
    data: &[(FrameTime, Real)],
    control_points: &[Point2],
    interpolation_method: Interpolation,
    chart_title: &str,
    chart_file_path: &OsStr,
    chart_resolution: (u32, u32),
) -> Result<()> {
    let root_area = BitMapBackend::new(
        chart_file_path,
        (chart_resolution.0, chart_resolution.1),
    )
    .into_drawing_area();
    root_area.fill(&WHITE)?;

    let root_area = root_area.titled(chart_title, ("sans-serif", 60))?;

    let x_sample_values: Vec<f64> = data.iter().map(|(x, _)| *x).collect();
    let control_points_line = create_control_points_line(control_points);
    let interpolated_line = create_interpolated_curve_from_control_points(
        &x_sample_values,
        control_points,
        interpolation_method,
    );

    let bounds = calculate_bounds(
        &[data_raw, data, &control_points_line, &interpolated_line],
        None,
    );
    let x_pad = 0.1;
    let y_pad = 0.1;
    let chart_min_value_x = bounds.x_min - x_pad;
    let chart_max_value_x = bounds.x_max + x_pad;
    let chart_min_value_y = bounds.y_min - y_pad;
    let chart_max_value_y = bounds.y_max + y_pad;

    let raw_y_values: Vec<f64> =
        data_raw.iter().map(|(_, y)| *y as f64).collect();
    let fitted_y_values: Vec<f64> =
        interpolated_line.iter().map(|(_, y)| *y as f64).collect();
    let quality = calculate_quality_of_fit(&raw_y_values, &fitted_y_values)
        .unwrap_or(0.0);

    let chart_caption = format!("Quality: {:.2}%", quality);

    let mut cc = ChartBuilder::on(&root_area)
        .margin(5)
        .set_all_label_area_size(50)
        .caption(&chart_caption, ("sans-serif", 40))
        .build_cartesian_2d(
            chart_min_value_x..chart_max_value_x,
            chart_min_value_y..chart_max_value_y,
        )?;

    cc.configure_mesh()
        .x_labels(20)
        .y_labels(10)
        .disable_mesh()
        .x_label_formatter(&|v| format!("{:.0}", v))
        .y_label_formatter(&|v| format!("{:.1}", v))
        .draw()?;

    draw_line_series(&mut cc, data_raw, &RED, 2, Some("Raw Data"))?;
    draw_line_series(&mut cc, data, &BLUE, 2, Some("Input Data"))?;
    draw_line_series(
        &mut cc,
        &control_points_line,
        &GREEN,
        2,
        Some("Control Points"),
    )?;
    draw_line_series(
        &mut cc,
        &interpolated_line,
        &MAGENTA,
        2,
        Some("Interpolated Curve"),
    )?;

    configure_chart_legend(&mut cc)?;

    // To avoid the IO failure being ignored silently, we manually
    // call the present function.
    root_area.present()?;
    debug!("Chart saved to: {:?}", chart_file_path);

    Ok(())
}

#[allow(dead_code)]
pub fn save_chart_linear_n_points_regression_pop(
    data_raw: &[(FrameTime, Real)],
    data_pop: &[(FrameTime, Real)],
    data_filtered: &[(FrameTime, Real)],
    control_points: &[Point2],
    chart_title: &str,
    chart_file_path: &OsStr,
    chart_resolution: (u32, u32),
) -> Result<()> {
    let root_area = BitMapBackend::new(
        chart_file_path,
        (chart_resolution.0, chart_resolution.1),
    )
    .into_drawing_area();

    root_area.fill(&WHITE)?;

    let root_area = root_area.titled(chart_title, ("sans-serif", 60))?;

    let line = create_control_points_line(&control_points);
    debug!("control points line: {:#?}", line);

    let bounds =
        calculate_bounds(&[data_raw, data_pop, data_filtered, &line], None);
    let x_pad = 0.1;
    let y_pad = 0.1;
    let chart_min_value_x = bounds.x_min - x_pad;
    let chart_max_value_x = bounds.x_max + x_pad;
    let chart_min_value_y = bounds.y_min - y_pad;
    let chart_max_value_y = bounds.y_max + y_pad;

    // Calculate quality of fit by comparing raw data to pop data.
    let raw_y_values: Vec<f64> =
        data_raw.iter().map(|(_, y)| *y as f64).collect();
    let pop_y_values: Vec<f64> =
        data_pop.iter().map(|(_, y)| *y as f64).collect();
    let quality =
        calculate_quality_of_fit(&raw_y_values, &pop_y_values).unwrap_or(0.0);

    let chart_caption = format!("Quality: {:.2}%", quality);

    let mut cc = ChartBuilder::on(&root_area)
        .margin(5)
        .set_all_label_area_size(50)
        .caption(&chart_caption, ("sans-serif", 40))
        .build_cartesian_2d(
            chart_min_value_x..chart_max_value_x,
            chart_min_value_y..chart_max_value_y,
        )?;

    cc.configure_mesh()
        .x_labels(20)
        .y_labels(10)
        .disable_mesh()
        .x_label_formatter(&|v| format!("{:.0}", v))
        .y_label_formatter(&|v| format!("{:.1}", v))
        .draw()?;

    draw_line_series(&mut cc, data_raw, &RED, 2, Some("Raw Data"))?;
    draw_line_series(&mut cc, data_pop, &BLUE, 2, Some("Pop Data"))?;
    draw_line_series(&mut cc, data_filtered, &CYAN, 2, Some("Filtered Data"))?;
    draw_line_series(&mut cc, &line, &GREEN, 2, Some("Control Points"))?;

    configure_chart_legend(&mut cc)?;

    // To avoid the IO failure being ignored silently, we manually
    // call the present function.
    root_area.present()?;
    debug!("Chart saved to: {:?}", chart_file_path);

    Ok(())
}

#[allow(dead_code)]
pub fn save_chart_derivative_curves(
    data_values: &[(FrameTime, Real)],
    data_velocity: &[(FrameTime, Real)],
    data_acceleration: &[(FrameTime, Real)],
    data_jerk: &[(FrameTime, Real)],
    chart_title: &str,
    chart_file_path: &OsStr,
    chart_resolution: (u32, u32),
) -> Result<()> {
    let root_area = BitMapBackend::new(
        chart_file_path,
        (chart_resolution.0, chart_resolution.1),
    )
    .into_drawing_area();

    root_area.fill(&WHITE)?;
    let root_area = root_area.titled(chart_title, ("sans-serif", 60))?;

    let chart_captions = &["Values", "Velocity", "Acceleration", "Jerk"];
    let line_colors = &[BLACK, RED, GREEN, BLUE];
    let data_list = &[data_values, data_velocity, data_acceleration, data_jerk];

    let drawing_areas = root_area.split_evenly((4, 1));
    for (i, drawing_area) in drawing_areas.iter().enumerate() {
        let data = data_list[i];

        let bounds = calculate_bounds(&[data], None);
        let x_pad = 0.1;
        let y_pad = (bounds.y_max - bounds.y_min) * 0.05;
        let chart_min_value_x = bounds.x_min - x_pad;
        let chart_max_value_x = bounds.x_max + x_pad;
        let chart_min_value_y = bounds.y_min - y_pad;
        let chart_max_value_y = bounds.y_max + y_pad;

        let chart_caption = chart_captions[i];
        let mut cc = ChartBuilder::on(drawing_area)
            .margin(5)
            .set_all_label_area_size(50)
            .caption(&chart_caption, ("sans-serif", 20))
            .build_cartesian_2d(
                chart_min_value_x..chart_max_value_x,
                chart_min_value_y..chart_max_value_y,
            )?;

        cc.configure_mesh()
            .x_labels(20)
            .y_labels(5)
            .disable_mesh()
            .x_label_formatter(&|v| format!("{:.0}", v))
            .y_label_formatter(&|v| format!("{:.3}", v))
            .draw()?;

        let line_color = &line_colors[i];
        let chart_caption = chart_captions[i];
        draw_line_series(&mut cc, data, line_color, 1, Some(chart_caption))?;
    }

    // To avoid the IO failure being ignored silently, we manually
    // call the present function.
    root_area.present()?;
    debug!("Chart saved to: {:?}", chart_file_path);

    Ok(())
}

#[allow(dead_code)]
pub fn save_chart_curvature_curves(
    data_values: &[(FrameTime, Real)],
    data_velocity: &[(FrameTime, Real)],
    data_acceleration: &[(FrameTime, Real)],
    data_curvature: &[(FrameTime, Real)],
    chart_title: &str,
    chart_file_path: &OsStr,
    chart_resolution: (u32, u32),
) -> Result<()> {
    let root_area = BitMapBackend::new(
        chart_file_path,
        (chart_resolution.0, chart_resolution.1),
    )
    .into_drawing_area();

    root_area.fill(&WHITE)?;
    let root_area = root_area.titled(chart_title, ("sans-serif", 60))?;

    let chart_captions = &["Values", "Velocity", "Acceleration", "Curvature"];
    let line_colors = &[BLACK, RED, GREEN, BLUE];
    let data_list = &[
        data_values,
        data_velocity,
        data_acceleration,
        data_curvature,
    ];

    let drawing_areas = root_area.split_evenly((4, 1));
    for (i, drawing_area) in drawing_areas.iter().enumerate() {
        let data = data_list[i];

        let bounds = calculate_bounds(&[data], None);
        let x_pad = 0.1;
        let y_pad = (bounds.y_max - bounds.y_min) * 0.05;
        let chart_min_value_x = bounds.x_min - x_pad;
        let chart_max_value_x = bounds.x_max + x_pad;
        let chart_min_value_y = bounds.y_min - y_pad;
        let chart_max_value_y = bounds.y_max + y_pad;

        let chart_caption = chart_captions[i];
        let mut cc = ChartBuilder::on(drawing_area)
            .margin(5)
            .set_all_label_area_size(50)
            .caption(&chart_caption, ("sans-serif", 20))
            .build_cartesian_2d(
                chart_min_value_x..chart_max_value_x,
                chart_min_value_y..chart_max_value_y,
            )?;

        cc.configure_mesh()
            .x_labels(20)
            .y_labels(5)
            .disable_mesh()
            .x_label_formatter(&|v| format!("{:.0}", v))
            .y_label_formatter(&|v| format!("{:.3}", v))
            .draw()?;

        let line_color = &line_colors[i];
        let chart_caption = chart_captions[i];
        draw_line_series(&mut cc, data, line_color, 1, Some(chart_caption))?;
    }

    // To avoid the IO failure being ignored silently, we manually
    // call the present function.
    root_area.present()?;
    debug!("Chart saved to: {:?}", chart_file_path);

    Ok(())
}

#[allow(dead_code)]
pub fn save_chart_curves_compare_two(
    data_a: &[(FrameTime, Real)],
    data_b: &[(FrameTime, Real)],
    chart_title: &str,
    chart_file_path: &OsStr,
    chart_resolution: (u32, u32),
) -> Result<()> {
    let root_area = BitMapBackend::new(
        chart_file_path,
        (chart_resolution.0, chart_resolution.1),
    )
    .into_drawing_area();

    root_area.fill(&WHITE)?;
    let root_area = root_area.titled(chart_title, ("sans-serif", 60))?;

    let data_list = &[data_a, data_b];

    let bounds = calculate_bounds(data_list, None);
    let x_pad = 0.1;
    let y_pad = (bounds.y_max - bounds.y_min) * 0.05;
    let chart_min_value_x = bounds.x_min - x_pad;
    let chart_max_value_x = bounds.x_max + x_pad;
    let chart_min_value_y = bounds.y_min - y_pad;
    let chart_max_value_y = bounds.y_max + y_pad;

    let chart_caption = "Compare Curves A and B";
    let mut cc = ChartBuilder::on(&root_area)
        .margin(5)
        .set_all_label_area_size(50)
        .caption(&chart_caption, ("sans-serif", 20))
        .build_cartesian_2d(
            chart_min_value_x..chart_max_value_x,
            chart_min_value_y..chart_max_value_y,
        )?;

    cc.configure_mesh()
        .x_labels(20)
        .y_labels(5)
        .disable_mesh()
        .x_label_formatter(&|v| format!("{:.0}", v))
        .y_label_formatter(&|v| format!("{:.3}", v))
        .draw()?;

    draw_line_series(&mut cc, data_a, &RED, 2, Some("Curve A"))?;
    draw_line_series(&mut cc, data_b, &GREEN, 2, Some("Curve B"))?;

    configure_chart_legend(&mut cc)?;

    // To avoid the IO failure being ignored silently, we manually
    // call the present function.
    root_area.present()?;
    debug!("Chart saved to: {:?}", chart_file_path);

    Ok(())
}

#[allow(dead_code)]
pub fn save_chart_curves_compare_many(
    data_curves: &Vec<Vec<(FrameTime, Real)>>,
    chart_title: &str,
    chart_file_path: &OsStr,
    chart_resolution: (u32, u32),
) -> Result<()> {
    let root_area = BitMapBackend::new(
        chart_file_path,
        (chart_resolution.0, chart_resolution.1),
    )
    .into_drawing_area();

    root_area.fill(&WHITE)?;
    let root_area = root_area.titled(chart_title, ("sans-serif", 60))?;

    let bounds = calculate_bounds_vec(data_curves, None);

    let x_pad = 0.1;
    let y_pad = (bounds.y_max - bounds.y_min) * 0.05;
    let chart_min_value_x = bounds.x_min - x_pad;
    let chart_max_value_x = bounds.x_max + x_pad;
    let chart_min_value_y = bounds.y_min - y_pad;
    let chart_max_value_y = bounds.y_max + y_pad;

    let chart_caption = "Compare Curves A and B";
    let mut cc = ChartBuilder::on(&root_area)
        .margin(5)
        .set_all_label_area_size(50)
        .caption(&chart_caption, ("sans-serif", 20))
        .build_cartesian_2d(
            chart_min_value_x..chart_max_value_x,
            chart_min_value_y..chart_max_value_y,
        )?;

    cc.configure_mesh()
        .x_labels(20)
        .y_labels(5)
        .disable_mesh()
        .x_label_formatter(&|v| format!("{:.0}", v))
        .y_label_formatter(&|v| format!("{:.3}", v))
        .draw()?;

    let colours = &[&RED, &GREEN, &BLUE, &CYAN, &MAGENTA, &YELLOW];
    for (i, data_curve) in data_curves.iter().enumerate() {
        let colour_index = i.rem_euclid(colours.len());
        let colour = colours[colour_index];
        let label = format!("Curve {}", i + 1);
        draw_line_series(&mut cc, data_curve, colour, 2, Some(&label))?;
    }

    configure_chart_legend(&mut cc)?;

    // To avoid the IO failure being ignored silently, we manually
    // call the present function.
    root_area.present()?;
    debug!("Chart saved to: {:?}", chart_file_path);

    Ok(())
}
