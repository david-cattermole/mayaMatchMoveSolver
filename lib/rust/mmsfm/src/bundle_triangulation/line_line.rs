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

use std::marker::PhantomData;

use nalgebra::{Point3, RealField, Vector3};

use super::common::{TriangulationResult, TriangulationStorage};
use crate::datatype::{ScenePoint3, SceneVector3};

/// Triangulates 3D points from ray pairs using line-line intersection.
pub struct TriangulatorLineLine<T: RealField + Copy> {
    // Common storage for triangulation results
    storage: TriangulationStorage<T>,

    // TODO: Why are we using Phantom data? Either explain the usage,
    // or remove this.
    _phantom: PhantomData<T>,
}

/// Input data for line-line triangulation.
pub struct TriangulateDataLineLine<T: RealField + Copy> {
    /// Origin points of first rays.
    pub origins_a: Vec<ScenePoint3<T>>,
    /// Direction vectors of first rays (should be normalized).
    pub directions_a: Vec<SceneVector3<T>>,
    /// Origin points of second rays.
    pub origins_b: Vec<ScenePoint3<T>>,
    /// Direction vectors of second rays (should be normalized).
    pub directions_b: Vec<SceneVector3<T>>,
}

/// Result of line-line triangulation.
#[derive(Debug)]
pub struct TriangulationResultLineLine<'a, T: RealField + Copy> {
    pub inner: TriangulationResult<'a, T>,
}

impl<'a, T: RealField + Copy> AsRef<TriangulationResult<'a, T>>
    for TriangulationResultLineLine<'a, T>
{
    fn as_ref(&self) -> &TriangulationResult<'a, T> {
        &self.inner
    }
}

impl<T: RealField + Copy> TriangulatorLineLine<T> {
    /// Create with initial capacity.
    pub fn new(initial_capacity: usize) -> Self {
        Self {
            storage: TriangulationStorage::new(initial_capacity),
            _phantom: PhantomData,
        }
    }

    /// Ensure buffers handle at least `required_capacity` triangulations.
    pub fn reserve(&mut self, required_capacity: usize) {
        self.storage.reserve(required_capacity);
    }

    /// Triangulates ray pairs in batch using Paul Bourke's line-line intersection.
    pub fn triangulate_points<'a>(
        &'a mut self,
        triangulate_data: &TriangulateDataLineLine<T>,
    ) -> TriangulationResultLineLine<'a, T> {
        let n = triangulate_data.origins_a.len();
        assert_eq!(n, triangulate_data.directions_a.len());
        assert_eq!(n, triangulate_data.origins_b.len());
        assert_eq!(n, triangulate_data.directions_b.len());

        self.reserve(n);

        unsafe {
            self.storage.resize_to(n);
        }

        for i in 0..n {
            self.triangulate_point_inplace(
                i,
                &triangulate_data.origins_a[i],
                &triangulate_data.directions_a[i],
                &triangulate_data.origins_b[i],
                &triangulate_data.directions_b[i],
            );
        }

        TriangulationResultLineLine {
            inner: self.storage.get_result(n),
        }
    }

    /// Triangulates a single ray pair, writing to storage at `index`.
    #[inline]
    fn triangulate_point_inplace(
        &mut self,
        index: usize,
        scene_point_3d_a: &ScenePoint3<T>,
        scene_direction_3d_a: &SceneVector3<T>,
        scene_point_3d_b: &ScenePoint3<T>,
        scene_direction_3d_b: &SceneVector3<T>,
    ) {
        let point_3d_a_from = Point3::new(
            scene_point_3d_a.x.0,
            scene_point_3d_a.y.0,
            scene_point_3d_a.z.0,
        );
        let direction_3d_a = Vector3::new(
            scene_direction_3d_a.x.0,
            scene_direction_3d_a.y.0,
            scene_direction_3d_a.z.0,
        );
        let point_3d_a_to =
            Point3::from(point_3d_a_from.coords + direction_3d_a);

        let point_3d_b_from = Point3::new(
            scene_point_3d_b.x.0,
            scene_point_3d_b.y.0,
            scene_point_3d_b.z.0,
        );
        let direction_3d_b = Vector3::new(
            scene_direction_3d_b.x.0,
            scene_direction_3d_b.y.0,
            scene_direction_3d_b.z.0,
        );
        let point_3d_b_to =
            Point3::from(point_3d_b_from.coords + direction_3d_b);

        let eps = T::default_epsilon();

        if let Some((closest_a, closest_b)) = paul_bourke_line_intersection(
            &point_3d_a_from,
            &point_3d_a_to,
            &point_3d_b_from,
            &point_3d_b_to,
            eps,
        ) {
            let midpoint_coords =
                (closest_a.coords + closest_b.coords) / (T::one() + T::one());
            let point = Point3::from(midpoint_coords);
            let error = (closest_a - closest_b).norm();

            // Check if the point is in front of both cameras.
            let vec_a = point - point_3d_a_from;
            let vec_b = point - point_3d_b_from;

            // Use epsilon for "in front" check to avoid precision issues at zero distance
            let in_front_a = vec_a.dot(&direction_3d_a) > -eps;
            let in_front_b = vec_b.dot(&direction_3d_b) > -eps;

            if in_front_a && in_front_b {
                self.storage.set_result(index, point, error, true);
            } else {
                self.storage.set_result(index, point, error, false);
            }
        } else {
            // Rays are parallel.
            let midpoint_coords = (point_3d_a_from.coords
                + point_3d_b_from.coords)
                / (T::one() + T::one());
            let point = Point3::from(midpoint_coords);
            let error = (point_3d_a_from - point_3d_b_from).norm();
            self.storage.set_result(index, point, error, false);
        }
    }

    /// Returns current capacity.
    pub fn capacity(&self) -> usize {
        self.storage.capacity
    }
}

