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

//! mmsfm CLI executable - Structure from Motion camera solver.

mod cli;
mod defaults;
mod parser;
mod undistort;

use anyhow::{Context, Result};
#[cfg(feature = "visualization")]
use nalgebra::Point3;
use rayon::ThreadPoolBuilder;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::thread::available_parallelism;
use std::time::Instant;

use cli::{
    parse_args, print_help, print_version, CliArgs, ParseResult, SolverType,
};
use mmio::bundle_writer::{write_bundle_file, BundlePoint};
use mmio::kuper_writer::{
    extract_zxy_euler_angles, maya_pose_to_kuper, write_kuper_file,
    KuperFrameData,
};
use mmio::mmcamera_common::{
    MmCameraAttrData, MmCameraData, MmCameraImageData,
};
use mmio::mmcamera_writer::write_mmcamera_file;
use mmio::mmresiduals_common::{
    MmResidualsData, MmResidualsFrameData, MmResidualsStatistics,
};
use mmio::mmresiduals_writer::write_mmresiduals_file;
use mmio::mmsettings_reader::{
    parse_mmsettings_file, AdjustmentSolverType, MmSettingsData,
};
use mmio::nuke_lens_reader::{read_nuke_lens_file, NukeLensData};
use mmio::nuke_lens_writer::write_nuke_lens_file;
use mmio::uvtrack_reader::{parse_file, FrameRange, MarkersData};
#[cfg(feature = "logging")]
use mmlogger::LevelFilter;
#[cfg(feature = "logging")]
use mmlogger::LogFormat;
use mmlogger::Logger;
use mmlogger::{mm_info_log, mm_progress_log, mm_warn_log};
use mmsfm::datatype::common::UnitValue;
use mmsfm::datatype::{
    BundlePositions, CameraFilmBack, CameraIntrinsics, CameraPoses, ImageSize,
    MillimeterUnit,
};
use mmsfm::sfm_camera::{
    camera_solve, CameraSolveConfig, GlobalAdjustmentConfig,
    IntermediateResultWriter, ReprojectionErrorStats, SolveQualityMetrics,
};
use undistort::undistort_markers_with_lens;

use mmsfm::camera_residual_error::compute_per_frame_per_marker_residuals;
#[cfg(feature = "visualization")]
use mmsfm::datatype::marker_observations::MarkerIndex;
#[cfg(feature = "visualization")]
use mmsfm::datatype::{UvPoint2, UvValue};
#[cfg(feature = "visualization")]
use mmsfm::visualization::{
    visualize_marker_reprojections_sequential,
    visualize_multi_frame_residuals_per_marker, visualize_sfm_trajectory_views,
    CameraPoseWithFrame, OutputFileNaming, TestType, ViewConfigurationBuilder,
    VisualizationType,
};

#[cfg(feature = "visualization")]
const ENABLE_VISUALIZATIONS: bool = true;
#[cfg(not(feature = "visualization"))]
const ENABLE_VISUALIZATIONS: bool = false;

fn main() {
    match run() {
        Ok(()) => {}
        Err(e) => {
            eprintln!("Error: {:#}", e);
            std::process::exit(1);
        }
    }
}

fn run() -> Result<()> {
    let args = match parse_args() {
        ParseResult::Args(args) => args,
        ParseResult::Help => {
            print_help();
            return Ok(());
        }
        ParseResult::Version => {
            print_version();
            return Ok(());
        }
        ParseResult::Error(msg) => {
            eprintln!("Error: {}", msg);
            eprintln!();
            print_help();
            std::process::exit(1);
        }
    };

    #[cfg(feature = "logging")]
    {
        std::fs::create_dir_all(&args.output_dir).with_context(|| {
            format!("Failed to create output directory: {}", args.output_dir)
        })?;
        let log_filename = match &args.prefix {
            Some(prefix) => format!("{}_solve.log", prefix),
            None => "solve.log".to_string(),
        };
        let log_path = format!("{}/{}", args.output_dir, log_filename);
        let file = std::fs::File::create(&log_path).with_context(|| {
            format!("Failed to create log file: {}", log_path)
        })?;
        let (stdout_format, stdout_level) = match args.console_level {
            cli::LogVerbosity::Warn => {
                (LogFormat::Plain, LevelFilter::WARN | LevelFilter::ERROR)
            }
            cli::LogVerbosity::Progress => (
                LogFormat::Plain,
                LevelFilter::PROGRESS | LevelFilter::WARN | LevelFilter::ERROR,
            ),
            cli::LogVerbosity::Info => (
                LogFormat::Plain,
                LevelFilter::INFO
                    | LevelFilter::PROGRESS
                    | LevelFilter::WARN
                    | LevelFilter::ERROR,
            ),
            cli::LogVerbosity::Debug => (LogFormat::Full, LevelFilter::ALL),
        };

        let (file_format, file_level) = match args.log_level {
            cli::LogVerbosity::Warn => {
                (LogFormat::Timestamp, LevelFilter::WARN | LevelFilter::ERROR)
            }
            cli::LogVerbosity::Progress => (
                LogFormat::Timestamp,
                LevelFilter::PROGRESS | LevelFilter::WARN | LevelFilter::ERROR,
            ),
            cli::LogVerbosity::Info => (
                LogFormat::Timestamp,
                LevelFilter::INFO
                    | LevelFilter::PROGRESS
                    | LevelFilter::WARN
                    | LevelFilter::ERROR,
            ),
            cli::LogVerbosity::Debug => (LogFormat::Full, LevelFilter::ALL),
        };

        let (log, handle) = mmlogger::channel_logger(
            std::io::stdout(),
            stdout_format,
            stdout_level,
            file,
            file_format,
            file_level,
        );

        let result = run_camera_solve(&args, &log);
        drop(log);
        handle.shutdown();
        result
    }

    #[cfg(not(feature = "logging"))]
    {
        let log = mmlogger::NoOpLogger;
        run_camera_solve(&args, &log)
    }
}

