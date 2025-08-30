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

use anyhow::Result;

use mmscenegraph_rust::constant::FrameTime;
use mmscenegraph_rust::constant::Real;
use mmscenegraph_rust::math::curve_fit::Point2;

pub const CHART_RESOLUTION: (u32, u32) = (1024, 1024);

pub struct ChartData {
    pub x_min: FrameTime,
    pub x_max: FrameTime,
    pub y_min: Real,
    pub y_max: Real,
}

pub type ChartCoord = Cartesian2d<RangedCoordf64, RangedCoordf64>;
pub type DrawingBackendResult<'a> = BitMapBackend<'a>;

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

// Calculate bounds for all data series.
pub fn calculate_bounds(
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

// Calculate bounds for all data series.
pub fn calculate_bounds_vec(
    data_series: &Vec<Vec<(FrameTime, Real)>>,
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

// Configure chart legend with consistent styling.
pub fn configure_chart_legend<'a>(
    chart: &mut ChartContext<'a, DrawingBackendResult<'a>, ChartCoord>,
) -> Result<()> {
    chart
        .configure_series_labels()
        .background_style(&WHITE.mix(0.8))
        .border_style(&BLACK)
        .label_font(("sans-serif", 15))
        .position(SeriesLabelPosition::UpperRight)
        .margin(5)
        .draw()
        .map_err(|e| {
            anyhow::anyhow!("Failed to configure chart legend: {}", e)
        })?;
    Ok(())
}

// Draw a line series with specified color and optional legend label.
pub fn draw_line_series<'a>(
    chart: &mut ChartContext<'a, DrawingBackendResult<'a>, ChartCoord>,
    data: &[(FrameTime, Real)],
    color: &'a RGBColor,
    point_size: u32,
    legend_label: Option<&str>,
) -> Result<()> {
    let series = chart
        .draw_series(
            LineSeries::new(data.iter().map(|x| (x.0 as f64, x.1)), color)
                .point_size(point_size),
        )
        .map_err(|e| anyhow::anyhow!("Failed to draw line series: {}", e))?;

    if let Some(label) = legend_label {
        series.label(label).legend(move |(x, y)| {
            PathElement::new(vec![(x, y), (x + 10, y)], color)
        });
    }

    Ok(())
}
