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

pub mod output_naming;
pub mod reprojection;
pub mod residuals;
pub mod scene;

pub use output_naming::{
    bundle_adjustment_solver_type_to_naming, test_output_file_naming,
    DataCondition, NamingSolverType, OutputFileNaming, Stage, TestType,
    ViewName, VisualizationType,
};
pub use reprojection::{
    visualize_marker_reprojections_2d_scatter,
    visualize_marker_reprojections_sequential,
};
pub use scene::{
    CameraPoseWithFrame, ViewConfiguration, ViewConfigurationBuilder,
};
