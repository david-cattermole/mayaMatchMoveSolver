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

use crate::datatype::uv_value::{UvPoint2, UvValue};

/// Represents a point correspondence between two frames in UV coordinate space.
///
/// This type is designed for UV coordinate correspondences (typically 0.0-1.0 range)
/// commonly used in homography estimation and 2D image transformations.
#[derive(Debug, Clone, Copy)]
pub struct UvPointCorrespondence<T>
where
    T: Copy + std::fmt::Debug + PartialEq + 'static,
{
    /// Source point in UV coordinates.
    pub src: UvPoint2<T>,
    /// Destination point in UV coordinates.
    pub dst: UvPoint2<T>,
}

impl<T> UvPointCorrespondence<T>
where
    T: Copy + std::fmt::Debug + PartialEq + 'static,
{
    /// Create a new UV point correspondence from coordinates.
    ///
    /// # Arguments
    /// * `src_x, src_y` - Source point UV coordinates.
    /// * `dst_x, dst_y` - Destination point UV coordinates.
    pub fn new(src_x: T, src_y: T, dst_x: T, dst_y: T) -> Self {
        Self {
            src: UvPoint2::new(UvValue(src_x), UvValue(src_y)),
            dst: UvPoint2::new(UvValue(dst_x), UvValue(dst_y)),
        }
    }

    /// Create from pre-computed UV points.
    pub fn from_uv_points(src: UvPoint2<T>, dst: UvPoint2<T>) -> Self {
        Self { src, dst }
    }
}

// Legacy alias for backward compatibility during transition

#[cfg(test)]
mod tests {
    use super::*;
    use crate::datatype::UnitValue;

    #[test]
    fn test_uv_point_correspondence_creation() {
        let corr = UvPointCorrespondence::new(0.25, 0.5, 0.75, 1.0);
        assert_eq!(corr.src.x.value(), 0.25);
        assert_eq!(corr.src.y.value(), 0.5);
        assert_eq!(corr.dst.x.value(), 0.75);
        assert_eq!(corr.dst.y.value(), 1.0);
    }

    #[test]
    fn test_uv_point_correspondence_from_points() {
        let src = UvValue::point2(0.1, 0.2);
        let dst = UvValue::point2(0.8, 0.9);
        let corr = UvPointCorrespondence::from_uv_points(src, dst);

        assert_eq!(corr.src, src);
        assert_eq!(corr.dst, dst);
    }

    #[test]
    fn test_legacy_point_correspondence() {
        // Test backward compatibility
        let corr = UvPointCorrespondence::new(1.0, 2.0, 3.0, 4.0);
        assert_eq!(corr.src.x.value(), 1.0);
        assert_eq!(corr.src.y.value(), 2.0);
        assert_eq!(corr.dst.x.value(), 3.0);
        assert_eq!(corr.dst.y.value(), 4.0);
    }
}
