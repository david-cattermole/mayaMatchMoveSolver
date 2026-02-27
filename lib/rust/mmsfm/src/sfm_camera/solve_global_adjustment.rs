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

//! Global focal length optimization using Differential Evolution or Grid Search.

use anyhow::{bail, Result};
use mmlogger::Logger;
use mmlogger::{mm_log_info, mm_log_progress};
use std::sync::atomic::AtomicUsize;
use std::sync::{Arc, Mutex};

use mmio::uvtrack_reader::{FrameRange, MarkersData};
use mmoptimise::global::{
    CachingEvaluator, DifferentialEvolution, DifferentialEvolutionConfig,
    DifferentialEvolutionStrategy, Evaluator, UniformGridSearch,
    UniformGridSearchConfig,
};

use super::config::GlobalAdjustmentConfig;
use super::config::GlobalAdjustmentMode;
use super::config::{CameraSolveConfig, SolveQuality, SolveQualityMetrics};
use super::focal_length_evaluator::CameraSolveFocalLengthEvaluator;
use super::intermediate_writer::IntermediateResultWriter;
use super::solve_core::camera_solve_inner;
use crate::datatype::MillimeterUnit;
use crate::datatype::UnitValue;
use crate::datatype::{
    BundlePositions, CameraFilmBack, CameraIntrinsics, CameraPoses, ImageSize,
};

/// Compile-time flag to enable verbose debug output.
#[allow(dead_code)]
const DEBUG: bool = false;

/// Print global solver details.
const PRINT_SOLVER_DETAILS: bool = true;

/// Wraps another evaluator and records all evaluations where the cost
/// was not `f64::MAX`, for use in refining the search bounds.
struct TrackingEvaluator<E: Evaluator> {
    inner: E,
    valid_focal_lengths: Arc<Mutex<Vec<(f64, f64)>>>, // (focal_length, cost)
}

impl<E: Evaluator> TrackingEvaluator<E> {
    fn new(inner: E) -> Self {
        Self {
            inner,
            valid_focal_lengths: Arc::new(Mutex::new(Vec::new())),
        }
    }

    fn get_valid_focal_lengths(&self) -> Vec<(f64, f64)> {
        self.valid_focal_lengths.lock().unwrap().clone()
    }
}

// Specialized implementation for TrackingEvaluator wrapping CachingEvaluator
impl<L: Logger + Sync>
    TrackingEvaluator<CachingEvaluator<CameraSolveFocalLengthEvaluator<L>>>
{
    fn cache_stats(&self) -> (usize, usize) {
        self.inner.cache_stats()
    }
}

impl<E: Evaluator> Evaluator for TrackingEvaluator<E> {
    fn evaluate(&self, x: &[f64]) -> f64 {
        let cost = self.inner.evaluate(x);

        // Track valid focal lengths (those that didn't fail)
        if cost < f64::MAX && !x.is_empty() {
            let focal_length = x[0];
            self.valid_focal_lengths
                .lock()
                .unwrap()
                .push((focal_length, cost));
        }

        cost
    }
}

/// Minimum valid focal length in millimeters (prevents division by
/// zero and physically impossible values).
const MIN_VALID_FOCAL_LENGTH: f64 = 0.1;

/// Number of standard deviations for refined bounds calculation.
///
/// This multiplier is used to increase or decrease the range of
/// values that is estimated from the first quick initial solves.
const REFINED_BOUNDS_STD_DEV_MULTIPLIER: f64 = 2.0;

