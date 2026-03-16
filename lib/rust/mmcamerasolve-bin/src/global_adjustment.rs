//
// Copyright (C) 2026 David Cattermole.
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

//! Global adjustment orchestration for lens parameter optimization.
//!
//! This module handles the case where lens distortion parameters are
//! jointly optimized alongside (or instead of) focal length. Unlike
//! the focal-length-only path in `mmsfm`, this path defers
//! undistortion into the evaluator loop so it can be re-applied with
//! different lens parameter values on each iteration.

use anyhow::{bail, Result};
use mmlogger::{mm_log_info, mm_log_progress, mm_log_warn, Logger};
use std::sync::atomic::AtomicUsize;
use std::sync::{Arc, Mutex};

use mmio::nuke_lens_common::NukeLensData;
use mmio::uvtrack_reader::{FrameRange, MarkersData};
use mmoptimise::global::{
    CachingEvaluator, DifferentialEvolution, DifferentialEvolutionConfig,
    DifferentialEvolutionStrategy, Evaluator, UniformGridSearch,
    UniformGridSearchConfig,
};
use mmsfm::datatype::common::UnitValue;
use mmsfm::datatype::{
    BundlePositions, CameraFilmBack, CameraIntrinsics, CameraPoses, ImageSize,
    MillimeterUnit,
};
use mmsfm::sfm_camera::IntermediateResultWriter;
use mmsfm::sfm_camera::{
    camera_solve_inner, AdjustmentParameterKind, AdjustmentParameterLayout,
    CameraSolveConfig, GlobalAdjustmentConfig, GlobalAdjustmentMode,
    SolveQuality, SolveQualityMetrics,
};

use crate::lens_evaluator::LensAwareEvaluator;
use crate::undistort::{apply_lens_overrides, undistort_markers_with_lens};

/// Print global solver details.
const PRINT_SOLVER_DETAILS: bool = true;

/// Log parameter bounds for each dimension in the layout.
fn log_parameter_bounds<L: Logger>(
    logger: &L,
    layout: &AdjustmentParameterLayout,
    indent: &str,
) {
    for (i, param) in layout.parameters.iter().enumerate() {
        match &param.kind {
            AdjustmentParameterKind::FocalLength => {
                mm_log_progress!(
                    logger,
                    "{}[{}] focal_length: [{:.2}, {:.2}] mm",
                    indent,
                    i,
                    param.bounds.0,
                    param.bounds.1
                );
            }
            AdjustmentParameterKind::LensParameter {
                layer_index,
                knob_name,
                ..
            } => {
                mm_log_progress!(
                    logger,
                    "{}[{}] layer {} {}: [{:.4}, {:.4}]",
                    indent,
                    i,
                    layer_index,
                    knob_name,
                    param.bounds.0,
                    param.bounds.1
                );
            }
        }
    }
}

/// Log parameter values alongside their initial values.
fn log_parameter_values<L: Logger>(
    logger: &L,
    layout: &AdjustmentParameterLayout,
    values: &[f64],
    indent: &str,
) {
    for (i, param) in layout.parameters.iter().enumerate() {
        match &param.kind {
            AdjustmentParameterKind::FocalLength => {
                mm_log_progress!(
                    logger,
                    "{}[{}] focal_length: {:.4} -> {:.4} mm",
                    indent,
                    i,
                    param.initial_value,
                    values[i]
                );
            }
            AdjustmentParameterKind::LensParameter {
                layer_index,
                knob_name,
                ..
            } => {
                mm_log_progress!(
                    logger,
                    "{}[{}] layer {} {}: {:.6} -> {:.6}",
                    indent,
                    i,
                    layer_index,
                    knob_name,
                    param.initial_value,
                    values[i]
                );
            }
        }
    }
}

/// Minimum valid focal length in millimeters.
const MIN_VALID_FOCAL_LENGTH: f64 = 0.1;

/// Number of standard deviations for refined bounds calculation.
const REFINED_BOUNDS_STD_DEV_MULTIPLIER: f64 = 2.0;

/// Wraps an evaluator and records all evaluations where cost != MAX.
struct TrackingEvaluator<E: Evaluator + Sync> {
    inner: E,
    valid_evaluations: Arc<Mutex<Vec<(Vec<f64>, f64)>>>,
}

impl<E: Evaluator + Sync> TrackingEvaluator<E> {
    fn new(inner: E) -> Self {
        Self {
            inner,
            valid_evaluations: Arc::new(Mutex::new(Vec::new())),
        }
    }

