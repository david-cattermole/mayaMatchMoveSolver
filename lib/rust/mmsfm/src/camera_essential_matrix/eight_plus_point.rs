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
use nalgebra::{DMatrix, DVector, Matrix3};

use crate::camera_essential_matrix::common::{
    build_constraint_matrix_bearing_vectors,
    validate_correspondences_homogeneous, CameraEssentialMatrixError,
    EssentialMatrixWorkspace,
};
use crate::datatype::BearingVectorCorrespondence;

/// Pre-allocated workspace for the N-point (8+) essential matrix algorithm.
///
/// Uses direct SVD on the constraint matrix for better numerical stability
/// with overdetermined systems. Suitable for N >= 8, optimal for N >= 30.
///
/// Reuse this across multiple calls to avoid runtime allocations.
pub struct EssentialMatrixEightPlusPointWorkspace {
    constraint_matrix: DMatrix<f64>,
    ata_matrix: DMatrix<f64>,
    eigenvectors: DMatrix<f64>,
    eigenvalues: DVector<f64>,
    essential_matrix: Matrix3<f64>,
    max_correspondences: usize,
}

impl EssentialMatrixWorkspace for EssentialMatrixEightPlusPointWorkspace {
    fn new() -> Self {
        Self::new_with_capacity(100)
    }

    fn clear(&mut self) {
        self.clear()
    }

    fn reuse_with<F, R>(&mut self, f: F) -> R
    where
        F: FnOnce(&mut Self) -> R,
    {
        self.reuse_with(f)
    }
}

impl EssentialMatrixEightPlusPointWorkspace {
    /// Create a new workspace supporting up to `max_correspondences` points.
    pub fn new_with_capacity(max_correspondences: usize) -> Self {
        assert!(
            max_correspondences >= 8,
            "Need at least 8 correspondences for overdetermined system"
        );

        Self {
            constraint_matrix: DMatrix::zeros(max_correspondences, 9),
            ata_matrix: DMatrix::zeros(9, 9),
            eigenvectors: DMatrix::zeros(9, 9),
            eigenvalues: DVector::zeros(9),
            essential_matrix: Matrix3::zeros(),
            max_correspondences,
        }
    }

    pub fn clear(&mut self) {
        self.constraint_matrix.fill(0.0);
        self.ata_matrix.fill(0.0);
        self.eigenvectors.fill(0.0);
        self.eigenvalues.fill(0.0);
        self.essential_matrix.fill(0.0);
    }

    pub fn reuse_with<F, R>(&mut self, f: F) -> R
    where
        F: FnOnce(&mut Self) -> R,
    {
        self.clear();
        f(self)
    }
}

impl EssentialMatrixEightPlusPointWorkspace {
    fn build_constraint_matrix(
        &mut self,
        correspondences: &[BearingVectorCorrespondence],
    ) -> Result<(), CameraEssentialMatrixError> {
        build_constraint_matrix_bearing_vectors(
            correspondences,
            &mut self.constraint_matrix,
        )
        .map_err(|_| CameraEssentialMatrixError::SingularMatrix)
    }

    fn solve_dlt_system(
        &mut self,
        n_points: usize,
    ) -> Result<(), CameraEssentialMatrixError> {
        let a_view = self.constraint_matrix.view((0, 0), (n_points, 9));

        // Use direct SVD on A. The solution is the right singular vector
        // corresponding to the smallest singular value (last row of V^T).
        let svd = a_view.svd(false, true);

        let v_t = match svd.v_t {
            Some(m) => m,
            None => return Err(CameraEssentialMatrixError::SingularMatrix),
        };

        let solution = v_t.row(v_t.nrows() - 1).transpose();

        if solution.norm() < 1e-12 {
            return Err(CameraEssentialMatrixError::SingularMatrix);
        }

        self.essential_matrix[(0, 0)] = solution[0];
        self.essential_matrix[(0, 1)] = solution[1];
        self.essential_matrix[(0, 2)] = solution[2];
        self.essential_matrix[(1, 0)] = solution[3];
        self.essential_matrix[(1, 1)] = solution[4];
        self.essential_matrix[(1, 2)] = solution[5];
        self.essential_matrix[(2, 0)] = solution[6];
        self.essential_matrix[(2, 1)] = solution[7];
        self.essential_matrix[(2, 2)] = solution[8];

        Ok(())
    }

