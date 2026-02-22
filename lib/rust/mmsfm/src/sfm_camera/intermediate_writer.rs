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

//! Writes intermediate camera solver results during a long-running solve.

use crate::datatype::{BundlePositions, CameraPoses};

use super::reprojection::ReprojectionErrorStats;

/// Writes intermediate solver results to some output (e.g. a file or channel).
///
/// Implementors own the data and may write on a background thread.
/// Errors should be logged internally, not propagated.
pub trait IntermediateResultWriter: Send + Sync {
    fn write_intermediate(
        &self,
        camera_poses: CameraPoses,
        bundle_positions: BundlePositions,
        stats: ReprojectionErrorStats,
    );
}