fn setup_thread_pool(threads: Option<usize>) -> Result<()> {
    match threads {
        Some(thread_count) => {
            ThreadPoolBuilder::new()
                .num_threads(thread_count)
                .build_global()
                .unwrap();
        }
        None => {
            let thread_count = available_parallelism()?.get();
            if thread_count > 0 {
                ThreadPoolBuilder::new()
                    .num_threads(thread_count)
                    .build_global()
                    .unwrap();
            }
        }
    }
    Ok(())
}

/// Writes intermediate solver results to disk during a solve.
struct FileIntermediateResultWriter {
    output_dir: String,
    prefix: Option<String>,
    focal_length_mm: f64,
    markers: Arc<MarkersData>,
    film_back: CameraFilmBack<f64>,
    frame_range: FrameRange,
    counter: AtomicUsize,
    nuke_lens: Option<Arc<NukeLensData>>,
}

impl IntermediateResultWriter for FileIntermediateResultWriter {
    fn write_intermediate(
        &self,
        camera_poses: CameraPoses,
        bundle_positions: BundlePositions,
        stats: ReprojectionErrorStats,
    ) {
        let n = self.counter.fetch_add(1, Ordering::Relaxed);
        let suffix = format!("_intermediate_{:03}", n);

        let prefix_str = self
            .prefix
            .as_ref()
            .map(|p| format!("{}{}", p, suffix))
            .unwrap_or(suffix.clone());

        // Write Kuper file.
        let kuper_path =
            format!("{}/{}_camera.kuper", self.output_dir, prefix_str);
        if let Err(e) =
            write_kuper_output(&kuper_path, &camera_poses, self.focal_length_mm)
        {
            eprintln!(
                "Warning: failed to write intermediate Kuper file: {}",
                e
            );
        }

        // Write bundle file.
        let bundle_path =
            format!("{}/{}_bundles.mmbundles", self.output_dir, prefix_str);
        if let Err(e) =
            write_bundle_output(&bundle_path, &self.markers, &bundle_positions)
        {
            eprintln!(
                "Warning: failed to write intermediate bundle file: {}",
                e
            );
        }

        // Write mmcamera file.
        let mmcamera_path =
            format!("{}/{}_camera.mmcamera", self.output_dir, prefix_str);
        let intrinsics = CameraIntrinsics::from_centered_lens(
            MillimeterUnit::new(self.focal_length_mm),
            self.film_back,
        );
        if let Err(e) = write_mmcamera_output_raw(
            &mmcamera_path,
            &camera_poses,
            &intrinsics,
            &self.film_back,
            &self.frame_range,
        ) {
            eprintln!(
                "Warning: failed to write intermediate mmcamera file: {}",
                e
            );
        }

        // Write nuke lens file.
        if let Some(ref lens_data) = self.nuke_lens {
            let lens_path =
                format!("{}/{}_lens.nk", self.output_dir, prefix_str);
            if let Err(e) = write_nuke_lens_file(&lens_path, lens_data) {
                eprintln!(
                    "Warning: failed to write intermediate Nuke lens file: {}",
                    e
                );
            }
        }

        eprintln!(
            "  Intermediate result #{}: mean={:.4}px median={:.4}px cameras={} bundles={}",
            n, stats.mean, stats.median, camera_poses.len(), bundle_positions.len()
        );
    }
}