    /// Compute essential matrix using the N-point DLT algorithm.
    ///
    /// Requires at least 8 correspondences (pre-normalised externally for best results).
    pub fn compute_essential_matrix(
        &mut self,
        correspondences: &[BearingVectorCorrespondence],
    ) -> Result<Matrix3<f64>, CameraEssentialMatrixError> {
        validate_correspondences_homogeneous(correspondences)?;

        if correspondences.len() < 8 {
            return Err(
                CameraEssentialMatrixError::InsufficientPointsForEightPoint,
            );
        }

        if correspondences.len() > self.max_correspondences {
            return Err(CameraEssentialMatrixError::InvalidInput);
        }

        self.build_constraint_matrix(correspondences)?;
        self.solve_dlt_system(correspondences.len())?;

        let final_essential = if self.essential_matrix.norm() > 1e-12 {
            self.essential_matrix / self.essential_matrix.norm()
        } else {
            return Err(CameraEssentialMatrixError::SingularMatrix);
        };

        Ok(final_essential)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::camera_essential_matrix::common::{
        apply_hartley_transform_to_points, calculate_average_angular_error,
        compute_hartley_normalization_transform,
    };
    use crate::datatype::CameraCoordValue;
    use nalgebra::Vector3;

    #[test]
    fn test_normalized_dlt_with_30_points() {
        let mut correspondences = Vec::new();
        for i in 0..30 {
            let angle = (i as f64) * std::f64::consts::PI * 2.0 / 30.0;
            let radius = 0.5 + 0.1 * (i as f64 / 30.0);
            correspondences.push(
                BearingVectorCorrespondence::from_homogeneous_coordinates(
                    CameraCoordValue::vector2(
                        angle.cos() * radius,
                        angle.sin() * radius,
                    ),
                    CameraCoordValue::vector2(
                        angle.cos() * radius * 0.9 + 0.1,
                        angle.sin() * radius * 0.9,
                    ),
                ),
            );
        }

        let points_a: Vec<Vector3<f64>> = correspondences
            .iter()
            .map(|c| Vector3::new(c.camera_a.x, c.camera_a.y, c.camera_a.z))
            .collect();
        let points_b: Vec<Vector3<f64>> = correspondences
            .iter()
            .map(|c| Vector3::new(c.camera_b.x, c.camera_b.y, c.camera_b.z))
            .collect();

        let transform_a = compute_hartley_normalization_transform(&points_a);
        let transform_b = compute_hartley_normalization_transform(&points_b);

        let normalized_points_a =
            apply_hartley_transform_to_points(&points_a, &transform_a);
        let normalized_points_b =
            apply_hartley_transform_to_points(&points_b, &transform_b);

        let normalized_correspondences: Vec<BearingVectorCorrespondence> =
            normalized_points_a
                .iter()
                .zip(normalized_points_b.iter())
                .map(|(a, b)| BearingVectorCorrespondence {
                    camera_a: *a,
                    camera_b: *b,
                })
                .collect();

        let mut workspace =
            EssentialMatrixEightPlusPointWorkspace::new_with_capacity(50);
        let result =
            workspace.compute_essential_matrix(&normalized_correspondences);
        assert!(result.is_ok());

        let normalized_essential_matrix = result.unwrap();

        let essential_matrix =
            transform_b.transpose() * normalized_essential_matrix * transform_a;

        let essential_matrix =
            crate::camera_essential_matrix::enforce_essential_matrix_constraints(
                &essential_matrix,
            )
            .unwrap();

        let det = essential_matrix.determinant();
        assert!(det.abs() < 1e-6, "Determinant should be near zero: {}", det);

        let svd = essential_matrix.svd(false, false);
        let sv = svd.singular_values;

        assert!(
            (sv[0] - sv[1]).abs() < 1e-6,
            "First two singular values should be equal: {} vs {}",
            sv[0],
            sv[1]
        );

        assert!(
            sv[2].abs() < 1e-6,
            "Third singular value should be zero: {}",
            sv[2]
        );

        let avg_error = calculate_average_angular_error(
            &essential_matrix,
            &correspondences,
        );
        assert!(
            avg_error < 0.1,
            "Average angular error should be low: {}",
            avg_error
        );
    }

    #[test]
    fn test_increasing_point_counts() {
        let base_correspondences: Vec<_> = (0..50)
            .map(|i| {
                let angle = (i as f64) * std::f64::consts::PI * 2.0 / 50.0;
                BearingVectorCorrespondence::from_homogeneous_coordinates(
                    CameraCoordValue::vector2(
                        angle.cos() * 0.5,
                        angle.sin() * 0.5,
                    ),
                    CameraCoordValue::vector2(
                        angle.cos() * 0.45 + 0.05,
                        angle.sin() * 0.45,
                    ),
                )
            })
            .collect();

        let points_a: Vec<Vector3<f64>> = base_correspondences
            .iter()
            .map(|c| Vector3::new(c.camera_a.x, c.camera_a.y, c.camera_a.z))
            .collect();
        let points_b: Vec<Vector3<f64>> = base_correspondences
            .iter()
            .map(|c| Vector3::new(c.camera_b.x, c.camera_b.y, c.camera_b.z))
            .collect();

        let transform_a = compute_hartley_normalization_transform(&points_a);
        let transform_b = compute_hartley_normalization_transform(&points_b);

        let normalized_points_a =
            apply_hartley_transform_to_points(&points_a, &transform_a);
        let normalized_points_b =
            apply_hartley_transform_to_points(&points_b, &transform_b);

        let normalized_correspondences: Vec<BearingVectorCorrespondence> =
            normalized_points_a
                .iter()
                .zip(normalized_points_b.iter())
                .map(|(a, b)| BearingVectorCorrespondence {
                    camera_a: *a,
                    camera_b: *b,
                })
                .collect();

        let mut workspace =
            EssentialMatrixEightPlusPointWorkspace::new_with_capacity(100);

        for n in &[8, 20, 30, 40] {
            let correspondences = &normalized_correspondences[..*n];
            let result = workspace
                .reuse_with(|ws| ws.compute_essential_matrix(correspondences));

            assert!(result.is_ok(), "Should succeed with {} points", n);

            let normalized_essential_matrix = result.unwrap();

            let essential_matrix = transform_b.transpose()
                * normalized_essential_matrix
                * transform_a;

            let essential_matrix =
                crate::camera_essential_matrix::enforce_essential_matrix_constraints(
                    &essential_matrix,
                )
                .unwrap();

            let avg_error = calculate_average_angular_error(
                &essential_matrix,
                &base_correspondences[..*n],
            );

            assert!(
                avg_error < 0.2,
                "Angular error with {} points should be reasonable: {}",
                n,
                avg_error
            );
        }
    }

    #[test]
    fn test_workspace_reuse() {
        let mut workspace =
            EssentialMatrixEightPlusPointWorkspace::new_with_capacity(40);

        let correspondences: Vec<_> = (0..20)
            .map(|i| {
                let angle = (i as f64) * std::f64::consts::PI / 10.0;
                BearingVectorCorrespondence::from_homogeneous_coordinates(
                    CameraCoordValue::vector2(
                        angle.cos() * 0.4,
                        angle.sin() * 0.4,
                    ),
                    CameraCoordValue::vector2(
                        angle.cos() * 0.38 + 0.08,
                        angle.sin() * 0.38,
                    ),
                )
            })
            .collect();

        let points_a: Vec<Vector3<f64>> = correspondences
            .iter()
            .map(|c| Vector3::new(c.camera_a.x, c.camera_a.y, c.camera_a.z))
            .collect();
        let points_b: Vec<Vector3<f64>> = correspondences
            .iter()
            .map(|c| Vector3::new(c.camera_b.x, c.camera_b.y, c.camera_b.z))
            .collect();

        let transform_a = compute_hartley_normalization_transform(&points_a);
        let transform_b = compute_hartley_normalization_transform(&points_b);

        let normalized_points_a =
            apply_hartley_transform_to_points(&points_a, &transform_a);
        let normalized_points_b =
            apply_hartley_transform_to_points(&points_b, &transform_b);

        let normalized_correspondences: Vec<BearingVectorCorrespondence> =
            normalized_points_a
                .iter()
                .zip(normalized_points_b.iter())
                .map(|(a, b)| BearingVectorCorrespondence {
                    camera_a: *a,
                    camera_b: *b,
                })
                .collect();

        for _ in 0..3 {
            let result = workspace.reuse_with(|ws| {
                ws.compute_essential_matrix(&normalized_correspondences)
            });

            assert!(result.is_ok());
            let normalized_essential_matrix = result.unwrap();

            let essential_matrix = transform_b.transpose()
                * normalized_essential_matrix
                * transform_a;

            let essential_matrix =
                crate::camera_essential_matrix::enforce_essential_matrix_constraints(
                    &essential_matrix,
                )
                .unwrap();

            let det = essential_matrix.determinant();
            assert!(det.abs() < 1e-6);
        }
    }
}
