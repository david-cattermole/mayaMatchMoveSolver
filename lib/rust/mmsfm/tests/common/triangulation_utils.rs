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

//! Triangulation test utilities.

use anyhow::Result;
use nalgebra::{Matrix3, Matrix3x4, Point2, Point3, Vector2, Vector3};
use std::f64::consts::PI;

use mmio::uvtrack_reader::FrameRange;
use mmio::uvtrack_reader::MarkersData;
use mmsfm_rust::bundle_triangulation::{
    OptimalAngularConfig, TriangulateDataLineLine,
    TriangulateDataOptimalAngular, TriangulatorLineLine,
    TriangulatorOptimalAngular,
};
use mmsfm_rust::camera_pose_maths::{
    compute_fundamental_matrix, create_projection_matrix,
};
use mmsfm_rust::camera_residual_error::{
    compute_reprojection_residuals, compute_residual_statistics,
};
use mmsfm_rust::datatype::camera_pose::create_camera_pose_from_maya_transform;
use mmsfm_rust::datatype::camera_pose::CameraPose;
use mmsfm_rust::datatype::conversions::{
    convert_ndc_points_to_camera_rays,
    convert_ndc_to_camera_coord_point_with_intrinsics,
    convert_ndc_to_camera_coord_point_with_intrinsics_inverted,
    convert_ndc_to_uv_points, convert_uv_to_ndc_points,
};
use mmsfm_rust::datatype::{
    CameraCoordPoint2, CameraCoordValue, CameraFilmBack, CameraIntrinsics,
    ImageSize, MillimeterUnit, NdcPoint2, UnitValue, UvPoint2, UvValue,
};

use crate::common::data_utils::load_marker_data;
use crate::common::marker_utils::extract_specific_frame_correspondences;
use crate::common::visualization::reprojection;
use crate::common::visualization::residuals;
use crate::common::visualization::scene::{
    visualize_sfm_scene_views, ViewConfigurationBuilder,
};

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

/// Available triangulation methods.
#[derive(Debug, Clone, Copy)]
pub enum TriangulationMethod {
    LineLine,
    OptimalAngular,
}

impl TriangulationMethod {
    pub fn name(&self) -> &str {
        match self {
            TriangulationMethod::LineLine => "Line-Line Intersection",
            TriangulationMethod::OptimalAngular => "Optimal Angular",
        }
    }

    pub fn short_name(&self) -> &str {
        match self {
            TriangulationMethod::LineLine => "lineline",
            TriangulationMethod::OptimalAngular => "optimal_angular",
        }
    }

    pub fn all() -> &'static [TriangulationMethod] {
        &[
            TriangulationMethod::LineLine,
            TriangulationMethod::OptimalAngular,
        ]
    }
}

/// Camera setup configuration for synthetic test scenes.
pub struct CameraConfiguration {
    pub camera_b_position: Point3<f64>,
    pub camera_b_tilt_degrees: f64,
    pub camera_b_pan_degrees: f64,
    pub camera_b_roll_degrees: f64,
    pub film_back_width_mm: f64,
    pub film_back_height_mm: f64,
    pub focal_length_mm: f64,
}

impl CameraConfiguration {
    pub fn new_pan(position: Point3<f64>, pan_degrees: f64) -> Self {
        Self {
            camera_b_position: position,
            camera_b_tilt_degrees: 0.0,
            camera_b_pan_degrees: pan_degrees,
            camera_b_roll_degrees: 0.0,
            film_back_width_mm: 36.0,
            film_back_height_mm: 24.0,
            focal_length_mm: 50.0,
        }
    }

    pub fn new_tilt(position: Point3<f64>, tilt_degrees: f64) -> Self {
        Self {
            camera_b_position: position,
            camera_b_tilt_degrees: tilt_degrees,
            camera_b_pan_degrees: 0.0,
            camera_b_roll_degrees: 0.0,
            film_back_width_mm: 36.0,
            film_back_height_mm: 24.0,
            focal_length_mm: 50.0,
        }
    }
}

