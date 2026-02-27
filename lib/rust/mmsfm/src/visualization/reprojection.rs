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

//! 2D marker reprojection visualization.
//!
//! Creates scatter plots comparing observed marker positions with reprojected
//! 3D points, showing triangulation accuracy.

use super::output_naming::OutputFileNaming;
use crate::camera_residual_error::reproject_3d_points_to_2d_uv_coordinates;
use crate::datatype::{
    camera_pose::CameraPose, CameraIntrinsics, ImageSize, UnitValue, UvPoint2,
};
use anyhow::Result;
use mmlogger::{mm_log_progress, Logger};
use nalgebra::Point3;
use plotters::coord::types::RangedCoordf64;
use plotters::prelude::*;

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

/// A pair of frame numbers for labeling two-camera visualizations.
#[derive(Debug, Clone, Copy)]
pub struct FramePair {
    pub frame_a: u32,
    pub frame_b: u32,
}

fn convert_uv_to_pixel_coords(
    uv_points: &[UvPoint2<f64>],
    image_size: &ImageSize<f64>,
) -> Vec<(f64, f64)> {
    uv_points
        .iter()
        .map(|uv| {
            let pixel_x = uv.x.value() * image_size.width.value();
            let pixel_y = uv.y.value() * image_size.height.value();
            (pixel_x, pixel_y)
        })
        .collect()
}

