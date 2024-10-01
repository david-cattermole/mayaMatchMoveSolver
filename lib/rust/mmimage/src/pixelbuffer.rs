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

#[derive(Copy, Clone, Debug, PartialEq, Eq)]
pub enum BufferDataType {
    None = 0,
    F32 = 1,
    F64 = 2,
}

/// This is a general data structure for storing pixels in memory.
///
/// The amount of memory can be grown if needed.
///
/// The stored data is 64-bit aligned, to allow SSE and AVX
/// instructions can be used by the compiler.
#[derive(Clone, Debug)]
pub struct ImagePixelBuffer {
    data_type: BufferDataType,
    image_width: usize,
    image_height: usize,
    num_channels: usize,
    // TODO: Should we use the maximum data type as the element here?
    // That way we might be able to enable the maximum amount of SIMD
    // instructions with auto-vectorization, because the data would be
    // correctly aligned at all times, at the cost of a little bit
    // extra memory used.
    data: Vec<f64>,
}

impl ImagePixelBuffer {
    pub fn empty() -> ImagePixelBuffer {
        ImagePixelBuffer {
            data_type: BufferDataType::None,
            image_width: 0,
            image_height: 0,
            num_channels: 0,
            data: Vec::new(),
        }
    }

    pub fn from_data(
        data_type: BufferDataType,
        image_width: usize,
        image_height: usize,
        num_channels: usize,
        data: Vec<f64>,
    ) -> ImagePixelBuffer {
        ImagePixelBuffer {
            data_type,
            image_width,
            image_height,
            num_channels,
            data,
        }
    }

    /// The type of data stored in the buffer; f32 or f64.
    pub fn data_type(&self) -> BufferDataType {
        self.data_type
    }

    /// Get the image width of the underlying buffer.
    pub fn image_width(&self) -> usize {
        self.image_width
    }

    /// Get the image height of the underlying buffer.
    pub fn image_height(&self) -> usize {
        self.image_height
    }

    /// Get the number of image channels in the underlying buffer.
    pub fn num_channels(&self) -> usize {
        self.num_channels
    }

    /// The number of pixels that can be held in the buffer.
    ///
    /// For a single RGBA pixel, this would return 1.
    pub fn pixel_count(&self) -> usize {
        let mut count = 0;
        if self.data_type == BufferDataType::None {
            // There is (conceptually) no count.
            count = 0;
        } else if self.data_type == BufferDataType::F32 {
            count = self.data.len()
                * (std::mem::size_of::<f64>() / std::mem::size_of::<f32>());
            count /= self.num_channels;
        } else if self.data_type == BufferDataType::F64 {
            count = self.data.len() / self.num_channels;
        }
        count
    }

    /// The number of values that can be held in the buffer.
    ///
    /// For a single RGBA pixel, this would return 4.
    pub fn element_count(&self) -> usize {
        let mut count = 0;
        if self.data_type == BufferDataType::None {
            // There is (conceptually) no count.
            count = 0;
        } else if self.data_type == BufferDataType::F32 {
            count = self.data.len()
                * (std::mem::size_of::<f64>() / std::mem::size_of::<f32>());
        } else if self.data_type == BufferDataType::F64 {
            count = self.data.len();
        }
        count
    }

    /// Get a slice of the underlying memory buffer, mutable or not.
    pub fn as_slice_f64(&self) -> &[f64] {
        &self.data[..]
    }
    pub fn as_slice_f32x2(&self) -> &[(f32, f32)] {
        unsafe { std::mem::transmute::<&[f64], &[(f32, f32)]>(&self.data[..]) }
    }
    // fn as_slice_f64x2(&self) -> &[(f64, f64)] {}
    pub fn as_slice_f32x4(&self) -> &[(f32, f32, f32, f32)] {
        unsafe {
            std::mem::transmute::<&[f64], &[(f32, f32, f32, f32)]>(
                &self.data[..],
            )
        }
    }
    // fn as_slice_f64x4(&self) -> &[(f64, f64, f64, f64)] {}
    // fn as_slice_f64_mut(&mut self) -> &mut [f64] {}
    // fn as_slice_f64x2_mut(&mut self) -> &mut [(f64, f64)] {}
    // fn as_slice_f32x2_mut(&mut self) -> &mut [(f32, f32)] {}
    pub fn as_slice_f32x4_mut(&mut self) -> &mut [(f32, f32, f32, f32)] {
        unsafe {
            std::mem::transmute::<&mut [f64], &mut [(f32, f32, f32, f32)]>(
                &mut self.data[..],
            )
        }
    }
    // fn as_slice_f64x4_mut(&mut self) -> &mut [(f64, f64, f64, f64)] {}

    /// Keeps the current buffer's data and resizes the memory to hold
    /// more elements.
    ///
    /// If less memory is needed for the needed pixels, the underlying
    /// memory buffer is strunk.
    pub fn resize(
        &mut self,
        data_type: BufferDataType,
        image_width: usize,
        image_height: usize,
        num_channels: usize,
    ) {
        self.image_width = image_width;
        self.image_height = image_height;
        let pixel_count = image_width * image_height;
        self.data_type = data_type;
        self.num_channels = num_channels;
        match data_type {
            BufferDataType::None => {
                // No resizing is needed or possible.
            }
            BufferDataType::F32 => {
                let byte_count = std::mem::size_of::<f32>()
                    * self.num_channels
                    * pixel_count;
                let new_size =
                    (byte_count as f64) / (std::mem::size_of::<f64>() as f64);
                self.data.resize(new_size.ceil() as usize, 0.0);
            }
            BufferDataType::F64 => {
                let new_size = self.num_channels * pixel_count;
                self.data.resize(new_size, 0.0);
            }
        }
    }
}
