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
use nalgebra::{Matrix3, SMatrix, SVector, Vector3};

use crate::camera_essential_matrix::common::{
    build_constraint_matrix_bearing_vectors_static,
    enforce_essential_matrix_constraints, validate_correspondences_homogeneous,
    CameraEssentialMatrixError, EssentialMatrixWorkspace,
};
use crate::datatype::BearingVectorCorrespondence;

type Matrix9<T> = SMatrix<T, 9, 9>;
type Vector9<T> = SVector<T, 9>;

const MAX_CORRESPONDENCES: usize = 1000;
type ConstraintMatrix<T> = SMatrix<T, MAX_CORRESPONDENCES, 9>;

/// Pre-allocated workspace for the 8-point essential matrix algorithm.
///
/// Reuse this across multiple calls to avoid runtime allocations.
/// Supports up to `MAX_CORRESPONDENCES` (1000) point correspondences.
pub struct EssentialMatrixEightPointWorkspace {
    constraint_matrix: ConstraintMatrix<f64>,
    ata_matrix: Matrix9<f64>,
    eigenvalues: Vector9<f64>,
    eigenvectors: Matrix9<f64>,
    svd_u: Matrix3<f64>,
    svd_vt: Matrix3<f64>,
    singular_values: Vector3<f64>,
    temp_essential: Matrix3<f64>,
    corrected_singular_values: Vector3<f64>,
    diagonal_matrix: Matrix3<f64>,
}

impl EssentialMatrixWorkspace for EssentialMatrixEightPointWorkspace {
    fn new() -> Self {
        Self {
            constraint_matrix: ConstraintMatrix::zeros(),
            ata_matrix: Matrix9::zeros(),
            eigenvalues: Vector9::zeros(),
            eigenvectors: Matrix9::zeros(),
            svd_u: Matrix3::zeros(),
            svd_vt: Matrix3::zeros(),
            singular_values: Vector3::zeros(),
            temp_essential: Matrix3::zeros(),
            corrected_singular_values: Vector3::zeros(),
            diagonal_matrix: Matrix3::zeros(),
        }
    }

    fn clear(&mut self) {
        self.constraint_matrix.fill(0.0);
        self.ata_matrix.fill(0.0);
        self.eigenvalues.fill(0.0);
        self.eigenvectors.fill(0.0);
        self.svd_u.fill(0.0);
        self.svd_vt.fill(0.0);
        self.singular_values.fill(0.0);
        self.temp_essential.fill(0.0);
        self.corrected_singular_values.fill(0.0);
        self.diagonal_matrix.fill(0.0);
    }

    fn reuse_with<F, R>(&mut self, f: F) -> R
    where
        F: FnOnce(&mut Self) -> R,
    {
        self.clear();
        f(self)
    }
}

impl EssentialMatrixEightPointWorkspace {
    pub fn new() -> Self {
        <Self as EssentialMatrixWorkspace>::new()
    }

    fn check_capacity(&self, num_correspondences: usize) {
        assert!(
            num_correspondences <= MAX_CORRESPONDENCES,
            "Workspace can handle at most {} correspondences, got {}",
            MAX_CORRESPONDENCES,
            num_correspondences
        );
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
}

impl EssentialMatrixEightPointWorkspace {
    fn build_constraint_matrix(
        &mut self,
        correspondences: &[BearingVectorCorrespondence],
    ) -> Result<(), CameraEssentialMatrixError> {
        let n_points = correspondences.len();
        assert!(n_points > 0, "Need at least one correspondence");
        self.check_capacity(n_points);

        build_constraint_matrix_bearing_vectors_static::<MAX_CORRESPONDENCES>(
            correspondences,
            &mut self.constraint_matrix,
        )
        .map_err(|_| CameraEssentialMatrixError::SingularMatrix)
    }