/// Creates a 2D scatter plot comparing observed markers with reprojected 3D points for two cameras.
pub fn visualize_marker_reprojections_2d_scatter(
    uv_coords_a: &[UvPoint2<f64>],
    uv_coords_b: &[UvPoint2<f64>],
    // TODO: Change Point3 datatype to ScenePoint3.
    points_3d: &[Point3<f64>],
    pose_a: &CameraPose,
    pose_b: &CameraPose,
    intrinsics_a: &CameraIntrinsics,
    intrinsics_b: &CameraIntrinsics,
    image_size_a: &ImageSize<f64>,
    image_size_b: &ImageSize<f64>,
    frame_pair: &FramePair,
    title: &str,
    output_image_size: &ImageSize<f64>,
    naming: &OutputFileNaming,
) -> Result<()> {
    let file_path = naming.full_path()?;

    let num_points = points_3d.len();
    // TODO: Convert this error into an assertion.
    if uv_coords_a.len() != num_points || uv_coords_b.len() != num_points {
        anyhow::bail!(
            "Inconsistent data sizes: {} 3D points, {} UV coords A, {} UV coords B",
            num_points,
            uv_coords_a.len(),
            uv_coords_b.len()
        );
    }

    // TODO: Convert this error into an assertion.
    if num_points == 0 {
        anyhow::bail!("No data points to visualize");
    }

    let reprojected_2d_uv_points_a = reproject_3d_points_to_2d_uv_coordinates(
        points_3d,
        pose_a,
        intrinsics_a,
    )?;
    let reprojected_2d_uv_points_b = reproject_3d_points_to_2d_uv_coordinates(
        points_3d,
        pose_b,
        intrinsics_b,
    )?;

    // Convert UV coordinates to pixel coordinates
    let pixel_coords_a = convert_uv_to_pixel_coords(uv_coords_a, image_size_a);
    let pixel_coords_b = convert_uv_to_pixel_coords(uv_coords_b, image_size_b);
    let reprojected_pixel_coords_a =
        convert_uv_to_pixel_coords(&reprojected_2d_uv_points_a, image_size_a);
    let reprojected_pixel_coords_b =
        convert_uv_to_pixel_coords(&reprojected_2d_uv_points_b, image_size_b);

    if DEBUG {
        let valid_reprojections_a = reprojected_2d_uv_points_a
            .iter()
            .filter(|uv| uv.x.value().is_finite() && uv.y.value().is_finite())
            .count();
        let valid_reprojections_b = reprojected_2d_uv_points_b
            .iter()
            .filter(|uv| uv.x.value().is_finite() && uv.y.value().is_finite())
            .count();

        mm_eprintln_debug!("=== Reprojection Debug ===");
        mm_eprintln_debug!("  3D points: {}", num_points);
        mm_eprintln_debug!(
            "  Camera A valid reprojections: {}/{}",
            valid_reprojections_a,
            num_points
        );
        mm_eprintln_debug!(
            "  Camera B valid reprojections: {}/{}",
            valid_reprojections_b,
            num_points
        );

        if !pixel_coords_a.is_empty() {
            let x_min_obs_a = pixel_coords_a
                .iter()
                .map(|pt| pt.0)
                .fold(f64::INFINITY, f64::min);
            let x_max_obs_a = pixel_coords_a
                .iter()
                .map(|pt| pt.0)
                .fold(f64::NEG_INFINITY, f64::max);
            let y_min_obs_a = pixel_coords_a
                .iter()
                .map(|pt| pt.1)
                .fold(f64::INFINITY, f64::min);
            let y_max_obs_a = pixel_coords_a
                .iter()
                .map(|pt| pt.1)
                .fold(f64::NEG_INFINITY, f64::max);

            mm_eprintln_debug!("Camera A observed pixel coordinates range:");
            mm_eprintln_debug!(
                "  X: {:.2} to {:.2} px (width: {:.2} px)",
                x_min_obs_a,
                x_max_obs_a,
                x_max_obs_a - x_min_obs_a
            );
            mm_eprintln_debug!(
                "  Y: {:.2} to {:.2} px (height: {:.2} px)",
                y_min_obs_a,
                y_max_obs_a,
                y_max_obs_a - y_min_obs_a
            );
        }

        if valid_reprojections_a > 0 {
            let finite_reproj_a: Vec<_> = reprojected_pixel_coords_a
                .iter()
                .filter(|pt| pt.0.is_finite() && pt.1.is_finite())
                .collect();
            let x_min_repr_a = finite_reproj_a
                .iter()
                .map(|pt| pt.0)
                .fold(f64::INFINITY, f64::min);
            let x_max_repr_a = finite_reproj_a
                .iter()
                .map(|pt| pt.0)
                .fold(f64::NEG_INFINITY, f64::max);
            let y_min_repr_a = finite_reproj_a
                .iter()
                .map(|pt| pt.1)
                .fold(f64::INFINITY, f64::min);
            let y_max_repr_a = finite_reproj_a
                .iter()
                .map(|pt| pt.1)
                .fold(f64::NEG_INFINITY, f64::max);

            mm_eprintln_debug!("Camera A reprojected pixel coordinates range:");
            mm_eprintln_debug!(
                "  X: {:.2} to {:.2} px (width: {:.2} px)",
                x_min_repr_a,
                x_max_repr_a,
                x_max_repr_a - x_min_repr_a
            );
            mm_eprintln_debug!(
                "  Y: {:.2} to {:.2} px (height: {:.2} px)",
                y_min_repr_a,
                y_max_repr_a,
                y_max_repr_a - y_min_repr_a
            );
        }

        mm_eprintln_debug!("Camera intrinsics A:");
        mm_eprintln_debug!(
            "  Focal length A: X={:.6}, Y={:.6} (normalized)",
            intrinsics_a.focal_length_x,
            intrinsics_a.focal_length_y
        );
        mm_eprintln_debug!(
            "  Principal point A: ({:.6}, {:.6})",
            intrinsics_a.principal_point.x.value(),
            intrinsics_a.principal_point.y.value()
        );
        mm_eprintln_debug!(
            "  Film back A: {:.1}mm x {:.1}mm (aspect: {:.3})",
            intrinsics_a.film_back.width.value(),
            intrinsics_a.film_back.height.value(),
            intrinsics_a.film_back.aspect_ratio()
        );

        mm_eprintln_debug!("Camera intrinsics B:");
        mm_eprintln_debug!(
            "  Focal length B: X={:.6}, Y={:.6} (normalized)",
            intrinsics_a.focal_length_x,
            intrinsics_a.focal_length_y
        );
        mm_eprintln_debug!(
            "  Principal point B: ({:.6}, {:.6})",
            intrinsics_a.principal_point.x.value(),
            intrinsics_a.principal_point.y.value()
        );
        mm_eprintln_debug!(
            "  Film back B: {:.1}mm x {:.1}mm (aspect: {:.3})",
            intrinsics_a.film_back.width.value(),
            intrinsics_a.film_back.height.value(),
            intrinsics_a.film_back.aspect_ratio()
        );

        if valid_reprojections_a == 0 {
            mm_eprintln_debug!("  WARNING: No valid reprojections for Camera A - all points behind camera (Maya: +Z)");
        }
        if valid_reprojections_b == 0 {
            mm_eprintln_debug!("  WARNING: No valid reprojections for Camera B - all points behind camera (Maya: +Z)");
        }
        mm_eprintln_debug!("==========================");
    }

    // Calculate reprojection error in pixels.
    let residual_errors_a: Vec<f64> = uv_coords_a
        .iter()
        .zip(reprojected_2d_uv_points_a.iter())
        .map(|(observed, reprojected)| {
            let dx_uv = observed.x.value() - reprojected.x.value();
            let dy_uv = observed.y.value() - reprojected.y.value();
            let dx_px = dx_uv * image_size_a.width.value();
            let dy_px = dy_uv * image_size_a.height.value();
            (dx_px * dx_px + dy_px * dy_px).sqrt()
        })
        .collect();
    let residual_errors_b: Vec<f64> = uv_coords_b
        .iter()
        .zip(reprojected_2d_uv_points_b.iter())
        .map(|(observed, reprojected)| {
            let dx_uv = observed.x.value() - reprojected.x.value();
            let dy_uv = observed.y.value() - reprojected.y.value();
            let dx_px = dx_uv * image_size_b.width.value();
            let dy_px = dy_uv * image_size_b.height.value();
            (dx_px * dx_px + dy_px * dy_px).sqrt()
        })
        .collect();

    let mean_error_a =
        residual_errors_a.iter().sum::<f64>() / residual_errors_a.len() as f64;
    let mean_error_b =
        residual_errors_b.iter().sum::<f64>() / residual_errors_b.len() as f64;
    let max_error_a = residual_errors_a.iter().fold(0.0f64, |a, &b| a.max(b));
    let max_error_b = residual_errors_b.iter().fold(0.0f64, |a, &b| a.max(b));

    let resolution = (
        output_image_size.effective_width() as u32,
        output_image_size.height.value() as u32,
    );
    let area = BitMapBackend::new(&file_path, resolution).into_drawing_area();
    area.fill(&WHITE)?;

    let areas = area.split_evenly((1, 2));
    let left_area = &areas[0];
    let right_area = &areas[1];

    let (subplot_width, subplot_height) = left_area.dim_in_pixel();
    let subplot_aspect_ratio = subplot_width as f64 / subplot_height as f64;

    let bounds_a = calculate_plot_bounds(
        &pixel_coords_a,
        &reprojected_pixel_coords_a,
        image_size_a,
    );
    let bounds_b = calculate_plot_bounds(
        &pixel_coords_b,
        &reprojected_pixel_coords_b,
        image_size_b,
    );
    let unified_bounds = unify_plot_bounds(&bounds_a, &bounds_b);

    // Match bounds to subplot aspect ratio to avoid distorting the geometry.
    let aspect_corrected_bounds =
        make_bounds_match_aspect_ratio(&unified_bounds, subplot_aspect_ratio);

    draw_camera_subplot(
        &left_area,
        &pixel_coords_a,
        &reprojected_pixel_coords_a,
        &residual_errors_a,
        &aspect_corrected_bounds,
        image_size_a,
        &format!("{} - Camera A (Frame {})", title, frame_pair.frame_a),
        mean_error_a,
        max_error_a,
    )?;

    draw_camera_subplot(
        &right_area,
        &pixel_coords_b,
        &reprojected_pixel_coords_b,
        &residual_errors_b,
        &aspect_corrected_bounds,
        image_size_b,
        &format!("{} - Camera B (Frame {})", title, frame_pair.frame_b),
        mean_error_b,
        max_error_b,
    )?;

    area.present()?;
    if DEBUG {
        mm_eprintln_debug!(
            "  Camera A mean error: {:.4} pixels (max: {:.4})",
            mean_error_a,
            max_error_a
        );
        mm_eprintln_debug!(
            "  Camera B mean error: {:.4} pixels (max: {:.4})",
            mean_error_b,
            max_error_b
        );
    }

    Ok(())
}

