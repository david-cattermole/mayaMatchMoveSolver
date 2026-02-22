//
// Copyright (C) 2025, 2026 David Cattermole.
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

//! Residual error visualization utilities.
//!
//! Creates line plots of reprojection errors with mean and median overlays.

use anyhow::Result;
use plotters::prelude::*;

use super::output_naming::OutputFileNaming;
use crate::camera_residual_error::ResidualStats;

/// Creates a line plot of residual errors with mean and median overlays.
///
/// NaN values in `residuals` are filtered out.
pub fn visualize_residual_errors_line_plot(
    residuals: &[f64],
    stats: &ResidualStats,
    title: &str,
    naming: &OutputFileNaming,
) -> Result<()> {
    let file_path = naming.full_path()?;

    let valid_data: Vec<(usize, f64)> = residuals
        .iter()
        .enumerate()
        .filter(|(_, &val)| val.is_finite())
        .map(|(i, &val)| (i, val))
        .collect();

    if valid_data.is_empty() {
        anyhow::bail!("No valid residual data to plot");
    }

    let resolution = (1920, 1080);
    let area = BitMapBackend::new(&file_path, resolution).into_drawing_area();
    area.fill(&WHITE)?;

    let x_max = residuals.len().saturating_sub(1);
    let y_min = stats.min * 0.95;
    let y_max = stats.max * 1.05;

    let mut chart = ChartBuilder::on(&area)
        .caption(title, ("sans-serif", 24))
        .margin(60)
        .x_label_area_size(50)
        .y_label_area_size(80)
        .build_cartesian_2d(0usize..x_max, y_min..y_max)?;

    chart
        .configure_mesh()
        .x_desc("Point Index")
        .y_desc("Residual Error (pixels)")
        .x_max_light_lines(10)
        .y_max_light_lines(8)
        .draw()?;

    chart
        .draw_series(LineSeries::new(
            valid_data.iter().map(|&(x, y)| (x, y)),
            BLUE.stroke_width(2),
        ))?
        .label("Residual Errors")
        .legend(|(x, y)| {
            PathElement::new(vec![(x, y), (x + 10, y)], BLUE.stroke_width(2))
        });

    chart
        .draw_series(LineSeries::new(
            vec![(0, stats.mean), (x_max, stats.mean)],
            RED.stroke_width(3),
        ))?
        .label(&format!("Mean: {:.4} px", stats.mean))
        .legend(|(x, y)| {
            PathElement::new(vec![(x, y), (x + 10, y)], RED.stroke_width(3))
        });

    chart
        .draw_series(LineSeries::new(
            vec![(0, stats.median), (x_max, stats.median)],
            GREEN.stroke_width(3),
        ))?
        .label(&format!("Median: {:.4} px", stats.median))
        .legend(|(x, y)| {
            PathElement::new(vec![(x, y), (x + 10, y)], GREEN.stroke_width(3))
        });

    chart
        .configure_series_labels()
        .background_style(&WHITE.mix(0.8))
        .border_style(&BLACK)
        .draw()?;

    let stats_text = format!(
        "Statistics:\nCount: {}\nMean: {:.4} px\nMedian: {:.4} px\nStd Dev: {:.4} px\nMin: {:.4} px\nMax: {:.4} px",
        stats.count, stats.mean, stats.median, stats.std_dev, stats.min, stats.max
    );

    let (width, _height) = area.dim_in_pixel();
    let text_x = (width as i32) - 260;
    let text_y = 80i32;

    area.draw(&Rectangle::new(
        [(text_x - 10, text_y - 10), (text_x + 240, text_y + 110)],
        WHITE.filled(),
    ))?;
    area.draw(&Rectangle::new(
        [(text_x - 10, text_y - 10), (text_x + 240, text_y + 110)],
        BLACK.stroke_width(1),
    ))?;

    for (i, line) in stats_text.lines().enumerate() {
        area.draw(&Text::new(
            line,
            (text_x, text_y + (i as i32) * 15),
            ("sans-serif", 12),
        ))?;
    }

    area.present()?;
    println!(
        "Residual error visualization saved to: {}",
        file_path.display()
    );

    Ok(())
}