fn run_camera_solve<L: Logger + Clone + Send + Sync>(
    args: &CliArgs,
    logger: &L,
) -> Result<()> {
    let total_start = Instant::now();

    // Load solver settings file if provided.
    let settings: Option<MmSettingsData> = if let Some(ref settings_path) =
        args.solver_settings_file
    {
        mm_info_log!(logger, "Loading solver settings from: {}", settings_path);
        let s = parse_mmsettings_file(settings_path)
            .map_err(|e| anyhow::anyhow!("{}", e))?;
        Some(s)
    } else {
        None
    };

    // Load Nuke lens distortion file if provided.
    let nuke_lens_data: Option<Arc<NukeLensData>> =
        if let Some(ref lens_path) = args.nuke_lens_file {
            mm_info_log!(logger, "Loading Nuke lens file from: {}", lens_path);
            let data = read_nuke_lens_file(lens_path)
                .map_err(|e| anyhow::anyhow!("{}", e))?;

            mm_info_log!(logger, "  Loaded {} lens layer(s)", data.layer_count);
            Some(Arc::new(data))
        } else {
            None
        };

    // Thread count: CLI flag > settings file > auto.
    let thread_count = args.threads.or_else(|| {
        settings
            .as_ref()
            .and_then(|s| s.adjustment_solver.as_ref())
            .and_then(|adj| adj.thread_count)
    });
    setup_thread_pool(thread_count)?;

    if let Some(ref mmcamera_path) = args.mmcamera_file {
        mm_info_log!(logger, "Using mmcamera defaults from: {}", mmcamera_path);
    }
    mm_info_log!(logger, "Loading UV markers from: {}", args.uv_file);

    let (file_info, mut markers) = parse_file(&args.uv_file)
        .with_context(|| format!("Failed to load UV file: {}", args.uv_file))?;

    mm_info_log!(logger, "Loaded {} markers:", markers.len());
    mm_info_log!(logger, "  Format version: {:?}", file_info.version);
    mm_info_log!(
        logger,
        "  Frame range: {} - {}",
        markers.frame_range.start_frame,
        markers.frame_range.end_frame
    );

    // Determine frame range: CLI > settings file > UV file.
    let settings_start = settings.as_ref().and_then(|s| s.start_frame);
    let settings_end = settings.as_ref().and_then(|s| s.end_frame);
    let frame_range = FrameRange {
        start_frame: args
            .start_frame
            .or(settings_start)
            .unwrap_or(markers.frame_range.start_frame),
        end_frame: args
            .end_frame
            .or(settings_end)
            .unwrap_or(markers.frame_range.end_frame),
    };

    mm_info_log!(
        logger,
        "  Using frame range: {} - {}",
        frame_range.start_frame,
        frame_range.end_frame
    );

    // Check for distorted/undistorted marker data.
    let has_explicit_distorted =
        markers.frame_data.iter().any(|fd| fd.has_distorted());

    if nuke_lens_data.is_some() {
        // Lens file provided - apply undistortion in-place.
        // For v3+ files with explicit distorted data, the source is u_coords_dist/v_coords_dist.
        // For v1/v2 files (or v3+ without distorted data), the source is u_coords/v_coords.
        mm_info_log!(
            logger,
            "  Applying lens undistortion to marker positions..."
        );

        undistort_markers_with_lens(
            &mut markers,
            nuke_lens_data.as_ref().unwrap(),
            has_explicit_distorted,
        )?;
        mm_info_log!(logger, "  Undistortion applied successfully.");
    } else if has_explicit_distorted {
        if file_info.marker_undistorted {
            // File has both distorted and undistorted data; use the stored undistorted positions.
            mm_info_log!(logger, "  UV file contains both distorted and undistorted data; using stored undistorted positions.");
        } else {
            mm_warn_log!(logger, "  UV file contains only distorted marker positions but no lens file was provided. Solving will use distorted positions which may reduce accuracy.");
        }
    }

    let film_back = CameraFilmBack::from_millimeters(
        args.film_back_width_mm,
        args.film_back_height_mm,
    );

    let camera_intrinsics = CameraIntrinsics::from_physical_parameters(
        MillimeterUnit::new(args.focal_length_mm),
        MillimeterUnit::new(args.lens_center_x_mm),
        MillimeterUnit::new(args.lens_center_y_mm),
        film_back,
    );

    let image_size = ImageSize::from_pixels(
        args.image_width as f64,
        args.image_height as f64,
    );

    mm_info_log!(logger, "Camera parameters:");
    mm_info_log!(logger, "  Focal length: {} mm", args.focal_length_mm);
    mm_info_log!(
        logger,
        "  Lens center: ({}, {}) mm",
        args.lens_center_x_mm,
        args.lens_center_y_mm
    );
    mm_info_log!(
        logger,
        "  Image size: {}x{} pixels",
        args.image_width,
        args.image_height
    );
    mm_info_log!(
        logger,
        "  Film back: {}x{} mm",
        args.film_back_width_mm,
        args.film_back_height_mm
    );

    let mut config = CameraSolveConfig::default();
    if let Some(ref s) = settings {
        config.origin_frame = s.origin_frame;
    }

    let settings_fl_bounds: Option<(f64, f64)> =
        settings.as_ref().and_then(|s| {
            s.adjustment_attributes
                .iter()
                .find(|a| a.name == "camera.focal_length_mm")
                .map(|a| (a.value_min, a.value_max))
        });
    let settings_fl_sample_count: Option<u32> =
        settings.as_ref().and_then(|s| {
            s.adjustment_attributes
                .iter()
                .find(|a| a.name == "camera.focal_length_mm")
                .and_then(|a| a.sample_count)
        });

    let enable_coarse_search = settings
        .as_ref()
        .and_then(|s| s.adjustment_solver.as_ref())
        .map(|adj| adj.evolution_value_range_estimate)
        .unwrap_or(true);

    // Determine solver type: CLI > settings file > default (None).
    let solver_type = if args.solver != SolverType::None {
        args.solver
    } else if let Some(ref s) = settings {
        if let Some(ref adj) = s.adjustment_solver {
            match adj.solver_type {
                AdjustmentSolverType::EvolutionRefine => SolverType::Refine,
                AdjustmentSolverType::EvolutionUniform => SolverType::Unknown,
                AdjustmentSolverType::UniformGrid => SolverType::Refine,
            }
        } else {
            SolverType::None
        }
    } else {
        SolverType::None
    };

    // Check if settings request uniform grid search.
    let use_uniform_grid = settings
        .as_ref()
        .and_then(|s| s.adjustment_solver.as_ref())
        .map(|adj| adj.solver_type == AdjustmentSolverType::UniformGrid)
        .unwrap_or(false);

    // Get generation count from settings file.
    let settings_generations: Option<usize> = settings
        .as_ref()
        .and_then(|s| s.adjustment_solver.as_ref())
        .and_then(|adj| adj.evolution_generation_count);

    // Configure global adjustment based on solver type.
    let global_adjustment_config = match solver_type {
        SolverType::None => None,
        SolverType::Refine => {
            if use_uniform_grid {
                let (min_fl, max_fl) = settings_fl_bounds.unwrap_or((
                    defaults::UNIFORM_GRID_FL_MIN_MM,
                    defaults::UNIFORM_GRID_FL_MAX_MM,
                ));
                let num_samples = settings_fl_sample_count
                    .unwrap_or(defaults::UNIFORM_GRID_DEFAULT_SAMPLES as u32)
                    as usize;

                mm_info_log!(
                    logger,
                    "Solver: uniform grid ({:.1}-{:.1} mm, {} samples)",
                    min_fl,
                    max_fl,
                    num_samples
                );
                Some(GlobalAdjustmentConfig::UniformGridSearch {
                    focal_length_bounds: (min_fl, max_fl),
                    num_samples,
                })
            } else {
                let (min_fl, max_fl) = settings_fl_bounds.unwrap_or((
                    (args.focal_length_mm
                        * defaults::REFINE_BOUNDS_LOWER_FACTOR)
                        .max(defaults::MIN_FOCAL_LENGTH_MM),
                    (args.focal_length_mm
                        * defaults::REFINE_BOUNDS_UPPER_FACTOR)
                        .min(defaults::MAX_FOCAL_LENGTH_MM),
                ));
                let generations = settings_generations
                    .unwrap_or(defaults::REFINE_DE_GENERATIONS);

                mm_info_log!(
                    logger,
                    "Solver: refine mode (DE SmallRefinement, {:.1}-{:.1} mm)",
                    min_fl,
                    max_fl
                );
                Some(GlobalAdjustmentConfig::DifferentialEvolution {
                    mode:
                        mmsfm::sfm_camera::GlobalAdjustmentMode::SmallRefinement,
                    focal_length_bounds: (min_fl, max_fl),
                    generations,
                    seed: defaults::REFINE_DE_SEED,
                    enable_coarse_search,
                })
            }
        }
        SolverType::Unknown => {
            let (min_fl, max_fl) = settings_fl_bounds.unwrap_or((
                defaults::UNKNOWN_FL_MIN_MM,
                defaults::UNKNOWN_FL_MAX_MM,
            ));
            let generations = settings_generations
                .unwrap_or(defaults::UNKNOWN_DE_GENERATIONS);

            mm_info_log!(
                logger,
                "Solver: unknown mode (DE LargeRefinement, {:.1}-{:.1} mm)",
                min_fl,
                max_fl
            );
            Some(GlobalAdjustmentConfig::DifferentialEvolution {
                mode: mmsfm::sfm_camera::GlobalAdjustmentMode::LargeRefinement,
                focal_length_bounds: (min_fl, max_fl),
                generations,
                seed: defaults::UNKNOWN_DE_SEED,
                enable_coarse_search,
            })
        }
    };

    let mut camera_poses = CameraPoses::new();
    let mut bundle_positions = BundlePositions::new();
    let mut quality_metrics = SolveQualityMetrics::default();

    mm_info_log!(logger, "Running camera solve...");

    // Create intermediate result writer if enabled.
    let intermediate_writer: Option<Arc<dyn IntermediateResultWriter>> = if args
        .intermediate_output
    {
        let (focal_length_mm_init, _, _) =
            camera_intrinsics.to_physical_parameters();

        // Create output directory early so intermediate writes
        // don't fail.
        std::fs::create_dir_all(&args.output_dir).with_context(|| {
            format!("Failed to create output directory: {}", args.output_dir)
        })?;

        Some(Arc::new(FileIntermediateResultWriter {
            output_dir: args.output_dir.clone(),
            prefix: args.prefix.clone(),
            focal_length_mm: focal_length_mm_init.value(),
            markers: Arc::new(markers.clone()),
            film_back,
            frame_range,
            counter: AtomicUsize::new(0),
            nuke_lens: nuke_lens_data.clone(),
        }))
    } else {
        None
    };

    let solve_start = Instant::now();
    camera_solve(
        logger,
        frame_range,
        &markers,
        &camera_intrinsics,
        &film_back,
        &image_size,
        &config,
        global_adjustment_config.as_ref(),
        intermediate_writer,
        &mut camera_poses,
        &mut bundle_positions,
        &mut quality_metrics,
    )?;
    let solve_duration = solve_start.elapsed();

    // Use the solved focal length for all downstream output.
    #[cfg_attr(not(feature = "visualization"), allow(unused_variables))]
    let camera_intrinsics = match quality_metrics.optimized_focal_length_mm {
        Some(solved_fl) => {
            mm_info_log!(
                logger,
                "  Solved focal length: {:.4} mm (input: {} mm)",
                solved_fl,
                args.focal_length_mm
            );
            CameraIntrinsics::from_physical_parameters(
                MillimeterUnit::new(solved_fl),
                MillimeterUnit::new(args.lens_center_x_mm),
                MillimeterUnit::new(args.lens_center_y_mm),
                film_back,
            )
        }
        None => camera_intrinsics,
    };

    mm_info_log!(
        logger,
        "Solve completed in {:.2}s: {} cameras, {} bundles, mean_err={:.4}px",
        solve_duration.as_secs_f64(),
        camera_poses.len(),
        bundle_positions.len(),
        quality_metrics.mean_reprojection_error,
    );

    mm_info_log!(logger, "Solve completed!");
    mm_info_log!(logger, "  Cameras solved: {}", camera_poses.len());
    mm_info_log!(logger, "  Bundles triangulated: {}", bundle_positions.len());
    mm_info_log!(
        logger,
        "  Mean reprojection error: {:.4} pixels",
        quality_metrics.mean_reprojection_error
    );
    mm_info_log!(
        logger,
        "  Median reprojection error: {:.4} pixels",
        quality_metrics.median_reprojection_error
    );

    #[cfg(feature = "visualization")]
    let viz_duration = {
        let viz_start = Instant::now();
        generate_visualizations(
            logger,
            &args.output_dir,
            args.prefix.clone(),
            &markers,
            &camera_poses,
            &bundle_positions,
            &camera_intrinsics,
            &image_size,
        )?;
        viz_start.elapsed()
    };
    #[cfg(not(feature = "visualization"))]
    let viz_duration = std::time::Duration::ZERO;

    let io_start = Instant::now();
    let kuper_filename = match &args.prefix {
        Some(prefix) => format!("{}_camera.kuper", prefix),
        None => "camera.kuper".to_string(),
    };
    let kuper_path = format!("{}/{}", args.output_dir, kuper_filename);

    mm_progress_log!(logger, "Writing Kuper file to: {}", kuper_path);

    std::fs::create_dir_all(&args.output_dir).with_context(|| {
        format!("Failed to create output directory: {}", args.output_dir)
    })?;

    let (focal_length_mm_val, _, _) =
        camera_intrinsics.to_physical_parameters();
    write_kuper_output(
        &kuper_path,
        &camera_poses,
        focal_length_mm_val.value(),
    )?;

    mm_info_log!(logger, "  Wrote {} frames", camera_poses.len());

    let bundle_filename = match &args.prefix {
        Some(prefix) => format!("{}_bundles.mmbundles", prefix),
        None => "bundles.mmbundles".to_string(),
    };
    let bundle_path = format!("{}/{}", args.output_dir, bundle_filename);

    mm_progress_log!(logger, "Writing bundle file to: {}", bundle_path);

    write_bundle_output(&bundle_path, &markers, &bundle_positions)?;

    mm_info_log!(logger, "  Wrote {} bundles", bundle_positions.len());

    let mmcamera_filename = match &args.prefix {
        Some(prefix) => format!("{}_camera.mmcamera", prefix),
        None => "camera.mmcamera".to_string(),
    };
    let mmcamera_path = format!("{}/{}", args.output_dir, mmcamera_filename);

    mm_progress_log!(logger, "Writing mmcamera file to: {}", mmcamera_path);

    write_mmcamera_output(
        &mmcamera_path,
        &args,
        &camera_poses,
        &camera_intrinsics,
        &film_back,
        &frame_range,
    )?;

    mm_info_log!(logger, "  Wrote {} frames (mmcamera)", camera_poses.len());

    let residuals_filename = match &args.prefix {
        Some(prefix) => format!("{}_residuals.mmresiduals", prefix),
        None => "residuals.mmresiduals".to_string(),
    };
    let residuals_path = format!("{}/{}", args.output_dir, residuals_filename);

    let (per_frame_residuals, residual_stats) =
        compute_per_frame_per_marker_residuals(
            &markers,
            &camera_poses,
            &bundle_positions,
            &camera_intrinsics,
            &image_size,
        )?;

    let mut sorted_frames: Vec<u32> =
        per_frame_residuals.keys().copied().collect();
    sorted_frames.sort();

    let per_frame_per_marker: Vec<MmResidualsFrameData> = sorted_frames
        .iter()
        .map(|&frame| MmResidualsFrameData {
            frame: frame as i64,
            errors: per_frame_residuals[&frame].clone(),
        })
        .collect();

    let residuals_data = MmResidualsData {
        marker_names: markers.names.clone(),
        frame_numbers: sorted_frames.iter().map(|&f| f as i64).collect(),
        image_width: Some(args.image_width as i64),
        image_height: Some(args.image_height as i64),
        statistics: MmResidualsStatistics {
            mean: residual_stats.mean,
            median: residual_stats.median,
            std_dev: residual_stats.std_dev,
            min: residual_stats.min,
            max: residual_stats.max,
            count: residual_stats.count,
        },
        per_frame_per_marker,
    };

    write_mmresiduals_file(
        std::path::Path::new(&residuals_path),
        &residuals_data,
    )
    .with_context(|| {
        format!("Failed to write mmresiduals file: {}", residuals_path)
    })?;

    mm_progress_log!(logger, "Writing residuals file to: {}", residuals_path);
    mm_info_log!(
        logger,
        "  Mean: {:.4} px, Median: {:.4} px, Count: {}",
        residual_stats.mean,
        residual_stats.median,
        residual_stats.count
    );

    if let Some(ref lens_data) = nuke_lens_data {
        let lens_filename = match &args.prefix {
            Some(prefix) => format!("{}_lens.nk", prefix),
            None => "lens.nk".to_string(),
        };
        let lens_path = format!("{}/{}", args.output_dir, lens_filename);

        mm_progress_log!(logger, "Writing Nuke lens file to: {}", lens_path);

        write_nuke_lens_file(&lens_path, lens_data).with_context(|| {
            format!("Failed to write Nuke lens file: {}", lens_path)
        })?;

        mm_info_log!(logger, "  Wrote {} lens layer(s)", lens_data.layer_count);
    }

    let io_duration = io_start.elapsed();

    let total_duration = total_start.elapsed();
    let total_time_secs = total_duration.as_secs_f64();
    let total_time_mins = total_time_secs / 60.0;

    mm_info_log!(logger, "=== Timing Summary ===");
    if quality_metrics.global_optimization_time_secs.is_some() {
        mm_info_log!(logger, "Solver stages:");
        if let Some(coarse_time) = quality_metrics.coarse_search_time_secs {
            let percentage = (coarse_time / total_time_secs) * 100.0;
            mm_info_log!(
                logger,
                "  Coarse search:        {:>6.2}s  {:>5.1}%",
                coarse_time,
                percentage
            );
        }
        if let Some(refined_time) = quality_metrics.refined_search_time_secs {
            let percentage = (refined_time / total_time_secs) * 100.0;
            mm_info_log!(
                logger,
                "  Refined search:       {:>6.2}s  {:>5.1}%",
                refined_time,
                percentage
            );
        }
        if let Some(global_time) = quality_metrics.global_optimization_time_secs
        {
            let percentage = (global_time / total_time_secs) * 100.0;
            mm_info_log!(
                logger,
                "  Global optimization:  {:>6.2}s  {:>5.1}%",
                global_time,
                percentage
            );
        }
        if let Some(final_time) = quality_metrics.final_solve_time_secs {
            let percentage = (final_time / total_time_secs) * 100.0;
            mm_info_log!(
                logger,
                "  Final solve:          {:>6.2}s  {:>5.1}%",
                final_time,
                percentage
            );
        }
        let total_solve_time =
            quality_metrics.global_optimization_time_secs.unwrap_or(0.0)
                + quality_metrics.final_solve_time_secs.unwrap_or(0.0);
        let percentage = (total_solve_time / total_time_secs) * 100.0;
        mm_info_log!(
            logger,
            "  Total solver time:    {:>6.2}s  {:>5.1}%",
            total_solve_time,
            percentage
        );
    } else {
        let solve_time = solve_duration.as_secs_f64();
        let percentage = (solve_time / total_time_secs) * 100.0;
        mm_info_log!(
            logger,
            "  Camera solve:         {:>6.2}s  {:>5.1}%",
            solve_time,
            percentage
        );
    }
    if ENABLE_VISUALIZATIONS && viz_duration > std::time::Duration::ZERO {
        let viz_time = viz_duration.as_secs_f64();
        let percentage = (viz_time / total_time_secs) * 100.0;
        mm_info_log!(
            logger,
            "  Visualizations:       {:>6.2}s  {:>5.1}%",
            viz_time,
            percentage
        );
    }
    let io_time = io_duration.as_secs_f64();
    let percentage = (io_time / total_time_secs) * 100.0;
    mm_info_log!(
        logger,
        "  File I/O:             {:>6.2}s  {:>5.1}%",
        io_time,
        percentage
    );
    mm_info_log!(
        logger,
        "  Total time:            {:.2}s ({:.2} minutes)",
        total_time_secs,
        total_time_mins
    );

    mm_info_log!(logger, "Total time: {:.2}s", total_time_secs);

    mm_progress_log!(logger, "Done!");

    Ok(())
}