/// Triangulate multiple points using line-line intersection.
pub fn triangulate_multiple_points_line_line(
    ndc_points_a: &[NdcPoint2<f64>],
    ndc_points_b: &[NdcPoint2<f64>],
    camera_pose_a: &CameraPose,
    camera_pose_b: &CameraPose,
    camera_intrinsics_a: &CameraIntrinsics,
    camera_intrinsics_b: &CameraIntrinsics,
) -> Result<Vec<Point3<f64>>> {
    assert!(ndc_points_a.len() == ndc_points_b.len());
    assert!(!ndc_points_a.is_empty());
    let num_points = ndc_points_a.len();

    let (ray_origins_a, ray_directions_a, ray_origins_b, ray_directions_b) =
        convert_ndc_points_to_camera_rays(
            ndc_points_a,
            ndc_points_b,
            camera_pose_a,
            camera_pose_b,
            camera_intrinsics_a,
            camera_intrinsics_b,
        );

    let mut triangulator = TriangulatorLineLine::new(num_points);
    let triangulate_data = TriangulateDataLineLine {
        origins_a: ray_origins_a,
        directions_a: ray_directions_a,
        origins_b: ray_origins_b,
        directions_b: ray_directions_b,
    };
    let result = triangulator.triangulate_points(&triangulate_data);
    assert_eq!(result.inner.points.len(), result.inner.valid.len());

    let mut triangulated_points = Vec::new();
    for i in 0..num_points {
        if result.inner.valid[i] {
            let point = &result.inner.points[i];
            triangulated_points.push(Point3::new(point.x, point.y, point.z));
        } else {
            triangulated_points.push(Point3::origin());
        }
    }
    assert_eq!(triangulated_points.len(), num_points);

    Ok(triangulated_points)
}

/// Triangulate multiple points using the Optimal Angular method.
pub fn triangulate_multiple_points_optimal_angular(
    ndc_points_a: &[NdcPoint2<f64>],
    ndc_points_b: &[NdcPoint2<f64>],
    camera_pose_a: &CameraPose,
    camera_pose_b: &CameraPose,
    camera_intrinsics_a: &CameraIntrinsics,
    camera_intrinsics_b: &CameraIntrinsics,
) -> Result<Vec<Point3<f64>>> {
    assert!(ndc_points_a.len() == ndc_points_b.len());
    assert!(!ndc_points_a.is_empty());
    let num_points = ndc_points_a.len();

    let center_a = camera_pose_a.center();
    let center_b = camera_pose_b.center();
    let rotation_transpose_a = camera_pose_a.rotation().transpose();
    let rotation_transpose_b = camera_pose_b.rotation().transpose();

    let camera_coords_a: Vec<(f64, f64)> = ndc_points_a
        .iter()
        .map(|ndc_a| {
            let cam_coord = convert_ndc_to_camera_coord_point_with_intrinsics(
                *ndc_a,
                camera_intrinsics_a,
            );
            (cam_coord.x.value(), cam_coord.y.value())
        })
        .collect();
    let camera_coords_b: Vec<(f64, f64)> = ndc_points_b
        .iter()
        .map(|ndc_b| {
            let cam_coord = convert_ndc_to_camera_coord_point_with_intrinsics(
                *ndc_b,
                camera_intrinsics_b,
            );
            (cam_coord.x.value(), cam_coord.y.value())
        })
        .collect();

    let config = OptimalAngularConfig::default();
    let mut triangulator = TriangulatorOptimalAngular::new(num_points, config);
    let mut triangulate_data = TriangulateDataOptimalAngular::new();

    for i in 0..num_points {
        triangulate_data.add_stereo_observation_from_coords(
            *center_a,
            *center_b,
            rotation_transpose_a,
            rotation_transpose_b,
            camera_coords_a[i],
            camera_coords_b[i],
        );
    }

    let result = triangulator.triangulate_points(&triangulate_data);
    let triangulation_results = result.as_ref();

    let mut triangulated_points = Vec::new();
    for i in 0..num_points {
        if triangulation_results.valid[i] {
            let point = &triangulation_results.points[i];
            triangulated_points.push(Point3::new(point.x, point.y, point.z));
        } else {
            triangulated_points.push(Point3::origin());
        }
    }
    assert_eq!(triangulated_points.len(), num_points);

    Ok(triangulated_points)
}

