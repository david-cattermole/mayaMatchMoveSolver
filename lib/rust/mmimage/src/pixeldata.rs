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

use crate::pixelbuffer::ImagePixelBuffer;
use exr::prelude::*;

#[derive(Debug)]
pub struct ImagePixelDataF32x4<'a> {
    buffer_ref: &'a ImagePixelBuffer,
}

impl ImagePixelDataF32x4<'_> {
    pub fn from_buffer(buffer_ref: &ImagePixelBuffer) -> ImagePixelDataF32x4 {
        ImagePixelDataF32x4 { buffer_ref }
    }
}

impl GetPixel for ImagePixelDataF32x4<'_> {
    type Pixel = (f32, f32, f32, f32);

    fn get_pixel(&self, position: Vec2<usize>) -> Self::Pixel {
        let column = position.x();
        let row = position.y();

        let index = (row * self.buffer_ref.image_width()) + column;
        let slice = self.buffer_ref.as_slice_f32x4();
        let pixel: (f32, f32, f32, f32) = slice[index];
        pixel
    }
}

#[derive(Debug)]
pub struct ImagePixelDataF64x2 {
    pub width: usize,
    pub height: usize,
    pub data: Vec<(f64, f64)>,
}

impl ImagePixelDataF64x2 {
    pub fn new() -> ImagePixelDataF64x2 {
        ImagePixelDataF64x2 {
            width: 0,
            height: 0,
            data: Vec::new(),
        }
    }
}

impl GetPixel for ImagePixelDataF64x2 {
    type Pixel = (f64, f64);

    fn get_pixel(&self, position: Vec2<usize>) -> Self::Pixel {
        let column = position.x();
        let row = position.y();

        let index = (row * self.width) + column;
        let pixel: (f64, f64) = self.data[index];
        pixel
    }
}