#[cfg(feature = "visualization")]
fn generate_visualizations<L: Logger + Sync>(
    logger: &L,
    output_dir: &str,
    prefix: Option<String>,
    markers: &MarkersData,
    camera_poses: &CameraPoses,
    bundle_positions: &BundlePositions,
    camera_intrinsics: &CameraIntrinsics,
    image_size: &ImageSize<f64>,
) -> Result<()> {
    // Create output directory if it doesn't exist.
    std::fs::create_dir_all(output_dir).with_context(|| {
        format!("Failed to create output directory: {}", output_dir)
    })?;

    let camera_poses_with_frames: Vec<CameraPoseWithFrame> = camera_poses
        .iter()
        .map(|(&frame, pose)| CameraPoseWithFrame {
            frame,
            pose: pose.clone(),
            is_initial: false,
        })
        .collect();

    let prefix_str = prefix.as_deref().unwrap_or("");

    let bundles: Vec<Point3<f64>> =
        bundle_positions.values().cloned().collect();

    let title = if prefix_str.is_empty() {
        "Camera Solve Result".to_string()
    } else {
        format!("{} - Camera Solve Result", prefix_str)
    };

    // Maps frame number to list of (marker_index, observed_uv).
    let frame_marker_data = build_frame_marker_data(markers);

    let dataset_name = prefix.as_deref().unwrap_or("solve");

    let viz_dir = match prefix_str {
        "" => format!("{}/visualizations", output_dir),
        p => format!("{}/{}_visualizations", output_dir, p),
    };

    let scene_frame_naming = OutputFileNaming::new(
        &viz_dir,
        TestType::CameraSolve,
        dataset_name,
        VisualizationType::Scene3d,
    )
    .with_flat_directory();

    let views = vec![ViewConfigurationBuilder::new()
        .view_name("top")
        .rotation_ortho_top()
        .resolution_hd()
        .build()];

    visualize_sfm_trajectory_views(
        logger,
        &camera_poses_with_frames,
        &bundles,
        &title,
        &scene_frame_naming,
        views,
        camera_intrinsics,
        1, // step_by
        None,
    )?;

    let reproj_naming = OutputFileNaming::new(
        &viz_dir,
        TestType::CameraSolve,
        dataset_name,
        VisualizationType::MarkerReprojection2d,
    )
    .with_flat_directory();

    let reproj_title = if prefix_str.is_empty() {
        "Marker Reprojections".to_string()
    } else {
        format!("{} - Marker Reprojections", prefix_str)
    };

    let output_image_size = ImageSize::from_pixels(1920.0, 1080.0);

    let sorted_frames: Vec<u32> = {
        let mut frames: Vec<u32> = camera_poses.keys().copied().collect();
        frames.sort();
        frames
    };
    let camera_pose_vec: Vec<_> = sorted_frames
        .iter()
        .map(|f| camera_poses[f].clone())
        .collect();
    let intrinsics_vec: Vec<_> = sorted_frames
        .iter()
        .map(|_| camera_intrinsics.clone())
        .collect();
    let image_sizes_vec: Vec<_> =
        sorted_frames.iter().map(|_| image_size.clone()).collect();
    let observations_per_camera: Vec<Vec<(usize, UvPoint2<f64>)>> =
        sorted_frames
            .iter()
            .map(|frame| {
                frame_marker_data.get(frame).cloned().unwrap_or_default()
            })
            .collect();

    visualize_marker_reprojections_sequential(
        logger,
        &camera_pose_vec,
        &bundles,
        &observations_per_camera,
        &intrinsics_vec,
        &image_sizes_vec,
        &reproj_title,
        &output_image_size,
        &reproj_naming,
    )?;

    let (per_frame_residuals, residual_stats) =
        compute_per_frame_per_marker_residuals(
            markers,
            camera_poses,
            bundle_positions,
            camera_intrinsics,
            image_size,
        )?;

    let residual_naming = OutputFileNaming::new(
        &viz_dir,
        TestType::CameraSolve,
        dataset_name,
        VisualizationType::ResidualsLinePlot,
    )
    .with_flat_directory();

    let residual_title = if prefix_str.is_empty() {
        "Per-Frame Reprojection Errors".to_string()
    } else {
        format!("{} - Per-Frame Reprojection Errors", prefix_str)
    };

    visualize_multi_frame_residuals_per_marker(
        logger,
        &per_frame_residuals,
        Some(&markers.names),
        &residual_stats,
        &residual_title,
        &residual_naming,
    )?;

    Ok(())
}