/// Runs the given triangulation method and returns triangulated 3D points.
pub fn run_triangulation_method(
    method: &TriangulationMethod,
    ndc_points_a: &[NdcPoint2<f64>],
    ndc_points_b: &[NdcPoint2<f64>],
    camera_pose_a: &CameraPose,
    camera_pose_b: &CameraPose,
    camera_intrinsics_a: &CameraIntrinsics,
    camera_intrinsics_b: &CameraIntrinsics,
) -> Result<Vec<Point3<f64>>> {
    match method {
        TriangulationMethod::LineLine => triangulate_multiple_points_line_line(
            ndc_points_a,
            ndc_points_b,
            camera_pose_a,
            camera_pose_b,
            camera_intrinsics_a,
            camera_intrinsics_b,
        ),
        TriangulationMethod::OptimalAngular => {
            triangulate_multiple_points_optimal_angular(
                ndc_points_a,
                ndc_points_b,
                camera_pose_a,
                camera_pose_b,
                camera_intrinsics_a,
                camera_intrinsics_b,
            )
        }
    }
}

/// Validates that triangulated points are in front of cameras.
///
/// Set `strict_validation=false` for camera configurations where some points may end up behind a camera.
pub fn validate_and_print_method_results(
    method: &TriangulationMethod,
    triangulated_points: &[Point3<f64>],
    camera_pose_a: &CameraPose,
    camera_pose_b: &CameraPose,
    strict_validation: bool,
) -> Result<()> {
    if DEBUG {
        println!("{} Triangulation Results:", method.name());
        for (i, point) in triangulated_points.iter().enumerate() {
            println!(
                "  Point {}: 3D ({:.6}, {:.6}, {:.6})",
                i, point.x, point.y, point.z
            );
        }
    }

    let mut points_in_front_a = 0;
    let mut points_in_front_b = 0;

    for (i, point) in triangulated_points.iter().enumerate() {
        let point_3d = Point3::from(*point);
        let in_front_a = camera_pose_a.is_point_in_front(&point_3d);
        let in_front_b = camera_pose_b.is_point_in_front(&point_3d);

        if in_front_a {
            points_in_front_a += 1;
        }
        if in_front_b {
            points_in_front_b += 1;
        }

        if DEBUG {
            println!(
                "  Point {}: Camera A front: {}, Camera B front: {}",
                i, in_front_a, in_front_b
            );
        }
    }

    if DEBUG {
        println!(
            "   {}/{} points in front of Camera A",
            points_in_front_a,
            triangulated_points.len()
        );
        println!(
            "   {}/{} points in front of Camera B",
            points_in_front_b,
            triangulated_points.len()
        );
    }

    if strict_validation {
        assert_eq!(
            points_in_front_a,
            triangulated_points.len(),
            "{}: All triangulated points should be in front of Camera A",
            method.name()
        );
        assert_eq!(
            points_in_front_b,
            triangulated_points.len(),
            "{}: All triangulated points should be in front of Camera B",
            method.name()
        );
        validate_geometric_consistency(
            camera_pose_a,
            camera_pose_b,
            triangulated_points,
        )?;
    } else {
        if DEBUG {
            if points_in_front_a == triangulated_points.len()
                && points_in_front_b == triangulated_points.len()
            {
                println!(
                "   {}: All points successfully triangulated in front of cameras",
                method.name()
            );
            } else {
                println!(
                "   Note: This camera configuration produces some triangulation behind cameras"
            );
                println!("         This demonstrates geometric limitations of certain camera setups");
            }
        }
    }

    Ok(())
}

