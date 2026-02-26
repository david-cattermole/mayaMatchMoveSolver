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

//! Centralized output file naming for mmsfm visualizations.

use anyhow::Result;
use std::path::PathBuf;

use crate::sfm_camera::BundleAdjustmentSolverType;

/// Type of test being run
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TestType {
    BundleAdjust,
    CameraPoseFromBundles,
    CameraSolve,
    Triangulation,
    RelativePose,
    CameraOrientation,
}

impl TestType {
    pub fn as_str(&self) -> &'static str {
        match self {
            TestType::BundleAdjust => "bundle_adjust",
            TestType::CameraPoseFromBundles => "camera_pose_from_bundles",
            TestType::CameraSolve => "camera_solve",
            TestType::Triangulation => "triangulation",
            TestType::RelativePose => "relative_pose",
            TestType::CameraOrientation => "camera_orientation",
        }
    }
}

/// Whether the input data is clean or noisy.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DataCondition {
    Clean,
    Noisy,
}

impl DataCondition {
    pub fn as_str(&self) -> &'static str {
        match self {
            DataCondition::Clean => "clean",
            DataCondition::Noisy => "noisy",
        }
    }
}

/// Solver type used for bundle optimization.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum NamingSolverType {
    DenseLM,
    SparseLevenbergMarquardt,
}

impl NamingSolverType {
    pub fn as_str(&self) -> &'static str {
        match self {
            NamingSolverType::DenseLM => "dense_lm",
            NamingSolverType::SparseLevenbergMarquardt => "sparse_lm",
        }
    }
}

pub fn bundle_adjustment_solver_type_to_naming(
    solver_type: &BundleAdjustmentSolverType,
) -> NamingSolverType {
    match solver_type {
        BundleAdjustmentSolverType::DenseLM => NamingSolverType::DenseLM,
        BundleAdjustmentSolverType::SparseLevenbergMarquardt => {
            NamingSolverType::SparseLevenbergMarquardt
        }
    }
}

/// Processing stage.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Stage {
    Initial,
    Optimised,
    Final,
}

impl Stage {
    pub fn as_str(&self) -> &'static str {
        match self {
            Stage::Initial => "00_initial",
            Stage::Optimised => "01_optimised",
            Stage::Final => "02_final",
        }
    }
}

/// Type of visualization being generated.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum VisualizationType {
    /// 3D scene with camera frustums and points.
    Scene3d,
    /// 2D marker reprojection scatter plot.
    MarkerReprojection2d,
    /// Residual error line plot.
    ResidualsLinePlot,
    /// Reprojection errors over time.
    ErrorsLinePlot,
    /// Correspondence count over time.
    CorrespondencesLinePlot,
}

impl VisualizationType {
    pub fn as_str(&self) -> &'static str {
        match self {
            VisualizationType::Scene3d => "scene_3d",
            VisualizationType::MarkerReprojection2d => {
                "marker_reprojections_2d"
            }
            VisualizationType::ResidualsLinePlot => "residuals_line_plot",
            VisualizationType::ErrorsLinePlot => "errors_line_plot",
            VisualizationType::CorrespondencesLinePlot => {
                "correspondences_line_plot"
            }
        }
    }
}

/// View angle for 3D visualizations.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ViewName {
    Front,
    Back,
    Top,
    Bottom,
    Right,
    Left,
    ThreeQuarterA,
    ThreeQuarterB,
}

impl ViewName {
    pub fn as_str(&self) -> &'static str {
        match self {
            ViewName::Front => "front",
            ViewName::Back => "back",
            ViewName::Top => "top",
            ViewName::Bottom => "bottom",
            ViewName::Right => "right",
            ViewName::Left => "left",
            ViewName::ThreeQuarterA => "three_quarter_a",
            ViewName::ThreeQuarterB => "three_quarter_b",
        }
    }
}

/// Builds consistent output file paths for visualizations.
#[derive(Debug, Clone)]
pub struct OutputFileNaming {
    /// Base output directory
    output_dir: PathBuf,
    test_type: TestType,
    dataset_name: String,
    visualization_type: VisualizationType,
    data_condition: Option<DataCondition>,
    solver_type: Option<NamingSolverType>,
    stage: Option<Stage>,
    view_name: Option<ViewName>,
    frame_number: Option<u32>,
    triangulation_method: Option<String>,
    /// When true, `directory_path()` returns `output_dir` directly
    /// without appending test_type/dataset/condition subdirectories.
    flat_directory: bool,
}

impl OutputFileNaming {
    pub fn new(
        output_dir: impl Into<PathBuf>,
        test_type: TestType,
        dataset_name: impl Into<String>,
        visualization_type: VisualizationType,
    ) -> Self {
        Self {
            output_dir: output_dir.into(),
            test_type,
            dataset_name: dataset_name.into(),
            visualization_type,
            data_condition: None,
            solver_type: None,
            stage: None,
            view_name: None,
            frame_number: None,
            triangulation_method: None,
            flat_directory: false,
        }
    }

    pub fn with_flat_directory(mut self) -> Self {
        self.flat_directory = true;
        self
    }

    pub fn with_condition(mut self, condition: DataCondition) -> Self {
        self.data_condition = Some(condition);
        self
    }

