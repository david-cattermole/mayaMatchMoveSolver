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

use crate::datatype::camera_film_back::CameraFilmBack;
use crate::datatype::common::UnitValue;
use crate::datatype::millimeter_unit::MillimeterUnit;
use crate::datatype::ndc_value::{NdcPoint2, NdcValue};

/// Camera intrinsics in normalized coordinate space
#[derive(Debug, Clone, PartialEq)]
pub struct CameraIntrinsics {
    /// Focal length in X direction, normalized by film back width:
    /// (focal_length_mm / film_back_width_mm).
    pub focal_length_x: f64,
    /// Focal length in Y direction, normalized by film back height:
    /// (focal_length_mm / film_back_height_mm).
    pub focal_length_y: f64,
    /// Principal point in NDC coordinates where (0,0) is center,
    /// range [-1.0, 1.0] where -1.0 represents the left-most or
    /// bottom most corner, and +1.0 represents the right-most or
    /// top-most corner.
    pub principal_point: NdcPoint2<f64>,
    /// Physical film back dimensions for FoV and aspect ratio
    /// calculations.
    pub film_back: CameraFilmBack<f64>,
}

impl CameraIntrinsics {
    /// Create camera intrinsics from physical parameters.
    ///
    /// This method derives the normalized intrinsic parameters from
    /// physical measurements:
    /// - The focal length in millimeters
    /// - The lens center position relative to the film back center
    /// - The film back (sensor) dimensions
    ///
    /// All calculations are performed in millimeters, with
    /// normalization based on the film back dimensions.
    ///
    /// # Coordinate System
    /// The lens center coordinates are relative to the film back
    /// center, where:
    /// - (0, 0) = center of the film back
    /// - (-film_back_width * 0.5, 0) = left edge of film back
    /// - (+film_back_width * 0.5, 0) = right edge of film back
    /// - (0, -film_back_height * 0.5) = bottom edge of film back
    /// - (0, +film_back_height * 0.5) = top edge of film back
    ///
    /// # Arguments
    /// * `focal_length_mm` - Focal length in millimeters.
    /// * `lens_center_x_mm` - Lens center X offset from film back center in millimeters.
    /// * `lens_center_y_mm` - Lens center Y offset from film back center in millimeters.
    /// * `film_back` - Physical sensor dimensions.
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// // Full-frame 35mm sensor with 50mm lens
    /// let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
    /// let focal_length = MillimeterUnit::new(50.0);
    /// let lens_center_x = MillimeterUnit::new(0.0); // Centered
    /// let lens_center_y = MillimeterUnit::new(0.0); // Centered
    ///
    /// let intrinsics = CameraIntrinsics::from_physical_parameters(
    ///     focal_length,
    ///     lens_center_x,
    ///     lens_center_y,
    ///     film_back
    /// );
    /// ```
    pub fn from_physical_parameters(
        focal_length_mm: MillimeterUnit<f64>,
        lens_center_x_mm: MillimeterUnit<f64>,
        lens_center_y_mm: MillimeterUnit<f64>,
        film_back: CameraFilmBack<f64>,
    ) -> Self {
        // Normalize focal lengths by film back dimensions.
        let focal_length_x = focal_length_mm.value() / film_back.width.value();
        let focal_length_y = focal_length_mm.value() / film_back.height.value();

        // Convert lens center from film back coordinates to NDC coordinates.
        //
        // In NDC space, (0,0) is the center, and the range is [-1.0, 1.0].
        //
        // lens_center is relative to film back center, so we
        // normalize by film back dimensions and scale by 2.
        let principal_point = NdcPoint2::new(
            NdcValue::new(
                (2.0 * lens_center_x_mm.value()) / film_back.width.value(),
            ),
            NdcValue::new(
                (2.0 * lens_center_y_mm.value()) / film_back.height.value(),
            ),
        );

        Self {
            focal_length_x,
            focal_length_y,
            principal_point,
            film_back,
        }
    }

    /// Create camera intrinsics with lens center at film back center.
    ///
    /// This is a convenience method for the common case where the lens center
    /// aligns with the center of the film back/sensor. The principal point will
    /// be at NDC coordinates (0.0, 0.0).
    ///
    /// # Arguments
    /// * `focal_length_mm` - Focal length in millimeters
    /// * `film_back` - Physical sensor dimensions
    pub fn from_centered_lens(
        focal_length_mm: MillimeterUnit<f64>,
        film_back: CameraFilmBack<f64>,
    ) -> Self {
        Self::from_physical_parameters(
            focal_length_mm,
            MillimeterUnit::new(0.0), // Centered X
            MillimeterUnit::new(0.0), // Centered Y
            film_back,
        )
    }