/// Creates a synthetic two-camera setup from the given configuration.
pub fn create_synthetic_camera_setup_with_config(
    config: &CameraConfiguration,
) -> Result<(CameraPose, CameraPose, CameraIntrinsics, CameraIntrinsics)> {
    let camera_pose_a = CameraPose::default();

    let camera_pose_b: CameraPose = create_camera_pose_from_maya_transform(
        config.camera_b_position.x,
        config.camera_b_position.y,
        config.camera_b_position.z,
        config.camera_b_tilt_degrees,
        config.camera_b_pan_degrees,
        config.camera_b_roll_degrees,
    );

    let film_back = CameraFilmBack::from_millimeters(
        config.film_back_width_mm,
        config.film_back_height_mm,
    );
    let focal_length = MillimeterUnit::new(config.focal_length_mm);
    let camera_intrinsics_a =
        CameraIntrinsics::from_centered_lens(focal_length, film_back);
    let camera_intrinsics_b =
        CameraIntrinsics::from_centered_lens(focal_length, film_back);

    Ok((
        camera_pose_a,
        camera_pose_b,
        camera_intrinsics_a,
        camera_intrinsics_b,
    ))
}

/// Checks that all triangulated points are at a reasonable distance from both cameras.
pub fn validate_geometric_consistency(
    camera_pose_a: &CameraPose,
    camera_pose_b: &CameraPose,
    points_3d: &[Point3<f64>],
) -> Result<()> {
    if DEBUG {
        println!("Geometric Validation for {} points:", points_3d.len());
    }
    for (i, point_3d) in points_3d.iter().enumerate() {
        let distance_from_a = (point_3d - camera_pose_a.center()).norm();
        let distance_from_b = (point_3d - camera_pose_b.center()).norm();

        if DEBUG {
            println!(
                "  Point {}: Distance from Camera A: {:.6}",
                i, distance_from_a
            );
            println!(
                "  Point {}: Distance from Camera B: {:.6}",
                i, distance_from_b
            );
        }

        assert!(
            distance_from_a > 0.1,
            "Point {} should be reasonable distance from Camera A (got {:.6}, expected > 0.1)",
            i, distance_from_a
        );
        assert!(
            distance_from_b > 0.1,
            "Point {} should be reasonable distance from Camera B (got {:.6}, expected > 0.1)",
            i, distance_from_b
        );
    }

    if DEBUG {
        println!("   Geometric consistency validated for all points");
    }

    Ok(())
}

/// Computes reprojection residuals, asserts they are within threshold, and saves a visualization.
pub fn generate_residual_analysis(
    points_3d: &[Point3<f64>],
    uv_coords_a: &[UvPoint2<f64>],
    uv_coords_b: &[UvPoint2<f64>],
    camera_pose_a: &CameraPose,
    camera_pose_b: &CameraPose,
    camera_intrinsics_a: &CameraIntrinsics,
    camera_intrinsics_b: &CameraIntrinsics,
    image_size_a: &ImageSize<f64>,
    image_size_b: &ImageSize<f64>,
    output_image_size: &ImageSize<f64>,
    title: &str,
    base_naming: &crate::common::OutputFileNaming,
    max_error_threshold: f64,
) -> Result<()> {
    let mut residuals = vec![0.0; points_3d.len()];
    compute_reprojection_residuals(
        points_3d,
        uv_coords_a,
        uv_coords_b,
        camera_pose_a,
        camera_pose_b,
        camera_intrinsics_a,
        camera_intrinsics_b,
        image_size_a,
        image_size_b,
        &mut residuals,
    )?;

    let stats = compute_residual_statistics(&residuals);

    if DEBUG {
        println!("Reprojection Residual Analysis:");
        println!("  Mean error: {:.6} pixels", stats.mean);
        println!("  Median error: {:.6} pixels", stats.median);
        println!("  Standard deviation: {:.6} pixels", stats.std_dev);
        println!("  Max error: {:.6} pixels", stats.max);
        println!("  Min error: {:.6} pixels", stats.min);
    }

    assert!(
        stats.max < max_error_threshold,
        "{}: Max reprojection error should be less than {:.1} pixels, got {:.6} pixels (mean: {:.6})",
        title,
        max_error_threshold,
        stats.max,
        stats.mean
    );

    if !residuals.is_empty() && stats.mean.is_finite() {
        use crate::common::VisualizationType;
        let naming_residuals = base_naming
            .clone_with_visualization(VisualizationType::ResidualsLinePlot);
        super::visualization::residuals::visualize_residual_errors_line_plot(
            &residuals,
            &stats,
            &format!("{} - Residual Errors", title),
            &naming_residuals,
        )?;
    } else {
        if DEBUG {
            println!(
                "Skipping residual visualization: no valid reprojection data"
            );
        }
    }

    Ok(())
}