/// Calculate a narrowed focal length search range from prior results.
///
/// Weights each result by inverse cost so better solves have more
/// influence. Returns `(weighted_mean, weighted_std_dev, min, max,
/// count)`, or `None` if there are no usable results.
fn calculate_refined_bounds(
    valid_focal_lengths: &[(f64, f64)],
) -> Option<(f64, f64, f64, f64, usize)> {
    if valid_focal_lengths.is_empty() {
        return None;
    }

    // Filter out any with truly invalid focal lengths.
    let filtered: Vec<_> = valid_focal_lengths
        .iter()
        .filter(|(fl, _cost)| *fl >= MIN_VALID_FOCAL_LENGTH)
        .copied()
        .collect();

    if filtered.is_empty() {
        return None;
    }

    // Lower cost = higher weight. Use epsilon to avoid divide-by-zero.
    let epsilon = 1e-10;
    let weights: Vec<f64> = filtered
        .iter()
        .map(|(_focal_len, cost)| 1.0 / (cost + epsilon))
        .collect();

    let total_weight: f64 = weights.iter().sum();
    if total_weight <= 0.0 {
        return None;
    }

    // Calculate weighted mean.
    let weighted_mean: f64 = filtered
        .iter()
        .zip(weights.iter())
        .map(|((focal_len, _cost), weight)| focal_len * weight)
        .sum::<f64>()
        / total_weight;

    // Calculate weighted variance.
    let weighted_variance: f64 = filtered
        .iter()
        .zip(weights.iter())
        .map(|((focal_len, _cost), weight)| {
            let diff = focal_len - weighted_mean;
            weight * diff * diff
        })
        .sum::<f64>()
        / total_weight;

    let weighted_std_dev = weighted_variance.sqrt();

    // Refined bounds: weighted_mean +/- k*weighted_std_dev
    //
    // No clamping to original bounds - let statistics drive the range.
    let refined_min = (weighted_mean
        - REFINED_BOUNDS_STD_DEV_MULTIPLIER * weighted_std_dev)
        .max(MIN_VALID_FOCAL_LENGTH);
    let refined_max =
        weighted_mean + REFINED_BOUNDS_STD_DEV_MULTIPLIER * weighted_std_dev;

    // Ensure bounds are valid
    if refined_min >= refined_max {
        return None;
    }

    Some((
        weighted_mean,
        weighted_std_dev,
        refined_min,
        refined_max,
        filtered.len(),
    ))
}

/// Run camera solve with global focal length optimization.
///
/// Searches for the best focal length using either Differential
/// Evolution or Uniform Grid search, then runs a final solve with
/// that focal length.
pub(super) fn run_camera_solve_with_global_adjustment<
    L: Logger + Clone + Send + Sync,