/// Creates a timeline plot of per-marker reprojection error across all frames.
pub fn visualize_multi_frame_residuals_per_marker(
    per_frame_residuals: &std::collections::HashMap<u32, Vec<f64>>,
    _marker_names: Option<&[String]>,
    stats: &ResidualStats,
    title: &str,
    naming: &OutputFileNaming,
) -> Result<()> {
    let file_path = naming.full_path()?;

    let mut frame_numbers: Vec<u32> =
        per_frame_residuals.keys().copied().collect();
    frame_numbers.sort();

    if frame_numbers.is_empty() {
        anyhow::bail!("No frame data to plot.");
    }

    let num_markers = per_frame_residuals[&frame_numbers[0]].len();
    if num_markers == 0 {
        anyhow::bail!("No marker data to plot.");
    }

    let resolution = (1920, 1080);
    let area = BitMapBackend::new(&file_path, resolution).into_drawing_area();
    area.fill(&WHITE)?;

    let frame_min = *frame_numbers.first().unwrap();
    let frame_max = *frame_numbers.last().unwrap();
    let y_min = if stats.min > 0.0 { 0.0 } else { stats.min * 0.95 };
    let y_max = stats.max * 1.05;

    let mut chart = ChartBuilder::on(&area)
        .caption(title, ("sans-serif", 24))
        .margin(60)
        .x_label_area_size(50)
        .y_label_area_size(80)
        .build_cartesian_2d(frame_min..frame_max, y_min..y_max)?;

    chart
        .configure_mesh()
        .x_desc("Frame Number")
        .y_desc("Reprojection Error (pixels)")
        .x_max_light_lines(10)
        .y_max_light_lines(8)
        .draw()?;

    let marker_color = RGBColor(0, 0, 250);

    for marker_idx in 0..num_markers {
        let marker_data: Vec<(u32, f64)> = frame_numbers
            .iter()
            .filter_map(|&frame| {
                let residuals = &per_frame_residuals[&frame];
                if marker_idx < residuals.len() {
                    let value = residuals[marker_idx];
                    if value.is_finite() {
                        Some((frame, value))
                    } else {
                        None
                    }
                } else {
                    None
                }
            })
            .collect();

        if !marker_data.is_empty() {
            chart.draw_series(LineSeries::new(
                marker_data.iter().map(|&(f, v)| (f, v)),
                marker_color.stroke_width(1),
            ))?;

            chart.draw_series(marker_data.iter().map(|&(f, v)| {
                Circle::new((f, v), 2, marker_color.mix(0.3).filled())
            }))?;
        }
    }

    chart
        .draw_series(LineSeries::new(
            vec![(frame_min, stats.mean), (frame_max, stats.mean)],
            RED.stroke_width(3),
        ))?
        .label(&format!("Mean: {:.4} px", stats.mean))
        .legend(|(x, y)| {
            PathElement::new(vec![(x, y), (x + 10, y)], RED.stroke_width(3))
        });

    chart
        .draw_series(LineSeries::new(
            vec![(frame_min, stats.median), (frame_max, stats.median)],
            GREEN.stroke_width(3),
        ))?
        .label(&format!("Median: {:.4} px", stats.median))
        .legend(|(x, y)| {
            PathElement::new(vec![(x, y), (x + 10, y)], GREEN.stroke_width(3))
        });

    chart
        .draw_series(std::iter::empty::<Circle<(u32, f64), i32>>())?
        .label(&format!("Markers ({} total)", num_markers))
        .legend(|(x, y)| {
            let marker_color = RGBColor(0, 0, 250);
            PathElement::new(
                vec![(x, y), (x + 10, y)],
                marker_color.mix(0.4).stroke_width(1),
            )
        });

    chart
        .configure_series_labels()
        .background_style(&WHITE.mix(0.8))
        .border_style(&BLACK)
        .draw()?;

    let stats_text = format!(
        "Statistics:\nFrames: {}\nMarkers: {}\nData Points: {}\nMean: {:.4} px\nMedian: {:.4} px\nStd Dev: {:.4} px\nMin: {:.4} px\nMax: {:.4} px",
        frame_numbers.len(),
        num_markers,
        stats.count,
        stats.mean,
        stats.median,
        stats.std_dev,
        stats.min,
        stats.max
    );

    let (width, _height) = area.dim_in_pixel();
    let text_x = (width as i32) - 260;
    let text_y = 80i32;

    area.draw(&Rectangle::new(
        [(text_x - 10, text_y - 10), (text_x + 240, text_y + 135)],
        WHITE.filled(),
    ))?;
    area.draw(&Rectangle::new(
        [(text_x - 10, text_y - 10), (text_x + 240, text_y + 135)],
        BLACK.stroke_width(1),
    ))?;

    for (i, line) in stats_text.lines().enumerate() {
        area.draw(&Text::new(
            line,
            (text_x, text_y + (i as i32) * 15),
            ("sans-serif", 12),
        ))?;
    }

    area.present()?;
    println!(
        "Multi-frame residual visualization saved to: {}",
        file_path.display()
    );

    Ok(())
}