/// Generates 3D scene views and 2D marker reprojection visualizations.
pub fn generate_visualization_outputs(
    camera_pose_a: &CameraPose,
    camera_pose_b: &CameraPose,
    points_3d: &[Point3<f64>],
    uv_coords_a: &[UvPoint2<f64>],
    uv_coords_b: &[UvPoint2<f64>],
    camera_intrinsics_a: &CameraIntrinsics,
    camera_intrinsics_b: &CameraIntrinsics,
    image_size_a: &ImageSize<f64>,
    image_size_b: &ImageSize<f64>,
    title: &str,
    base_naming: &crate::common::OutputFileNaming,
    max_error_threshold: f64,
) -> Result<()> {
    if DEBUG {
        println!("Generating comprehensive visualizations...");
    }

    let views = vec![
        ViewConfigurationBuilder::new()
            .view_name("front")
            .rotation_ortho_front()
            .resolution_hd()
            .build(),
        ViewConfigurationBuilder::new()
            .view_name("top")
            .rotation_ortho_top()
            .resolution_hd()
            .build(),
        ViewConfigurationBuilder::new()
            .view_name("right")
            .rotation_ortho_right()
            .resolution_hd()
            .build(),
    ];

    use crate::common::Stage;
    let naming_scene = base_naming.clone_with_stage(Stage::Initial);
    visualize_sfm_scene_views(
        &mmlogger::NoOpLogger,
        camera_pose_a,
        camera_pose_b,
        points_3d,
        title,
        &naming_scene,
        views,
        camera_intrinsics_a,
        camera_intrinsics_b,
    )?;

    if DEBUG {
        println!("3D scene visualizations generated.");

        // Generate 2D marker reprojection and residual visualizations.
        println!(
            "Generating 2D marker reprojection and residual visualizations..."
        );
    }

    let frame_pair = crate::common::data_utils::FramePair {
        frame_a: 1,
        frame_b: 2,
    };

    use crate::common::VisualizationType;
    let naming_marker_2d = base_naming
        .clone_with_visualization(VisualizationType::MarkerReprojection2d);
    let output_image_size = ImageSize::full_hd();
    super::visualization::reprojection::visualize_marker_reprojections_2d_scatter(
        uv_coords_a,
        uv_coords_b,
        points_3d,
        camera_pose_a,
        camera_pose_b,
        camera_intrinsics_a,
        camera_intrinsics_b,
        image_size_a,
        image_size_b,
        &frame_pair,
        title,
        &output_image_size,
        &naming_marker_2d,
    )?;

    if let Err(e) = generate_residual_analysis(
        points_3d,
        uv_coords_a,
        uv_coords_b,
        camera_pose_a,
        camera_pose_b,
        camera_intrinsics_a,
        camera_intrinsics_b,
        &image_size_a,
        &image_size_b,
        &output_image_size,
        title,
        base_naming,
        max_error_threshold,
    ) {
        if DEBUG {
            println!("Warning: Residual analysis failed: {}", e);
            println!(
                "This may occur when triangulated points are behind cameras"
            );
        }
    }

    if DEBUG {
        println!(
            "2D marker reprojection and residual visualizations generated"
        );
        println!("All visualizations generated successfully");
    }
    Ok(())
}