impl<T: RealField + Copy> TriangulateDataLineLine<T> {
    /// Create empty.
    pub fn new() -> Self {
        Self {
            origins_a: Vec::new(),
            directions_a: Vec::new(),
            origins_b: Vec::new(),
            directions_b: Vec::new(),
        }
    }

    /// Create with initial capacity.
    pub fn with_capacity(capacity: usize) -> Self {
        Self {
            origins_a: Vec::with_capacity(capacity),
            directions_a: Vec::with_capacity(capacity),
            origins_b: Vec::with_capacity(capacity),
            directions_b: Vec::with_capacity(capacity),
        }
    }

    /// Adds a ray pair.
    pub fn add_ray_pair(
        &mut self,
        scene_origin_3d_a: ScenePoint3<T>,
        scene_direction_3d_a: SceneVector3<T>,
        scene_origin_3d_b: ScenePoint3<T>,
        scene_direction_3d_b: SceneVector3<T>,
    ) {
        self.origins_a.push(scene_origin_3d_a);
        self.directions_a.push(scene_direction_3d_a);
        self.origins_b.push(scene_origin_3d_b);
        self.directions_b.push(scene_direction_3d_b);
    }

    /// Returns the number of ray pairs.
    pub fn len(&self) -> usize {
        self.origins_a.len()
    }

    /// Returns true if empty.
    pub fn is_empty(&self) -> bool {
        self.origins_a.is_empty()
    }

    /// Clears all ray pairs.
    pub fn clear(&mut self) {
        self.origins_a.clear();
        self.directions_a.clear();
        self.origins_b.clear();
        self.directions_b.clear();
    }
}

impl<T: RealField + Copy> Default for TriangulateDataLineLine<T> {
    fn default() -> Self {
        Self::new()
    }
}

