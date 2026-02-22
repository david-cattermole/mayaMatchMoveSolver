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

//! 3D Visualization utilities for Structure from Motion data
//!
//! This module provides functions for rendering camera frustums, 3D
//! point clouds, and complete SfM scenes using the plotters crate.

use super::output_naming::{OutputFileNaming, ViewName};
use crate::datatype::camera_pose::CameraPose;
use crate::datatype::{CameraFrustum, CameraIntrinsics};
use anyhow::Result;
use nalgebra::{Point3, Vector3};
use plotters::coord::cartesian::Cartesian3d;
use plotters::coord::types::RangedCoordf64;
use plotters::prelude::*;
use rayon::prelude::*;
use std::collections::{HashMap, HashSet};

/// Maps frame numbers to the set of bundle indices visible in that frame.
pub type BundleVisibilityMap = HashMap<u32, HashSet<usize>>;

#[derive(Debug, Clone)]
pub struct EpipolarLineOptions {
    pub enabled: bool,
    pub camera_colors: Vec<RGBColor>,
    pub line_width: u32,
    pub opacity: f64,
    pub max_points: Option<usize>,
}

/// Configuration for a 3D scene view.
#[derive(Debug, Clone)]
pub struct ViewConfiguration {
    pub tilt: f64,
    pub pan: f64,
    pub roll: f64,
    pub view_name: String,
    pub resolution: (u32, u32),
    pub epipolar_options: EpipolarLineOptions,
    pub show_coordinate_axes: bool,
    pub frustum_depth: f64,
}

#[derive(Debug, Clone)]
pub struct ViewConfigurationBuilder {
    tilt: Option<f64>,
    pan: Option<f64>,
    roll: Option<f64>,
    view_name: Option<String>,
    resolution: Option<(u32, u32)>,
    epipolar_options: Option<EpipolarLineOptions>,
    show_coordinate_axes: Option<bool>,
    frustum_depth: Option<f64>,
}

impl Default for EpipolarLineOptions {
    fn default() -> Self {
        Self {
            enabled: true,
            camera_colors: vec![
                RGBColor(255, 100, 100),
                RGBColor(100, 100, 255),
            ],
            line_width: 1,
            opacity: 0.4,
            max_points: Some(50),
        }
    }
}

impl ViewConfiguration {
    fn tilt_radians(&self) -> f64 {
        self.tilt.to_radians()
    }

    fn pan_radians(&self) -> f64 {
        self.pan.to_radians()
    }

    fn roll_radians(&self) -> f64 {
        self.roll.to_radians()
    }
}

impl ViewConfigurationBuilder {
    pub fn new() -> Self {
        Self {
            tilt: None,
            pan: None,
            roll: None,
            view_name: None,
            resolution: None,
            epipolar_options: None,
            show_coordinate_axes: None,
            frustum_depth: None,
        }
    }

    pub fn view_name(mut self, name: &str) -> Self {
        self.view_name = Some(name.to_string());
        self
    }

    pub fn rotation_ortho_tilt_pan_roll(
        mut self,
        tilt: f64,
        pan: f64,
        roll: f64,
    ) -> Self {
        self.tilt = Some(tilt);
        self.pan = Some(pan);
        self.roll = Some(roll);
        self
    }

    pub fn rotation_ortho_top(mut self) -> Self {
        self.tilt = Some(90.0);
        self.pan = Some(0.0);
        self.roll = Some(0.0);
        self
    }

    pub fn rotation_ortho_bottom(mut self) -> Self {
        self.tilt = Some(-90.0);
        self.pan = Some(0.0);
        self.roll = Some(0.0);
        self
    }

    pub fn rotation_ortho_right(mut self) -> Self {
        self.tilt = Some(0.0);
        self.pan = Some(90.0);
        self.roll = Some(0.0);
        self
    }

    pub fn rotation_ortho_left(mut self) -> Self {
        self.tilt = Some(0.0);
        self.pan = Some(-90.0);
        self.roll = Some(0.0);
        self
    }

    pub fn rotation_ortho_front(mut self) -> Self {
        self.tilt = Some(0.0);
        self.pan = Some(0.0);
        self.roll = Some(0.0);
        self
    }

