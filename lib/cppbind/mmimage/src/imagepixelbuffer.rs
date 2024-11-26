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

use crate::cxxbridge::ffi::BufferDataType as BindBufferDataType;
use crate::cxxbridge::ffi::PixelF32x4 as BindPixelF32x4;
use mmimage_rust::pixelbuffer::BufferDataType as CoreBufferDataType;
use mmimage_rust::pixelbuffer::ImagePixelBuffer as CoreImagePixelBuffer;

#[allow(dead_code)]
fn core_to_bind_buffer_data_type(
    value: CoreBufferDataType,
) -> BindBufferDataType {
    match value {
        CoreBufferDataType::None => BindBufferDataType::None,
        CoreBufferDataType::F16 => BindBufferDataType::F16,
        CoreBufferDataType::F32 => BindBufferDataType::F32,
        CoreBufferDataType::F64 => BindBufferDataType::F64,
    }
}

fn bind_to_core_buffer_data_type(
    value: BindBufferDataType,
) -> CoreBufferDataType {
    match value {
        BindBufferDataType::None => CoreBufferDataType::None,
        BindBufferDataType::F16 => CoreBufferDataType::F16,
        BindBufferDataType::F32 => CoreBufferDataType::F32,
        BindBufferDataType::F64 => CoreBufferDataType::F64,
        _ => CoreBufferDataType::None,
    }
}

#[derive(Debug)]
pub struct ShimImagePixelBuffer {
    inner: CoreImagePixelBuffer,
}

impl ShimImagePixelBuffer {
    pub fn empty() -> Self {
        Self {
            inner: CoreImagePixelBuffer::empty(),
        }
    }

    pub fn get_inner(&self) -> &CoreImagePixelBuffer {
        &self.inner
    }

    pub fn set_inner(&mut self, pixel_data: CoreImagePixelBuffer) {
        self.inner = pixel_data;
    }

    pub fn data_type(&self) -> BindBufferDataType {
        match self.inner.data_type() {
            CoreBufferDataType::None => BindBufferDataType::None,
            CoreBufferDataType::F16 => BindBufferDataType::F16,
            CoreBufferDataType::F32 => BindBufferDataType::F32,
            CoreBufferDataType::F64 => BindBufferDataType::F64,
        }
    }

    pub fn image_width(&self) -> usize {
        self.inner.image_width()
    }

    pub fn image_height(&self) -> usize {
        self.inner.image_height()
    }

    pub fn num_channels(&self) -> usize {
        self.inner.num_channels()
    }

    pub fn pixel_count(&self) -> usize {
        self.inner.pixel_count()
    }

    pub fn element_count(&self) -> usize {
        self.inner.element_count()
    }

    pub fn as_slice_f32x4(&self) -> &[BindPixelF32x4] {
        let slice = self.inner.as_slice_f32x4();
        // SAFETY: We assume that the BindPixelF32x4's memory layout is
        // exactly the same as (f32, f32, f32, f32).
        unsafe {
            std::mem::transmute::<&[(f32, f32, f32, f32)], &[BindPixelF32x4]>(
                slice,
            )
        }
    }

    pub fn as_slice_f32x4_mut(&mut self) -> &mut [BindPixelF32x4] {
        let slice = self.inner.as_slice_f32x4_mut();
        // SAFETY: We assume that the BindPixelF32x4's memory layout is
        // exactly the same as (f32, f32, f32, f32).
        unsafe {
            std::mem::transmute::<
                &mut [(f32, f32, f32, f32)],
                &mut [BindPixelF32x4],
            >(slice)
        }
    }

    pub fn resize(
        &mut self,
        data_type: BindBufferDataType,
        image_width: usize,
        image_height: usize,
        num_channels: usize,
    ) {
        let data_type = bind_to_core_buffer_data_type(data_type);
        self.inner
            .resize(data_type, image_width, image_height, num_channels);
    }
}

pub fn shim_create_image_pixel_buffer_box() -> Box<ShimImagePixelBuffer> {
    Box::new(ShimImagePixelBuffer::empty())
}