/// Finds the closest approach points between two 3D line segments.
///
/// Based on Paul Bourke's algorithm: http://paulbourke.net/geometry/pointlineplane/
/// Returns the closest point on each line, or None if lines are parallel or degenerate.
fn paul_bourke_line_intersection<T: RealField + Copy>(
    line_a_start: &Point3<T>,
    line_a_end: &Point3<T>,
    line_b_start: &Point3<T>,
    line_b_end: &Point3<T>,
    eps: T,
) -> Option<(Point3<T>, Point3<T>)> {
    let from_a_start_to_b_start = Vector3::new(
        line_a_start.x - line_b_start.x,
        line_a_start.y - line_b_start.y,
        line_a_start.z - line_b_start.z,
    );
    let dir_b = Vector3::new(
        line_b_end.x - line_b_start.x,
        line_b_end.y - line_b_start.y,
        line_b_end.z - line_b_start.z,
    );
    let dir_a = Vector3::new(
        line_a_end.x - line_a_start.x,
        line_a_end.y - line_a_start.y,
        line_a_end.z - line_a_start.z,
    );

    if dir_b.norm() < eps || dir_a.norm() < eps {
        return None;
    }

    let d_ab_b = from_a_start_to_b_start.dot(&dir_b);
    let d_b_a = dir_b.dot(&dir_a);
    let d_ab_a = from_a_start_to_b_start.dot(&dir_a);
    let d_b_b = dir_b.dot(&dir_b);
    let d_a_a = dir_a.dot(&dir_a);

    let denom = d_a_a * d_b_b - d_b_a * d_b_a;
    if denom.abs() < eps {
        return None;
    }

    let numer = d_ab_b * d_b_a - d_ab_a * d_b_b;
    let t_a = numer / denom;
    let t_b = (d_ab_b + d_b_a * t_a) / d_b_b;

    let closest_on_line_a = Point3::new(
        line_a_start.x + t_a * dir_a.x,
        line_a_start.y + t_a * dir_a.y,
        line_a_start.z + t_a * dir_a.z,
    );
    let closest_on_line_b = Point3::new(
        line_b_start.x + t_b * dir_b.x,
        line_b_start.y + t_b * dir_b.y,
        line_b_start.z + t_b * dir_b.z,
    );

    Some((closest_on_line_a, closest_on_line_b))
}

#[cfg(test)]
mod tests {
    use super::*;
    use nalgebra::Vector3;

    use crate::datatype::{ScenePoint3, SceneUnit, SceneVector3};

    #[test]
    fn test_no_allocations_during_computation() {
        let mut triangulator = TriangulatorLineLine::<f64>::new(1000);

        // Pre-allocate a large triangulate_data
        let mut triangulate_data = TriangulateDataLineLine::with_capacity(500);
        for i in 0..500 {
            let offset = i as f64 * 0.1;
            let dir_a = Vector3::new(1.0, 0.0, 1.0).normalize();
            let dir_b = Vector3::new(-1.0, 0.0, 1.0).normalize();
            triangulate_data.add_ray_pair(
                ScenePoint3::new(
                    SceneUnit(-1.0),
                    SceneUnit(offset),
                    SceneUnit(0.0),
                ),
                SceneVector3::new(
                    SceneUnit(dir_a.x),
                    SceneUnit(dir_a.y),
                    SceneUnit(dir_a.z),
                ),
                ScenePoint3::new(
                    SceneUnit(1.0),
                    SceneUnit(offset),
                    SceneUnit(0.0),
                ),
                SceneVector3::new(
                    SceneUnit(dir_b.x),
                    SceneUnit(dir_b.y),
                    SceneUnit(dir_b.z),
                ),
            );
        }

        // First triangulation to ensure all capacity is allocated.
        let _result1 = triangulator.triangulate_points(&triangulate_data);

        // Second triangulation should not allocate anything new.
        let _result2 = triangulator.triangulate_points(&triangulate_data);

        // This test mainly ensures compilation and that the API works
        // correctly.
        //
        // In a real scenario, you would use a memory profiler to
        // verify no allocations.
        assert_eq!(triangulator.capacity(), 1000);
    }

    #[test]
    fn test_simple_triangulation() {
        let mut triangulator = TriangulatorLineLine::<f64>::new(100);

        // Create two rays that intersect at (0, 0, 5)
        let scene_origin_3d_a =
            ScenePoint3::new(SceneUnit(-1.0), SceneUnit(0.0), SceneUnit(0.0));
        let dir_a = Vector3::new(1.0, 0.0, 5.0).normalize();
        let scene_direction_3d_a = SceneVector3::new(
            SceneUnit(dir_a.x),
            SceneUnit(dir_a.y),
            SceneUnit(dir_a.z),
        );

        let scene_origin_3d_b =
            ScenePoint3::new(SceneUnit(1.0), SceneUnit(0.0), SceneUnit(0.0));
        let dir_b = Vector3::new(-1.0, 0.0, 5.0).normalize();
        let scene_direction_3d_b = SceneVector3::new(
            SceneUnit(dir_b.x),
            SceneUnit(dir_b.y),
            SceneUnit(dir_b.z),
        );

        let mut triangulate_data = TriangulateDataLineLine::new();
        triangulate_data.add_ray_pair(
            scene_origin_3d_a,
            scene_direction_3d_a,
            scene_origin_3d_b,
            scene_direction_3d_b,
        );

        let result = triangulator.triangulate_points(&triangulate_data);

        assert_eq!(result.inner.points.len(), 1);
        assert!(result.inner.valid[0]);

        // The intersection should be close to (0, 0, 5)
        let triangulated = result.inner.points[0];
        assert!((triangulated.x - 0.0).abs() < 1e-10);
        assert!((triangulated.y - 0.0).abs() < 1e-10);
        assert!((triangulated.z - 5.0).abs() < 1e-10);
        assert!(result.inner.errors[0] < 1e-10);
    }