    pub fn rotation_ortho_back(mut self) -> Self {
        self.tilt = Some(0.0);
        self.pan = Some(180.0);
        self.roll = Some(0.0);
        self
    }

    pub fn rotation_ortho_three_quarter_a(mut self) -> Self {
        self.tilt = Some(45.0);
        self.pan = Some(45.0);
        self.roll = Some(0.0);
        self
    }

    pub fn rotation_ortho_three_quarter_b(mut self) -> Self {
        self.tilt = Some(45.0);
        self.pan = Some(-45.0);
        self.roll = Some(0.0);
        self
    }

    pub fn resolution(mut self, width: u32, height: u32) -> Self {
        self.resolution = Some((width, height));
        self
    }

    pub fn resolution_hd(mut self) -> Self {
        self.resolution = Some((1920, 1080));
        self
    }

    pub fn resolution_uhd(mut self) -> Self {
        self.resolution = Some((3840, 2160));
        self
    }

    pub fn resolution_square_1k(mut self) -> Self {
        self.resolution = Some((1024, 1024));
        self
    }

    pub fn resolution_square_2k(mut self) -> Self {
        self.resolution = Some((2048, 2048));
        self
    }

    pub fn resolution_square_4k(mut self) -> Self {
        self.resolution = Some((4096, 4096));
        self
    }

    pub fn epipolar_options(mut self, options: EpipolarLineOptions) -> Self {
        self.epipolar_options = Some(options);
        self
    }

    pub fn show_coordinate_axes(mut self, show_coordinate_axes: bool) -> Self {
        self.show_coordinate_axes = Some(show_coordinate_axes);
        self
    }

    pub fn frustum_depth(mut self, size: f64) -> Self {
        self.frustum_depth = Some(size);
        self
    }

    pub fn build(self) -> ViewConfiguration {
        let view_name = self.view_name.expect(
            "view_name is required - call .view_name() before .build()",
        );
        let tilt = self.tilt.expect(
            "rotation is required - call a rotation method before .build()",
        );
        let pan = self.pan.expect(
            "rotation is required - call a rotation method before .build()",
        );
        let roll = self.roll.expect(
            "rotation is required - call a rotation method before .build()",
        );

        ViewConfiguration {
            tilt,
            pan,
            roll,
            view_name,
            resolution: self.resolution.unwrap_or((1024, 768)),
            epipolar_options: self
                .epipolar_options
                .unwrap_or_else(EpipolarLineOptions::default),
            show_coordinate_axes: self.show_coordinate_axes.unwrap_or(true),
            frustum_depth: self.frustum_depth.unwrap_or(1.0),
        }
    }
}

#[derive(Debug)]
pub struct SceneBounds {
    pub x_min: f64,
    pub x_max: f64,
    pub y_min: f64,
    pub y_max: f64,
    pub z_min: f64,
    pub z_max: f64,
}

impl SceneBounds {
    pub fn new() -> Self {
        Self {
            x_min: f64::MAX,
            x_max: f64::MIN,
            y_min: f64::MAX,
            y_max: f64::MIN,
            z_min: f64::MAX,
            z_max: f64::MIN,
        }
    }

    pub fn update_with_point(&mut self, point: &Point3<f64>) {
        self.x_min = self.x_min.min(point.x);
        self.x_max = self.x_max.max(point.x);
        self.y_min = self.y_min.min(point.y);
        self.y_max = self.y_max.max(point.y);
        self.z_min = self.z_min.min(point.z);
        self.z_max = self.z_max.max(point.z);
    }

    pub fn with_padding(&self, padding: f64) -> Self {
        let x_range = self.x_max - self.x_min;
        let y_range = self.y_max - self.y_min;
        let z_range = self.z_max - self.z_min;

        let x_pad = x_range * padding;
        let y_pad = y_range * padding;
        let z_pad = z_range * padding;

        Self {
            x_min: self.x_min - x_pad,
            x_max: self.x_max + x_pad,
            y_min: self.y_min - y_pad,
            y_max: self.y_max + y_pad,
            z_min: self.z_min - z_pad,
            z_max: self.z_max + z_pad,
        }
    }
}