#[derive(Debug, Clone)]
struct PlotBounds {
    x_min: f64,
    x_max: f64,
    y_min: f64,
    y_max: f64,
}

fn calculate_plot_bounds(
    observed: &[(f64, f64)],
    reprojected: &[(f64, f64)],
    image_size: &ImageSize<f64>,
) -> PlotBounds {
    let mut x_min = f64::MAX;
    let mut x_max = f64::MIN;
    let mut y_min = f64::MAX;
    let mut y_max = f64::MIN;
    let mut has_valid_points = false;

    for coords in observed.iter().chain(reprojected.iter()) {
        let x_val = coords.0;
        let y_val = coords.1;
        if x_val.is_finite() && y_val.is_finite() {
            x_min = x_min.min(x_val);
            x_max = x_max.max(x_val);
            y_min = y_min.min(y_val);
            y_max = y_max.max(y_val);
            has_valid_points = true;
        }
    }

    let image_width = image_size.width.value();
    let image_height = image_size.height.value();

    if !has_valid_points {
        return PlotBounds {
            x_min: -image_width * 0.2,
            x_max: image_width * 1.2,
            y_min: -image_height * 0.2,
            y_max: image_height * 1.2,
        };
    }

    // Always include the full image area, even if data falls outside.
    let image_x_min = 0.0;
    let image_x_max = image_width;
    let image_y_min = 0.0;
    let image_y_max = image_height;

    x_min = x_min.min(image_x_min);
    x_max = x_max.max(image_x_max);
    y_min = y_min.min(image_y_min);
    y_max = y_max.max(image_y_max);

    // Add 10% padding.
    let x_range = x_max - x_min;
    let y_range = y_max - y_min;
    let x_pad = x_range * 0.1;
    let y_pad = y_range * 0.1;

    PlotBounds {
        x_min: x_min - x_pad,
        x_max: x_max + x_pad,
        y_min: y_min - y_pad,
        y_max: y_max + y_pad,
    }
}

