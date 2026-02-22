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

//! Configuration types and quality metrics for camera solving.

use mmio::uvtrack_reader::FrameNumber;

/// Bundle adjustment solver type selection.
#[derive(Debug, Clone, PartialEq)]
pub enum BundleAdjustmentSolverType {
    /// Dense Levenberg-Marquardt, suitable for small problems.
    DenseLM,
    /// Sparse Levenberg-Marquardt with direct CHOLMOD factorization.
    SparseLevenbergMarquardt,
}

/// Global adjustment mode for focal length optimization.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum GlobalAdjustmentMode {
    /// Fine-tuning near a known focal length using small mutation steps.
    SmallRefinement,
    /// Broad search for an unknown focal length using large mutation steps.
    LargeRefinement,
}

/// Configuration for global focal length optimization.
#[derive(Debug, Clone)]
pub enum GlobalAdjustmentConfig {
    /// Differential Evolution optimizer.
    DifferentialEvolution {
        /// Optimization mode (SmallRefinement or LargeRefinement).
        mode: GlobalAdjustmentMode,
        /// Focal length search bounds (min, max) in millimeters.
        focal_length_bounds: (f64, f64),
        /// Number of DE generations (iterations).
        generations: usize,
        /// Random seed for reproducible results.
        seed: u64,
        /// When true, runs a fast draft-quality search before the refined search.
        enable_coarse_search: bool,
    },

    /// Uniform Grid Search optimizer.
    UniformGridSearch {
        /// Focal length search bounds (min, max) in millimeters.
        focal_length_bounds: (f64, f64),
        /// Number of uniformly-spaced samples to evaluate.
        num_samples: usize,
    },
}

impl GlobalAdjustmentConfig {
    /// Create configuration for fine-tuning near a known focal length using Differential Evolution.
    pub fn small_refinement(
        focal_length_bounds: (f64, f64),
        generations: usize,
        seed: u64,
    ) -> Self {
        Self::DifferentialEvolution {
            mode: GlobalAdjustmentMode::SmallRefinement,
            focal_length_bounds,
            generations,
            seed,
            enable_coarse_search: true,
        }
    }

    /// Create configuration for broad search of an unknown focal length using Differential Evolution.
    pub fn large_refinement(
        focal_length_bounds: (f64, f64),
        generations: usize,
        seed: u64,
    ) -> Self {
        Self::DifferentialEvolution {
            mode: GlobalAdjustmentMode::LargeRefinement,
            focal_length_bounds,
            generations,
            seed,
            enable_coarse_search: true,
        }
    }

    /// Create configuration for exhaustive Uniform Grid Search.
    pub fn uniform_grid_search(
        focal_length_bounds: (f64, f64),
        num_samples: usize,
    ) -> Self {
        Self::UniformGridSearch {
            focal_length_bounds,
            num_samples,
        }
    }
}

/// Configuration for camera solver.
#[derive(Debug, Clone)]
pub struct CameraSolveConfig {
    /// Frame to use as the coordinate system origin.
    pub origin_frame: FrameNumber,
    /// Scale factor for the scene (1.0 = unit scale).
    pub scene_scale: f64,
    /// Number of iterations for bundle adjustment.
    pub bundle_iter_num: usize,
    /// Bundle adjustment solver type for the main solve.
    pub bundle_solver_type: BundleAdjustmentSolverType,
    /// Bundle adjustment solver type for the initial two-camera initialization.
    pub root_solver_type: BundleAdjustmentSolverType,
    /// Number of iterations for root frame solving.
    pub root_iter_num: usize,
    /// Number of iterations for animated attribute solving.
    pub anim_iter_num: usize,
    /// Minimum number of solver iterations.
    pub min_num_iterations: usize,
    /// When true, add noise to initial parameters to avoid local minima.
    pub enable_noise: bool,
    /// Scale factor for rotation noise as a fraction of angular field of view.
    pub rotation_noise_scale_factor: f64,
    /// Scale factor for translation noise as a fraction of scene scale.
    pub translation_noise_scale_factor: f64,
}

use crate::sfm_camera::constants::DEFAULT_ANIM_ITER_NUM;
use crate::sfm_camera::constants::DEFAULT_BUNDLE_ITER_NUM;
use crate::sfm_camera::constants::DEFAULT_MIN_NUM_ITERATIONS;
use crate::sfm_camera::constants::DEFAULT_ROOT_ITER_NUM;
use crate::sfm_camera::constants::DEFAULT_SCENE_SCALE;

impl Default for CameraSolveConfig {
    fn default() -> Self {
        Self {
            origin_frame: 0,
            scene_scale: DEFAULT_SCENE_SCALE,
            bundle_iter_num: DEFAULT_BUNDLE_ITER_NUM,
            bundle_solver_type:
                BundleAdjustmentSolverType::SparseLevenbergMarquardt,
            root_solver_type: BundleAdjustmentSolverType::DenseLM,
            root_iter_num: DEFAULT_ROOT_ITER_NUM,
            anim_iter_num: DEFAULT_ANIM_ITER_NUM,
            min_num_iterations: DEFAULT_MIN_NUM_ITERATIONS,
            enable_noise: false,
            rotation_noise_scale_factor: 0.01,
            translation_noise_scale_factor: 0.01,
        }
    }
}

/// Quality metrics for the camera solve.
#[derive(Debug, Clone, Default)]
pub struct SolveQualityMetrics {
    /// Mean reprojection error across all frames (in pixels).
    pub mean_reprojection_error: f64,
    /// Median reprojection error (in pixels).
    pub median_reprojection_error: f64,
    /// Total number of markers used in solve.
    pub total_markers_used: usize,
    /// Total number of bundles successfully triangulated.
    pub total_bundles_triangulated: usize,
    /// Number of frames successfully solved.
    pub frames_solved: usize,
    /// Number of frames that could not be solved.
    pub frames_unsolved: usize,
    /// Optimized focal length from global adjustment, if enabled.
    pub optimized_focal_length_mm: Option<f64>,
    /// Time spent in the coarse global search stage (seconds), DE mode only.
    pub coarse_search_time_secs: Option<f64>,
    /// Time spent in the refined global search stage (seconds), DE mode only.
    pub refined_search_time_secs: Option<f64>,
    /// Total time spent in global optimization (seconds).
    pub global_optimization_time_secs: Option<f64>,
    /// Time spent in the final solve (seconds).
    pub final_solve_time_secs: Option<f64>,
}

/// The quality of the solve.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SolveQuality {
    /// A draft solve, which is faster but lower quality.
    Draft,
    /// A final solve, which is slower but higher quality.
    Final,
}
