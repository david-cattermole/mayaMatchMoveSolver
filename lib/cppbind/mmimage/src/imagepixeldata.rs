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

use crate::cxxbridge::ffi::Pixel2DF64;
use crate::cxxbridge::ffi::PixelRgbaF32;
use mmimage_rust::pixeldata::ImagePixelData2DF64 as CoreImagePixelData2DF64;
use mmimage_rust::pixeldata::ImagePixelDataRgbaF32 as CoreImagePixelDataRgbaF32;

#[derive(Debug, Clone)]
pub struct ShimImagePixelDataRgbaF32 {
    inner: CoreImagePixelDataRgbaF32,
}

#[derive(Debug, Clone)]
pub struct ShimImagePixelData2DF64 {
    inner: CoreImagePixelData2DF64,
}

impl ShimImagePixelDataRgbaF32 {
    pub fn new() -> Self {
        Self {
            inner: CoreImagePixelDataRgbaF32::new(),
        }
    }

    pub fn get_inner(&self) -> &CoreImagePixelDataRgbaF32 {
        &self.inner
    }

    pub fn set_inner(&mut self, pixel_data: CoreImagePixelDataRgbaF32) {
        self.inner = pixel_data;
    }

    pub fn width(&self) -> usize {
        self.inner.width
    }

    pub fn height(&self) -> usize {
        self.inner.height
    }

    pub fn data(&self) -> &[PixelRgbaF32] {
        let slice = &self.inner.data[..];
        // SAFETY: We assume that the PixelRgbaF32's memory layout is
        // exactly the same as (f32, f32, f32, f32).
        unsafe {
            std::mem::transmute::<&[(f32, f32, f32, f32)], &[PixelRgbaF32]>(
                slice,
            )
        }
    }

    pub fn data_mut(&mut self) -> &mut [PixelRgbaF32] {
        let slice = &mut self.inner.data[..];
        // SAFETY: We assume that the PixelRgbaF32's memory layout is
        // exactly the same as (f32, f32, f32, f32).
        unsafe {
            std::mem::transmute::<
                &mut [(f32, f32, f32, f32)],
                &mut [PixelRgbaF32],
            >(slice)
        }
    }
}

impl ShimImagePixelData2DF64 {
    pub fn new() -> Self {
        Self {
            inner: CoreImagePixelData2DF64::new(),
        }
    }

    pub fn get_inner(&self) -> &CoreImagePixelData2DF64 {
        &self.inner
    }

    pub fn set_inner(&mut self, pixel_data: CoreImagePixelData2DF64) {
        self.inner = pixel_data;
    }

    pub fn width(&self) -> usize {
        self.inner.width
    }

    pub fn height(&self) -> usize {
        self.inner.height
    }

    pub fn data(&self) -> &[Pixel2DF64] {
        let slice = &self.inner.data[..];
        // SAFETY: We assume that the Pixel2DF64's memory layout is
        // exactly the same as (f64, f64).
        unsafe { std::mem::transmute::<&[(f64, f64)], &[Pixel2DF64]>(slice) }
    }

    pub fn data_mut(&mut self) -> &mut [Pixel2DF64] {
        let slice = &mut self.inner.data[..];
        // SAFETY: We assume that the Pixel2DF64's memory layout is
        // exactly the same as (f64, f64).
        unsafe {
            std::mem::transmute::<&mut [(f64, f64)], &mut [Pixel2DF64]>(slice)
        }
    }
}

pub fn shim_create_image_pixel_data_rgba_f32_box(
) -> Box<ShimImagePixelDataRgbaF32> {
    Box::new(ShimImagePixelDataRgbaF32::new())
}

pub fn shim_create_image_pixel_data_2d_f64_box() -> Box<ShimImagePixelData2DF64>
{
    Box::new(ShimImagePixelData2DF64::new())
}
