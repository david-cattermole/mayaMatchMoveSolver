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

use anyhow::Result;
use nalgebra::Matrix3;

use crate::camera_essential_matrix::common::{
    is_valid_essential_matrix, select_best_candidate_by_angular_error_dynamic,
    CameraEssentialMatrixError, EssentialMatrixWorkspace,
};
use crate::datatype::BearingVectorCorrespondence;

use super::solve::five_point_relative_pose;

/// Workspace for the 5-point essential matrix algorithm.
pub struct EssentialMatrixFivePointWorkspace {
    // TODO: Pre-allocate memory here to avoid per-call allocations.
}

impl EssentialMatrixWorkspace for EssentialMatrixFivePointWorkspace {
    fn new() -> Self {
        Self {}
    }

    fn clear(&mut self) {}

    fn reuse_with<F, R>(&mut self, f: F) -> R
    where
        F: FnOnce(&mut Self) -> R,
    {
        self.clear();
        f(self)
    }
}

impl EssentialMatrixFivePointWorkspace {
    pub fn new() -> Self {
        <Self as EssentialMatrixWorkspace>::new()
    }

    pub fn clear(&mut self) {
        <Self as EssentialMatrixWorkspace>::clear(self)
    }

    pub fn reuse_with<F, R>(&mut self, f: F) -> R
    where
        F: FnOnce(&mut Self) -> R,
    {
        <Self as EssentialMatrixWorkspace>::reuse_with(self, f)
    }

    /// Compute essential matrices using the 5-point algorithm.
    ///
    /// Requires exactly 5 correspondences. Returns up to 10 candidate matrices.
    pub fn compute_essential_matrices(
        &mut self,
        correspondences: &[BearingVectorCorrespondence],
    ) -> Result<Vec<Matrix3<f64>>, CameraEssentialMatrixError> {
        if correspondences.len() != 5 {
            return Err(
                CameraEssentialMatrixError::InvalidPointCountForFivePoint,
            );
        }

        let mut points1 = [[0.0; 2]; 5];
        let mut points2 = [[0.0; 2]; 5];

        for (i, corr) in correspondences.iter().enumerate() {
            points1[i] = [corr.camera_a.x, corr.camera_a.y];
            points2[i] = [corr.camera_b.x, corr.camera_b.y];
        }

        let poses = five_point_relative_pose(&points1, &points2)
            .map_err(|_e| CameraEssentialMatrixError::NoValidSolution)?;

        // Convert poses to essential matrices: E = [t]_x * R
        let mut essential_matrices = Vec::new();

        for pose in poses {
            let t = pose.translation;
            let t_skew =
                Matrix3::new(0.0, -t.z, t.y, t.z, 0.0, -t.x, -t.y, t.x, 0.0);
            let essential = t_skew * pose.rotation;

            let norm = essential.norm();
            if norm > 1e-10 {
                let normalized = essential / norm;
                if is_valid_essential_matrix(&normalized) {
                    essential_matrices.push(normalized);
                }
            }
        }

        if essential_matrices.is_empty() {
            return Err(CameraEssentialMatrixError::NoValidSolution);
        }

        Ok(essential_matrices)
    }

    /// Compute the best essential matrix from 5 or more correspondences.
    ///
    /// Selects the candidate with the lowest average angular error.
    pub fn compute_best_essential_matrix(
        &mut self,
        correspondences: &[BearingVectorCorrespondence],
    ) -> Result<Matrix3<f64>, CameraEssentialMatrixError> {
        let num_points = correspondences.len();

        if num_points < 5 {
            return Err(
                CameraEssentialMatrixError::InvalidPointCountForFivePoint,
            );
        }

        let poses = if num_points == 5 {
            let mut points1 = [[0.0; 2]; 5];
            let mut points2 = [[0.0; 2]; 5];

            for (i, corr) in correspondences.iter().enumerate() {
                points1[i] = [corr.camera_a.x, corr.camera_a.y];
                points2[i] = [corr.camera_b.x, corr.camera_b.y];
            }

            use crate::camera_essential_matrix::five_point::solve::five_point_relative_pose;
            five_point_relative_pose(&points1, &points2)
                .map_err(|_e| CameraEssentialMatrixError::NoValidSolution)?
        } else {
            let mut points1 = Vec::with_capacity(num_points);
            let mut points2 = Vec::with_capacity(num_points);

            for corr in correspondences.iter() {
                points1.push((corr.camera_a.x, corr.camera_a.y));
                points2.push((corr.camera_b.x, corr.camera_b.y));
            }

            use crate::camera_essential_matrix::five_point::solve::five_point_relative_pose_overdetermined;
            five_point_relative_pose_overdetermined(&points1, &points2)
                .map_err(|_e| CameraEssentialMatrixError::NoValidSolution)?
        };

        // Convert poses to essential matrices: E = [t]_x * R
        let mut essential_matrices = Vec::new();

        for pose in poses {
            let t = pose.translation;
            let t_skew =
                Matrix3::new(0.0, -t.z, t.y, t.z, 0.0, -t.x, -t.y, t.x, 0.0);
            let essential = t_skew * pose.rotation;

            let norm = essential.norm();
            if norm > 1e-10 {
                let normalized = essential / norm;
                if is_valid_essential_matrix(&normalized) {
                    essential_matrices.push(normalized);
                }
            }
        }

        if essential_matrices.is_empty() {
            return Err(CameraEssentialMatrixError::NoValidSolution);
        }

        select_best_candidate_by_angular_error_dynamic(
            &essential_matrices,
            correspondences,
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::datatype::CameraCoordValue;

    #[test]
    fn test_workspace_creation() {
        let _workspace = EssentialMatrixFivePointWorkspace::new();
    }

    #[test]
    fn test_workspace_trait() {
        let mut workspace = EssentialMatrixFivePointWorkspace::new();
        workspace.clear();

        let result = workspace.reuse_with(|ws| {
            ws.clear();
            42
        });

        assert_eq!(result, 42);
    }

    #[test]
    fn test_invalid_point_count() {
        let mut workspace = EssentialMatrixFivePointWorkspace::new();

        // Test with 4 points (should fail)
        let correspondences = vec![
            BearingVectorCorrespondence::new(
                CameraCoordValue::vector2(-0.5, -0.5),
                CameraCoordValue::vector2(-0.4, -0.6),
            ),
            BearingVectorCorrespondence::new(
                CameraCoordValue::vector2(0.5, -0.5),
                CameraCoordValue::vector2(0.4, -0.6),
            ),
            BearingVectorCorrespondence::new(
                CameraCoordValue::vector2(-0.5, 0.5),
                CameraCoordValue::vector2(-0.4, 0.4),
            ),
            BearingVectorCorrespondence::new(
                CameraCoordValue::vector2(0.5, 0.5),
                CameraCoordValue::vector2(0.4, 0.4),
            ),
        ];

        let result = workspace.compute_essential_matrices(&correspondences);
        assert!(result.is_err());
    }
}
