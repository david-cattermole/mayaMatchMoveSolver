//
// Copyright (C) 2023 David Cattermole.
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

/// Defines a region of a 2D image.
///
/// An almost direct clone of the exr::meta::attribute::IntegerBounds.
#[derive(Debug, Clone)]
pub struct ImageRegionRectangle {
    pub position_x: i32,
    pub position_y: i32,
    pub size_x: usize,
    pub size_y: usize,
}

impl ImageRegionRectangle {
    pub fn new(
        position_x: i32,
        position_y: i32,
        size_x: usize,
        size_y: usize,
    ) -> ImageRegionRectangle {
        ImageRegionRectangle {
            position_x,
            position_y,
            size_x,
            size_y,
        }
    }

    pub fn default() -> ImageRegionRectangle {
        ImageRegionRectangle {
            position_x: 0,
            position_y: 0,
            size_x: 0,
            size_y: 0,
        }
    }

    pub fn as_exr_integer_bounds(&self) -> exr::meta::attribute::IntegerBounds {
        let position = exr::math::Vec2::<i32>(self.position_x, self.position_y);
        let size = exr::math::Vec2::<usize>(self.size_x, self.size_y);
        exr::meta::attribute::IntegerBounds { position, size }
    }
}

#[derive(Debug, Clone)]
pub struct Vec2F32 {
    pub x: f32,
    pub y: f32,
}

impl Vec2F32 {
    pub fn new(x: f32, y: f32) -> Vec2F32 {
        Vec2F32 { x, y }
    }

    pub fn default() -> Vec2F32 {
        Vec2F32 { x: 0.0, y: 0.0 }
    }
}

#[derive(Debug, Clone)]
pub struct Vec2I32 {
    pub x: i32,
    pub y: i32,
}

impl Vec2I32 {
    pub fn new(x: i32, y: i32) -> Vec2I32 {
        Vec2I32 { x, y }
    }

    pub fn default() -> Vec2I32 {
        Vec2I32 { x: 0, y: 0 }
    }
}