#[cfg(feature = "visualization")]
/// Build a map from frame number to list of (marker_index, uv_position).
fn build_frame_marker_data(
    markers: &MarkersData,
) -> std::collections::HashMap<u32, Vec<(MarkerIndex, UvPoint2<f64>)>> {
    let mut frame_marker_data: std::collections::HashMap<
        u32,
        Vec<(MarkerIndex, UvPoint2<f64>)>,
    > = std::collections::HashMap::new();

    for (marker_index, frame_data) in markers.frame_data.iter().enumerate() {
        for i in 0..frame_data.frames.len() {
            let frame = frame_data.frames[i];
            let uv_point = UvPoint2::new(
                UvValue::new(frame_data.u_coords[i]),
                UvValue::new(frame_data.v_coords[i]),
            );
            frame_marker_data
                .entry(frame)
                .or_insert_with(Vec::new)
                .push((marker_index, uv_point));
        }
    }

    frame_marker_data
}

fn write_kuper_output(
    kuper_path: &str,
    camera_poses: &CameraPoses,
    focal_length_mm: f64,
) -> Result<()> {
    let frame_list = camera_poses.generate_sorted_frame_list();

    let kuper_frames: Vec<KuperFrameData> = frame_list
        .iter()
        .map(|&frame| {
            let pose = &camera_poses[&frame];
            maya_pose_to_kuper(
                frame,
                pose.center(),
                pose.rotation(),
                focal_length_mm,
            )
        })
        .collect();

    write_kuper_file(kuper_path, &kuper_frames)
        .with_context(|| format!("Failed to write Kuper file: {}", kuper_path))
}