/// Calculate uniform scene bounds with equal scaling for all axes.
pub fn calculate_uniform_scene_bounds(
    camera_poses: &[&CameraPose],
    points_3d: &[Point3<f64>],
    intrinsics: &CameraIntrinsics,
    frustum_depth: f64,
    scene_center: &Vector3<f64>,
) -> SceneBounds {
    let natural_bounds = calculate_scene_bounds_with_axes(
        camera_poses,
        points_3d,
        intrinsics,
        frustum_depth,
        scene_center,
    );

    let x_range = natural_bounds.x_max - natural_bounds.x_min;
    let y_range = natural_bounds.y_max - natural_bounds.y_min;
    let z_range = natural_bounds.z_max - natural_bounds.z_min;
    let max_range = x_range.max(y_range).max(z_range);

    let x_center = (natural_bounds.x_max + natural_bounds.x_min) * 0.5;
    let y_center = (natural_bounds.y_max + natural_bounds.y_min) * 0.5;
    let z_center = (natural_bounds.z_max + natural_bounds.z_min) * 0.5;
    let half_max_range = max_range * 0.5;

    SceneBounds {
        x_min: x_center - half_max_range,
        x_max: x_center + half_max_range,
        y_min: y_center - half_max_range,
        y_max: y_center + half_max_range,
        z_min: z_center - half_max_range,
        z_max: z_center + half_max_range,
    }
}

/// Calculate scene bounds including coordinate axes endpoints.
pub fn calculate_scene_bounds_with_axes(
    camera_poses: &[&CameraPose],
    points_3d: &[Point3<f64>],
    intrinsics: &CameraIntrinsics,
    frustum_depth: f64,
    scene_center: &Vector3<f64>,
) -> SceneBounds {
    let mut bounds = SceneBounds::new();

    for pose in camera_poses {
        bounds.update_with_point(pose.center());
    }

    for point in points_3d {
        bounds.update_with_point(point);
    }

    for pose in camera_poses {
        let frustum = CameraFrustum::from_camera_intrinsics(
            pose,
            intrinsics,
            frustum_depth,
        );
        for corner in &frustum.corners {
            bounds.update_with_point(corner);
        }
    }

    let x_range = bounds.x_max - bounds.x_min;
    let y_range = bounds.y_max - bounds.y_min;
    let z_range = bounds.z_max - bounds.z_min;
    let max_range = x_range.max(y_range).max(z_range);
    let axis_length = max_range * AXIS_PAD_FACTOR;

    bounds.update_with_point(&Point3::from(*scene_center));
    bounds.update_with_point(&Point3::new(
        scene_center.x + axis_length,
        scene_center.y,
        scene_center.z,
    ));
    bounds.update_with_point(&Point3::new(
        scene_center.x,
        scene_center.y + axis_length,
        scene_center.z,
    ));
    bounds.update_with_point(&Point3::new(
        scene_center.x,
        scene_center.y,
        scene_center.z + axis_length,
    ));

    bounds.with_padding(0.1)
}

pub fn calculate_scene_center(
    camera_poses: &[&CameraPose],
    points_3d: &[Point3<f64>],
) -> Vector3<f64> {
    let mut min_x = f64::MAX;
    let mut max_x = f64::MIN;
    let mut min_y = f64::MAX;
    let mut max_y = f64::MIN;
    let mut min_z = f64::MAX;
    let mut max_z = f64::MIN;

    for pose in camera_poses {
        let center = pose.center();
        min_x = min_x.min(center.x);
        max_x = max_x.max(center.x);
        min_y = min_y.min(center.y);
        max_y = max_y.max(center.y);
        min_z = min_z.min(center.z);
        max_z = max_z.max(center.z);
    }

    for point in points_3d {
        min_x = min_x.min(point.x);
        max_x = max_x.max(point.x);
        min_y = min_y.min(point.y);
        max_y = max_y.max(point.y);
        min_z = min_z.min(point.z);
        max_z = max_z.max(point.z);
    }

    if camera_poses.is_empty() && points_3d.is_empty() {
        return Vector3::new(0.0, 0.0, 0.0);
    }

    Vector3::new(
        (min_x + max_x) * 0.5,
        (min_y + max_y) * 0.5,
        (min_z + max_z) * 0.5,
    )
}