/// Merges two sets of plot bounds into one that encompasses both.
fn unify_plot_bounds(
    bounds_a: &PlotBounds,
    bounds_b: &PlotBounds,
) -> PlotBounds {
    PlotBounds {
        x_min: bounds_a.x_min.min(bounds_b.x_min),
        x_max: bounds_a.x_max.max(bounds_b.x_max),
        y_min: bounds_a.y_min.min(bounds_b.y_min),
        y_max: bounds_a.y_max.max(bounds_b.y_max),
    }
}

/// Expands bounds to match the target aspect ratio, centered on the original bounds.
fn make_bounds_match_aspect_ratio(
    bounds: &PlotBounds,
    target_aspect_ratio: f64,
) -> PlotBounds {
    let current_width = bounds.x_max - bounds.x_min;
    let current_height = bounds.y_max - bounds.y_min;
    let current_aspect_ratio = current_width / current_height;

    let x_center = (bounds.x_max + bounds.x_min) * 0.5;
    let y_center = (bounds.y_max + bounds.y_min) * 0.5;

    // Always expand (never shrink) to keep all data visible.
    let (new_width, new_height) = if current_aspect_ratio < target_aspect_ratio
    {
        (current_height * target_aspect_ratio, current_height)
    } else {
        (current_width, current_width / target_aspect_ratio)
    };

    PlotBounds {
        x_min: x_center - new_width * 0.5,
        x_max: x_center + new_width * 0.5,
        y_min: y_center - new_height * 0.5,
        y_max: y_center + new_height * 0.5,
    }
}

