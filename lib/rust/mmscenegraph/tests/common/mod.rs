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

use plotters::coord::types::RangedCoordf64;
use plotters::prelude::*;

#[allow(unused_imports)]
use log::debug;

use anyhow::bail;
use anyhow::Result;

use std::ffi::OsStr;
use std::fs::File;
use std::io::Read;
use std::path::Path;
use std::path::PathBuf;

use mmscenegraph_rust::constant::FrameTime;
use mmscenegraph_rust::constant::Real;
use mmscenegraph_rust::math::curve_fit::AngleRadian;
use mmscenegraph_rust::math::curve_fit::Point2;

pub const CHART_RESOLUTION: (u32, u32) = (1024, 1024);

#[allow(dead_code)]
pub fn find_data_dir() -> Result<PathBuf> {
    let directory = PathBuf::from("C:/Users/catte/dev/mayaMatchMoveSolver/lib/rust/mmscenegraph/tests/data/");
    if directory.is_dir() {
        Ok(directory)
    } else {
        bail!("Could not find data directory directory.")
    }
}

#[allow(dead_code)]
pub fn construct_input_file_path(
    base_dir: &Path,
    file_name: &str,
) -> Result<PathBuf> {
    let mut file_path = PathBuf::new();
    file_path.push(base_dir);
    file_path.push(file_name);
    if !file_path.is_file() {
        bail!("Could not find file name {:?}", file_path);
    }
    Ok(file_path)
}

#[allow(dead_code)]
pub fn construct_output_file_path(
    base_dir: &Path,
    file_name: &str,
) -> Result<PathBuf> {
    let mut file_path = PathBuf::new();
    file_path.push(base_dir);
    file_path.push(file_name);
    Ok(file_path)
}

#[allow(dead_code)]
pub fn read_chan_file(file_name: &OsStr) -> Result<Vec<(FrameTime, Real)>> {
    let mut file = File::open(file_name)?;
    let mut buffer = String::new();
    file.read_to_string(&mut buffer)?;

    let mut data = Vec::new();
    for line in buffer.lines() {
        let mut line_iter = line.split_ascii_whitespace();
        let line_start = line_iter.next().expect("First frame number.");
        let line_end = line_iter.next().expect("Second value.");

        let frame = line_start
            .parse::<FrameTime>()
            .expect("Frame number must be integer.");
        let value = line_end
            .parse::<Real>()
            .expect("Value must be floating-point.");
        data.push((frame, value));
    }

    Ok(data)
}

#[allow(dead_code)]
pub fn print_chan_data(data: &[(FrameTime, Real)]) {
    for pair in data {
        let frame: FrameTime = pair.0;
        let value: Real = pair.1;
        println!("frame={frame} value={value}");
    }
}

#[allow(dead_code)]
pub fn print_actual_pops(
    x_values: &[f64],
    y_values_pop: &[f64],
    y_values_raw: &[f64],
    threshold: f64,
) -> Vec<f64> {
    println!("print_actual_pops: start");
    let mut out = Vec::new();
    for (x, (y_pop, y_raw)) in
        x_values.iter().zip(y_values_pop.iter().zip(y_values_raw))
    {
        let diff = (y_raw - y_pop).abs();
        if diff > threshold {
            println!("print_actual_pop: x={x} diff={diff}");
            out.push(*x)
        }
    }
    println!("print_actual_pops: end; count={}", out.len());

    out
}

#[allow(dead_code)]
pub fn print_derivative_arrays(
    velocity: &[f64],
    acceleration: &[f64],
    jerk: &[f64],
) {
    println!("Velocity (1st order derivative) count {} :", velocity.len());
    for (i, v) in velocity.iter().enumerate() {
        println!("i={i} v={v}");
    }

    println!(
        "Acceleration (2nd order derivative) count {} :",
        acceleration.len()
    );
    for (i, v) in acceleration.iter().enumerate() {
        println!("i={i} v={v}");
    }

    println!("Jerk (3rd order derivative) count {} :", jerk.len());
    for (i, v) in jerk.iter().enumerate() {
        println!("i={i} v={v}");
    }
}

