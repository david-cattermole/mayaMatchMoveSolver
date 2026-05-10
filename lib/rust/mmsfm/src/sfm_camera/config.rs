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

/// What kind of parameter an optimizer vector element represents.
#[derive(Debug, Clone)]
pub enum AdjustmentParameterKind {
    /// Focal length in millimeters. `x[i]` is `focal_length_mm`.
    FocalLength,
    /// A lens distortion parameter from a Nuke lens layer.
    LensParameter {
        /// Layer index (0-based) into `NukeLensData.layer_node_names`.
        layer_index: u8,
        /// Index into the `ParameterBlock [f64; 22]` for this layer.
        param_index: usize,
        /// Human-readable knob name for logging (e.g. `"Distortion"`).
        knob_name: String,
    },
}

/// One parameter in the global adjustment optimization vector.
#[derive(Debug, Clone)]
pub struct AdjustmentParameter {
    /// What this parameter controls.
    pub kind: AdjustmentParameterKind,
    /// Optimizer search bounds `(min, max)`.
    pub bounds: (f64, f64),
    /// Starting value (from CLI args or loaded Nuke lens file).
    pub initial_value: f64,
    /// Number of samples for uniform grid search. 0 means use default.
    pub sample_count: usize,
}

/// Describes the full optimizer parameter vector layout.
///
/// Maps each index in the flat `x: &[f64]` vector to its semantic
/// meaning. For example, if optimizing focal_length + Distortion, the
/// layout has 2 parameters and `x` has length 2.
#[derive(Debug, Clone, Default)]
pub struct AdjustmentParameterLayout {
    pub parameters: Vec<AdjustmentParameter>,
}

impl AdjustmentParameterLayout {
    /// Number of dimensions in the optimizer parameter vector.
    pub fn num_dimensions(&self) -> usize {
        self.parameters.len()
    }

    /// Optimizer bounds for each dimension: `Vec<(min, max)>`.
    pub fn bounds(&self) -> Vec<(f64, f64)> {
        self.parameters.iter().map(|p| p.bounds).collect()
    }

    /// True if any parameter is a `FocalLength`.
    pub fn has_focal_length(&self) -> bool {
        self.parameters
            .iter()
            .any(|p| matches!(p.kind, AdjustmentParameterKind::FocalLength))
    }

    /// True if any parameter is a `LensParameter`.
    pub fn has_lens_parameters(&self) -> bool {
        self.parameters.iter().any(|p| {
            matches!(p.kind, AdjustmentParameterKind::LensParameter { .. })
        })
    }

    /// Index of the focal length parameter in the vector, if present.
    pub fn focal_length_index(&self) -> Option<usize> {
        self.parameters.iter().position(|p| {
            matches!(p.kind, AdjustmentParameterKind::FocalLength)
        })
    }

    /// Focal length bounds `(min, max)`, if a focal length parameter exists.
    pub fn focal_length_bounds(&self) -> Option<(f64, f64)> {
        self.parameters.iter().find_map(|p| {
            if matches!(p.kind, AdjustmentParameterKind::FocalLength) {
                Some(p.bounds)
            } else {
                None
            }
        })
    }

    /// Extract lens parameter overrides from an optimizer vector `x`.
    /// Returns `Vec<(layer_index, param_index, value)>`.
    pub fn lens_overrides_from_params(
        &self,
        x: &[f64],
    ) -> Vec<(u8, usize, f64)> {
        self.parameters
            .iter()
            .enumerate()
            .filter_map(|(i, p)| match &p.kind {
                AdjustmentParameterKind::LensParameter {
                    layer_index,
                    param_index,
                    ..
                } => Some((*layer_index, *param_index, x[i])),
                _ => None,
            })
            .collect()
    }

    /// Get the initial values as a vector (same ordering as the parameter vector).
    pub fn initial_values(&self) -> Vec<f64> {
        self.parameters.iter().map(|p| p.initial_value).collect()
    }

    /// Per-parameter sample counts for uniform grid search.
    ///
    /// Returns `sample_count` for each parameter, substituting
    /// `default_samples` wherever `sample_count` is 0.
    pub fn num_samples_per_param(&self, default_samples: usize) -> Vec<usize> {
        self.parameters
            .iter()
            .map(|p| {
                if p.sample_count > 0 {
                    p.sample_count
                } else {
                    default_samples
                }
            })
            .collect()
    }
}