/// Generates all visualization outputs for a single triangulation method.
pub fn generate_method_visualization(
    method: &TriangulationMethod,
    triangulated_points: &[Point3<f64>],
    uv_coords_a: &[UvPoint2<f64>],
    uv_coords_b: &[UvPoint2<f64>],
    camera_pose_a: &CameraPose,
    camera_pose_b: &CameraPose,
    camera_intrinsics_a: &CameraIntrinsics,
    camera_intrinsics_b: &CameraIntrinsics,
    image_size_a: &ImageSize<f64>,
    image_size_b: &ImageSize<f64>,
    title: &str,
    base_naming: &crate::common::OutputFileNaming,
    max_error_threshold: f64,
) -> Result<()> {
    let method_title = format!("{} ({})", title, method.name());

    if DEBUG {
        println!(
            "\nGenerating visualizations for {} method...",
            method.name()
        );
    }

    generate_visualization_outputs(
        camera_pose_a,
        camera_pose_b,
        triangulated_points,
        uv_coords_a,
        uv_coords_b,
        camera_intrinsics_a,
        camera_intrinsics_b,
        image_size_a,
        image_size_b,
        &method_title,
        base_naming,
        max_error_threshold,
    )?;

    Ok(())
}

/// Runs all triangulation methods, validates results, and generates visualizations.
pub fn run_triangulate_all_methods(
    uv_coords_a: &[UvPoint2<f64>],
    uv_coords_b: &[UvPoint2<f64>],
    ndc_points_a: &[NdcPoint2<f64>],
    ndc_points_b: &[NdcPoint2<f64>],
    camera_pose_a: &CameraPose,
    camera_pose_b: &CameraPose,
    camera_intrinsics_a: &CameraIntrinsics,
    camera_intrinsics_b: &CameraIntrinsics,
    title: &str,
    base_naming: &crate::common::OutputFileNaming,
    image_size: ImageSize<f64>,
    // TODO: Remove the need for this "strict_validation", it
    // should always be strict.
    strict_validation: bool,
    max_error_threshold: f64,
) -> Result<()> {
    if DEBUG {
        println!(
            "Camera A: Position {:?}, No rotation",
            camera_pose_a.center()
        );
        println!("Camera B: Position {:?}", camera_pose_b.center());
        println!(
            "Test points: {} point pairs across camera frustums\n",
            ndc_points_a.len()
        );
    }

    for method in TriangulationMethod::all() {
        if DEBUG {
            println!("\n--- Testing {} Method ---", method.name());
        }

        let result = match run_triangulation_method(
            method,
            &ndc_points_a,
            &ndc_points_b,
            camera_pose_a,
            camera_pose_b,
            camera_intrinsics_a,
            camera_intrinsics_b,
        ) {
            Ok(points) => points,
            Err(e) => return Err(e),
        };

        validate_and_print_method_results(
            method,
            &result,
            camera_pose_a,
            camera_pose_b,
            strict_validation,
        )?;

        let method_naming =
            base_naming.clone_with_triangulation_method(method.short_name());

        generate_method_visualization(
            method,
            &result,
            &uv_coords_a,
            &uv_coords_b,
            camera_pose_a,
            camera_pose_b,
            camera_intrinsics_a,
            camera_intrinsics_b,
            &image_size,
            &image_size,
            title,
            &method_naming,
            max_error_threshold,
        )?;
    }

    if DEBUG {
        println!("\nTriangulation validation test completed successfully!");
        println!(
            "All methods completed. Check output directory for visualizations."
        );
    }
    Ok(())
}