#[allow(dead_code)]
pub fn print_curvature_arrays(
    velocity: &[f64],
    acceleration: &[f64],
    curvature: &[f64],
) {
    println!("Velocity (1st order derivative) count {} :", velocity.len());
    for (i, v) in velocity.iter().enumerate() {
        println!("i={i} v={v}");
    }

    println!(
        "Acceleration (2nd order derivative) count {} :",
        acceleration.len()
    );
    for (i, v) in acceleration.iter().enumerate() {
        println!("i={i} v={v}");
    }

    println!("Curvature count {} :", curvature.len());
    for (i, v) in curvature.iter().enumerate() {
        println!("i={i} v={v}");
    }
}

#[allow(dead_code)]
pub fn chan_data_filter_only_x(data: &[(FrameTime, Real)]) -> Vec<Real> {
    data.iter().map(|x| x.0 as Real).collect()
}

#[allow(dead_code)]
pub fn chan_data_filter_only_y(data: &[(FrameTime, Real)]) -> Vec<Real> {
    data.iter().map(|x| x.1 as Real).collect()
}

#[allow(dead_code)]
pub fn chan_data_combine_xy(
    x_values: &[FrameTime],
    y_values: &[Real],
) -> Vec<(FrameTime, Real)> {
    assert_eq!(x_values.len(), y_values.len());
    x_values
        .iter()
        .zip(y_values.iter())
        .map(|x| (*x.0, *x.1))
        .collect()
}

fn calculate_data_min_max_values(
    data: &[(FrameTime, Real)],
    out_x_min: &mut FrameTime,
    out_x_max: &mut FrameTime,
    out_y_min: &mut Real,
    out_y_max: &mut Real,
) {
    for (x, y) in data.iter() {
        let x = *x as FrameTime;
        let y = *y as Real;

        if x.is_finite() {
            if x < *out_x_min {
                *out_x_min = x;
            }

            if x > *out_x_max {
                *out_x_max = x;
            }
        }

        if y.is_finite() {
            if y < *out_y_min {
                *out_y_min = y;
            }

            if y > *out_y_max {
                *out_y_max = y;
            }
        }
    }
}

fn calculate_control_point_min_max_values(
    control_points: &[Point2],
    out_x_min: &mut FrameTime,
    out_x_max: &mut FrameTime,
    out_y_min: &mut Real,
    out_y_max: &mut Real,
) {
    for control_point in control_points {
        let x = control_point.x();
        let y = control_point.y();

        if x.is_finite() {
            if x < *out_x_min {
                *out_x_min = x;
            }

            if x > *out_x_max {
                *out_x_max = x;
            }
        }

        if y.is_finite() {
            if y < *out_y_min {
                *out_y_min = y;
            }

            if y > *out_y_max {
                *out_y_max = y;
            }
        }
    }
}

struct ChartData {
    x_min: FrameTime,
    x_max: FrameTime,
    y_min: Real,
    y_max: Real,
}

// Calculate bounds for all data series
fn calculate_bounds(
    data_series: &[&[(FrameTime, Real)]],
    control_points: Option<&[Point2]>,
) -> ChartData {
    let mut bounds = ChartData {
        x_min: FrameTime::MAX,
        x_max: FrameTime::MIN,
        y_min: Real::MAX,
        y_max: Real::MIN,
    };

    for data in data_series {
        calculate_data_min_max_values(
            data,
            &mut bounds.x_min,
            &mut bounds.x_max,
            &mut bounds.y_min,
            &mut bounds.y_max,
        );
    }

    if let Some(points) = control_points {
        calculate_control_point_min_max_values(
            points,
            &mut bounds.x_min,
            &mut bounds.x_max,
            &mut bounds.y_min,
            &mut bounds.y_max,
        );
    }

    bounds
}

// Generate caption for control points
fn generate_control_points_caption(control_points: &[Point2]) -> String {
    control_points
        .iter()
        .enumerate()
        .map(|(i, p)| format!("P{}y={:.3}", i, p.y()))
        .collect::<Vec<_>>()
        .join(" ")
}

type ChartCoord = Cartesian2d<RangedCoordf64, RangedCoordf64>;
type DrawingBackendResult<'a> = BitMapBackend<'a>;