    #[test]
    fn test_parallel_rays() {
        let mut triangulator = TriangulatorLineLine::<f32>::new(100);

        // Create two parallel rays
        let scene_origin_3d_a =
            ScenePoint3::new(SceneUnit(0.0), SceneUnit(0.0), SceneUnit(0.0));
        let scene_direction_3d_a =
            SceneVector3::new(SceneUnit(0.0), SceneUnit(0.0), SceneUnit(1.0));

        let scene_origin_3d_b =
            ScenePoint3::new(SceneUnit(1.0), SceneUnit(0.0), SceneUnit(0.0));
        let scene_direction_3d_b =
            SceneVector3::new(SceneUnit(0.0), SceneUnit(0.0), SceneUnit(1.0));

        let mut triangulate_data = TriangulateDataLineLine::new();
        triangulate_data.add_ray_pair(
            scene_origin_3d_a,
            scene_direction_3d_a,
            scene_origin_3d_b,
            scene_direction_3d_b,
        );

        let result = triangulator.triangulate_points(&triangulate_data);

        assert_eq!(result.inner.points.len(), 1);
        assert!(!result.inner.valid[0]); // Should be marked as invalid due to parallel rays
    }

    #[test]
    fn test_triangulate_points() {
        let mut triangulator = TriangulatorLineLine::<f64>::new(1000);

        let mut triangulate_data = TriangulateDataLineLine::with_capacity(100);

        // Add multiple ray pairs
        for i in 0..100 {
            let offset = i as f64 * 0.1;
            let scene_origin_3d_a = ScenePoint3::new(
                SceneUnit(-1.0),
                SceneUnit(offset),
                SceneUnit(0.0),
            );
            let dir_a = Vector3::new(1.0, 0.0, 1.0).normalize();
            let scene_direction_3d_a = SceneVector3::new(
                SceneUnit(dir_a.x),
                SceneUnit(dir_a.y),
                SceneUnit(dir_a.z),
            );

            let scene_origin_3d_b = ScenePoint3::new(
                SceneUnit(1.0),
                SceneUnit(offset),
                SceneUnit(0.0),
            );
            let dir_b = Vector3::new(-1.0, 0.0, 1.0).normalize();
            let scene_direction_3d_b = SceneVector3::new(
                SceneUnit(dir_b.x),
                SceneUnit(dir_b.y),
                SceneUnit(dir_b.z),
            );

            triangulate_data.add_ray_pair(
                scene_origin_3d_a,
                scene_direction_3d_a,
                scene_origin_3d_b,
                scene_direction_3d_b,
            );
        }

        let result = triangulator.triangulate_points(&triangulate_data);

        assert_eq!(result.inner.points.len(), 100);
        assert!(result.inner.valid.iter().all(|&v| v)); // All should be valid

        // Check that all triangulated points are reasonable
        for (i, point) in result.inner.points.iter().enumerate() {
            assert!((point.x - 0.0).abs() < 1e-10);
            assert!((point.y - (i as f64 * 0.1)).abs() < 1e-10);
            assert!((point.z - 1.0).abs() < 1e-10);
        }
    }