/// Draws the image boundary rectangle and center cross.
fn draw_image_boundaries<DB: DrawingBackend>(
    chart: &mut ChartContext<
        DB,
        plotters::coord::cartesian::Cartesian2d<RangedCoordf64, RangedCoordf64>,
    >,
    image_size: &ImageSize<f64>,
) -> Result<()>
where
    DB::ErrorType: 'static,
{
    let width = image_size.width.value();
    let height = image_size.height.value();

    let x_min = 0.0;
    let x_max = width;
    let y_min = 0.0;
    let y_max = height;

    let boundary_style = MAGENTA.mix(0.8).stroke_width(2);

    chart.draw_series(LineSeries::new(
        vec![(x_min, y_min), (x_max, y_min)],
        boundary_style.clone(),
    ))?;
    chart.draw_series(LineSeries::new(
        vec![(x_max, y_min), (x_max, y_max)],
        boundary_style.clone(),
    ))?;
    chart.draw_series(LineSeries::new(
        vec![(x_max, y_max), (x_min, y_max)],
        boundary_style.clone(),
    ))?;
    chart.draw_series(LineSeries::new(
        vec![(x_min, y_max), (x_min, y_min)],
        boundary_style.clone(),
    ))?;

    let center_style = MAGENTA.mix(0.5).stroke_width(1);
    let center_x = width / 2.0;
    let center_y = height / 2.0;
    let center_size = 20.0;

    chart.draw_series(LineSeries::new(
        vec![
            (center_x - center_size, center_y),
            (center_x + center_size, center_y),
        ],
        center_style.clone(),
    ))?;
    chart.draw_series(LineSeries::new(
        vec![
            (center_x, center_y - center_size),
            (center_x, center_y + center_size),
        ],
        center_style,
    ))?;

    Ok(())
}