    /// Convert normalized intrinsics back to physical parameters.
    ///
    /// This method reconstructs the physical parameters from the normalized
    /// intrinsics, given the film back dimensions.
    ///
    /// # Arguments
    /// * `film_back` - Physical sensor dimensions
    ///
    /// # Returns
    /// A tuple containing (focal_length_mm, lens_center_x_mm, lens_center_y_mm)
    pub fn to_physical_parameters(
        &self,
    ) -> (
        MillimeterUnit<f64>,
        MillimeterUnit<f64>,
        MillimeterUnit<f64>,
    ) {
        // Convert normalized focal length back to millimeters.
        // We use focal_length_x since both should give the same physical focal length.
        let focal_length_mm = MillimeterUnit::new(
            self.focal_length_x * self.film_back.width.value(),
        );

        // Convert NDC principal point back to lens center coordinates.
        //
        // In NDC space, (0,0) is center with range [-1,1], so we
        // scale by film back dimensions and divide by 2.
        let lens_center_x_mm = MillimeterUnit::new(
            self.principal_point.x.value() * self.film_back.width.value() * 0.5,
        );
        let lens_center_y_mm = MillimeterUnit::new(
            self.principal_point.y.value()
                * self.film_back.height.value()
                * 0.5,
        );

        (focal_length_mm, lens_center_x_mm, lens_center_y_mm)
    }

    /// Calculate the horizontal focal length in millimeters.
    ///
    /// # Returns
    /// Horizontal focal length in millimeters.
    pub fn horizontal_focal_length_mm(&self) -> MillimeterUnit<f64> {
        MillimeterUnit::new(self.focal_length_x * self.film_back.width.value())
    }

    /// Calculate the vertical focal length in millimeters.
    ///
    /// # Returns
    /// Vertical focal length in millimeters.
    pub fn vertical_focal_length_mm(&self) -> MillimeterUnit<f64> {
        MillimeterUnit::new(self.focal_length_y * self.film_back.height.value())
    }

    /// Calculate the horizontal field of view in radians.
    ///
    /// # Returns
    /// Horizontal field of view angle in radians
    pub fn horizontal_fov_radians(&self) -> f64 {
        // FoV = 2 * arctan(sensor_width / (2 * focal_length))
        //
        // focal_length_x is normalized by width, so we need the actual focal
        // length in mm.
        let focal_length_mm =
            self.focal_length_x * self.film_back.width.value();
        2.0 * (self.film_back.width.value() / (2.0 * focal_length_mm)).atan()
    }

    /// Calculate the horizontal field of view in degrees.
    ///
    /// # Returns
    /// Horizontal field of view angle in degrees
    pub fn horizontal_fov_degrees(&self) -> f64 {
        self.horizontal_fov_radians().to_degrees()
    }

    /// Calculate the vertical field of view in radians.
    ///
    /// # Returns
    /// Vertical field of view angle in radians
    pub fn vertical_fov_radians(&self) -> f64 {
        // FoV = 2 * arctan(sensor_height / (2 * focal_length))
        let focal_length_mm =
            self.focal_length_y * self.film_back.height.value();
        2.0 * (self.film_back.height.value() / (2.0 * focal_length_mm)).atan()
    }

    /// Calculate the vertical field of view in degrees.
    ///
    /// # Returns
    /// Vertical field of view angle in degrees
    pub fn vertical_fov_degrees(&self) -> f64 {
        self.vertical_fov_radians().to_degrees()
    }

    /// Calculate the diagonal field of view in radians.
    ///
    /// # Returns
    /// Diagonal field of view angle in radians
    pub fn diagonal_fov_radians(&self) -> f64 {
        // Calculate diagonal sensor dimension.
        let diagonal_mm = (self.film_back.width.value().powi(2)
            + self.film_back.height.value().powi(2))
        .sqrt();

        // Use horizontal focal length for diagonal calculation.
        let focal_length_mm =
            self.focal_length_x * self.film_back.width.value();
        2.0 * (diagonal_mm / (2.0 * focal_length_mm)).atan()
    }