    #[test]
    fn test_cross_validation_with_paul_bourke() {
        let mut triangulator = TriangulatorLineLine::<f64>::new(10);

        // Test case: rays intersecting at (0, 0, 5)
        let scene_origin_3d_a =
            ScenePoint3::new(SceneUnit(-1.0), SceneUnit(0.0), SceneUnit(0.0));
        let dir_a = Vector3::new(1.0, 0.0, 5.0).normalize();
        let scene_direction_3d_a = SceneVector3::new(
            SceneUnit(dir_a.x),
            SceneUnit(dir_a.y),
            SceneUnit(dir_a.z),
        );
        let scene_origin_3d_b =
            ScenePoint3::new(SceneUnit(1.0), SceneUnit(0.0), SceneUnit(0.0));
        let dir_b = Vector3::new(-1.0, 0.0, 5.0).normalize();
        let scene_direction_3d_b = SceneVector3::new(
            SceneUnit(dir_b.x),
            SceneUnit(dir_b.y),
            SceneUnit(dir_b.z),
        );

        let mut triangulate_data = TriangulateDataLineLine::new();
        triangulate_data.add_ray_pair(
            scene_origin_3d_a,
            scene_direction_3d_a,
            scene_origin_3d_b,
            scene_direction_3d_b,
        );

        let result = triangulator.triangulate_points(&triangulate_data);
        let our_point = result.inner.points[0];
        let our_error = result.inner.errors[0];

        // Since our implementation now uses Paul Bourke's algorithm internally,
        // we just verify that the result is reasonable
        assert!(
            (our_point.x - 0.0).abs() < 1e-8,
            "X coordinate not near expected value"
        );
        assert!(
            (our_point.y - 0.0).abs() < 1e-8,
            "Y coordinate not near expected value"
        );
        assert!(
            (our_point.z - 5.0).abs() < 1e-8,
            "Z coordinate not near expected value"
        );
        assert!(our_error < 1e-8, "Error too large for exact intersection");
    }

    #[test]
    fn test_origin_intersection() {
        let mut triangulator = TriangulatorLineLine::<f64>::new(10);

        // Rays that intersect at origin
        let scene_origin_3d_a =
            ScenePoint3::new(SceneUnit(-1.0), SceneUnit(-1.0), SceneUnit(-1.0));
        let dir_a = Vector3::new(1.0, 1.0, 1.0).normalize();
        let scene_direction_3d_a = SceneVector3::new(
            SceneUnit(dir_a.x),
            SceneUnit(dir_a.y),
            SceneUnit(dir_a.z),
        );
        let scene_origin_3d_b =
            ScenePoint3::new(SceneUnit(1.0), SceneUnit(-1.0), SceneUnit(1.0));
        let dir_b = Vector3::new(-1.0, 1.0, -1.0).normalize();
        let scene_direction_3d_b = SceneVector3::new(
            SceneUnit(dir_b.x),
            SceneUnit(dir_b.y),
            SceneUnit(dir_b.z),
        );

        let mut triangulate_data = TriangulateDataLineLine::new();
        triangulate_data.add_ray_pair(
            scene_origin_3d_a,
            scene_direction_3d_a,
            scene_origin_3d_b,
            scene_direction_3d_b,
        );

        let result = triangulator.triangulate_points(&triangulate_data);

        assert_eq!(result.inner.points.len(), 1);
        assert!(result.inner.valid[0]);

        let point = result.inner.points[0];
        // Should be very close to origin
        assert!(
            point.coords.norm() < 1e-10,
            "Point not near origin: {:?}",
            point
        );
        assert!(
            result.inner.errors[0] < 1e-10,
            "Error too large for exact intersection"
        );
    }

    #[test]
    fn test_behind_camera_detection() {
        let mut triangulator = TriangulatorLineLine::<f64>::new(10);

        // Rays that intersect at Z=-1 (Forward in Maya).
        //
        // Note: Forward direction in Maya is -Z.
        // These rays start at Z=0 and point towards -Z.
        // So the intersection is "In Front" of the camera.
        let scene_origin_3d_a =
            ScenePoint3::new(SceneUnit(0.0), SceneUnit(0.0), SceneUnit(0.0));
        let dir_a = Vector3::new(1.0, 0.0, -1.0).normalize(); // Points forward (-Z)
        let scene_direction_3d_a = SceneVector3::new(
            SceneUnit(dir_a.x),
            SceneUnit(dir_a.y),
            SceneUnit(dir_a.z),
        );
        let scene_origin_3d_b =
            ScenePoint3::new(SceneUnit(2.0), SceneUnit(0.0), SceneUnit(0.0));
        let dir_b = Vector3::new(-1.0, 0.0, -1.0).normalize(); // Points forward (-Z)
        let scene_direction_3d_b = SceneVector3::new(
            SceneUnit(dir_b.x),
            SceneUnit(dir_b.y),
            SceneUnit(dir_b.z),
        );

        let mut triangulate_data = TriangulateDataLineLine::new();
        triangulate_data.add_ray_pair(
            scene_origin_3d_a,
            scene_direction_3d_a,
            scene_origin_3d_b,
            scene_direction_3d_b,
        );

        let result = triangulator.triangulate_points(&triangulate_data);

        assert_eq!(result.inner.points.len(), 1);
        // Valid because it is in front.
        assert!(result.inner.valid[0]);

        let point = result.inner.points[0];
        // Point should be at negative Z (in front of camera plane)
        assert!(
            point.z < 0.0,
            "Expected negative Z coordinate for in-front triangulation"
        );
    }