/// Draws a single camera subplot with observed vs reprojected markers.
fn draw_camera_subplot<DB: DrawingBackend>(
    area: &DrawingArea<DB, plotters::coord::Shift>,
    observed: &[(f64, f64)],
    reprojected: &[(f64, f64)],
    _errors: &[f64],
    bounds: &PlotBounds,
    image_size: &ImageSize<f64>,
    subplot_title: &str,
    mean_error: f64,
    max_error: f64,
) -> Result<()>
where
    DB::ErrorType: 'static,
{
    let mut chart = ChartBuilder::on(area)
        .caption(subplot_title, ("sans-serif", 20))
        .margin(40)
        .x_label_area_size(50)
        .y_label_area_size(60)
        .build_cartesian_2d(
            bounds.x_min..bounds.x_max,
            bounds.y_min..bounds.y_max,
        )?;

    chart
        .configure_mesh()
        .x_desc("X (pixels, 0=left)")
        .y_desc("Y (pixels, 0=bottom)")
        .x_max_light_lines(8)
        .y_max_light_lines(6)
        .draw()?;

    draw_image_boundaries(&mut chart, image_size)?;

    // Draw error vectors behind points.
    for (obs, reproj) in observed.iter().zip(reprojected.iter()) {
        let obs_x = obs.0;
        let obs_y = obs.1;
        let reproj_x = reproj.0;
        let reproj_y = reproj.1;
        if obs_x.is_finite()
            && obs_y.is_finite()
            && reproj_x.is_finite()
            && reproj_y.is_finite()
        {
            chart.draw_series(LineSeries::new(
                vec![(obs_x, obs_y), (reproj_x, reproj_y)],
                GREEN.mix(0.6).stroke_width(1),
            ))?;
        }
    }

    chart
        .draw_series(
            observed
                .iter()
                .filter(|pt| pt.0.is_finite() && pt.1.is_finite())
                .map(|pt| Circle::new(*pt, 4, BLUE.filled())),
        )?
        .label("Observed Markers")
        .legend(|(x, y)| Circle::new((x + 5, y), 4, BLUE.filled()));

    chart
        .draw_series(
            reprojected
                .iter()
                .filter(|pt| pt.0.is_finite() && pt.1.is_finite())
                .map(|pt| Cross::new(*pt, 4, RED.stroke_width(2))),
        )?
        .label("Reprojected 3D Points")
        .legend(|(x, y)| Cross::new((x + 5, y), 4, RED.stroke_width(2)));

    chart
        .draw_series(std::iter::empty::<Circle<(f64, f64), u32>>())?
        .label("Error Vectors")
        .legend(|(x, y)| {
            PathElement::new(
                vec![(x, y), (x + 10, y)],
                GREEN.mix(0.6).stroke_width(1),
            )
        });

    let width = image_size.width.value();
    let height = image_size.height.value();
    chart
        .draw_series(std::iter::empty::<Circle<(f64, f64), u32>>())?
        .label(format!(
            "Image Boundaries (0,0)-({:.0},{:.0})",
            width, height
        ))
        .legend(|(x, y)| {
            PathElement::new(
                vec![(x, y), (x + 10, y)],
                MAGENTA.mix(0.8).stroke_width(2),
            )
        });

    // Add image center to legend.
    chart
        .draw_series(std::iter::empty::<Circle<(f64, f64), u32>>())?
        .label(format!(
            "Image Center ({:.0},{:.0})",
            width / 2.0,
            height / 2.0
        ))
        .legend(|(x, y)| {
            PathElement::new(
                vec![(x + 2, y), (x + 8, y), (x + 5, y - 3), (x + 5, y + 3)],
                MAGENTA.mix(0.5).stroke_width(1),
            )
        });

    chart
        .configure_series_labels()
        .background_style(&WHITE.mix(0.8))
        .border_style(&BLACK)
        .draw()?;

    let stats_text = format!(
        "Statistics:\nPoints: {}\nMean Error: {:.3} px\nMax Error: {:.3} px",
        observed.len(),
        mean_error,
        max_error
    );

    let (width, _height) = area.dim_in_pixel();
    let text_x = (width as i32) - 200;
    let text_y = 60i32;

    area.draw(&Rectangle::new(
        [(text_x - 10, text_y - 10), (text_x + 180, text_y + 70)],
        WHITE.filled(),
    ))?;
    area.draw(&Rectangle::new(
        [(text_x - 10, text_y - 10), (text_x + 180, text_y + 70)],
        BLACK.stroke_width(1),
    ))?;

    for (i, line) in stats_text.lines().enumerate() {
        area.draw(&Text::new(
            line,
            (text_x, text_y + (i as i32) * 15),
            ("sans-serif", 12),
        ))?;
    }

    Ok(())
}