/// Calculate scene bounds for all frames in a camera solve
pub fn calculate_scene_bounds_for_all_frames(
    solved_poses: &std::collections::HashMap<u32, CameraPose>,
    bundle_points: &[Point3<f64>],
) -> SceneBounds {
    let mut bounds = SceneBounds::new();

    for pose in solved_poses.values() {
        bounds.update_with_point(pose.center());
    }

    for point in bundle_points {
        bounds.update_with_point(point);
    }

    bounds.with_padding(0.1)
}

const AXIS_PAD_FACTOR: f64 = 0.15;

fn euler_zxy_to_projection_params(
    tilt_rad: f64,
    pan_rad: f64,
    roll_rad: f64,
) -> (f64, f64) {
    let cos_roll = roll_rad.cos();
    let sin_roll = roll_rad.sin();
    let cos_tilt = tilt_rad.cos();
    let sin_tilt = tilt_rad.sin();
    let cos_pan = pan_rad.cos();
    let sin_pan = pan_rad.sin();

    let rot_z = nalgebra::Matrix3::new(
        cos_roll, -sin_roll, 0.0, sin_roll, cos_roll, 0.0, 0.0, 0.0, 1.0,
    );

    let rot_x = nalgebra::Matrix3::new(
        1.0, 0.0, 0.0, 0.0, cos_tilt, -sin_tilt, 0.0, sin_tilt, cos_tilt,
    );

    let rot_y = nalgebra::Matrix3::new(
        cos_pan, 0.0, sin_pan, 0.0, 1.0, 0.0, -sin_pan, 0.0, cos_pan,
    );

    let forward_vector = nalgebra::Vector3::new(0.0, 0.0, -1.0);
    let rotated_forward = rot_y * rot_x * rot_z * forward_vector;

    let yaw = rotated_forward.x.atan2(-rotated_forward.z);
    let pitch = rotated_forward
        .y
        .asin()
        .clamp(-std::f64::consts::FRAC_PI_2, std::f64::consts::FRAC_PI_2);

    (yaw, pitch)
}

/// Draws coordinate axes (X=Red, Y=Green, Z=Blue).
fn draw_coordinate_axes<DB: DrawingBackend>(
    chart: &mut ChartContext<
        DB,
        Cartesian3d<RangedCoordf64, RangedCoordf64, RangedCoordf64>,
    >,
    bounds: &SceneBounds,
    center: &Vector3<f64>,
) -> Result<()>
where
    DB::ErrorType: 'static,
{
    let x_range = bounds.x_max - bounds.x_min;
    let y_range = bounds.y_max - bounds.y_min;
    let z_range = bounds.z_max - bounds.z_min;
    let max_range = x_range.max(y_range).max(z_range);
    let axis_length = max_range * AXIS_PAD_FACTOR;

    let origin = (center.x, center.y, center.z);

    let x_end = (center.x + axis_length, center.y, center.z);
    chart
        .draw_series(LineSeries::new(vec![origin, x_end], RED.stroke_width(3)))?
        .label("X Axis")
        .legend(|(x, y)| {
            Rectangle::new([(x, y), (x + 10, y + 2)], RED.filled())
        });

    let y_end = (center.x, center.y + axis_length, center.z);
    chart
        .draw_series(LineSeries::new(
            vec![origin, y_end],
            GREEN.stroke_width(3),
        ))?
        .label("Y Axis")
        .legend(|(x, y)| {
            Rectangle::new([(x, y), (x + 10, y + 2)], GREEN.filled())
        });

    let z_end = (center.x, center.y, center.z + axis_length);
    chart
        .draw_series(LineSeries::new(
            vec![origin, z_end],
            BLUE.stroke_width(3),
        ))?
        .label("Z Axis")
        .legend(|(x, y)| {
            Rectangle::new([(x, y), (x + 10, y + 2)], BLUE.filled())
        });

    Ok(())
}

