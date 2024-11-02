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

pub fn find_data_dir() -> Result<PathBuf> {
    let directory = PathBuf::from("C:/Users/catte/dev/mayaMatchMoveSolver/lib/rust/mmscenegraph/tests/data/");
    if directory.is_dir() {
        Ok(directory)
    } else {
        bail!("Could not find data directory directory.")
    }
}

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

pub fn construct_output_file_path(
    base_dir: &Path,
    file_name: &str,
) -> Result<PathBuf> {
    let mut file_path = PathBuf::new();
    file_path.push(base_dir);
    file_path.push(file_name);
    Ok(file_path)
}

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

pub fn chan_data_filter_only_x(data: &[(FrameTime, Real)]) -> Vec<Real> {
    data.iter().map(|x| x.0 as Real).collect()
}

pub fn chan_data_filter_only_y(data: &[(FrameTime, Real)]) -> Vec<Real> {
    data.iter().map(|x| x.1 as Real).collect()
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

        if x < *out_x_min {
            *out_x_min = x;
        } else if x > *out_x_max {
            *out_x_max = x;
        }

        if y < *out_y_min {
            *out_y_min = y;
        } else if y > *out_y_max {
            *out_y_max = y;
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

        if x < *out_x_min {
            *out_x_min = x;
        } else if x > *out_x_max {
            *out_x_max = x;
        }

        if y < *out_y_min {
            *out_y_min = y;
        } else if y > *out_y_max {
            *out_y_max = y;
        }
    }
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

    let mut x_min: FrameTime = FrameTime::MAX;
    let mut x_max: FrameTime = FrameTime::MIN;
    let mut y_min: Real = Real::MAX;
    let mut y_max: Real = Real::MIN;

    calculate_data_min_max_values(
        data_raw, &mut x_min, &mut x_max, &mut y_min, &mut y_max,
    );
    calculate_data_min_max_values(
        data, &mut x_min, &mut x_max, &mut y_min, &mut y_max,
    );
    debug!("x_min={x_min}");
    debug!("x_max={x_max}");
    debug!("y_min={y_min}");
    debug!("y_max={y_max}");

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

    let mut line = Vec::<(FrameTime, Real)>::new();
    line.push(((point.x() as Real - dir_x) as FrameTime, point.y() - dir_y));
    line.push((point.x() as FrameTime, point.y()));
    line.push(((point.x() as Real + dir_x) as FrameTime, point.y() + dir_y));
    debug!("line: {:#?}", line);

    let angle = angle.as_degrees();
    let chart_caption = format!("angle: {angle}");

    let x_pad = 0.1;
    let y_pad = 0.1;
    let chart_min_value_x = x_min - x_pad;
    let chart_max_value_x = x_max + x_pad;
    let chart_min_value_y = y_min - y_pad;
    let chart_max_value_y = y_max + y_pad;

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

    cc.draw_series(
        LineSeries::new(data_raw.iter().map(|x| (x.0, x.1)), &RED)
            .point_size(2),
    )
    .unwrap();

    cc.draw_series(
        LineSeries::new(data.iter().map(|x| (x.0, x.1)), &BLUE).point_size(2),
    )
    .unwrap();

    cc.draw_series(LineSeries::new(line.iter().map(|x| (x.0, x.1)), &GREEN))
        .unwrap();

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

    let mut x_min: FrameTime = FrameTime::MAX;
    let mut x_max: FrameTime = FrameTime::MIN;
    let mut y_min: Real = Real::MAX;
    let mut y_max: Real = Real::MIN;
    calculate_data_min_max_values(
        data_raw, &mut x_min, &mut x_max, &mut y_min, &mut y_max,
    );
    calculate_data_min_max_values(
        data, &mut x_min, &mut x_max, &mut y_min, &mut y_max,
    );
    debug!("x_min={x_min}");
    debug!("x_max={x_max}");
    debug!("y_min={y_min}");
    debug!("y_max={y_max}");

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

    let mut line = Vec::<(FrameTime, Real)>::new();
    line.push((point_a.x(), point_a.y()));
    line.push((point_b.x(), point_b.y()));
    line.push((point_c.x(), point_c.y()));
    debug!("line: {:#?}", line);

    let chart_caption = format!(
        "Ay={:.3} By={:.3} Cy={:.3}",
        point_a.y(),
        point_b.y(),
        point_c.y()
    );

    let x_pad = 0.1;
    let y_pad = 0.1;
    let chart_min_value_x = x_min - x_pad;
    let chart_max_value_x = x_max + x_pad;
    let chart_min_value_y = y_min - y_pad;
    let chart_max_value_y = y_max + y_pad;

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

    cc.draw_series(
        LineSeries::new(data_raw.iter().map(|x| (x.0, x.1)), &RED)
            .point_size(2),
    )
    .unwrap();

    cc.draw_series(
        LineSeries::new(data.iter().map(|x| (x.0, x.1)), &BLUE).point_size(2),
    )
    .unwrap();

    cc.draw_series(
        LineSeries::new(line.iter().map(|x| (x.0, x.1)), &GREEN).point_size(2),
    )
    .unwrap();

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

    // Calculate bounds from raw data, processed data, and control
    // points.
    let mut x_min: FrameTime = FrameTime::MAX;
    let mut x_max: FrameTime = FrameTime::MIN;
    let mut y_min: Real = Real::MAX;
    let mut y_max: Real = Real::MIN;
    calculate_data_min_max_values(
        data_raw, &mut x_min, &mut x_max, &mut y_min, &mut y_max,
    );
    calculate_data_min_max_values(
        data, &mut x_min, &mut x_max, &mut y_min, &mut y_max,
    );
    calculate_control_point_min_max_values(
        control_points,
        &mut x_min,
        &mut x_max,
        &mut y_min,
        &mut y_max,
    );
    debug!("x_min={x_min}");
    debug!("x_max={x_max}");
    debug!("y_min={y_min}");
    debug!("y_max={y_max}");

    // Create control point line series
    let mut line =
        Vec::<(FrameTime, Real)>::with_capacity(control_points.len());
    for control_point in control_points {
        line.push((control_point.x(), control_point.y()));
    }
    debug!("control points line: {:#?}", line);

    // Create caption showing Y values of all control points
    let chart_caption = control_points
        .iter()
        .enumerate()
        .map(|(i, p)| format!("P{}y={:.3}", i, p.y()))
        .collect::<Vec<_>>()
        .join(" ");

    let x_pad = 0.1;
    let y_pad = 0.1;
    let chart_min_value_x = x_min - x_pad;
    let chart_max_value_x = x_max + x_pad;
    let chart_min_value_y = y_min - y_pad;
    let chart_max_value_y = y_max + y_pad;

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

    // Draw original data points in red
    cc.draw_series(
        LineSeries::new(data_raw.iter().map(|x| (x.0, x.1)), &RED)
            .point_size(2),
    )?;

    // Draw processed data points in blue
    cc.draw_series(
        LineSeries::new(data.iter().map(|x| (x.0, x.1)), &BLUE).point_size(2),
    )?;

    // Draw control points and their connecting lines in green
    cc.draw_series(
        LineSeries::new(line.iter().map(|x| (x.0, x.1)), &GREEN).point_size(3),
    )?;

    // To avoid the IO failure being ignored silently, we manually
    // call the present function
    root_area.present()?;
    debug!("Chart saved to: {:?}", chart_file_path);

    Ok(())
}