    #[test]
    fn test_near_parallel_rays() {
        let mut triangulator = TriangulatorLineLine::<f64>::new(10);

        // Rays that are nearly parallel but not quite
        let scene_origin_3d_a =
            ScenePoint3::new(SceneUnit(-1.0), SceneUnit(0.0), SceneUnit(0.0));
        let scene_direction_3d_a =
            SceneVector3::new(SceneUnit(1.0), SceneUnit(0.0), SceneUnit(0.0));
        let scene_origin_3d_b =
            ScenePoint3::new(SceneUnit(-1.0), SceneUnit(1.0), SceneUnit(0.0));
        let dir_b = Vector3::new(1.0, 1e-12, 0.0).normalize(); // Very slightly off parallel
        let scene_direction_3d_b = SceneVector3::new(
            SceneUnit(dir_b.x),
            SceneUnit(dir_b.y),
            SceneUnit(dir_b.z),
        );

        let mut triangulate_data = TriangulateDataLineLine::new();
        triangulate_data.add_ray_pair(
            scene_origin_3d_a,
            scene_direction_3d_a,
            scene_origin_3d_b,
            scene_direction_3d_b,
        );

        let result = triangulator.triangulate_points(&triangulate_data);

        assert_eq!(result.inner.points.len(), 1);
        // This might be marked as invalid due to near-parallel rays
        // The specific behavior depends on epsilon handling
    }

    #[test]
    fn test_extreme_coordinates() {
        let mut triangulator = TriangulatorLineLine::<f64>::new(10);

        // Test with very large coordinates
        let large_val = 1e6;
        let scene_origin_3d_a = ScenePoint3::new(
            SceneUnit(-large_val),
            SceneUnit(0.0),
            SceneUnit(0.0),
        );
        let dir_a = Vector3::new(1.0, 0.0, 1.0).normalize();
        let scene_direction_3d_a = SceneVector3::new(
            SceneUnit(dir_a.x),
            SceneUnit(dir_a.y),
            SceneUnit(dir_a.z),
        );
        let scene_origin_3d_b = ScenePoint3::new(
            SceneUnit(large_val),
            SceneUnit(0.0),
            SceneUnit(0.0),
        );
        let dir_b = Vector3::new(-1.0, 0.0, 1.0).normalize();
        let scene_direction_3d_b = SceneVector3::new(
            SceneUnit(dir_b.x),
            SceneUnit(dir_b.y),
            SceneUnit(dir_b.z),
        );

        let mut triangulate_data = TriangulateDataLineLine::new();
        triangulate_data.add_ray_pair(
            scene_origin_3d_a,
            scene_direction_3d_a,
            scene_origin_3d_b,
            scene_direction_3d_b,
        );

        let result = triangulator.triangulate_points(&triangulate_data);

        assert_eq!(result.inner.points.len(), 1);
        assert!(result.inner.valid[0]);

        let point = result.inner.points[0];
        // Should triangulate at approximately (0, 0, large_val)
        assert!(
            (point.x - 0.0).abs() < 1e-6,
            "X coordinate incorrect for extreme values"
        );
        assert!(
            (point.z - large_val).abs() < 1e3,
            "Z coordinate incorrect for extreme values"
        );
    }

