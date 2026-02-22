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

mod common;
mod depth_average;
mod line_line;
mod optimal_angular;

pub use crate::bundle_triangulation::common::{
    calculate_point_angle_radian, is_point_in_front_of_cameras,
    is_triangulation_quality_good, triangulate_points_batch,
    triangulate_points_from_relative_pose, TriangulationResult,
    TriangulationStorage, Triangulator,
};
pub use crate::bundle_triangulation::depth_average::{
    AggregationMode, DepthAverageConfig, TriangulateDataDepthAverage,
    TriangulationResultDepthAverage, TriangulatorDepthAverage,
};
pub use crate::bundle_triangulation::line_line::{
    TriangulateDataLineLine, TriangulationResultLineLine, TriangulatorLineLine,
};
pub use crate::bundle_triangulation::optimal_angular::{
    OptimalAngularConfig, TriangulateDataOptimalAngular,
    TriangulationResultOptimalAngular, TriangulatorOptimalAngular,
};