>(
    logger: &L,
    scene_frame_range: FrameRange,
    markers: &MarkersData,
    camera_intrinsics: &CameraIntrinsics,
    film_back: &CameraFilmBack<f64>,
    image_size: &ImageSize<f64>,
    config: &CameraSolveConfig,
    global_config: &GlobalAdjustmentConfig,
    intermediate_writer: Option<Arc<dyn IntermediateResultWriter>>,
    camera_poses: &mut CameraPoses,
    bundle_positions: &mut BundlePositions,
    quality_metrics: &mut SolveQualityMetrics,
) -> Result<()> {
    // Extract initial focal length from provided intrinsics.
    let initial_focal_length_mm =
        camera_intrinsics.to_physical_parameters().0.value();

    match global_config {
        GlobalAdjustmentConfig::DifferentialEvolution {
            mode,
            focal_length_bounds,
            generations,
            seed,
            enable_coarse_search,
        } => {
            // Validate bounds.
            if focal_length_bounds.0 >= focal_length_bounds.1 {
                bail!("Invalid focal length bounds: min must be < max");
            }
            if focal_length_bounds.0 <= 0.0 {
                bail!("Focal length bounds must be positive");
            }

            if PRINT_SOLVER_DETAILS {
                mm_log_progress!(
                    logger,
                    "Global adjustment: Differential Evolution"
                );
                mm_log_info!(
                    logger,
                    "  Initial: {:.2} mm",
                    initial_focal_length_mm
                );
                mm_log_info!(
                    logger,
                    "  Bounds: {:.2} - {:.2} mm",
                    focal_length_bounds.0,
                    focal_length_bounds.1
                );
                mm_log_info!(logger, "  Mode: {:?}", mode);
                mm_log_info!(logger, "  Generations: {}", generations);
            }

            // Create DE configuration based on mode.
            let de_config = match mode {
                GlobalAdjustmentMode::SmallRefinement => {
                    DifferentialEvolutionConfig::small_refinement(
                        1, // Single parameter (focal length).
                        vec![*focal_length_bounds],
                        *generations,
                        *seed,
                    )
                }
                GlobalAdjustmentMode::LargeRefinement => {
                    DifferentialEvolutionConfig::large_refinement(
                        1,
                        vec![*focal_length_bounds],
                        *generations,
                        *seed,
                    )
                }
            };

            // Optimization strategy:
            // - If enable_coarse_search:
            //   Stage 1: Fast coarse search over full range (draft quality)
            //   Stage 2: Refined search over statistically narrowed range (final quality)
            //   Stage 3: Full solve with optimized focal length (final quality)
            // - If !enable_coarse_search:
            //   Stage 1: Single refined search over full range (final quality)
            //   Stage 2: Full solve with optimized focal length (final quality)
            //
            // The difference between modes is in the DE strategy parameters:
            // - LargeRefinement: aggressive global search.
            // - SmallRefinement: greedy local refinement.

            let mut best_focal_length = vec![initial_focal_length_mm];
            let mut best_cost = f64::MAX;

            // Track timing for different stages
            let mut coarse_search_time_secs: Option<f64> = None;
            let mut refined_search_time_secs: Option<f64> = None;

            // Stage 1: Optional coarse search
            if *enable_coarse_search {
                // Create modified config for coarse search with less
                // strict diversity threshold to allow faster early
                // stopping.
                let mut coarse_de_config = de_config;
                coarse_de_config.diversity_tolerance = Some(1e-2);

                // Because coarse search should have global
                // exploration of the problem space.
                coarse_de_config.strategy =
                    DifferentialEvolutionStrategy::Rand1Bin;

                // Run DE optimization.
                if PRINT_SOLVER_DETAILS {
                    mm_log_info!(
                        logger,
                        "  Starting Differential Evolution optimization..."
                    );
                    mm_log_info!(
                        logger,
                        "  Population size: {} (typical for {} parameters)",
                        coarse_de_config.population_size,
                        coarse_de_config.num_dimensions
                    );
                    mm_log_info!(logger, "  Using three-stage optimization: coarse + refined + final");
                    mm_log_info!(logger, "  Mode: {:?}", mode);
                    mm_log_progress!(logger, "  === DE Stage 1: Coarse Search ===  Focal length bounds: {:.2} - {:.2} mm",
                        focal_length_bounds.0, focal_length_bounds.1);
                    mm_log_info!(
                        logger,
                        "  Coarse diversity tolerance: {:.2e}",
                        coarse_de_config.diversity_tolerance.unwrap_or(0.0)
                    );
                }

                let de_start_time = std::time::Instant::now();
                let mut de_solver =
                    DifferentialEvolution::new(coarse_de_config)?;

                // Create evaluator with shared generation counter from DE
                // solver. Use draft quality for fast (but low-quality)
                // optimization.
                let solve_quality = SolveQuality::Draft;
                let evaluator = CameraSolveFocalLengthEvaluator::new(
                    scene_frame_range,
                    Arc::new(markers.clone()),
                    *film_back,
                    image_size.clone(),
                    Arc::new(config.clone()),
                    solve_quality,
                    de_solver.current_generation.clone(),
                    logger.clone(),
                );

                // Wrap with caching to avoid redundant evaluations when
                // trial vectors are clamped to bounds.
                let cached_evaluator = CachingEvaluator::new(evaluator);

                // Wrap with tracking for SmallRefinement mode to collect
                // statistics.
                let tracking_evaluator =
                    TrackingEvaluator::new(cached_evaluator);

                // Run coarse optimization.
                //
                // Note: Initial focal length is used as starting point
                // for DE, but not pre-evaluated to avoid blocking
                // parallel execution.
                best_cost = de_solver.run(
                    &tracking_evaluator,
                    &mut best_focal_length,
                    logger,
                )?;

                // Log cache statistics.
                let (cache_hits, cache_misses) =
                    tracking_evaluator.cache_stats();
                if PRINT_SOLVER_DETAILS {
                    mm_log_info!(logger, "  Coarse DE cache stats: {} hits, {} misses ({:.1}% hit rate)",
                        cache_hits,
                        cache_misses,
                        if cache_hits + cache_misses > 0 {
                            100.0 * cache_hits as f64
                                / (cache_hits + cache_misses) as f64
                        } else {
                            0.0
                        });
                }

                // Get valid focal lengths for potential refinement.
                let valid_focal_lengths =
                    tracking_evaluator.get_valid_focal_lengths();
                if PRINT_SOLVER_DETAILS {
                    mm_log_info!(
                        logger,
                        "  Valid focal lengths from coarse search: {}/{}",
                        valid_focal_lengths.len(),
                        cache_hits + cache_misses
                    );

                    if !valid_focal_lengths.is_empty() {
                        // Find best and worst costs.
                        let mut costs: Vec<f64> = valid_focal_lengths
                            .iter()
                            .map(|(_fl, cost)| *cost)
                            .collect();
                        costs.sort_by(|a, b| a.partial_cmp(b).unwrap());
                        let best_cost = costs[0];
                        let worst_cost = costs[costs.len() - 1];
                        let median_cost = if costs.len().is_multiple_of(2) {
                            (costs[costs.len() / 2 - 1]
                                + costs[costs.len() / 2])
                                / 2.0
                        } else {
                            costs[costs.len() / 2]
                        };

                        mm_log_info!(logger, "  Quality range: best={:.4} px, median={:.4} px, worst={:.4} px",
                                best_cost, median_cost, worst_cost
                            );

                        // Show focal length range
                        let mut focal_lengths: Vec<f64> = valid_focal_lengths
                            .iter()
                            .map(|(fl, _cost)| *fl)
                            .collect();
                        focal_lengths.sort_by(|a, b| a.partial_cmp(b).unwrap());
                        mm_log_info!(
                            logger,
                            "  Focal length range: {:.2} - {:.2} mm",
                            focal_lengths[0],
                            focal_lengths[focal_lengths.len() - 1]
                        );
                    }
                }

                let de_elapsed = de_start_time.elapsed();
                coarse_search_time_secs = Some(de_elapsed.as_secs_f64());

                if PRINT_SOLVER_DETAILS {
                    mm_log_info!(
                        logger,
                        "  Coarse DE optimization completed in {:.2}s",
                        coarse_search_time_secs.unwrap()
                    );
                }

                // Stage 2: Refined search based on coarse results
                // For both modes, run refined search based on valid focal lengths
                if let Some((
                    weighted_mean,
                    weighted_std_dev,
                    refined_min,
                    refined_max,
                    num_valid,
                )) = calculate_refined_bounds(&valid_focal_lengths)
                {
                    if PRINT_SOLVER_DETAILS {
                        mm_log_progress!(
                            logger,
                            "  === DE Stage 2: Refined Search  ===  Focal length bounds: {:.2} - {:.2} mm",
                            refined_min,
                            refined_max,
                        );
                        mm_log_info!(
                            logger,
                            "    Total evaluations: {}",
                            valid_focal_lengths.len()
                        );
                        mm_log_info!(
                            logger,
                            "    Valid focal lengths used: {}",
                            num_valid
                        );
                        mm_log_info!(
                            logger,
                            "    Weighted mean focal length: {:.2} mm",
                            weighted_mean
                        );
                        mm_log_info!(
                            logger,
                            "    Weighted std deviation: {:.2} mm",
                            weighted_std_dev
                        );
                        mm_log_info!(
                            logger,
                            "    Original bounds: {:.2} - {:.2} mm (range: {:.2} mm)",
                            focal_length_bounds.0,
                            focal_length_bounds.1,
                            focal_length_bounds.1 - focal_length_bounds.0
                        );
                        mm_log_info!(
                            logger,
                            "    Refined bounds:  {:.2} - {:.2} mm (range: {:.2} mm)",
                            refined_min,
                            refined_max,
                            refined_max - refined_min
                        );
                        let range_change_pct = ((refined_max - refined_min)
                            / (focal_length_bounds.1 - focal_length_bounds.0)
                            - 1.0)
                            * 100.0;
                        mm_log_info!(
                            logger,
                            "    Range change: {:+.1}% {}",
                            range_change_pct.abs(),
                            if range_change_pct > 0.0 {
                                "(expanded)"
                            } else if range_change_pct < 0.0 {
                                "(narrowed)"
                            } else {
                                "(unchanged)"
                            }
                        );
                    }

                    // Create new DE config with refined bounds and full solver.
                    //
                    // Use appropriate strategy based on mode.
                    let refined_de_config = match mode {
                        GlobalAdjustmentMode::SmallRefinement => {
                            DifferentialEvolutionConfig::small_refinement(
                                1, // Single parameter (focal length)
                                vec![(refined_min, refined_max)],
                                *generations,
                                *seed + 1, // Different seed for refined search.
                            )
                        }
                        GlobalAdjustmentMode::LargeRefinement => {
                            DifferentialEvolutionConfig::large_refinement(
                                1, // Single parameter (focal length).
                                vec![(refined_min, refined_max)],
                                *generations,
                                *seed + 1, // Different seed for refined search.
                            )
                        }
                    };

                    let refined_de_start = std::time::Instant::now();

                    // Create new DE solver for refined search
                    let mut refined_de_solver =
                        DifferentialEvolution::new(refined_de_config)?;

                    // Create evaluator with final quality for refined search
                    let solve_quality = SolveQuality::Final;
                    let refined_evaluator =
                        CameraSolveFocalLengthEvaluator::new(
                            scene_frame_range,
                            Arc::new(markers.clone()),
                            *film_back,
                            image_size.clone(),
                            Arc::new(config.clone()),
                            solve_quality,
                            refined_de_solver.current_generation.clone(),
                            logger.clone(),
                        );

                    let refined_cached =
                        CachingEvaluator::new(refined_evaluator);

                    if PRINT_SOLVER_DETAILS {
                        mm_log_info!(
                            logger,
                            "  Starting refined DE optimization..."
                        );
                    }

                    // Run refined optimization starting from coarse best result
                    let mut refined_best = best_focal_length.clone();
                    let refined_cost = refined_de_solver.run(
                        &refined_cached,
                        &mut refined_best,
                        logger,
                    )?;

                    best_focal_length = refined_best;
                    best_cost = refined_cost;

                    let refined_elapsed = refined_de_start.elapsed();
                    refined_search_time_secs =
                        Some(refined_elapsed.as_secs_f64());

                    if PRINT_SOLVER_DETAILS {
                        let (ref_hits, ref_misses) =
                            refined_cached.cache_stats();
                        mm_log_info!(logger, "  Refined DE cache stats: {} hits, {} misses ({:.1}% hit rate)",
                                ref_hits,
                                ref_misses,
                                if ref_hits + ref_misses > 0 {
                                    100.0 * ref_hits as f64
                                        / (ref_hits + ref_misses) as f64
                                } else {
                                    0.0
                                }
                            );
                        mm_log_info!(
                            logger,
                            "  Refined DE optimization completed in {:.2}s",
                            refined_search_time_secs.unwrap()
                        );
                        mm_log_info!(logger, "  Refined best focal length: {:.2} mm (cost: {:.4} px)",
                                best_focal_length[0], best_cost
                            );
                    }
                } else if PRINT_SOLVER_DETAILS {
                    mm_log_warn!(logger, "  Could not calculate refined bounds from valid focal lengths");
                    mm_log_warn!(
                        logger,
                        "  Skipping refined search, using coarse result"
                    );
                }
            } else {
                // Coarse search disabled - run single high-quality search
                if PRINT_SOLVER_DETAILS {
                    mm_log_info!(
                        logger,
                        "  Starting Differential Evolution optimization..."
                    );
                    mm_log_info!(logger, "  Coarse search disabled - running single refined search");
                    mm_log_progress!(logger, "  === DE Stage 1: Refined Search (Full Range) ===  Focal length bounds: {:.2} - {:.2} mm",
                            focal_length_bounds.0, focal_length_bounds.1
                        );
                    mm_log_info!(logger, "  Mode: {:?}", mode);
                }

                let refined_de_start = std::time::Instant::now();

                // Create DE solver with original bounds
                let mut refined_de_solver =
                    DifferentialEvolution::new(de_config)?;

                // Create evaluator with final quality
                let solve_quality = SolveQuality::Final;
                let refined_evaluator = CameraSolveFocalLengthEvaluator::new(
                    scene_frame_range,
                    Arc::new(markers.clone()),
                    *film_back,
                    image_size.clone(),
                    Arc::new(config.clone()),
                    solve_quality,
                    refined_de_solver.current_generation.clone(),
                    logger.clone(),
                );

                let refined_cached = CachingEvaluator::new(refined_evaluator);

                // Run refined optimization
                best_cost = refined_de_solver.run(
                    &refined_cached,
                    &mut best_focal_length,
                    logger,
                )?;

                let refined_elapsed = refined_de_start.elapsed();
                refined_search_time_secs = Some(refined_elapsed.as_secs_f64());

                if PRINT_SOLVER_DETAILS {
                    let (ref_hits, ref_misses) = refined_cached.cache_stats();
                    mm_log_info!(logger, "  Refined DE cache stats: {} hits, {} misses ({:.1}% hit rate)",
                            ref_hits,
                            ref_misses,
                            if ref_hits + ref_misses > 0 {
                                100.0 * ref_hits as f64
                                    / (ref_hits + ref_misses) as f64
                            } else {
                                0.0
                            }
                        );
                    mm_log_info!(
                        logger,
                        "  Refined DE optimization completed in {:.2}s",
                        refined_search_time_secs.unwrap()
                    );
                    mm_log_info!(
                        logger,
                        "  Best focal length: {:.2} mm (cost: {:.4} px)",
                        best_focal_length[0],
                        best_cost
                    );
                }
            }

            if best_cost >= f64::MAX {
                bail!(
                    "Camera solve failed for all focal length candidates in range [{:.2}, {:.2}] mm",
                    focal_length_bounds.0, focal_length_bounds.1
                );
            }

            if PRINT_SOLVER_DETAILS {
                mm_log_info!(logger, "  Global optimization result:");
                mm_log_info!(
                    logger,
                    "    Initial focal length: {:.2} mm",
                    initial_focal_length_mm
                );
                mm_log_info!(
                    logger,
                    "    Optimized focal length: {:.2} mm",
                    best_focal_length[0]
                );
                mm_log_info!(logger, "    Final cost: {:.4} px", best_cost);
            }

            // Run final solve with optimized focal length to populate
            // outputs.
            if PRINT_SOLVER_DETAILS {
                mm_log_progress!(logger, "  === DE Stage 3: Final Solve ===");
                mm_log_info!(logger, "  Running full camera solve with optimized focal length: {:.2} mm",
                        best_focal_length[0]
                    );
            }

            let final_solve_start = std::time::Instant::now();
            let optimized_intrinsics = CameraIntrinsics::from_centered_lens(
                MillimeterUnit::new(best_focal_length[0]),
                *film_back,
            );

            let solve_quality = SolveQuality::Final;
            let print_summary = true;
            camera_solve_inner(
                logger,
                scene_frame_range,
                markers,
                &optimized_intrinsics,
                image_size,
                config,
                solve_quality,
                print_summary,
                intermediate_writer,
                camera_poses,
                bundle_positions,
                quality_metrics,
            )?;
            let final_solve_time_secs =
                final_solve_start.elapsed().as_secs_f64();

            // Populate timing metrics for DE mode
            quality_metrics.coarse_search_time_secs = coarse_search_time_secs;
            quality_metrics.refined_search_time_secs = refined_search_time_secs;
            quality_metrics.global_optimization_time_secs = Some(
                coarse_search_time_secs.unwrap_or(0.0)
                    + refined_search_time_secs.unwrap_or(0.0),
            );
            quality_metrics.final_solve_time_secs = Some(final_solve_time_secs);

            // Record optimized focal length in metrics.
            quality_metrics.optimized_focal_length_mm =
                Some(best_focal_length[0]);

            Ok(())
        }
        GlobalAdjustmentConfig::UniformGridSearch {
            focal_length_bounds,
            num_samples,
        } => {
            // Validate bounds.
            if focal_length_bounds.0 >= focal_length_bounds.1 {
                bail!("Invalid focal length bounds: min must be < max");
            }
            if focal_length_bounds.0 <= 0.0 {
                bail!("Focal length bounds must be positive");
            }
            if *num_samples < 1 {
                bail!("num_samples must be >= 1");
            }

            if PRINT_SOLVER_DETAILS {
                mm_log_progress!(
                    logger,
                    "Global adjustment: Uniform Grid Search"
                );
                mm_log_info!(
                    logger,
                    "  Initial: {:.2} mm",
                    initial_focal_length_mm
                );
                mm_log_info!(
                    logger,
                    "  Bounds: {:.2} - {:.2} mm",
                    focal_length_bounds.0,
                    focal_length_bounds.1
                );
                mm_log_info!(logger, "  Num samples: {}", num_samples);
            }

            // Create grid search configuration.
            let grid_config = UniformGridSearchConfig {
                num_dimensions: 1,
                num_samples_per_dimension: vec![*num_samples],
                bounds: vec![*focal_length_bounds],
            };

            let grid_solver = UniformGridSearch::new(grid_config)?;

            // Create evaluator (dummy generation counter since grid
            // search is deterministic).
            let solve_quality = SolveQuality::Final;
            let evaluator = CameraSolveFocalLengthEvaluator::new(
                scene_frame_range,
                Arc::new(markers.clone()),
                *film_back,
                image_size.clone(),
                Arc::new(config.clone()),
                solve_quality,
                Arc::new(AtomicUsize::new(0)),
                logger.clone(),
            );

            // Wrap with caching to avoid redundant evaluations.
            let cached_evaluator = CachingEvaluator::new(evaluator);

            if PRINT_SOLVER_DETAILS {
                mm_log_info!(
                    logger,
                    "  Starting Uniform Grid Search optimization..."
                );
            }

            let grid_start_time = std::time::Instant::now();

            let mut best_focal_length = vec![initial_focal_length_mm];
            let best_cost = grid_solver.run(
                &cached_evaluator,
                &mut best_focal_length,
                logger,
            )?;
            let grid_elapsed = grid_start_time.elapsed();

            if PRINT_SOLVER_DETAILS {
                mm_log_info!(
                    logger,
                    "  Grid search completed in {:.2}s",
                    grid_elapsed.as_secs_f64()
                );
            }

            if best_cost >= f64::MAX {
                bail!(
                    "Camera solve failed for all focal length candidates in range [{:.2}, {:.2}] mm",
                    focal_length_bounds.0, focal_length_bounds.1
                );
            }

            if PRINT_SOLVER_DETAILS {
                mm_log_info!(logger, "  Global optimization result:");
                mm_log_info!(
                    logger,
                    "    Initial focal length: {:.2} mm",
                    initial_focal_length_mm
                );
                mm_log_info!(
                    logger,
                    "    Optimized focal length: {:.2} mm",
                    best_focal_length[0]
                );
                mm_log_info!(
                    logger,
                    "    Improvement: {:.2} mm ({:+.1}%)",
                    best_focal_length[0] - initial_focal_length_mm,
                    ((best_focal_length[0] - initial_focal_length_mm)
                        / initial_focal_length_mm)
                        * 100.0
                );
                mm_log_info!(logger, "    Final cost: {:.4} px", best_cost);
            }

            // Run final solve with optimized focal length to populate
            // outputs.
            let final_solve_start = std::time::Instant::now();
            let optimized_intrinsics = CameraIntrinsics::from_centered_lens(
                MillimeterUnit::new(best_focal_length[0]),
                *film_back,
            );

            let solve_quality = SolveQuality::Final;
            let print_summary = true;
            camera_solve_inner(
                logger,
                scene_frame_range,
                markers,
                &optimized_intrinsics,
                image_size,
                config,
                solve_quality,
                print_summary,
                intermediate_writer,
                camera_poses,
                bundle_positions,
                quality_metrics,
            )?;
            let final_solve_time_secs =
                final_solve_start.elapsed().as_secs_f64();

            // Populate timing metrics for UGS mode
            quality_metrics.global_optimization_time_secs =
                Some(grid_elapsed.as_secs_f64());
            quality_metrics.final_solve_time_secs = Some(final_solve_time_secs);

            // Record optimized focal length in metrics.
            quality_metrics.optimized_focal_length_mm =
                Some(best_focal_length[0]);

            Ok(())
        }
    }
}