/// Write bundle positions to a file, named by marker index.
fn write_bundle_output(
    bundle_path: &str,
    markers: &MarkersData,
    bundle_positions: &BundlePositions,
) -> Result<()> {
    let bundles: Vec<BundlePoint> = bundle_positions
        .iter()
        .map(|(&marker_index, &position)| {
            let name = markers
                .names
                .get(marker_index)
                .cloned()
                .unwrap_or_else(|| marker_index.to_string());
            BundlePoint { name, position }
        })
        .collect();

    write_bundle_file(bundle_path, &bundles).with_context(|| {
        format!("Failed to write bundle file: {}", bundle_path)
    })
}

fn write_mmcamera_output(
    mmcamera_path: &str,
    args: &CliArgs,
    camera_poses: &CameraPoses,
    camera_intrinsics: &CameraIntrinsics,
    film_back: &CameraFilmBack<f64>,
    frame_range: &FrameRange,
) -> Result<()> {
    write_mmcamera_output_inner(
        mmcamera_path,
        args.prefix.as_deref().unwrap_or("camera"),
        Some(args.image_width as i64),
        Some(args.image_height as i64),
        camera_poses,
        camera_intrinsics,
        film_back,
        frame_range,
    )
}

/// Write camera poses to an .mmcamera file without needing full CLI args.
fn write_mmcamera_output_raw(
    mmcamera_path: &str,
    camera_poses: &CameraPoses,
    camera_intrinsics: &CameraIntrinsics,
    film_back: &CameraFilmBack<f64>,
    frame_range: &FrameRange,
) -> Result<()> {
    write_mmcamera_output_inner(
        mmcamera_path,
        "camera",
        None,
        None,
        camera_poses,
        camera_intrinsics,
        film_back,
        frame_range,
    )
}

