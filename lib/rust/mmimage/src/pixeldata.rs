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

use exr::prelude::*;

#[derive(Debug, Clone)]
pub struct ImagePixelDataRgbaF32 {
    pub width: usize,
    pub height: usize,
    pub data: Vec<(f32, f32, f32, f32)>,
}

impl ImagePixelDataRgbaF32 {
    pub fn new() -> ImagePixelDataRgbaF32 {
        ImagePixelDataRgbaF32 {
            width: 0,
            height: 0,
            data: Vec::new(),
        }
    }
}

impl GetPixel for ImagePixelDataRgbaF32 {
    type Pixel = (f32, f32, f32, f32);

    fn get_pixel(&self, position: Vec2<usize>) -> Self::Pixel {
        let column = position.x();
        let row = position.y();

        let index = (row * self.width) + column;
        let pixel: (f32, f32, f32, f32) = self.data[index];
        pixel
        // (0.0, 0.0, 0.0, 0.0)
    }
}

#[derive(Debug, Clone)]
pub struct ImagePixelData2DF64 {
    pub width: usize,
    pub height: usize,
    pub data: Vec<(f64, f64)>,
}

impl ImagePixelData2DF64 {
    pub fn new() -> ImagePixelData2DF64 {
        ImagePixelData2DF64 {
            width: 0,
            height: 0,
            data: Vec::new(),
        }
    }
}

impl GetPixel for ImagePixelData2DF64 {
    type Pixel = (f64, f64);

    fn get_pixel(&self, position: Vec2<usize>) -> Self::Pixel {
        let column = position.x();
        let row = position.y();

        let index = (row * self.width) + column;
        let pixel: (f64, f64) = self.data[index];
        pixel
        // (0.0, 0.0)
    }
}