    fn get_valid_evaluations(&self) -> Vec<(Vec<f64>, f64)> {
        self.valid_evaluations.lock().unwrap().clone()
    }
}

impl<E: Evaluator + Sync> TrackingEvaluator<CachingEvaluator<E>> {
    fn cache_stats(&self) -> (usize, usize) {
        self.inner.cache_stats()
    }
}

impl<E: Evaluator + Sync> Evaluator for TrackingEvaluator<E> {
    fn evaluate(&self, x: &[f64]) -> f64 {
        let cost = self.inner.evaluate(x);
        if cost < f64::MAX && !x.is_empty() {
            self.valid_evaluations
                .lock()
                .unwrap()
                .push((x.to_vec(), cost));
        }
        cost
    }
}

/// Calculate narrowed search range from prior valid evaluations.
///
/// Weights each result by inverse cost. Returns per-dimension
/// `(weighted_mean, weighted_std_dev, refined_min, refined_max)` or
/// `None` if there are no usable results.
///
/// For focal length dimensions, values below `MIN_VALID_FOCAL_LENGTH`
/// are treated as physically invalid and excluded. Lens distortion
/// parameters have no such constraint and all values are kept.
fn calculate_refined_bounds_nd(
    valid_evaluations: &[(Vec<f64>, f64)],
    parameter_layout: &AdjustmentParameterLayout,
) -> Option<Vec<(f64, f64, f64, f64)>> {
    let num_dimensions = parameter_layout.num_dimensions();
    if valid_evaluations.is_empty() {
        return None;
    }

    let epsilon = 1e-10;
    let weights: Vec<f64> = valid_evaluations
        .iter()
        .map(|(_, cost)| 1.0 / (cost + epsilon))
        .collect();
    let total_weight: f64 = weights.iter().sum();
    if total_weight <= 0.0 {
        return None;
    }

    let mut results = Vec::with_capacity(num_dimensions);
    for dim in 0..num_dimensions {
        let values: Vec<f64> = valid_evaluations
            .iter()
            .filter_map(|(params, _)| params.get(dim).copied())
            .collect();
        if values.len() != valid_evaluations.len() {
            return None;
        }

        // For focal length only: filter out physically invalid values
        // (focal length must be positive). Lens distortion parameters
        // can be zero or negative, so no minimum-value filter applies.
        let is_focal_length = matches!(
            parameter_layout.parameters.get(dim).map(|p| &p.kind),
            Some(AdjustmentParameterKind::FocalLength)
        );
        let filtered: Vec<_> = values
            .iter()
            .zip(weights.iter())
            .filter(|(&v, _)| !is_focal_length || v >= MIN_VALID_FOCAL_LENGTH)
            .map(|(&v, &w)| (v, w))
            .collect();

        if filtered.is_empty() {
            return None;
        }

        let filtered_total_weight: f64 = filtered.iter().map(|(_, w)| w).sum();
        if filtered_total_weight <= 0.0 {
            return None;
        }

        let weighted_mean: f64 =
            filtered.iter().map(|(v, w)| v * w).sum::<f64>()
                / filtered_total_weight;

        let weighted_variance: f64 = filtered
            .iter()
            .map(|(v, w)| {
                let diff = v - weighted_mean;
                w * diff * diff
            })
            .sum::<f64>()
            / filtered_total_weight;

        let weighted_std_dev = weighted_variance.sqrt();

        // Clamp focal length refined min to a physically valid value.
        let refined_min = if is_focal_length {
            (weighted_mean
                - REFINED_BOUNDS_STD_DEV_MULTIPLIER * weighted_std_dev)
                .max(MIN_VALID_FOCAL_LENGTH)
        } else {
            weighted_mean - REFINED_BOUNDS_STD_DEV_MULTIPLIER * weighted_std_dev
        };
        let refined_max = weighted_mean
            + REFINED_BOUNDS_STD_DEV_MULTIPLIER * weighted_std_dev;

        if refined_min >= refined_max {
            return None;
        }

        results.push((
            weighted_mean,
            weighted_std_dev,
            refined_min,
            refined_max,
        ));
    }

    Some(results)
}