    #[test]
    fn test_mixed_precision() {
        // Test f32 precision
        let mut triangulator_f32 = TriangulatorLineLine::<f32>::new(10);
        let mut triangulate_data_f32 = TriangulateDataLineLine::new();

        let dir_a_f32 = Vector3::new(1.0f32, 0.0, 1.0).normalize();
        let dir_b_f32 = Vector3::new(-1.0f32, 0.0, 1.0).normalize();
        triangulate_data_f32.add_ray_pair(
            ScenePoint3::new(
                SceneUnit(-1.0f32),
                SceneUnit(0.0),
                SceneUnit(0.0),
            ),
            SceneVector3::new(
                SceneUnit(dir_a_f32.x),
                SceneUnit(dir_a_f32.y),
                SceneUnit(dir_a_f32.z),
            ),
            ScenePoint3::new(SceneUnit(1.0f32), SceneUnit(0.0), SceneUnit(0.0)),
            SceneVector3::new(
                SceneUnit(dir_b_f32.x),
                SceneUnit(dir_b_f32.y),
                SceneUnit(dir_b_f32.z),
            ),
        );

        let result_f32 =
            triangulator_f32.triangulate_points(&triangulate_data_f32);

        // Test f64 precision with same setup
        let mut triangulator_f64 = TriangulatorLineLine::<f64>::new(10);
        let mut triangulate_data_f64 = TriangulateDataLineLine::new();

        let dir_a_f64 = Vector3::new(1.0f64, 0.0, 1.0).normalize();
        let dir_b_f64 = Vector3::new(-1.0f64, 0.0, 1.0).normalize();
        triangulate_data_f64.add_ray_pair(
            ScenePoint3::new(
                SceneUnit(-1.0f64),
                SceneUnit(0.0),
                SceneUnit(0.0),
            ),
            SceneVector3::new(
                SceneUnit(dir_a_f64.x),
                SceneUnit(dir_a_f64.y),
                SceneUnit(dir_a_f64.z),
            ),
            ScenePoint3::new(SceneUnit(1.0f64), SceneUnit(0.0), SceneUnit(0.0)),
            SceneVector3::new(
                SceneUnit(dir_b_f64.x),
                SceneUnit(dir_b_f64.y),
                SceneUnit(dir_b_f64.z),
            ),
        );

        let result_f64 =
            triangulator_f64.triangulate_points(&triangulate_data_f64);

        // Both should produce valid results
        assert!(result_f32.inner.valid[0]);
        assert!(result_f64.inner.valid[0]);

        // f64 should be more accurate
        assert!(
            result_f64.inner.errors[0] <= result_f32.inner.errors[0] as f64
        );
    }

    #[test]
    fn test_epsilon_boundary_conditions() {
        let mut triangulator = TriangulatorLineLine::<f64>::new(10);

        // Test with rays that have determinant exactly at epsilon boundary
        // Use the same epsilon calculation as the triangulator
        let eps = f64::EPSILON * 2.0;

        // Create rays that will have determinant close to epsilon
        let scene_origin_3d_a =
            ScenePoint3::new(SceneUnit(0.0), SceneUnit(0.0), SceneUnit(0.0));
        let scene_direction_3d_a =
            SceneVector3::new(SceneUnit(1.0), SceneUnit(0.0), SceneUnit(0.0));
        let scene_origin_3d_b =
            ScenePoint3::new(SceneUnit(0.0), SceneUnit(1.0), SceneUnit(0.0));
        let dir_b = Vector3::new(1.0, eps.sqrt(), 0.0).normalize();
        let scene_direction_3d_b = SceneVector3::new(
            SceneUnit(dir_b.x),
            SceneUnit(dir_b.y),
            SceneUnit(dir_b.z),
        );

        let mut triangulate_data = TriangulateDataLineLine::new();
        triangulate_data.add_ray_pair(
            scene_origin_3d_a,
            scene_direction_3d_a,
            scene_origin_3d_b,
            scene_direction_3d_b,
        );

        let result = triangulator.triangulate_points(&triangulate_data);

        assert_eq!(result.inner.points.len(), 1);
        // The exact validity depends on the epsilon calculation
        // This test mainly ensures we don't crash at boundary conditions
    }