/// Runs a triangulation test from a marker file using exact known camera poses.
pub fn run_triangulation_test_from_file(
    markers: &MarkersData,
    frame_range: &FrameRange,
    expected_frame_range: FrameRange,
    correspondence_frames: (u32, u32),
    film_back: CameraFilmBack<f64>,
    focal_length: MillimeterUnit<f64>,
    pose_b_translation: Vector3<f64>,
    pose_b_rotation: Vector3<f64>,
    title: &str,
    base_naming: &crate::common::OutputFileNaming,
    strict_validation: bool,
    max_error_threshold: f64,
) -> Result<()> {
    if DEBUG {
        println!(
            "Perfect Triangulation Test - Test Cube Dataset with Exact Poses"
        );
        println!(
            "================================================================"
        );

        println!("Loaded marker data:");
        println!(
            "  Frame range: {} to {}",
            frame_range.start_frame, frame_range.end_frame
        );
        println!("  Number of markers: {}", markers.frame_data.len());
    }

    assert_eq!(
        frame_range.start_frame, expected_frame_range.start_frame,
        "Expected data to start at frame {}.",
        expected_frame_range.start_frame
    );
    assert_eq!(
        frame_range.end_frame, expected_frame_range.end_frame,
        "Expected data to end at frame {}.",
        expected_frame_range.end_frame
    );

    let intrinsics_a =
        CameraIntrinsics::from_centered_lens(focal_length, film_back);
    let intrinsics_b =
        CameraIntrinsics::from_centered_lens(focal_length, film_back);

    if DEBUG {
        println!("Camera intrinsics configuration:");
        println!("  Focal length X: {:.6}", intrinsics_a.focal_length_x);
        println!("  Focal length Y: {:.6}", intrinsics_a.focal_length_y);
        println!(
            "  Principal point: ({:.6}, {:.6})",
            intrinsics_a.principal_point.x.value(),
            intrinsics_a.principal_point.y.value()
        );
    }

    let (frame_a, frame_b) = correspondence_frames;
    let (uv_coords_a, uv_coords_b) =
        extract_specific_frame_correspondences(markers, frame_a, frame_b)?;

    assert_eq!(uv_coords_a.len(), uv_coords_b.len());
    let num_points = uv_coords_a.len();

    if DEBUG {
        println!("Point correspondences:");
        println!("  Frame {} points: {}", frame_a, uv_coords_a.len());
        println!("  Frame {} points: {}", frame_b, uv_coords_b.len());
        println!("  Total point pairs: {}", num_points);

        // Show a few UV coordinate examples.
        println!("Sample UV coordinates:");

        for i in 0..uv_coords_a.len() {
            println!(
            "  Point {}: Frame {} ({:.6}, {:.6}) -> Frame {} ({:.6}, {:.6})",
            i,
            frame_a,
            uv_coords_a[i].x,
            uv_coords_a[i].y,
            frame_b,
            uv_coords_b[i].x,
            uv_coords_b[i].y
        );
        }
    }

    let ndc_points_a = convert_uv_to_ndc_points(&uv_coords_a);
    let ndc_points_b = convert_uv_to_ndc_points(&uv_coords_b);

    if DEBUG {
        println!(
            "Converted {} UV points to NDC coordinates",
            ndc_points_a.len()
        );
    }

    let pose_a = CameraPose::default();
    let pose_b = create_camera_pose_from_maya_transform(
        pose_b_translation.x,
        pose_b_translation.y,
        pose_b_translation.z,
        pose_b_rotation.x,
        pose_b_rotation.y,
        pose_b_rotation.z,
    );

    if DEBUG {
        println!("Exact camera poses constructed:");
        println!("  Pose A (identity): center {:?}", pose_a.center());
        println!("  Pose B: center {:?}", pose_b.center());
    }

    run_triangulate_all_methods(
        &uv_coords_a,
        &uv_coords_b,
        &ndc_points_a,
        &ndc_points_b,
        &pose_a,
        &pose_b,
        &intrinsics_a,
        &intrinsics_b,
        title,
        base_naming,
        ImageSize::full_hd(),
        strict_validation,
        max_error_threshold,
    )?;

    if DEBUG {
        println!(
            "Test cube triangulation test with exact poses completed successfully!"
        );
    }

    Ok(())
}