    pub fn with_solver(mut self, solver: NamingSolverType) -> Self {
        self.solver_type = Some(solver);
        self
    }

    pub fn with_stage(mut self, stage: Stage) -> Self {
        self.stage = Some(stage);
        self
    }

    pub fn with_view(mut self, view: ViewName) -> Self {
        self.view_name = Some(view);
        self
    }

    pub fn with_frame(mut self, frame: u32) -> Self {
        self.frame_number = Some(frame);
        self
    }

    pub fn with_triangulation_method(
        mut self,
        method: impl Into<String>,
    ) -> Self {
        self.triangulation_method = Some(method.into());
        self
    }

    /// Returns the output directory path.
    ///
    /// Format: `{output_dir}/{test_type}/{dataset}/{condition}_{solver}_{triangulation_method}`
    pub fn directory_path(&self) -> Result<PathBuf> {
        let mut path = self.output_dir.clone();

        if self.flat_directory {
            return Ok(path);
        }

        path.push(self.test_type.as_str());

        // Always add dataset name.
        path.push(self.dataset_name.clone());

        let mut parts = Vec::new();

        if let Some(condition) = &self.data_condition {
            parts.push(condition.as_str().to_string());
        }

        if let Some(solver) = &self.solver_type {
            parts.push(solver.as_str().to_string());
        }

        if let Some(method) = &self.triangulation_method {
            parts.push(method.clone());
        }

        if !parts.is_empty() {
            let name = parts.join("_");
            path.push(name);
        }

        Ok(path)
    }

    /// Returns the filename (without directory, with extension).
    ///
    /// Format: `{dataset}_{condition}_{solver}_{triangulation_method}_{visualization_type}_{stage}_{view}{frame}.png`
    pub fn filename(&self) -> String {
        let mut parts = Vec::new();

        parts.push(self.dataset_name.clone());

        if let Some(condition) = &self.data_condition {
            parts.push(condition.as_str().to_string());
        }

        if let Some(solver) = &self.solver_type {
            parts.push(solver.as_str().to_string());
        }

        if let Some(method) = &self.triangulation_method {
            parts.push(method.clone());
        }

        parts.push(self.visualization_type.as_str().to_string());

        if let Some(stage) = &self.stage {
            parts.push(stage.as_str().to_string());
        }

        if let Some(view) = &self.view_name {
            parts.push(view.as_str().to_string());
        }

        let mut filename = parts.join("_");

        if let Some(frame) = self.frame_number {
            filename.push_str(&format!(".{:04}", frame));
        }

        filename.push_str(".png");

        filename
    }

    /// Returns the full path (directory + filename), creating directories as needed.
    pub fn full_path(&self) -> Result<PathBuf> {
        let dir_path = self.directory_path()?;

        if !dir_path.exists() {
            std::fs::create_dir_all(&dir_path)?;
        }

        let mut path = dir_path;
        path.push(self.filename());
        Ok(path)
    }

    /// Clone with a different stage.
    pub fn clone_with_stage(&self, stage: Stage) -> Self {
        let mut cloned = self.clone();
        cloned.stage = Some(stage);
        cloned
    }

    /// Clone with a different view.
    pub fn clone_with_view(&self, view: ViewName) -> Self {
        let mut cloned = self.clone();
        cloned.view_name = Some(view);
        cloned
    }

    /// Clone with a different visualization type.
    pub fn clone_with_visualization(
        &self,
        viz_type: VisualizationType,
    ) -> Self {
        let mut cloned = self.clone();
        cloned.visualization_type = viz_type;
        cloned
    }

    /// Clone with a different frame number.
    pub fn clone_with_frame(&self, frame: u32) -> Self {
        let mut cloned = self.clone();
        cloned.frame_number = Some(frame);
        cloned
    }

    /// Clone with a different triangulation method.
    pub fn clone_with_triangulation_method(
        &self,
        method: impl Into<String>,
    ) -> Self {
        let mut cloned = self.clone();
        cloned.triangulation_method = Some(method.into());
        cloned
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn test_output_dir() -> PathBuf {
        PathBuf::from("/tmp/test_output")
    }

    #[test]
    fn test_simple_filename() {
        let naming = OutputFileNaming::new(
            test_output_dir(),
            TestType::BundleAdjust,
            "cube_a",
            VisualizationType::Scene3d,
        );

        assert_eq!(naming.filename(), "cube_a_scene_3d.png");
    }

    #[test]
    fn test_full_filename() {
        let naming = OutputFileNaming::new(
            test_output_dir(),
            TestType::BundleAdjust,
            "cube_a",
            VisualizationType::Scene3d,
        )
        .with_condition(DataCondition::Clean)
        .with_solver(NamingSolverType::DenseLM)
        .with_stage(Stage::Initial)
        .with_view(ViewName::Front);

        assert_eq!(
            naming.filename(),
            "cube_a_clean_dense_lm_scene_3d_00_initial_front.png"
        );
    }

    #[test]
    fn test_trajectory_frame_filename() {
        let naming = OutputFileNaming::new(
            test_output_dir(),
            TestType::CameraSolve,
            "cube_a",
            VisualizationType::Scene3d,
        )
        .with_view(ViewName::Top)
        .with_frame(42);

        assert_eq!(naming.filename(), "cube_a_scene_3d_top.0042.png");
    }
}
