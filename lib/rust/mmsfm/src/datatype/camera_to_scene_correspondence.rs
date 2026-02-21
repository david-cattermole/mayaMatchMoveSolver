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

use nalgebra::Vector3;

use crate::datatype::camera_coord_value::{
    CameraCoordPoint2, CameraCoordValue,
};
use crate::datatype::common::UnitValue;
use crate::datatype::scene_unit::{ScenePoint3, SceneUnit};

/// Represents a point correspondence between a 2D normalized camera coordinate point
/// and a 3D scene point.
///
/// This is used for Perspective-n-Point (PnP) problems where we have known 3D scene
/// coordinates and their corresponding 2D normalized camera projections. The camera
/// coordinates are normalized (intrinsic parameters already applied).
#[derive(Debug, Clone, Copy)]
pub struct CameraToSceneCorrespondence<T>
where
    T: Copy + std::fmt::Debug + PartialEq + 'static,
{
    /// 2D point in normalized camera coordinates.
    pub camera_point: CameraCoordPoint2<T>,
    /// 3D point in scene coordinates.
    pub scene_point: ScenePoint3<T>,
}

impl<T> CameraToSceneCorrespondence<T>
where
    T: Copy + std::fmt::Debug + PartialEq + 'static,
{
    /// Create a new camera to scene correspondence.
    ///
    /// # Arguments
    /// * `cam_x, cam_y` - Normalized camera coordinates
    /// * `scene_x, scene_y, scene_z` - Scene coordinates
    pub fn new(cam_x: T, cam_y: T, scene_x: T, scene_y: T, scene_z: T) -> Self {
        Self {
            camera_point: CameraCoordValue::point2(cam_x, cam_y),
            scene_point: ScenePoint3::new(
                SceneUnit(scene_x),
                SceneUnit(scene_y),
                SceneUnit(scene_z),
            ),
        }
    }

    /// Create from pre-computed camera and scene points.
    pub fn from_points(
        camera_point: CameraCoordPoint2<T>,
        scene_point: ScenePoint3<T>,
    ) -> Self {
        Self {
            camera_point,
            scene_point,
        }
    }
}

impl<T> CameraToSceneCorrespondence<T>
where
    T: Copy + From<f64> + std::fmt::Debug + PartialEq + 'static,
{
    /// Get the camera point as a homogeneous vector (x, y, 1).
    pub fn camera_point_homogeneous(&self) -> Vector3<T> {
        Vector3::new(
            self.camera_point.coords.x.value(),
            self.camera_point.coords.y.value(),
            T::from(1.0),
        )
    }

    /// Get raw camera coordinates as Vector2.
    pub fn camera_point_raw(&self) -> nalgebra::Vector2<T> {
        nalgebra::Vector2::new(
            self.camera_point.coords.x.value(),
            self.camera_point.coords.y.value(),
        )
    }

    /// Get raw scene coordinates as Vector3.
    pub fn scene_point_raw(&self) -> nalgebra::Vector3<T> {
        nalgebra::Vector3::new(
            self.scene_point.coords.x.value(),
            self.scene_point.coords.y.value(),
            self.scene_point.coords.z.value(),
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::datatype::UnitValue;

    #[test]
    fn test_camera_to_scene_correspondence_creation() {
        let corr = CameraToSceneCorrespondence::new(0.5, 0.3, 1.0, 2.0, 5.0);
        assert_eq!(corr.camera_point.x.value(), 0.5);
        assert_eq!(corr.camera_point.y.value(), 0.3);
        assert_eq!(corr.scene_point.x.value(), 1.0);
        assert_eq!(corr.scene_point.y.value(), 2.0);
        assert_eq!(corr.scene_point.z.value(), 5.0);
    }

    #[test]
    fn test_camera_to_scene_correspondence_homogeneous() {
        let corr = CameraToSceneCorrespondence::new(0.1, 0.2, 1.0, 2.0, 3.0);
        let homo = corr.camera_point_homogeneous();
        assert_eq!(homo.x, 0.1);
        assert_eq!(homo.y, 0.2);
        assert_eq!(homo.z, 1.0);
    }

    #[test]
    fn test_camera_to_scene_correspondence_from_points() {
        let camera_point = CameraCoordValue::point2(0.5, 0.3);
        let scene_point = SceneUnit::point3(2.0, 1.5, 10.0);
        let corr =
            CameraToSceneCorrespondence::from_points(camera_point, scene_point);

        assert_eq!(corr.camera_point, camera_point);
        assert_eq!(corr.scene_point, scene_point);
    }
}