// Draw a line series with specified color
fn draw_line_series<'a>(
    chart: &mut ChartContext<'a, DrawingBackendResult, ChartCoord>,
    data: &[(FrameTime, Real)],
    color: &RGBColor,
    point_size: u32,
) -> Result<()> {
    chart
        .draw_series(
            LineSeries::new(data.iter().map(|x| (x.0 as f64, x.1)), color)
                .point_size(point_size),
        )
        .map_err(|e| anyhow::anyhow!("Failed to draw line series: {}", e))?;
    Ok(())
}

// Create a control points line with proper type conversion
fn create_control_points_line(points: &[Point2]) -> Vec<(f64, Real)> {
    points.iter().map(|p| (p.x() as f64, p.y())).collect()
}

fn create_control_points_from_points(
    point_a: Point2,
    point_b: Point2,
    point_c: Point2,
) -> Vec<(f64, Real)> {
    let mut line = Vec::<(FrameTime, Real)>::new();
    line.push((point_a.x(), point_a.y()));
    line.push((point_b.x(), point_b.y()));
    line.push((point_c.x(), point_c.y()));
    line
}

fn create_control_points_from_point_and_dir(
    point: Point2,
    dir_x: Real,
    dir_y: Real,
) -> Vec<(f64, Real)> {
    let mut line = Vec::<(FrameTime, Real)>::new();
    line.push(((point.x() as Real - dir_x) as FrameTime, point.y() - dir_y));
    line.push((point.x() as FrameTime, point.y()));
    line.push(((point.x() as Real + dir_x) as FrameTime, point.y() + dir_y));
    line
}

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
    let bounds = calculate_bounds(&[data_raw, data], None);

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

    let (dir_x, dir_y) = angle.as_direction();

    // Scale up to X axis range.
    let dir_x = dir_x * x_diff;
    let dir_y = dir_y * x_diff;

    let line = create_control_points_from_point_and_dir(point, dir_x, dir_y);
    debug!("line: {:#?}", line);

    let x_pad = 0.1;
    let y_pad = 0.1;
    let chart_min_value_x = bounds.x_min - x_pad;
    let chart_max_value_x = bounds.x_max + x_pad;
    let chart_min_value_y = bounds.y_min - y_pad;
    let chart_max_value_y = bounds.y_max + y_pad;

    let angle = angle.as_degrees();
    let chart_caption = format!("angle: {angle}");

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

    draw_line_series(&mut cc, data_raw, &RED, 2)?;
    draw_line_series(&mut cc, data, &BLUE, 2)?;
    draw_line_series(&mut cc, &line, &GREEN, 2)?;

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

    let (dir_x, dir_y) = angle.as_direction();

    // Scale up to X axis range.
    let dir_x = dir_x * x_diff;
    let dir_y = dir_y * x_diff;

    let line = create_control_points_from_point_and_dir(point, dir_x, dir_y);
    debug!("line: {:#?}", line);

    let x_pad = 0.1;
    let y_pad = 0.1;
    let chart_min_value_x = bounds.x_min - x_pad;
    let chart_max_value_x = bounds.x_max + x_pad;
    let chart_min_value_y = bounds.y_min - y_pad;
    let chart_max_value_y = bounds.y_max + y_pad;

    let angle = angle.as_degrees();
    let chart_caption = format!("angle: {angle}");

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

    draw_line_series(&mut cc, data_raw, &RED, 2)?;
    draw_line_series(&mut cc, data_pop, &BLUE, 2)?;
    draw_line_series(&mut cc, data_filtered, &CYAN, 2)?;
    draw_line_series(&mut cc, &line, &GREEN, 2)?;

    // To avoid the IO failure being ignored silently, we manually
    // call the present function.
    root_area.present()?;
    debug!("Chart saved to: {:?}", chart_file_path);

    Ok(())
}