/// Run global adjustment with lens parameter optimization.
///
/// This function handles the case where `parameter_layout` includes
/// lens distortion parameters. Unlike the mmsfm focal-length-only
/// path, undistortion is deferred into the evaluator loop so lens
/// parameters can be varied on each iteration.
///
/// After optimization, the optimized lens parameters are applied to
/// `nuke_lens_data` and stored in `quality_metrics`.
pub fn run_global_adjustment<L: Logger + Clone + Send + Sync>(
    logger: &L,
    scene_frame_range: FrameRange,
    // Distorted markers (NOT pre-undistorted).
    distorted_markers: &MarkersData,
    camera_intrinsics: &CameraIntrinsics,
    film_back: &CameraFilmBack<f64>,
    image_size: &ImageSize<f64>,
    config: &CameraSolveConfig,
    global_config: &GlobalAdjustmentConfig,
    nuke_lens: &Arc<NukeLensData>,
    has_explicit_distorted: bool,
    intermediate_writer: Option<Arc<dyn IntermediateResultWriter>>,
    camera_poses: &mut CameraPoses,
    bundle_positions: &mut BundlePositions,
    quality_metrics: &mut SolveQualityMetrics,
) -> Result<()> {
    let parameter_layout = global_config.parameter_layout();
    let num_dimensions = parameter_layout.num_dimensions();
    let bounds = parameter_layout.bounds();

    let initial_focal_length_mm =
        camera_intrinsics.to_physical_parameters().0.value();

    match global_config {
        GlobalAdjustmentConfig::DifferentialEvolution {
            mode,
            generations,
            seed,
            enable_coarse_search,
            ..
        } => {
            if PRINT_SOLVER_DETAILS {
                mm_log_progress!(
                    logger,
                    "[DE] Global adjustment (lens): Differential Evolution"
                );
                mm_log_info!(
                    logger,
                    "[DE]   Initial focal length: {:.2} mm",
                    initial_focal_length_mm
                );
                mm_log_info!(logger, "[DE]   Mode: {:?}", mode);
                mm_log_info!(logger, "[DE]   Generations: {}", generations);
            }

            let de_config = match mode {
                GlobalAdjustmentMode::SmallRefinement => {
                    DifferentialEvolutionConfig::small_refinement(
                        num_dimensions,
                        bounds.clone(),
                        *generations,
                        *seed,
                    )
                }
                GlobalAdjustmentMode::LargeRefinement => {
                    DifferentialEvolutionConfig::large_refinement(
                        num_dimensions,
                        bounds.clone(),
                        *generations,
                        *seed,
                    )
                }
            };

            let mut best_params = parameter_layout.initial_values();
            let mut best_cost;

            let mut coarse_search_time_secs: Option<f64> = None;
            let mut refined_search_time_secs: Option<f64> = None;

            if *enable_coarse_search {
                let mut coarse_de_config = de_config.clone();
                coarse_de_config.diversity_tolerance = Some(1e-2);
                coarse_de_config.strategy =
                    DifferentialEvolutionStrategy::Rand1Bin;

                if PRINT_SOLVER_DETAILS {
                    mm_log_progress!(logger, "[DE] Stage 1: Coarse Search...");
                    log_parameter_bounds(logger, parameter_layout, "[DE]   ");
                }

                let de_start_time = std::time::Instant::now();
                let mut de_solver =
                    DifferentialEvolution::new(coarse_de_config)?;

                let evaluator = LensAwareEvaluator::new(
                    scene_frame_range,
                    Arc::new(distorted_markers.clone()),
                    has_explicit_distorted,
                    Arc::clone(nuke_lens),
                    *film_back,
                    image_size.clone(),
                    Arc::new(config.clone()),
                    SolveQuality::Draft,
                    parameter_layout.clone(),
                    de_solver.current_generation.clone(),
                    logger.clone(),
                );

                let cached_evaluator = CachingEvaluator::new(evaluator);
                let tracking_evaluator =
                    TrackingEvaluator::new(cached_evaluator);

                best_cost = de_solver.run(
                    &tracking_evaluator,
                    &mut best_params,
                    logger,
                )?;

                if PRINT_SOLVER_DETAILS {
                    let (cache_hits, cache_misses) =
                        tracking_evaluator.cache_stats();
                    mm_log_info!(
                        logger,
                        "[DE]   Coarse cache: {} hits, {} misses",
                        cache_hits,
                        cache_misses
                    );
                }

                let valid_evals = tracking_evaluator.get_valid_evaluations();

                let de_elapsed = de_start_time.elapsed();
                coarse_search_time_secs = Some(de_elapsed.as_secs_f64());

                if PRINT_SOLVER_DETAILS {
                    mm_log_info!(
                        logger,
                        "[DE]   Coarse completed in {:.2}s ({} valid evals)",
                        coarse_search_time_secs.unwrap(),
                        valid_evals.len()
                    );
                }

                // Stage 2: Refined search based on coarse results.
                if let Some(refined_bounds) =
                    calculate_refined_bounds_nd(&valid_evals, parameter_layout)
                {
                    let refined_bound_pairs: Vec<(f64, f64)> = refined_bounds
                        .iter()
                        .map(|(_, _, min, max)| (*min, *max))
                        .collect();

                    if PRINT_SOLVER_DETAILS {
                        mm_log_progress!(
                            logger,
                            "[DE] Stage 2: Refined Search..."
                        );
                        for (i, (_mean, _std_dev, rmin, rmax)) in
                            refined_bounds.iter().enumerate()
                        {
                            if let Some(param) =
                                parameter_layout.parameters.get(i)
                            {
                                match &param.kind {
                                    AdjustmentParameterKind::FocalLength => {
                                        mm_log_progress!(
                                            logger,
                                            "[DE]   [{}] focal_length: [{:.4}, {:.4}] mm",
                                            i, rmin, rmax
                                        );
                                    }
                                    AdjustmentParameterKind::LensParameter {
                                        layer_index,
                                        knob_name,
                                        ..
                                    } => {
                                        mm_log_progress!(
                                            logger,
                                            "[DE]   [{}] layer {} {}: [{:.4}, {:.4}]",
                                            i, layer_index, knob_name, rmin, rmax
                                        );
                                    }
                                }
                            }
                        }
                    }

                    let refined_de_config = match mode {
                        GlobalAdjustmentMode::SmallRefinement => {
                            DifferentialEvolutionConfig::small_refinement(
                                num_dimensions,
                                refined_bound_pairs,
                                *generations,
                                *seed + 1,
                            )
                        }
                        GlobalAdjustmentMode::LargeRefinement => {
                            DifferentialEvolutionConfig::large_refinement(
                                num_dimensions,
                                refined_bound_pairs,
                                *generations,
                                *seed + 1,
                            )
                        }
                    };

                    let refined_de_start = std::time::Instant::now();
                    let mut refined_de_solver =
                        DifferentialEvolution::new(refined_de_config)?;

                    let refined_evaluator = LensAwareEvaluator::new(
                        scene_frame_range,
                        Arc::new(distorted_markers.clone()),
                        has_explicit_distorted,
                        Arc::clone(nuke_lens),
                        *film_back,
                        image_size.clone(),
                        Arc::new(config.clone()),
                        SolveQuality::Final,
                        parameter_layout.clone(),
                        refined_de_solver.current_generation.clone(),
                        logger.clone(),
                    );

                    let refined_cached =
                        CachingEvaluator::new(refined_evaluator);

                    let mut refined_best = best_params.clone();
                    let refined_cost = refined_de_solver.run(
                        &refined_cached,
                        &mut refined_best,
                        logger,
                    )?;

                    best_params = refined_best;
                    best_cost = refined_cost;

                    let refined_elapsed = refined_de_start.elapsed();
                    refined_search_time_secs =
                        Some(refined_elapsed.as_secs_f64());

                    if PRINT_SOLVER_DETAILS {
                        mm_log_info!(
                            logger,
                            "[DE]   Refined completed in {:.2}s",
                            refined_search_time_secs.unwrap()
                        );
                    }
                } else if PRINT_SOLVER_DETAILS {
                    mm_log_warn!(
                        logger,
                        "[DE] Could not calculate refined bounds; using coarse result"
                    );
                }
            } else {
                // Single high-quality search.
                if PRINT_SOLVER_DETAILS {
                    mm_log_progress!(logger, "[DE] Stage 1: Refined Search...");
                    log_parameter_bounds(logger, parameter_layout, "[DE]   ");
                }

                let refined_de_start = std::time::Instant::now();
                let mut refined_de_solver =
                    DifferentialEvolution::new(de_config)?;

                let evaluator = LensAwareEvaluator::new(
                    scene_frame_range,
                    Arc::new(distorted_markers.clone()),
                    has_explicit_distorted,
                    Arc::clone(nuke_lens),
                    *film_back,
                    image_size.clone(),
                    Arc::new(config.clone()),
                    SolveQuality::Final,
                    parameter_layout.clone(),
                    refined_de_solver.current_generation.clone(),
                    logger.clone(),
                );

                let refined_cached = CachingEvaluator::new(evaluator);

                best_cost = refined_de_solver.run(
                    &refined_cached,
                    &mut best_params,
                    logger,
                )?;

                let refined_elapsed = refined_de_start.elapsed();
                refined_search_time_secs = Some(refined_elapsed.as_secs_f64());

                if PRINT_SOLVER_DETAILS {
                    mm_log_info!(
                        logger,
                        "[DE]   Completed in {:.2}s",
                        refined_search_time_secs.unwrap()
                    );
                }
            }

            if best_cost >= f64::MAX {
                bail!("Lens parameter optimization failed for all candidates");
            }

            // Log optimized parameters.
            if PRINT_SOLVER_DETAILS {
                mm_log_progress!(
                    logger,
                    "[DE] Optimization complete (cost={:.4} px):",
                    best_cost
                );
                log_parameter_values(
                    logger,
                    parameter_layout,
                    &best_params,
                    "[DE]   ",
                );
            }

            // Final solve with optimized parameters.
            run_final_solve(
                logger,
                scene_frame_range,
                distorted_markers,
                film_back,
                image_size,
                config,
                nuke_lens,
                has_explicit_distorted,
                parameter_layout,
                &best_params,
                intermediate_writer,
                camera_poses,
                bundle_positions,
                quality_metrics,
            )?;

            // Store timing metrics.
            quality_metrics.coarse_search_time_secs = coarse_search_time_secs;
            quality_metrics.refined_search_time_secs = refined_search_time_secs;
            quality_metrics.global_optimization_time_secs = Some(
                coarse_search_time_secs.unwrap_or(0.0)
                    + refined_search_time_secs.unwrap_or(0.0),
            );

            // Store optimized parameter values.
            store_optimized_params(
                parameter_layout,
                &best_params,
                quality_metrics,
            );

            Ok(())
        }
        GlobalAdjustmentConfig::UniformGridSearch {
            num_samples_per_param,
            ..
        } => {
            let num_samples_vec: Vec<usize> =
                if num_samples_per_param.len() == num_dimensions {
                    num_samples_per_param.clone()
                } else {
                    vec![
                        num_samples_per_param.first().copied().unwrap_or(11);
                        num_dimensions
                    ]
                };

            if PRINT_SOLVER_DETAILS {
                mm_log_progress!(
                    logger,
                    "[UGS] Global adjustment (lens): Uniform Grid Search"
                );
                for (i, param) in parameter_layout.parameters.iter().enumerate()
                {
                    let n = num_samples_vec.get(i).copied().unwrap_or(0);
                    match &param.kind {
                        AdjustmentParameterKind::FocalLength => {
                            mm_log_progress!(
                                logger,
                                "[UGS]   [{}] focal_length: [{:.2}, {:.2}] mm ({} samples)",
                                i,
                                param.bounds.0,
                                param.bounds.1,
                                n
                            );
                        }
                        AdjustmentParameterKind::LensParameter {
                            layer_index,
                            knob_name,
                            ..
                        } => {
                            mm_log_progress!(
                                logger,
                                "[UGS]   [{}] layer {} {}: [{:.4}, {:.4}] ({} samples)",
                                i,
                                layer_index,
                                knob_name,
                                param.bounds.0,
                                param.bounds.1,
                                n
                            );
                        }
                    }
                }
                mm_log_info!(
                    logger,
                    "[UGS]   Total grid points: {}",
                    num_samples_vec.iter().product::<usize>()
                );
            }

            let grid_config = UniformGridSearchConfig {
                num_dimensions,
                num_samples_per_dimension: num_samples_vec,
                bounds,
            };
            let grid_solver = UniformGridSearch::new(grid_config)?;

            let evaluator = LensAwareEvaluator::new(
                scene_frame_range,
                Arc::new(distorted_markers.clone()),
                has_explicit_distorted,
                Arc::clone(nuke_lens),
                *film_back,
                image_size.clone(),
                Arc::new(config.clone()),
                SolveQuality::Final,
                parameter_layout.clone(),
                Arc::new(AtomicUsize::new(0)),
                logger.clone(),
            );

            let cached_evaluator = CachingEvaluator::new(evaluator);

            let grid_start_time = std::time::Instant::now();
            let mut best_params = parameter_layout.initial_values();
            let best_cost =
                grid_solver.run(&cached_evaluator, &mut best_params, logger)?;
            let grid_elapsed = grid_start_time.elapsed();

            if best_cost >= f64::MAX {
                bail!("Lens parameter optimization failed for all grid candidates");
            }

            if PRINT_SOLVER_DETAILS {
                mm_log_progress!(
                    logger,
                    "[UGS] Grid search complete in {:.2}s (cost={:.4} px):",
                    grid_elapsed.as_secs_f64(),
                    best_cost
                );
                log_parameter_values(
                    logger,
                    parameter_layout,
                    &best_params,
                    "[UGS]   ",
                );
            }

            // Final solve with optimized parameters.
            run_final_solve(
                logger,
                scene_frame_range,
                distorted_markers,
                film_back,
                image_size,
                config,
                nuke_lens,
                has_explicit_distorted,
                parameter_layout,
                &best_params,
                intermediate_writer,
                camera_poses,
                bundle_positions,
                quality_metrics,
            )?;

            quality_metrics.global_optimization_time_secs =
                Some(grid_elapsed.as_secs_f64());

            // Store optimized parameter values.
            store_optimized_params(
                parameter_layout,
                &best_params,
                quality_metrics,
            );

            Ok(())
        }
    }
}