fn draw_epipolar_lines<DB: DrawingBackend>(
    chart: &mut ChartContext<
        DB,
        Cartesian3d<RangedCoordf64, RangedCoordf64, RangedCoordf64>,
    >,
    camera_poses: &[&CameraPose],
    points_3d: &[Point3<f64>],
    options: &EpipolarLineOptions,
) -> Result<()>
where
    DB::ErrorType: 'static,
{
    if !options.enabled || points_3d.is_empty() || camera_poses.is_empty() {
        return Ok(());
    }

    let points_to_draw = if let Some(max_points) = options.max_points {
        if points_3d.len() > max_points {
            let step = points_3d.len() / max_points;
            points_3d.iter().step_by(step).collect::<Vec<_>>()
        } else {
            points_3d.iter().collect::<Vec<_>>()
        }
    } else {
        points_3d.iter().collect::<Vec<_>>()
    };

    for (camera_idx, pose) in camera_poses.iter().enumerate() {
        let camera_position = pose.center();

        let color = if camera_idx < options.camera_colors.len() {
            options.camera_colors[camera_idx]
        } else {
            RGBColor(128, 128, 128)
        };

        let line_color = color.mix(options.opacity);

        for point in &points_to_draw {
            let start =
                (camera_position.x, camera_position.y, camera_position.z);
            let end = (point.x, point.y, point.z);

            chart.draw_series(LineSeries::new(
                vec![start, end],
                line_color.stroke_width(options.line_width),
            ))?;
        }
    }

    if !camera_poses.is_empty() && !options.camera_colors.is_empty() {
        let legend_color = options.camera_colors[0].mix(options.opacity);
        chart
            .draw_series(std::iter::empty::<Circle<(f64, f64, f64), u32>>())?
            .label("Epipolar Lines")
            .legend(move |(x, y)| {
                PathElement::new(
                    vec![(x, y), (x + 10, y)],
                    legend_color.stroke_width(2),
                )
            });
    }

    Ok(())
}

/// A camera pose associated with a specific frame, for trajectory visualization.
#[derive(Debug, Clone)]
pub struct CameraPoseWithFrame {
    pub frame: u32,
    pub pose: CameraPose,
    pub is_initial: bool,
}

fn map_view_name_str(name: &str) -> ViewName {
    match name {
        "front" => ViewName::Front,
        "back" => ViewName::Back,
        "top" => ViewName::Top,
        "bottom" => ViewName::Bottom,
        "right" => ViewName::Right,
        "left" => ViewName::Left,
        "three_quarter_a" => ViewName::ThreeQuarterA,
        "three_quarter_b" => ViewName::ThreeQuarterB,
        _ => ViewName::Front,
    }
}

/// Renders multiple views of a two-camera SfM scene.
pub fn visualize_sfm_scene_views(
    pose_a: &CameraPose,
    pose_b: &CameraPose,
    points_3d: &[Point3<f64>],
    title: &str,
    naming: &OutputFileNaming,
    views: Vec<ViewConfiguration>,
    intrinsics_a: &CameraIntrinsics,
    intrinsics_b: &CameraIntrinsics,
) -> Result<()> {
    views.par_iter().try_for_each(|view_config| -> Result<()> {
        let view_name = map_view_name_str(&view_config.view_name);
        let view_naming = naming.clone_with_view(view_name);

        render_single_view_with_intrinsics(
            pose_a,
            pose_b,
            points_3d,
            &format!("{} - {}", title, view_config.view_name),
            &view_naming,
            view_config,
            intrinsics_a,
            intrinsics_b,
        )
    })?;
    Ok(())
}