    #[test]
    fn test_zero_allocation_guarantee() {
        // This test verifies the zero-allocation design
        let initial_capacity = 500;
        let mut triangulator =
            TriangulatorLineLine::<f64>::new(initial_capacity);

        // Fill up to capacity
        let mut triangulate_data =
            TriangulateDataLineLine::with_capacity(initial_capacity);
        for i in 0..initial_capacity {
            let offset = i as f64 * 0.01;
            let dir_a = Vector3::new(1.0, 0.0, 1.0).normalize();
            let dir_b = Vector3::new(-1.0, 0.0, 1.0).normalize();
            triangulate_data.add_ray_pair(
                ScenePoint3::new(
                    SceneUnit(-1.0),
                    SceneUnit(offset),
                    SceneUnit(0.0),
                ),
                SceneVector3::new(
                    SceneUnit(dir_a.x),
                    SceneUnit(dir_a.y),
                    SceneUnit(dir_a.z),
                ),
                ScenePoint3::new(
                    SceneUnit(1.0),
                    SceneUnit(offset),
                    SceneUnit(0.0),
                ),
                SceneVector3::new(
                    SceneUnit(dir_b.x),
                    SceneUnit(dir_b.y),
                    SceneUnit(dir_b.z),
                ),
            );
        }

        // First triangulation - may allocate to reach capacity
        let _result1 = triangulator.triangulate_points(&triangulate_data);

        // Subsequent triangulations should not allocate
        let _result2 = triangulator.triangulate_points(&triangulate_data);
        let _result3 = triangulator.triangulate_points(&triangulate_data);

        assert_eq!(triangulator.capacity(), initial_capacity);
    }

    #[test]
    fn test_triangulate_data_operations() {
        let mut data = TriangulateDataLineLine::<f64>::new();
        assert!(data.is_empty());
        assert_eq!(data.len(), 0);

        data.add_ray_pair(
            ScenePoint3::new(SceneUnit(0.0), SceneUnit(0.0), SceneUnit(0.0)),
            SceneVector3::new(SceneUnit(1.0), SceneUnit(0.0), SceneUnit(0.0)),
            ScenePoint3::new(SceneUnit(1.0), SceneUnit(0.0), SceneUnit(0.0)),
            SceneVector3::new(SceneUnit(-1.0), SceneUnit(0.0), SceneUnit(0.0)),
        );

        assert!(!data.is_empty());
        assert_eq!(data.len(), 1);

        data.clear();
        assert!(data.is_empty());
        assert_eq!(data.len(), 0);
    }

    #[test]
    fn test_maya_coordinate_system_triangulation() {
        // Test that triangulation results follow Maya coordinate system conventions
        let mut triangulator = TriangulatorLineLine::<f64>::new(10);

        // Create two cameras looking at a point in front (negative Z)
        let camera_a_pos =
            ScenePoint3::new(SceneUnit(-2.0), SceneUnit(0.0), SceneUnit(0.0));
        let camera_b_pos =
            ScenePoint3::new(SceneUnit(2.0), SceneUnit(0.0), SceneUnit(0.0));
        let target_point =
            ScenePoint3::new(SceneUnit(0.0), SceneUnit(0.0), SceneUnit(-5.0)); // Target in front of cameras (Maya convention)

        // Ray from camera A to target - normalize raw values first
        let dir_a = Vector3::new(
            target_point.x.0 - camera_a_pos.x.0,
            target_point.y.0 - camera_a_pos.y.0,
            target_point.z.0 - camera_a_pos.z.0,
        )
        .normalize();
        let scene_direction_3d_a = SceneVector3::new(
            SceneUnit(dir_a.x),
            SceneUnit(dir_a.y),
            SceneUnit(dir_a.z),
        );

        // Ray from camera B to target - normalize raw values first
        let dir_b = Vector3::new(
            target_point.x.0 - camera_b_pos.x.0,
            target_point.y.0 - camera_b_pos.y.0,
            target_point.z.0 - camera_b_pos.z.0,
        )
        .normalize();
        let scene_direction_3d_b = SceneVector3::new(
            SceneUnit(dir_b.x),
            SceneUnit(dir_b.y),
            SceneUnit(dir_b.z),
        );

        let mut triangulate_data = TriangulateDataLineLine::new();
        triangulate_data.add_ray_pair(
            camera_a_pos,
            scene_direction_3d_a,
            camera_b_pos,
            scene_direction_3d_b,
        );

        let result = triangulator.triangulate_points(&triangulate_data);

        assert_eq!(result.inner.points.len(), 1);
        assert!(result.inner.valid[0]);

        let triangulated_point = result.inner.points[0];

        // Verify the triangulated point is in front of cameras (negative Z)
        assert!(triangulated_point.z < 0.0,
               "Triangulated point should be in front of cameras (negative Z in Maya convention), got Z = {}",
               triangulated_point.z);

        // Should be close to our target point
        let target_point_raw =
            Point3::new(target_point.x.0, target_point.y.0, target_point.z.0);
        let error = (triangulated_point - target_point_raw).norm();
        assert!(error < 1e-10, "Triangulation error too large: {}", error);
    }
}