/// Store optimized parameter values into `quality_metrics`.
fn store_optimized_params(
    parameter_layout: &AdjustmentParameterLayout,
    best_params: &[f64],
    quality_metrics: &mut SolveQualityMetrics,
) {
    // Focal length.
    if let Some(fl_idx) = parameter_layout.focal_length_index() {
        quality_metrics.optimized_focal_length_mm = Some(best_params[fl_idx]);
    }

    // Lens parameters.
    let lens_params: Vec<(u8, usize, String, f64)> = parameter_layout
        .parameters
        .iter()
        .enumerate()
        .filter_map(|(i, param)| {
            if let AdjustmentParameterKind::LensParameter {
                layer_index,
                param_index,
                knob_name,
            } = &param.kind
            {
                Some((
                    *layer_index,
                    *param_index,
                    knob_name.clone(),
                    best_params[i],
                ))
            } else {
                None
            }
        })
        .collect();

    if !lens_params.is_empty() {
        quality_metrics.optimized_lens_parameters = Some(lens_params);
    }
}

/// Run the final camera solve with optimized parameters.
///
/// Applies the best lens parameters found during optimization,
/// undistorts markers with the optimized lens, then runs a full
/// final-quality solve.
fn run_final_solve<L: Logger + Clone + Send + Sync>(
    logger: &L,
    scene_frame_range: FrameRange,
    distorted_markers: &MarkersData,
    film_back: &CameraFilmBack<f64>,
    image_size: &ImageSize<f64>,
    config: &CameraSolveConfig,
    nuke_lens: &Arc<NukeLensData>,
    has_explicit_distorted: bool,
    parameter_layout: &AdjustmentParameterLayout,
    best_params: &[f64],
    intermediate_writer: Option<Arc<dyn IntermediateResultWriter>>,
    camera_poses: &mut CameraPoses,
    bundle_positions: &mut BundlePositions,
    quality_metrics: &mut SolveQualityMetrics,
) -> Result<()> {
    if PRINT_SOLVER_DETAILS {
        mm_log_progress!(logger, "[Solve] Final Solve...");
    }

    // Apply optimized lens overrides to a clone of NukeLensData.
    let overrides = parameter_layout.lens_overrides_from_params(best_params);
    let mut modified_lens = (**nuke_lens).clone();
    apply_lens_overrides(&mut modified_lens, &overrides);

    // Undistort a clone of markers with the optimized lens.
    let mut undistorted_markers = distorted_markers.clone();
    undistort_markers_with_lens(
        &mut undistorted_markers,
        &modified_lens,
        has_explicit_distorted,
    )?;

    // Determine focal length.
    let focal_length_mm = match parameter_layout.focal_length_index() {
        Some(idx) => best_params[idx],
        None => modified_lens.camera_parameters.focal_length_cm * 10.0,
    };

    let optimized_intrinsics = CameraIntrinsics::from_centered_lens(
        MillimeterUnit::new(focal_length_mm),
        *film_back,
    );

    if PRINT_SOLVER_DETAILS {
        mm_log_info!(
            logger,
            "[Solve]   focal_length={:.4} mm",
            focal_length_mm
        );
    }

    let final_solve_start = std::time::Instant::now();
    camera_solve_inner(
        logger,
        scene_frame_range,
        &undistorted_markers,
        &optimized_intrinsics,
        image_size,
        config,
        SolveQuality::Final,
        true,
        intermediate_writer,
        camera_poses,
        bundle_positions,
        quality_metrics,
    )?;
    quality_metrics.final_solve_time_secs =
        Some(final_solve_start.elapsed().as_secs_f64());

    Ok(())
}