/// Renders per-frame trajectory views showing how the camera moves over time.
pub fn visualize_sfm_trajectory_views(
    camera_poses_with_frames: &[CameraPoseWithFrame],
    points_3d: &[Point3<f64>],
    title: &str,
    naming: &OutputFileNaming,
    views: Vec<ViewConfiguration>,
    intrinsics: &CameraIntrinsics,
    step_by: usize,
    bundle_visibility: Option<&BundleVisibilityMap>,
) -> Result<()> {
    let camera_pose_refs: Vec<&CameraPose> = camera_poses_with_frames
        .iter()
        .map(|frame_pose| &frame_pose.pose)
        .collect();
    let scene_center = calculate_scene_center(&camera_pose_refs, points_3d);

    let frustum_depth = views.get(0).map(|v| v.frustum_depth).unwrap_or(1.0);

    let scene_bounds = calculate_uniform_scene_bounds(
        &camera_pose_refs,
        points_3d,
        intrinsics,
        frustum_depth,
        &scene_center,
    );

    let mut frame_list: Vec<u32> = camera_poses_with_frames
        .iter()
        .map(|frame_pose| frame_pose.frame)
        .collect();
    frame_list.sort();
    frame_list.dedup();

    if let Some(first_frame) = frame_list.first() {
        if let Some(first_view) = views.first() {
            let view_name = map_view_name_str(&first_view.view_name);
            let example_naming =
                naming.clone_with_view(view_name).with_frame(*first_frame);
            if let Ok(example_path) = example_naming.full_path() {
                print!(
                    "Generating trajectory views: {} ",
                    example_path.display()
                );
                let _ = std::io::Write::flush(&mut std::io::stdout());
            }
        }
    }

    frame_list.par_iter().step_by(step_by).try_for_each(
        |&frame| -> Result<()> {
            for view_config in &views {
                let view_name = map_view_name_str(&view_config.view_name);
                let frame_naming =
                    naming.clone_with_view(view_name).with_frame(frame);

                let frame_title = format!(
                    "{} - {} - Frame {:04}",
                    title, view_config.view_name, frame
                );

                render_trajectory_frame_with_history(
                    camera_poses_with_frames,
                    frame,
                    points_3d,
                    &frame_title,
                    &frame_naming,
                    view_config,
                    intrinsics,
                    &scene_bounds,
                    bundle_visibility,
                )?;
            }

            print!(".");
            let _ = std::io::Write::flush(&mut std::io::stdout());

            Ok(())
        },
    )?;

    println!();

    Ok(())
}

fn render_single_view_with_intrinsics(
    pose_a: &CameraPose,
    pose_b: &CameraPose,
    points_3d: &[Point3<f64>],
    title: &str,
    naming: &OutputFileNaming,
    view_config: &ViewConfiguration,
    intrinsics_a: &CameraIntrinsics,
    intrinsics_b: &CameraIntrinsics,
) -> Result<()> {
    let file_path = naming.full_path()?;

    let area = BitMapBackend::new(&file_path, view_config.resolution)
        .into_drawing_area();
    area.fill(&WHITE)?;

    let camera_poses = vec![pose_a, pose_b];
    let scene_center = calculate_scene_center(&camera_poses, points_3d);
    let bounds = calculate_uniform_scene_bounds(
        &camera_poses,
        points_3d,
        intrinsics_a,
        view_config.frustum_depth,
        &scene_center,
    );

    let mut chart = ChartBuilder::on(&area)
        .caption(title, ("sans-serif", 20))
        .build_cartesian_3d(
            bounds.x_min..bounds.x_max,
            bounds.y_min..bounds.y_max,
            bounds.z_min..bounds.z_max,
        )?;

    let (yaw, pitch) = euler_zxy_to_projection_params(
        view_config.tilt_radians(),
        view_config.pan_radians(),
        view_config.roll_radians(),
    );

    chart.with_projection(|mut pb| {
        pb.yaw = yaw;
        pb.pitch = pitch;
        pb.scale = 1.0;
        pb.into_matrix()
    });

    chart
        .configure_axes()
        .light_grid_style(BLACK.mix(AXIS_PAD_FACTOR))
        .max_light_lines(3)
        .draw()?;

    if view_config.show_coordinate_axes {
        draw_coordinate_axes(&mut chart, &bounds, &scene_center)?;
    }

    draw_epipolar_lines(
        &mut chart,
        &camera_poses,
        points_3d,
        &view_config.epipolar_options,
    )?;

    let frustum_a = CameraFrustum::from_camera_intrinsics(
        pose_a,
        intrinsics_a,
        view_config.frustum_depth,
    );

    let frustum_b = CameraFrustum::from_camera_intrinsics(
        pose_b,
        intrinsics_b,
        view_config.frustum_depth,
    );

    for (start, end) in frustum_a.get_lines() {
        chart.draw_series(LineSeries::new(
            vec![(start.x, start.y, start.z), (end.x, end.y, end.z)],
            RED.stroke_width(2),
        ))?;
    }

    for (start, end) in frustum_b.get_lines() {
        chart.draw_series(LineSeries::new(
            vec![(start.x, start.y, start.z), (end.x, end.y, end.z)],
            BLUE.stroke_width(2),
        ))?;
    }

    chart
        .draw_series(std::iter::once(Circle::new(
            (pose_a.center().x, pose_a.center().y, pose_a.center().z),
            3,
            RED.filled(),
        )))?
        .label("Camera A")
        .legend(|(x, y)| Circle::new((x + 5, y), 3, RED.filled()));

    chart
        .draw_series(std::iter::once(Circle::new(
            (pose_b.center().x, pose_b.center().y, pose_b.center().z),
            3,
            BLUE.filled(),
        )))?
        .label("Camera B")
        .legend(|(x, y)| Circle::new((x + 5, y), 3, BLUE.filled()));

    if !points_3d.is_empty() {
        chart
            .draw_series(points_3d.iter().map(|point| {
                Circle::new(
                    (point.x, point.y, point.z),
                    2,
                    GREEN.mix(0.7).filled(),
                )
            }))?
            .label("3D Points")
            .legend(|(x, y)| Circle::new((x + 5, y), 2, GREEN.filled()));
    }

    chart.configure_series_labels().border_style(BLACK).draw()?;

    area.present()
        .map_err(|e| anyhow::anyhow!("Failed to save visualization: {}", e))?;
    println!("SfM visualization saved to: {}", file_path.display());

    Ok(())
}