/// Creates synthetic 3D points arranged in a grid at the given depth.
pub fn create_synthetic_3d_points_grid(
    grid_size: usize,
    spacing: f64,
    depth: f64,
    center_y: f64,
) -> Vec<Point3<f64>> {
    let mut points = Vec::new();
    let offset = (grid_size - 1) as f64 * spacing / 2.0;

    for i in 0..grid_size {
        for j in 0..grid_size {
            let x = i as f64 * spacing - offset;
            let y = j as f64 * spacing - offset + center_y;
            let z = depth;
            points.push(Point3::new(x, y, z));
        }
    }

    points
}

/// Projects a 3D world point to NDC coordinates. Returns `None` if the point is behind the camera.
pub fn forward_project_point_to_ndc(
    point_3d: &Point3<f64>,
    camera_pose: &CameraPose,
    camera_intrinsics: &CameraIntrinsics,
) -> Option<NdcPoint2<f64>> {
    if !camera_pose.is_point_in_front(point_3d) {
        return None;
    }

    // Transform the point from world space to camera space.
    let extrinsic = camera_pose.as_extrinsic_matrix();
    let point_homogeneous =
        nalgebra::Vector4::new(point_3d.x, point_3d.y, point_3d.z, 1.0);
    let point_camera = extrinsic * point_homogeneous;

    // Divide by -Z (Maya convention: camera looks down -Z).
    let x_norm = point_camera.x / -point_camera.z;
    let y_norm = point_camera.y / -point_camera.z;

    let focal_x = camera_intrinsics.focal_length_x;
    let focal_y = camera_intrinsics.focal_length_y;
    let principal_x = camera_intrinsics.principal_point.x.value();
    let principal_y = camera_intrinsics.principal_point.y.value();

    // ndc = camera_coord * (2 * focal_length) + principal_point
    let ndc_x = x_norm * (2.0 * focal_x) + principal_x;
    let ndc_y = y_norm * (2.0 * focal_y) + principal_y;

    Some(NdcPoint2::new(
        mmsfm_rust::datatype::NdcValue::new(ndc_x),
        mmsfm_rust::datatype::NdcValue::new(ndc_y),
    ))
}

/// Projects 3D world points to NDC for multiple cameras. Fails if any point is behind any camera.
pub fn forward_project_points_to_nview(
    points_3d: &[Point3<f64>],
    camera_poses: &[CameraPose],
    camera_intrinsics: &[CameraIntrinsics],
) -> Result<Vec<Vec<NdcPoint2<f64>>>> {
    assert_eq!(
        camera_poses.len(),
        camera_intrinsics.len(),
        "Number of camera poses must match number of intrinsics"
    );

    let num_cameras = camera_poses.len();
    let mut ndc_points_per_camera = Vec::with_capacity(num_cameras);

    for cam_idx in 0..num_cameras {
        let mut ndc_points = Vec::with_capacity(points_3d.len());

        for point_3d in points_3d {
            if let Some(ndc_point) = forward_project_point_to_ndc(
                point_3d,
                &camera_poses[cam_idx],
                &camera_intrinsics[cam_idx],
            ) {
                ndc_points.push(ndc_point);
            } else {
                anyhow::bail!(
                    "Point {:?} is behind camera {} - all points must be visible in all cameras",
                    point_3d,
                    cam_idx
                );
            }
        }

        ndc_points_per_camera.push(ndc_points);
    }

    Ok(ndc_points_per_camera)
}