/// Creates one 2D scatter plot per camera comparing observed markers with reprojected 3D points.
pub fn visualize_marker_reprojections_sequential<L: Logger + Sync>(
    logger: &L,
    camera_poses: &[CameraPose],
    points_3d: &[Point3<f64>],
    observations_per_camera: &[Vec<(usize, UvPoint2<f64>)>],
    intrinsics: &[CameraIntrinsics],
    image_sizes: &[ImageSize<f64>],
    title: &str,
    output_image_size: &ImageSize<f64>,
    naming: &OutputFileNaming,
) -> Result<()> {
    use rayon::prelude::*;

    let num_cameras = camera_poses.len();
    if intrinsics.len() != num_cameras
        || image_sizes.len() != num_cameras
        || observations_per_camera.len() != num_cameras
    {
        anyhow::bail!(
            "Inconsistent input sizes: {} cameras, {} intrinsics, {} image sizes, {} observation groups",
            num_cameras,
            intrinsics.len(),
            image_sizes.len(),
            observations_per_camera.len()
        );
    }

    if num_cameras > 0 {
        let example_naming = naming.clone().with_frame(1);
        if let Ok(example_path) = example_naming.full_path() {
            mm_log_progress!(
                logger,
                "Generating marker reprojections: {}",
                example_path.display()
            );
        }
    }

    (0..num_cameras)
        .into_par_iter()
        .try_for_each(|cam_idx| -> Result<()> {
            let camera_pose = &camera_poses[cam_idx];
            let camera_intrinsics = &intrinsics[cam_idx];
            let image_size = &image_sizes[cam_idx];
            let observations = &observations_per_camera[cam_idx];

            if observations.is_empty() {
                return Ok(());
            }

            let mut uv_observed = Vec::with_capacity(observations.len());
            let mut points_3d_observed = Vec::with_capacity(observations.len());

            for &(point_idx, uv) in observations {
                if point_idx < points_3d.len() {
                    uv_observed.push(uv);
                    points_3d_observed.push(points_3d[point_idx]);
                }
            }

            let reprojected_uv = reproject_3d_points_to_2d_uv_coordinates(
                &points_3d_observed,
                camera_pose,
                camera_intrinsics,
            )?;

            let camera_naming = naming.clone().with_frame((cam_idx + 1) as u32);
            let file_path = camera_naming.full_path()?;

            let observed_pixels =
                convert_uv_to_pixel_coords(&uv_observed, image_size);
            let reprojected_pixels =
                convert_uv_to_pixel_coords(&reprojected_uv, image_size);

            let output_width = output_image_size.width.value() as u32;
            let output_height = output_image_size.height.value() as u32;

            let area =
                BitMapBackend::new(&file_path, (output_width, output_height))
                    .into_drawing_area();
            area.fill(&WHITE)?;

            let camera_title = format!("{} - Camera {}", title, cam_idx + 1);

            let img_width = image_size.width.value();
            let img_height = image_size.height.value();

            let mut chart = ChartBuilder::on(&area)
                .caption(&camera_title, ("sans-serif", 30).into_font())
                .margin(15)
                .x_label_area_size(40)
                .y_label_area_size(60)
                .build_cartesian_2d(0.0..img_width, img_height..0.0)?;

            chart
                .configure_mesh()
                .x_desc("X (pixels, 0=left)")
                .y_desc("Y (pixels, 0=bottom)")
                .draw()?;

            let boundary_style = MAGENTA.mix(0.8).stroke_width(2);
            chart.draw_series(LineSeries::new(
                vec![(0.0, 0.0), (img_width, 0.0)],
                boundary_style.clone(),
            ))?;
            chart.draw_series(LineSeries::new(
                vec![(img_width, 0.0), (img_width, img_height)],
                boundary_style.clone(),
            ))?;
            chart.draw_series(LineSeries::new(
                vec![(img_width, img_height), (0.0, img_height)],
                boundary_style.clone(),
            ))?;
            chart.draw_series(LineSeries::new(
                vec![(0.0, img_height), (0.0, 0.0)],
                boundary_style.clone(),
            ))?;

            let center_style = MAGENTA.mix(0.5).stroke_width(1);
            let center_x = img_width / 2.0;
            let center_y = img_height / 2.0;
            let center_size = 20.0;

            chart.draw_series(LineSeries::new(
                vec![
                    (center_x - center_size, center_y),
                    (center_x + center_size, center_y),
                ],
                center_style.clone(),
            ))?;
            chart.draw_series(LineSeries::new(
                vec![
                    (center_x, center_y - center_size),
                    (center_x, center_y + center_size),
                ],
                center_style,
            ))?;

            for ((&obs, &reproj), _) in observed_pixels
                .iter()
                .zip(reprojected_pixels.iter())
                .zip(points_3d_observed.iter())
            {
                if obs.0.is_finite()
                    && obs.1.is_finite()
                    && reproj.0.is_finite()
                    && reproj.1.is_finite()
                {
                    chart.draw_series(LineSeries::new(
                        vec![(obs.0, obs.1), (reproj.0, reproj.1)],
                        GREEN.mix(0.6).stroke_width(1),
                    ))?;
                }
            }

            chart
                .draw_series(
                    observed_pixels
                        .iter()
                        .filter(|pt| pt.0.is_finite() && pt.1.is_finite())
                        .map(|&(x, y)| Circle::new((x, y), 4, BLUE.filled())),
                )?
                .label("Observed Markers")
                .legend(|(x, y)| Circle::new((x + 5, y), 4, BLUE.filled()));

            chart
                .draw_series(
                    reprojected_pixels
                        .iter()
                        .filter(|pt| pt.0.is_finite() && pt.1.is_finite())
                        .map(|&(x, y)| Cross::new((x, y), 4, RED.stroke_width(2))),
                )?
                .label("Reprojected 3D Points")
                .legend(|(x, y)| Cross::new((x + 5, y), 4, RED.stroke_width(2)));

            chart
                .draw_series(std::iter::empty::<Circle<(f64, f64), u32>>())?
                .label("Error Vectors")
                .legend(|(x, y)| {
                    PathElement::new(
                        vec![(x, y), (x + 10, y)],
                        GREEN.mix(0.6).stroke_width(1),
                    )
                });

            chart
                .draw_series(std::iter::empty::<Circle<(f64, f64), u32>>())?
                .label(format!(
                    "Image Boundaries (0,0)-({:.0},{:.0})",
                    img_width, img_height
                ))
                .legend(|(x, y)| {
                    PathElement::new(
                        vec![(x, y), (x + 10, y)],
                        MAGENTA.mix(0.8).stroke_width(2),
                    )
                });

            chart
                .draw_series(std::iter::empty::<Circle<(f64, f64), u32>>())?
                .label(format!(
                    "Image Center ({:.0},{:.0})",
                    center_x, center_y
                ))
                .legend(|(x, y)| {
                    PathElement::new(
                        vec![(x + 2, y), (x + 8, y), (x + 5, y - 3), (x + 5, y + 3)],
                        MAGENTA.mix(0.5).stroke_width(1),
                    )
                });

            chart
                .configure_series_labels()
                .background_style(&WHITE.mix(0.8))
                .border_style(&BLACK)
                .draw()?;

            let residual_errors: Vec<f64> = uv_observed
                .iter()
                .zip(reprojected_uv.iter())
                .map(|(observed, reprojected)| {
                    let dx_uv = observed.x.value() - reprojected.x.value();
                    let dy_uv = observed.y.value() - reprojected.y.value();
                    let dx_px = dx_uv * img_width;
                    let dy_px = dy_uv * img_height;
                    (dx_px * dx_px + dy_px * dy_px).sqrt()
                })
                .collect();

            let mean_error = if !residual_errors.is_empty() {
                residual_errors.iter().sum::<f64>() / residual_errors.len() as f64
            } else {
                0.0
            };
            let max_error = residual_errors.iter().fold(0.0f64, |a, &b| a.max(b));

            let num_markers = observed_pixels.len();
            let stats_text = format!(
                "Statistics:\nCamera: {} of {}\nMarkers: {}\nMean Error: {:.3} px\nMax Error: {:.3} px\nImage: {:.0}x{:.0} px",
                cam_idx + 1,
                num_cameras,
                num_markers,
                mean_error,
                max_error,
                img_width,
                img_height
            );

            let (width, _height) = area.dim_in_pixel();
            let text_x = (width as i32) - 220;
            let text_y = 60i32;

            area.draw(&Rectangle::new(
                [(text_x - 10, text_y - 10), (text_x + 200, text_y + 100)],
                WHITE.filled(),
            ))?;
            area.draw(&Rectangle::new(
                [(text_x - 10, text_y - 10), (text_x + 200, text_y + 100)],
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

            Ok(())
        })?;

    mm_log_progress!(
        logger,
        "Generated {} marker reprojection frames",
        num_cameras
    );

    Ok(())
}