fn render_trajectory_frame_with_history(
    all_camera_poses: &[CameraPoseWithFrame],
    current_frame: u32,
    points_3d: &[Point3<f64>],
    title: &str,
    naming: &OutputFileNaming,
    view_config: &ViewConfiguration,
    intrinsics: &CameraIntrinsics,
    scene_bounds: &SceneBounds,
    bundle_visibility: Option<&BundleVisibilityMap>,
) -> Result<()> {
    let file_path = naming.full_path()?;

    let area = BitMapBackend::new(&file_path, view_config.resolution)
        .into_drawing_area();
    area.fill(&WHITE)?;

    let bounds = scene_bounds;

    if all_camera_poses.is_empty() {
        return Err(anyhow::anyhow!("No camera poses available"));
    }

    let current_frame_exists = all_camera_poses
        .iter()
        .any(|frame_pose| frame_pose.frame == current_frame);
    if !current_frame_exists {
        return Err(anyhow::anyhow!(
            "Current frame {} not found in camera poses",
            current_frame
        ));
    }

    let camera_pose_refs: Vec<&CameraPose> = all_camera_poses
        .iter()
        .map(|frame_pose| &frame_pose.pose)
        .collect();
    let scene_center = calculate_scene_center(&camera_pose_refs, points_3d);

    let mut chart = ChartBuilder::on(&area)
        .caption(title, ("sans-serif", 20))
        .build_cartesian_3d(
            bounds.x_min..bounds.x_max,
            bounds.y_min..bounds.y_max,
            bounds.z_min..bounds.z_max,
        )?;

    let (yaw, pitch) = euler_zxy_to_projection_params(
        view_config.tilt_radians(),
        view_config.pan_radians(),
        view_config.roll_radians(),
    );

    chart.with_projection(|mut pb| {
        pb.yaw = yaw;
        pb.pitch = pitch;
        pb.scale = 1.0;
        pb.into_matrix()
    });

    chart
        .configure_axes()
        .light_grid_style(BLACK.mix(AXIS_PAD_FACTOR))
        .max_light_lines(3)
        .draw()?;

    if view_config.show_coordinate_axes {
        draw_coordinate_axes(&mut chart, bounds, &scene_center)?;
    }

    if !points_3d.is_empty() {
        chart
            .draw_series(points_3d.iter().map(|point| {
                Circle::new(
                    (point.x, point.y, point.z),
                    2,
                    GREEN.mix(0.7).filled(),
                )
            }))?
            .label("3D Points")
            .legend(|(x, y)| Circle::new((x + 5, y), 2, GREEN.filled()));
    }

    let current_pose_opt = all_camera_poses
        .iter()
        .find(|frame_pose| frame_pose.frame == current_frame);

    if let Some(current_frame_pose) = current_pose_opt {
        if !points_3d.is_empty() {
            let visible_points: Vec<Point3<f64>> =
                if let Some(visibility_map) = bundle_visibility {
                    if let Some(visible_indices) =
                        visibility_map.get(&current_frame)
                    {
                        points_3d
                            .iter()
                            .enumerate()
                            .filter_map(|(idx, point)| {
                                if visible_indices.contains(&idx) {
                                    Some(*point)
                                } else {
                                    None
                                }
                            })
                            .collect()
                    } else {
                        Vec::new()
                    }
                } else {
                    points_3d.to_vec()
                };

            if !visible_points.is_empty() {
                let current_camera_poses = vec![&current_frame_pose.pose];

                let mut epipolar_options = view_config.epipolar_options.clone();
                epipolar_options.enabled = true;
                epipolar_options.camera_colors = vec![RGBColor(50, 50, 50)];
                epipolar_options.opacity = 0.5;
                epipolar_options.line_width = 1;

                draw_epipolar_lines(
                    &mut chart,
                    &current_camera_poses,
                    &visible_points,
                    &epipolar_options,
                )?;
            }
        }
    }

    let poses_up_to_current: Vec<&CameraPoseWithFrame> = all_camera_poses
        .iter()
        .filter(|frame_pose| frame_pose.frame <= current_frame)
        .collect();

    if poses_up_to_current.len() >= 2 {
        let trajectory_points: Vec<(f64, f64, f64)> = poses_up_to_current
            .iter()
            .map(|frame_pose| {
                let center = frame_pose.pose.center();
                (center.x, center.y, center.z)
            })
            .collect();

        chart
            .draw_series(LineSeries::new(
                trajectory_points,
                CYAN.stroke_width(2),
            ))?
            .label("Past Trajectory")
            .legend(|(x, y)| {
                PathElement::new(
                    vec![(x, y), (x + 10, y)],
                    CYAN.stroke_width(2),
                )
            });
    }

    let poses_from_current: Vec<&CameraPoseWithFrame> = all_camera_poses
        .iter()
        .filter(|frame_pose| frame_pose.frame >= current_frame)
        .collect();

    if poses_from_current.len() >= 2 {
        let trajectory_points: Vec<(f64, f64, f64)> = poses_from_current
            .iter()
            .map(|frame_pose| {
                let center = frame_pose.pose.center();
                (center.x, center.y, center.z)
            })
            .collect();

        chart
            .draw_series(LineSeries::new(
                trajectory_points,
                MAGENTA.stroke_width(2),
            ))?
            .label("Future Trajectory")
            .legend(|(x, y)| {
                PathElement::new(
                    vec![(x, y), (x + 10, y)],
                    MAGENTA.stroke_width(2),
                )
            });
    }

    let current_frame_pose = all_camera_poses
        .iter()
        .find(|frame_pose| frame_pose.frame == current_frame)
        .ok_or_else(|| {
            anyhow::anyhow!("Current frame {} not found", current_frame)
        })?;

    let current_frustum = CameraFrustum::from_camera_intrinsics(
        &current_frame_pose.pose,
        intrinsics,
        view_config.frustum_depth,
    );

    let (color, marker_size) = if current_frame_pose.is_initial {
        if current_frame_pose.frame == 1 {
            (RED, 4)
        } else {
            (BLUE, 4)
        }
    } else {
        (BLUE, 4)
    };

    for (start, end) in current_frustum.get_lines() {
        chart.draw_series(LineSeries::new(
            vec![(start.x, start.y, start.z), (end.x, end.y, end.z)],
            color.stroke_width(2),
        ))?;
    }

    chart
        .draw_series(std::iter::once(Circle::new(
            (
                current_frame_pose.pose.center().x,
                current_frame_pose.pose.center().y,
                current_frame_pose.pose.center().z,
            ),
            marker_size,
            color.filled(),
        )))?
        .label(&format!("Current Frame {}", current_frame))
        .legend(move |(x, y)| {
            Circle::new((x + 5, y), marker_size, color.filled())
        });

    chart.configure_series_labels().border_style(BLACK).draw()?;

    area.present()
        .map_err(|e| anyhow::anyhow!("Failed to save visualization: {}", e))?;

    Ok(())
}