#[allow(dead_code)]
pub fn save_chart_linear_n3_regression(
    data_raw: &[(FrameTime, Real)],
    data: &[(FrameTime, Real)],
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
    let bounds = calculate_bounds(&[data_raw, data], None);

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

    let line = create_control_points_from_points(point_a, point_b, point_c);
    debug!("line: {:#?}", line);

    let x_pad = 0.1;
    let y_pad = 0.1;
    let chart_min_value_x = bounds.x_min - x_pad;
    let chart_max_value_x = bounds.x_max + x_pad;
    let chart_min_value_y = bounds.y_min - y_pad;
    let chart_max_value_y = bounds.y_max + y_pad;

    let chart_caption = format!(
        "Ay={:.3} By={:.3} Cy={:.3}",
        point_a.y(),
        point_b.y(),
        point_c.y()
    );

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

    draw_line_series(&mut cc, data_raw, &RED, 2)?;
    draw_line_series(&mut cc, data, &BLUE, 2)?;
    draw_line_series(&mut cc, &line, &GREEN, 2)?;

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

    let line = create_control_points_from_points(point_a, point_b, point_c);
    debug!("line: {:#?}", line);

    let x_pad = 0.1;
    let y_pad = 0.1;
    let chart_min_value_x = bounds.x_min - x_pad;
    let chart_max_value_x = bounds.x_max + x_pad;
    let chart_min_value_y = bounds.y_min - y_pad;
    let chart_max_value_y = bounds.y_max + y_pad;

    let chart_caption = format!(
        "Ay={:.3} By={:.3} Cy={:.3}",
        point_a.y(),
        point_b.y(),
        point_c.y()
    );

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

    draw_line_series(&mut cc, data_raw, &RED, 2)?;
    draw_line_series(&mut cc, data_pop, &BLUE, 2)?;
    draw_line_series(&mut cc, data_filtered, &CYAN, 2)?;
    draw_line_series(&mut cc, &line, &GREEN, 2)?;

    // To avoid the IO failure being ignored silently, we manually
    // call the present function.
    root_area.present()?;
    debug!("Chart saved to: {:?}", chart_file_path);

    Ok(())
}

#[allow(dead_code)]
pub fn save_chart_linear_n_points_regression(
    data_raw: &[(FrameTime, Real)],
    data: &[(FrameTime, Real)],
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
    let bounds = calculate_bounds(&[data_raw, data], None);
    let line = create_control_points_line(&control_points);

    let x_pad = 0.1;
    let y_pad = 0.1;
    let chart_min_value_x = bounds.x_min - x_pad;
    let chart_max_value_x = bounds.x_max + x_pad;
    let chart_min_value_y = bounds.y_min - y_pad;
    let chart_max_value_y = bounds.y_max + y_pad;

    let chart_caption = generate_control_points_caption(control_points);

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

    draw_line_series(&mut cc, data_raw, &RED, 2)?;
    draw_line_series(&mut cc, data, &BLUE, 2)?;
    draw_line_series(&mut cc, &line, &GREEN, 2)?;

    // To avoid the IO failure being ignored silently, we manually
    // call the present function
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
    let bounds = calculate_bounds(&[data_raw, data_pop, data_filtered], None);
    let line = create_control_points_line(&control_points);
    debug!("control points line: {:#?}", line);

    let x_pad = 0.1;
    let y_pad = 0.1;
    let chart_min_value_x = bounds.x_min - x_pad;
    let chart_max_value_x = bounds.x_max + x_pad;
    let chart_min_value_y = bounds.y_min - y_pad;
    let chart_max_value_y = bounds.y_max + y_pad;

    let chart_caption = generate_control_points_caption(control_points);

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

    draw_line_series(&mut cc, data_raw, &RED, 2)?;
    draw_line_series(&mut cc, data_pop, &BLUE, 2)?;
    draw_line_series(&mut cc, data_filtered, &CYAN, 2)?;
    draw_line_series(&mut cc, &line, &GREEN, 2)?;

    // To avoid the IO failure being ignored silently, we manually
    // call the present function
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

        let line_color = line_colors[i];
        draw_line_series(&mut cc, data, &line_color, 1)?;
    }

    // To avoid the IO failure being ignored silently, we manually
    // call the present function
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

        let line_color = line_colors[i];
        draw_line_series(&mut cc, data, &line_color, 1)?;
    }

    // To avoid the IO failure being ignored silently, we manually
    // call the present function
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

    draw_line_series(&mut cc, data_a, &RED, 2)?;
    draw_line_series(&mut cc, data_b, &GREEN, 2)?;

    // To avoid the IO failure being ignored silently, we manually
    // call the present function
    root_area.present()?;
    debug!("Chart saved to: {:?}", chart_file_path);

    Ok(())
}