    /// Calculate the diagonal field of view in degrees.
    ///
    /// # Returns
    /// Diagonal field of view angle in degrees.
    pub fn diagonal_fov_degrees(&self) -> f64 {
        self.diagonal_fov_radians().to_degrees()
    }

    /// Get the aspect ratio of the film back (width / height).
    ///
    /// # Returns
    /// Aspect ratio as width divided by height.
    pub fn aspect_ratio(&self) -> f64 {
        self.film_back.aspect_ratio()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;

    #[test]
    fn test_camera_intrinsics_new() {
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let intrinsics = CameraIntrinsics::from_physical_parameters(
            MillimeterUnit::new(36.0), // 36.0 mm focal length
            MillimeterUnit::new(0.0),  // Centered horizontally
            MillimeterUnit::new(-4.8), // -0.4 * 24.0 * 0.5
            film_back,
        );
        assert_relative_eq!(intrinsics.focal_length_x, 1.0, epsilon = 1e-10);
        assert_relative_eq!(intrinsics.focal_length_y, 1.5, epsilon = 1e-10);
        assert_relative_eq!(
            intrinsics.principal_point.x.value(),
            0.0,
            epsilon = 1e-10
        );
        assert_relative_eq!(
            intrinsics.principal_point.y.value(),
            -0.4,
            epsilon = 1e-10
        );
        assert_eq!(intrinsics.film_back.width.value(), 36.0);
        assert_eq!(intrinsics.film_back.height.value(), 24.0);
    }

    #[test]
    fn test_from_physical_parameters_centered_lens() {
        // Full-frame 35mm sensor with 50mm lens, centered.
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let focal_length = MillimeterUnit::new(50.0);
        let lens_center_x = MillimeterUnit::new(0.0); // Centered
        let lens_center_y = MillimeterUnit::new(0.0); // Centered

        let intrinsics = CameraIntrinsics::from_physical_parameters(
            focal_length,
            lens_center_x,
            lens_center_y,
            film_back,
        );

        // Focal length X normalized: 50mm / 36mm = 1.389
        assert_relative_eq!(
            intrinsics.focal_length_x,
            50.0 / 36.0,
            epsilon = 1e-10
        );

        // Focal length Y normalized: 50mm / 24mm = 2.083
        assert_relative_eq!(
            intrinsics.focal_length_y,
            50.0 / 24.0,
            epsilon = 1e-10
        );

        // Principal point should be at NDC center (0.0, 0.0).
        assert_relative_eq!(
            intrinsics.principal_point.x.value(),
            0.0,
            epsilon = 1e-10
        );
        assert_relative_eq!(
            intrinsics.principal_point.y.value(),
            0.0,
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_from_physical_parameters_offset_lens() {
        // Full-frame 35mm sensor with lens offset to left edge.
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let focal_length = MillimeterUnit::new(50.0);
        let lens_center_x = MillimeterUnit::new(-18.0); // Left edge of film back (-36/2)
        let lens_center_y = MillimeterUnit::new(0.0); // Centered vertically

        let intrinsics = CameraIntrinsics::from_physical_parameters(
            focal_length,
            lens_center_x,
            lens_center_y,
            film_back,
        );

        // Focal length X normalized: 50mm / 36mm = 1.389
        assert_relative_eq!(
            intrinsics.focal_length_x,
            50.0 / 36.0,
            epsilon = 1e-10
        );

        // Focal length Y normalized: 50mm / 24mm = 2.083
        assert_relative_eq!(
            intrinsics.focal_length_y,
            50.0 / 24.0,
            epsilon = 1e-10
        );

        // Principal point X should be at left edge (-1.0 in NDC).
        assert_relative_eq!(
            intrinsics.principal_point.x.value(),
            -1.0,
            epsilon = 1e-10
        );

        // Principal point Y should be at center (0.0 in NDC).
        assert_relative_eq!(
            intrinsics.principal_point.y.value(),
            0.0,
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_from_physical_parameters_right_edge_lens() {
        // Test lens center at right edge of film back.
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let focal_length = MillimeterUnit::new(50.0);
        let lens_center_x = MillimeterUnit::new(18.0); // Right edge (+36/2)
        let lens_center_y = MillimeterUnit::new(0.0);

        let intrinsics = CameraIntrinsics::from_physical_parameters(
            focal_length,
            lens_center_x,
            lens_center_y,
            film_back,
        );

        // Principal point X should be at right edge (1.0 in NDC).
        assert_relative_eq!(
            intrinsics.principal_point.x.value(),
            1.0,
            epsilon = 1e-10
        );
        assert_relative_eq!(
            intrinsics.principal_point.y.value(),
            0.0,
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_from_physical_parameters_corner_lens() {
        // Test lens center at bottom-left corner.
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let focal_length = MillimeterUnit::new(50.0);
        let lens_center_x = MillimeterUnit::new(-18.0); // Left edge
        let lens_center_y = MillimeterUnit::new(-12.0); // Bottom edge

        let intrinsics = CameraIntrinsics::from_physical_parameters(
            focal_length,
            lens_center_x,
            lens_center_y,
            film_back,
        );

        // Principal point should be at bottom-left corner (-1.0, -1.0 in NDC)
        assert_relative_eq!(
            intrinsics.principal_point.x.value(),
            -1.0,
            epsilon = 1e-10
        );
        assert_relative_eq!(
            intrinsics.principal_point.y.value(),
            -1.0,
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_from_centered_lens() {
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let focal_length = MillimeterUnit::new(50.0);

        let intrinsics =
            CameraIntrinsics::from_centered_lens(focal_length, film_back);

        // Should be identical to centered physical parameters.
        assert_relative_eq!(
            intrinsics.focal_length_x,
            50.0 / 36.0,
            epsilon = 1e-10
        );
        assert_relative_eq!(
            intrinsics.focal_length_y,
            50.0 / 24.0,
            epsilon = 1e-10
        );
        assert_relative_eq!(
            intrinsics.principal_point.x.value(),
            0.0,
            epsilon = 1e-10
        );
        assert_relative_eq!(
            intrinsics.principal_point.y.value(),
            0.0,
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_to_physical_parameters_round_trip() {
        // Test round-trip conversion: physical -> normalized -> physical
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let original_focal_length = MillimeterUnit::new(85.0);
        let original_lens_center_x = MillimeterUnit::new(-5.0);
        let original_lens_center_y = MillimeterUnit::new(3.0);

        // Convert to normalized.
        let intrinsics = CameraIntrinsics::from_physical_parameters(
            original_focal_length,
            original_lens_center_x,
            original_lens_center_y,
            film_back,
        );

        // Convert back to physical.
        let (
            recovered_focal_length,
            recovered_lens_center_x,
            recovered_lens_center_y,
        ) = intrinsics.to_physical_parameters();

        // Should match original values.
        assert_relative_eq!(
            recovered_focal_length.value(),
            original_focal_length.value(),
            epsilon = 1e-10
        );
        assert_relative_eq!(
            recovered_lens_center_x.value(),
            original_lens_center_x.value(),
            epsilon = 1e-10
        );
        assert_relative_eq!(
            recovered_lens_center_y.value(),
            original_lens_center_y.value(),
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_aps_c_sensor() {
        // Test with APS-C sensor.
        let film_back = CameraFilmBack::from_millimeters(22.3, 14.9);
        let focal_length = MillimeterUnit::new(35.0);
        let lens_center_x = MillimeterUnit::new(1.0); // Slightly off-center
        let lens_center_y = MillimeterUnit::new(-0.5);

        let intrinsics = CameraIntrinsics::from_physical_parameters(
            focal_length,
            lens_center_x,
            lens_center_y,
            film_back,
        );

        // Verify focal length X normalization.
        assert_relative_eq!(
            intrinsics.focal_length_x,
            35.0 / 22.3,
            epsilon = 1e-10
        );

        // Verify focal length Y normalization.
        assert_relative_eq!(
            intrinsics.focal_length_y,
            35.0 / 14.9,
            epsilon = 1e-10
        );

        // Verify lens center offset calculation with NDC coordinates.
        //
        // Principal point in NDC = 2.0 * lens_center / film_back_dimension
        let expected_principal_x = 2.0 * 1.0 / 22.3;
        let expected_principal_y = 2.0 * -0.5 / 14.9;

        assert_relative_eq!(
            intrinsics.principal_point.x.value(),
            expected_principal_x,
            epsilon = 1e-10
        );
        assert_relative_eq!(
            intrinsics.principal_point.y.value(),
            expected_principal_y,
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_different_sensor_formats() {
        // Test that the same physical parameters work with different
        // sensor formats.
        let focal_length = MillimeterUnit::new(50.0);
        let lens_center_x = MillimeterUnit::new(2.0); // Slightly off-center
        let lens_center_y = MillimeterUnit::new(-1.0);

        // Full-frame 35mm.
        let film_back_ff = CameraFilmBack::from_millimeters(36.0, 24.0);
        let intrinsics_ff = CameraIntrinsics::from_physical_parameters(
            focal_length,
            lens_center_x,
            lens_center_y,
            film_back_ff,
        );

        // APS-C.
        let film_back_aps_c = CameraFilmBack::from_millimeters(22.3, 14.9);
        let intrinsics_aps_c = CameraIntrinsics::from_physical_parameters(
            focal_length,
            lens_center_x,
            lens_center_y,
            film_back_aps_c,
        );

        // Different sensors should produce different normalized
        // intrinsics because the physical dimensions are different.
        assert_ne!(
            intrinsics_ff.focal_length_x,
            intrinsics_aps_c.focal_length_x
        );
        assert_ne!(
            intrinsics_ff.focal_length_y,
            intrinsics_aps_c.focal_length_y
        );
        assert_ne!(
            intrinsics_ff.principal_point.x.value(),
            intrinsics_aps_c.principal_point.x.value()
        );
        assert_ne!(
            intrinsics_ff.principal_point.y.value(),
            intrinsics_aps_c.principal_point.y.value()
        );

        // Verify focal length X scaling.
        assert_relative_eq!(
            intrinsics_ff.focal_length_x,
            50.0 / 36.0,
            epsilon = 1e-10
        );
        assert_relative_eq!(
            intrinsics_aps_c.focal_length_x,
            50.0 / 22.3,
            epsilon = 1e-10
        );

        // Verify focal length Y scaling.
        assert_relative_eq!(
            intrinsics_ff.focal_length_y,
            50.0 / 24.0,
            epsilon = 1e-10
        );
        assert_relative_eq!(
            intrinsics_aps_c.focal_length_y,
            50.0 / 14.9,
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_edge_case_values() {
        // Test with very small focal length.
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let tiny_focal_length = MillimeterUnit::new(8.0); // Very wide angle

        let intrinsics = CameraIntrinsics::from_physical_parameters(
            tiny_focal_length,
            MillimeterUnit::new(0.0),
            MillimeterUnit::new(0.0),
            film_back,
        );

        assert_relative_eq!(
            intrinsics.focal_length_x,
            8.0 / 36.0,
            epsilon = 1e-10
        );
        assert_relative_eq!(
            intrinsics.focal_length_y,
            8.0 / 24.0,
            epsilon = 1e-10
        );

        // Test with very large focal length.
        let large_focal_length = MillimeterUnit::new(800.0); // Super telephoto
        let intrinsics_tele = CameraIntrinsics::from_physical_parameters(
            large_focal_length,
            MillimeterUnit::new(0.0),
            MillimeterUnit::new(0.0),
            film_back,
        );

        assert_relative_eq!(
            intrinsics_tele.focal_length_x,
            800.0 / 36.0,
            epsilon = 1e-10
        );
        assert_relative_eq!(
            intrinsics_tele.focal_length_y,
            800.0 / 24.0,
            epsilon = 1e-10
        );

        // Test with extreme lens center positions.
        let extreme_center = CameraIntrinsics::from_physical_parameters(
            MillimeterUnit::new(50.0),
            MillimeterUnit::new(18.0), // Far right edge.
            MillimeterUnit::new(-12.0), // Bottom edge.
            film_back,
        );

        assert_relative_eq!(
            extreme_center.principal_point.x.value(),
            1.0,
            epsilon = 1e-10
        );
        assert_relative_eq!(
            extreme_center.principal_point.y.value(),
            -1.0,
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_fov_calculations() {
        // Test with 50mm lens on full-frame 35mm sensor.
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let focal_length = MillimeterUnit::new(50.0);
        let intrinsics =
            CameraIntrinsics::from_centered_lens(focal_length, film_back);

        // Calculate expected horizontal FoV: 2 * atan(36 / (2 * 50)) = 2 * atan(0.36)
        let expected_horizontal_fov_rad: f64 =
            2.0_f64 * (36.0_f64 / (2.0_f64 * 50.0_f64)).atan();
        let expected_horizontal_fov_deg: f64 =
            expected_horizontal_fov_rad.to_degrees();

        assert_relative_eq!(
            intrinsics.horizontal_fov_radians(),
            expected_horizontal_fov_rad,
            epsilon = 1e-10
        );
        assert_relative_eq!(
            intrinsics.horizontal_fov_degrees(),
            expected_horizontal_fov_deg,
            epsilon = 1e-8
        );

        // Calculate expected vertical FoV: 2 * atan(24 / (2 * 50))
        let expected_vertical_fov_rad: f64 =
            2.0_f64 * (24.0_f64 / (2.0_f64 * 50.0_f64)).atan();
        let expected_vertical_fov_deg: f64 =
            expected_vertical_fov_rad.to_degrees();

        assert_relative_eq!(
            intrinsics.vertical_fov_radians(),
            expected_vertical_fov_rad,
            epsilon = 1e-10
        );
        assert_relative_eq!(
            intrinsics.vertical_fov_degrees(),
            expected_vertical_fov_deg,
            epsilon = 1e-8
        );

        // Test diagonal FoV.
        let diagonal_mm: f64 = (36.0_f64.powi(2) + 24.0_f64.powi(2)).sqrt();
        let expected_diagonal_fov_rad: f64 =
            2.0_f64 * (diagonal_mm / (2.0_f64 * 50.0_f64)).atan();

        assert_relative_eq!(
            intrinsics.diagonal_fov_radians(),
            expected_diagonal_fov_rad,
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_fov_validation_sta_dataset() {
        // Validate the FoV for STA test dataset.
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let focal_length = MillimeterUnit::new(41.6);
        let intrinsics =
            CameraIntrinsics::from_centered_lens(focal_length, film_back);

        let horizontal_fov_deg = intrinsics.horizontal_fov_degrees();

        assert_relative_eq!(horizontal_fov_deg, 46.8, epsilon = 0.1);
        println!(
            "STA dataset: {}mm focal length = {:.1}° horizontal FoV",
            41.6, horizontal_fov_deg
        );
    }

    #[test]
    fn test_fov_validation_operahouse_dataset() {
        // Validate the FoV for Opera House test dataset.
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let focal_length = MillimeterUnit::new(91.0);
        let intrinsics =
            CameraIntrinsics::from_centered_lens(focal_length, film_back);

        let horizontal_fov_deg = intrinsics.horizontal_fov_degrees();

        assert_relative_eq!(horizontal_fov_deg, 22.4, epsilon = 0.1);
        println!(
            "Opera House dataset: {}mm focal length = {:.1}° horizontal FoV",
            91.0, horizontal_fov_deg
        );
    }

    #[test]
    fn test_aspect_ratio_calculation() {
        // Test aspect ratio calculation.
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let focal_length = MillimeterUnit::new(50.0);
        let intrinsics =
            CameraIntrinsics::from_centered_lens(focal_length, film_back);

        assert_relative_eq!(intrinsics.aspect_ratio(), 1.5, epsilon = 1e-10);

        // Test with APS-C sensor.
        let film_back_aps_c = CameraFilmBack::from_millimeters(22.3, 14.9);
        let intrinsics_aps_c =
            CameraIntrinsics::from_centered_lens(focal_length, film_back_aps_c);

        assert_relative_eq!(
            intrinsics_aps_c.aspect_ratio(),
            22.3 / 14.9,
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_common_lens_fov_values() {
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);

        // Test known lens focal lengths and their approximate FoV values.
        let test_cases = [
            (14.0, 104.3), // Ultra wide angle.
            (24.0, 73.7),  // Wide angle.
            (35.0, 54.4),  // Wide angle.
            (50.0, 39.6),  // Normal lens.
            (85.0, 23.9),  // Portrait lens.
            (135.0, 15.2), // Telephoto.
            (200.0, 10.3), // Long telephoto.
        ];

        for (focal_mm, expected_fov_deg) in test_cases {
            let focal_length = MillimeterUnit::new(focal_mm);
            let intrinsics =
                CameraIntrinsics::from_centered_lens(focal_length, film_back);
            let actual_fov_deg = intrinsics.horizontal_fov_degrees();

            assert_relative_eq!(
                actual_fov_deg,
                expected_fov_deg,
                epsilon = 0.2
            );

            // Additional assertion for better error messages.
            if (actual_fov_deg - expected_fov_deg).abs() > 0.2 {
                panic!(
                    "{}mm lens should have ~{:.1}° FoV, got {:.1}°",
                    focal_mm, expected_fov_deg, actual_fov_deg
                );
            }
        }
    }
}