    /// Compute essential matrix using the 8-point algorithm.
    ///
    /// Requires exactly 8 point correspondences.
    pub fn compute_essential_matrix(
        &mut self,
        correspondences: &[BearingVectorCorrespondence],
    ) -> Result<Matrix3<f64>, CameraEssentialMatrixError> {
        validate_correspondences_homogeneous(correspondences)?;

        let num_points = 8;
        if correspondences.len() != num_points {
            return Err(
                CameraEssentialMatrixError::InsufficientPointsForEightPoint,
            );
        }

        self.build_constraint_matrix(&correspondences)?;

        // Find the null space of A by computing the smallest eigenvector of A^T*A.
        let constraint_view = self.constraint_matrix.rows(0, num_points);
        self.ata_matrix.gemm(
            1.0,
            &constraint_view.transpose(),
            &constraint_view,
            0.0,
        );

        assert_eq!(self.ata_matrix.nrows(), 9, "A^T * A must be 9x9");
        assert_eq!(self.ata_matrix.ncols(), 9, "A^T * A must be 9x9");

        let eigen_result = self.ata_matrix.symmetric_eigen();
        self.eigenvalues.copy_from(&eigen_result.eigenvalues);
        self.eigenvectors.copy_from(&eigen_result.eigenvectors);

        assert_eq!(self.eigenvalues.len(), 9, "Must have 9 eigenvalues");
        assert_eq!(
            self.eigenvectors.nrows(),
            9,
            "Eigenvectors matrix must be 9x9"
        );
        assert_eq!(
            self.eigenvectors.ncols(),
            9,
            "Eigenvectors matrix must be 9x9"
        );

        let mut min_idx = 0;
        let mut min_val = self.eigenvalues[0];
        for (i, &val) in self.eigenvalues.iter().enumerate() {
            if val < min_val {
                min_val = val;
                min_idx = i;
            }
        }

        let solution = self.eigenvectors.column(min_idx);

        if solution.norm() < 1e-12 {
            return Err(CameraEssentialMatrixError::SingularMatrix);
        }

        self.temp_essential = Matrix3::from_row_slice(solution.as_slice());
        self.temp_essential =
            enforce_essential_matrix_constraints(&self.temp_essential)?;

        let final_essential = if self.temp_essential.norm() > 1e-12 {
            self.temp_essential / self.temp_essential.norm()
        } else {
            return Err(CameraEssentialMatrixError::SingularMatrix);
        };

        Ok(final_essential)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::camera_essential_matrix::common::calculate_average_angular_error;
    use crate::datatype::camera_pose::CameraPose;
    use crate::datatype::CameraCoordValue;
    use nalgebra::{Point3, Rotation3, Vector3};

    fn create_test_correspondences() -> Vec<BearingVectorCorrespondence> {
        vec![
            BearingVectorCorrespondence::from_homogeneous_coordinates(
                CameraCoordValue::vector2(-0.5, -0.5),
                CameraCoordValue::vector2(-0.4, -0.6),
            ),
            BearingVectorCorrespondence::from_homogeneous_coordinates(
                CameraCoordValue::vector2(0.5, -0.5),
                CameraCoordValue::vector2(0.4, -0.6),
            ),
            BearingVectorCorrespondence::from_homogeneous_coordinates(
                CameraCoordValue::vector2(-0.5, 0.5),
                CameraCoordValue::vector2(-0.4, 0.4),
            ),
            BearingVectorCorrespondence::from_homogeneous_coordinates(
                CameraCoordValue::vector2(0.5, 0.5),
                CameraCoordValue::vector2(0.4, 0.4),
            ),
            BearingVectorCorrespondence::from_homogeneous_coordinates(
                CameraCoordValue::vector2(0.0, 0.0),
                CameraCoordValue::vector2(0.05, 0.02),
            ),
            BearingVectorCorrespondence::from_homogeneous_coordinates(
                CameraCoordValue::vector2(0.2, 0.3),
                CameraCoordValue::vector2(0.25, 0.35),
            ),
            BearingVectorCorrespondence::from_homogeneous_coordinates(
                CameraCoordValue::vector2(-0.3, 0.2),
                CameraCoordValue::vector2(-0.25, 0.25),
            ),
            BearingVectorCorrespondence::from_homogeneous_coordinates(
                CameraCoordValue::vector2(0.4, -0.2),
                CameraCoordValue::vector2(0.45, -0.15),
            ),
        ]
    }

    #[test]
    fn test_synthetic_ground_truth() {
        let rotation = Rotation3::from_axis_angle(&Vector3::y_axis(), 0.1);
        let translation = Vector3::new(0.5, 0.1, -0.2).normalize();
        let known_essential = rotation * translation.cross_matrix();

        let points_3d = vec![
            Point3::new(0.2, 0.3, -5.0),
            Point3::new(-0.5, 0.8, -6.0),
            Point3::new(0.8, -0.2, -7.0),
            Point3::new(-0.1, -0.5, -8.0),
            Point3::new(1.2, 1.3, -9.0),
            Point3::new(-1.5, -0.8, -10.0),
            Point3::new(1.8, -1.2, -11.0),
            Point3::new(-1.1, 1.5, -12.0),
        ];

        let cam1_pose = CameraPose::default();
        let cam2_pose = CameraPose::new(rotation.into(), translation.into());

        let correspondences: Vec<_> = points_3d
            .iter()
            .map(|p| {
                let p_cam1 = cam1_pose.rotation() * (p - cam1_pose.center());
                let p_cam2 = cam2_pose.rotation() * (p - cam2_pose.center());
                BearingVectorCorrespondence::from_homogeneous_coordinates(
                    CameraCoordValue::vector2(
                        p_cam1.x / p_cam1.z,
                        p_cam1.y / p_cam1.z,
                    ),
                    CameraCoordValue::vector2(
                        p_cam2.x / p_cam2.z,
                        p_cam2.y / p_cam2.z,
                    ),
                )
            })
            .collect();

        let mut workspace = EssentialMatrixEightPointWorkspace::new();
        let computed_essential = workspace
            .compute_essential_matrix(&correspondences)
            .unwrap();

        let e1_normalized = computed_essential / computed_essential.norm();
        let e2_normalized = known_essential / known_essential.norm();

        let diff = (e1_normalized - e2_normalized).norm();
        let diff_neg = (e1_normalized + e2_normalized).norm();

        assert!(
            diff.min(diff_neg) < 1e-5,
            "Computed essential matrix should match ground truth"
        );
    }

    #[test]
    fn test_insufficient_points() {
        let correspondences = create_test_correspondences();
        let mut workspace = EssentialMatrixEightPointWorkspace::new();
        let result = workspace.compute_essential_matrix(&correspondences[..3]);
        assert!(matches!(
            result,
            Err(CameraEssentialMatrixError::InsufficientPointsForEightPoint)
        ));
    }

    #[test]
    fn test_epipolar_constraint() {
        let correspondences = create_test_correspondences();
        let mut workspace = EssentialMatrixEightPointWorkspace::new();
        let essential_matrix = workspace
            .compute_essential_matrix(&correspondences)
            .unwrap();

        for corr in &correspondences {
            let constraint_value =
                corr.camera_b.transpose() * &essential_matrix * &corr.camera_a;
            assert!(
                constraint_value[(0, 0)].abs() < 0.2,
                "Epipolar constraint should be satisfied"
            );
        }
    }

    #[test]
    fn test_essential_matrix_properties() {
        let correspondences = create_test_correspondences();
        let mut workspace = EssentialMatrixEightPointWorkspace::new();
        let essential_matrix = workspace
            .compute_essential_matrix(&correspondences)
            .unwrap();

        assert!(
            essential_matrix.determinant().abs() < 1e-8,
            "Essential matrix determinant should be zero"
        );

        let svd = essential_matrix.svd(false, false);
        let sv = svd.singular_values;
        assert!(
            (sv[0] - sv[1]).abs() < 1e-8,
            "First two singular values should be equal"
        );
        assert!(sv[2].abs() < 1e-8, "Third singular value should be zero");
    }

    #[test]
    fn test_degenerate_motion() {
        let correspondences = (0..8)
            .map(|i| {
                let x = -0.5 + (i as f64 * 0.15);
                let y = -0.5 + (i as f64 * 0.2);
                BearingVectorCorrespondence::from_homogeneous_coordinates(
                    CameraCoordValue::vector2(x, y),
                    CameraCoordValue::vector2(x, y),
                )
            })
            .collect::<Vec<_>>();

        let mut workspace = EssentialMatrixEightPointWorkspace::new();
        let result = workspace.compute_essential_matrix(&correspondences);

        if let Err(e) = result {
            assert!(matches!(e, CameraEssentialMatrixError::SingularMatrix));
        }
    }

    #[test]
    fn test_pure_translation() {
        let rotation = Rotation3::identity();
        let translation = Vector3::new(0.5, 0.0, 0.0);
        let known_essential = rotation * translation.cross_matrix();

        let points_3d = vec![
            Point3::new(0.2, 0.3, -5.0),
            Point3::new(-0.5, 0.8, -6.0),
            Point3::new(0.8, -0.2, -7.0),
            Point3::new(-0.1, -0.5, -8.0),
            Point3::new(1.2, 1.3, -9.0),
            Point3::new(-1.5, -0.8, -10.0),
            Point3::new(1.8, -1.2, -11.0),
            Point3::new(-1.1, 1.5, -12.0),
        ];

        let cam1_pose = CameraPose::default();
        let cam2_pose = CameraPose::new(rotation.into(), translation.into());

        let correspondences: Vec<_> = points_3d
            .iter()
            .map(|p| {
                let p_cam1 = cam1_pose.rotation() * (p - cam1_pose.center());
                let p_cam2 = cam2_pose.rotation() * (p - cam2_pose.center());
                BearingVectorCorrespondence::from_homogeneous_coordinates(
                    CameraCoordValue::vector2(
                        p_cam1.x / p_cam1.z,
                        p_cam1.y / p_cam1.z,
                    ),
                    CameraCoordValue::vector2(
                        p_cam2.x / p_cam2.z,
                        p_cam2.y / p_cam2.z,
                    ),
                )
            })
            .collect();

        let mut workspace = EssentialMatrixEightPointWorkspace::new();
        let essential_matrix = workspace
            .compute_essential_matrix(&correspondences)
            .unwrap();

        // For pure translation, E should be anti-symmetric: E + E^T ≈ 0.
        let transpose = essential_matrix.transpose();
        let antisymmetric_test = &essential_matrix + &transpose;
        assert!(
            antisymmetric_test.norm() < 1e-5,
            "Essential matrix should be anti-symmetric for pure translation, got norm {}",
            antisymmetric_test.norm()
        );

        let e1_normalized = essential_matrix / essential_matrix.norm();
        let e2_normalized = known_essential / known_essential.norm();

        let diff = (e1_normalized - e2_normalized).norm();
        let diff_neg = (e1_normalized + e2_normalized).norm();

        assert!(
            diff.min(diff_neg) < 1e-5,
            "Computed essential matrix should match ground truth for pure translation"
        );
    }

    #[test]
    fn test_colinear_points() {
        let correspondences = (0..8)
            .map(|i| {
                let x = -1.0 + (i as f64 * 0.2);
                BearingVectorCorrespondence::from_homogeneous_coordinates(
                    CameraCoordValue::vector2(x, 0.0),
                    CameraCoordValue::vector2(x + 0.1, 0.0),
                )
            })
            .collect::<Vec<_>>();

        let mut workspace = EssentialMatrixEightPointWorkspace::new();
        let result = workspace.compute_essential_matrix(&correspondences);

        if let Ok(essential_matrix) = result {
            assert!(
                essential_matrix.determinant().abs() < 1e-6,
                "Determinant should be near-zero"
            );
        }
    }

    #[test]
    fn test_planar_scene() {
        let correspondences = create_test_correspondences();
        let mut workspace = EssentialMatrixEightPointWorkspace::new();
        let result = workspace.compute_essential_matrix(&correspondences);
        assert!(result.is_ok(), "Planar scene should still produce a result");

        let essential_matrix = result.unwrap();
        assert!(
            essential_matrix.determinant().abs() < 1e-6,
            "Determinant should be near-zero"
        );
    }

    #[test]
    fn test_gaussian_noise_robustness() {
        let correspondences = create_test_correspondences();
        let noise_level = 0.01;

        let noisy_correspondences: Vec<_> = correspondences
            .iter()
            .enumerate()
            .map(|(i, corr)| {
                let noise_factor = (i as f64 * 0.123).sin() * noise_level;
                BearingVectorCorrespondence::from_homogeneous_coordinates(
                    CameraCoordValue::vector2(
                        corr.camera_a.x + noise_factor,
                        corr.camera_a.y + noise_factor * 0.7,
                    ),
                    CameraCoordValue::vector2(
                        corr.camera_b.x + noise_factor * 0.9,
                        corr.camera_b.y + noise_factor * 1.1,
                    ),
                )
            })
            .collect();

        let mut workspace = EssentialMatrixEightPointWorkspace::new();
        let result = workspace.compute_essential_matrix(&noisy_correspondences);
        assert!(
            result.is_ok(),
            "Algorithm should be robust to moderate noise"
        );

        let essential_matrix = result.unwrap();
        let avg_error = calculate_average_angular_error(
            &essential_matrix,
            &noisy_correspondences,
        );
        assert!(
            avg_error < 0.5,
            "Average angular error should be reasonable with noise"
        );
    }
}