/// Bundle adjustment solver type selection.
#[derive(Debug, Clone, PartialEq)]
pub enum BundleAdjustmentSolverType {
    /// Dense Levenberg-Marquardt, suitable for small problems.
    DenseLM,
    /// Sparse Levenberg-Marquardt with direct CHOLMOD factorization.
    SparseLevenbergMarquardt,
    /// Sparse Levenberg-Marquardt with Schur complement elimination.
    /// Exploits the block structure of bundle adjustment problems
    /// to eliminate 3D point parameters first, solving a much smaller
    /// camera-only system. Faster than SparseLevenbergMarquardt when
    /// the number of 3D points is much larger than the number of cameras.
    SchurComplementLM,
}

/// Global adjustment mode for focal length optimization.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum GlobalAdjustmentMode {
    /// Fine-tuning near a known focal length using small mutation steps.
    SmallRefinement,
    /// Broad search for an unknown focal length using large mutation steps.
    LargeRefinement,
}

/// Configuration for global parameter optimization.
#[derive(Debug, Clone)]
pub enum GlobalAdjustmentConfig {
    /// Differential Evolution optimizer.
    DifferentialEvolution {
        /// Optimization mode (SmallRefinement or LargeRefinement).
        mode: GlobalAdjustmentMode,
        /// Parameter vector layout (describes what each `x[i]` controls).
        parameter_layout: AdjustmentParameterLayout,
        /// Number of DE generations (iterations).
        generations: usize,
        /// Random seed for reproducible results.
        seed: u64,
        /// When true, runs a fast draft-quality search before the refined search.
        enable_coarse_search: bool,
    },

    /// Uniform Grid Search optimizer.
    UniformGridSearch {
        /// Parameter vector layout (describes what each `x[i]` controls).
        parameter_layout: AdjustmentParameterLayout,
        /// Number of uniformly-spaced samples per parameter dimension.
        num_samples_per_param: Vec<usize>,
    },
}

impl GlobalAdjustmentConfig {
    /// Create configuration for fine-tuning near a known focal length using Differential Evolution.
    pub fn small_refinement(
        focal_length_bounds: (f64, f64),
        generations: usize,
        seed: u64,
    ) -> Self {
        let parameters = vec![AdjustmentParameter {
            kind: AdjustmentParameterKind::FocalLength,
            bounds: focal_length_bounds,
            initial_value: (focal_length_bounds.0 + focal_length_bounds.1)
                / 2.0,
            sample_count: 0,
        }];
        Self::DifferentialEvolution {
            mode: GlobalAdjustmentMode::SmallRefinement,
            parameter_layout: AdjustmentParameterLayout { parameters },
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
        let parameters = vec![AdjustmentParameter {
            kind: AdjustmentParameterKind::FocalLength,
            bounds: focal_length_bounds,
            initial_value: (focal_length_bounds.0 + focal_length_bounds.1)
                / 2.0,
            sample_count: 0,
        }];
        Self::DifferentialEvolution {
            mode: GlobalAdjustmentMode::LargeRefinement,
            parameter_layout: AdjustmentParameterLayout { parameters },
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
        let parameters = vec![AdjustmentParameter {
            kind: AdjustmentParameterKind::FocalLength,
            bounds: focal_length_bounds,
            initial_value: (focal_length_bounds.0 + focal_length_bounds.1)
                / 2.0,
            sample_count: 0,
        }];
        Self::UniformGridSearch {
            parameter_layout: AdjustmentParameterLayout { parameters },
            num_samples_per_param: vec![num_samples],
        }
    }

    /// Get the parameter layout for this configuration.
    pub fn parameter_layout(&self) -> &AdjustmentParameterLayout {
        match self {
            Self::DifferentialEvolution {
                parameter_layout, ..
            } => parameter_layout,
            Self::UniformGridSearch {
                parameter_layout, ..
            } => parameter_layout,
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
    /// Optimized lens parameters from global adjustment.
    /// Each tuple: `(layer_index, param_index, knob_name, optimized_value)`.
    pub optimized_lens_parameters: Option<Vec<(u8, usize, String, f64)>>,
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