fn write_mmcamera_output_inner(
    mmcamera_path: &str,
    camera_name: &str,
    image_width: Option<i64>,
    image_height: Option<i64>,
    camera_poses: &CameraPoses,
    camera_intrinsics: &CameraIntrinsics,
    film_back: &CameraFilmBack<f64>,
    frame_range: &FrameRange,
) -> Result<()> {
    let frame_list = camera_poses.generate_sorted_frame_list();

    let (focal_length_mm, _lens_cx, _lens_cy) =
        camera_intrinsics.to_physical_parameters();
    let focal_length_val = focal_length_mm.value();
    let film_back_width_val = film_back.width.value();
    let film_back_height_val = film_back.height.value();

    let mut translate_x = Vec::with_capacity(frame_list.len());
    let mut translate_y = Vec::with_capacity(frame_list.len());
    let mut translate_z = Vec::with_capacity(frame_list.len());
    let mut rotate_x = Vec::with_capacity(frame_list.len());
    let mut rotate_y = Vec::with_capacity(frame_list.len());
    let mut rotate_z = Vec::with_capacity(frame_list.len());
    let mut focal_length = Vec::with_capacity(frame_list.len());
    let mut fb_width = Vec::with_capacity(frame_list.len());
    let mut fb_height = Vec::with_capacity(frame_list.len());
    let mut fb_offset_x = Vec::with_capacity(frame_list.len());
    let mut fb_offset_y = Vec::with_capacity(frame_list.len());

    for &frame in &frame_list {
        let pose = &camera_poses[&frame];
        let center = pose.center();
        let (rx, ry, rz) = extract_zxy_euler_angles(pose.rotation());
        let f = frame as i64;

        translate_x.push((f, center.x));
        translate_y.push((f, center.y));
        translate_z.push((f, center.z));
        rotate_x.push((f, rx));
        rotate_y.push((f, ry));
        rotate_z.push((f, rz));
        focal_length.push((f, focal_length_val));
        fb_width.push((f, film_back_width_val));
        fb_height.push((f, film_back_height_val));
        fb_offset_x.push((f, 0.0));
        fb_offset_y.push((f, 0.0));
    }

    let data = MmCameraData {
        name: camera_name.to_string(),
        start_frame: frame_range.start_frame as i64,
        end_frame: frame_range.end_frame as i64,
        image: MmCameraImageData {
            file_path: None,
            width: image_width,
            height: image_height,
            pixel_aspect_ratio: Some(1.0),
        },
        attr: MmCameraAttrData {
            translate_x,
            translate_y,
            translate_z,
            rotate_x,
            rotate_y,
            rotate_z,
            focal_length,
            film_back_width: fb_width,
            film_back_height: fb_height,
            film_back_offset_x: fb_offset_x,
            film_back_offset_y: fb_offset_y,
        },
    };

    write_mmcamera_file(std::path::Path::new(mmcamera_path), &data)
        .with_context(|| {
            format!("Failed to write mmcamera file: {}", mmcamera_path)
        })
}
