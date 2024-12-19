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

use rayon::prelude::*;

use crate::cxxbridge::ffi::CameraParameters as BindCameraParameters;
use crate::cxxbridge::ffi::DistortionDirection as BindDistortionDirection;

use crate::cxxbridge::ffi::apply_f64_to_f32_3de_classic;
use crate::cxxbridge::ffi::apply_f64_to_f64_3de_classic;
use crate::cxxbridge::ffi::apply_identity_to_f32_3de_classic;
use crate::cxxbridge::ffi::apply_identity_to_f64_3de_classic;
use crate::cxxbridge::ffi::Parameters3deClassic as BindParameters3deClassic;

use crate::cxxbridge::ffi::apply_f64_to_f32_3de_radial_std_deg4;
use crate::cxxbridge::ffi::apply_f64_to_f64_3de_radial_std_deg4;
use crate::cxxbridge::ffi::apply_identity_to_f32_3de_radial_std_deg4;
use crate::cxxbridge::ffi::apply_identity_to_f64_3de_radial_std_deg4;
use crate::cxxbridge::ffi::Parameters3deRadialStdDeg4 as BindParameters3deRadialStdDeg4;

use crate::cxxbridge::ffi::apply_f64_to_f32_3de_anamorphic_std_deg4;
use crate::cxxbridge::ffi::apply_f64_to_f64_3de_anamorphic_std_deg4;
use crate::cxxbridge::ffi::apply_identity_to_f32_3de_anamorphic_std_deg4;
use crate::cxxbridge::ffi::apply_identity_to_f64_3de_anamorphic_std_deg4;
use crate::cxxbridge::ffi::Parameters3deAnamorphicStdDeg4 as BindParameters3deAnamorphicStdDeg4;

use crate::cxxbridge::ffi::apply_f64_to_f32_3de_anamorphic_std_deg4_rescaled;
use crate::cxxbridge::ffi::apply_f64_to_f64_3de_anamorphic_std_deg4_rescaled;
use crate::cxxbridge::ffi::apply_identity_to_f32_3de_anamorphic_std_deg4_rescaled;
use crate::cxxbridge::ffi::apply_identity_to_f64_3de_anamorphic_std_deg4_rescaled;
use crate::cxxbridge::ffi::Parameters3deAnamorphicStdDeg4Rescaled as BindParameters3deAnamorphicStdDeg4Rescaled;

use crate::cxxbridge::ffi::apply_f64_to_f32_3de_anamorphic_std_deg6;
use crate::cxxbridge::ffi::apply_f64_to_f64_3de_anamorphic_std_deg6;
use crate::cxxbridge::ffi::apply_identity_to_f32_3de_anamorphic_std_deg6;
use crate::cxxbridge::ffi::apply_identity_to_f64_3de_anamorphic_std_deg6;
use crate::cxxbridge::ffi::Parameters3deAnamorphicStdDeg6 as BindParameters3deAnamorphicStdDeg6;

use crate::cxxbridge::ffi::apply_f64_to_f32_3de_anamorphic_std_deg6_rescaled;
use crate::cxxbridge::ffi::apply_f64_to_f64_3de_anamorphic_std_deg6_rescaled;
use crate::cxxbridge::ffi::apply_identity_to_f32_3de_anamorphic_std_deg6_rescaled;
use crate::cxxbridge::ffi::apply_identity_to_f64_3de_anamorphic_std_deg6_rescaled;
use crate::cxxbridge::ffi::Parameters3deAnamorphicStdDeg6Rescaled as BindParameters3deAnamorphicStdDeg6Rescaled;

/// Valid num-thread values are -1 to i32::MAX. If given -2, -1 is
/// assumed.
///
/// Returns the number of threads initalized, or 0 if an error
/// occurred during initialization.
pub fn initialize_global_thread_pool(num_threads: i32) -> i32 {
    let mut num_threads: i32 = std::cmp::max(-1, num_threads);
    if num_threads == -1 {
        num_threads = num_cpus::get_physical() as i32;
    } else if num_threads == 0 {
        num_threads = num_cpus::get() as i32;
    }
    let result = rayon::ThreadPoolBuilder::new()
        .num_threads(num_threads as usize)
        .build_global();
    match result {
        Ok(_) => num_threads,
        Err(_) => 0,
    }
}

fn apply_identity_func<
    T: Copy + Send + Sync,
    LensParameter: Copy + Sized + Send + Sync,
>(
    direction: BindDistortionDirection,
    image_width: usize,
    image_height: usize,
    start_image_width: usize,
    start_image_height: usize,
    end_image_width: usize,
    end_image_height: usize,
    out_data: &mut [T],
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: LensParameter,
    func: unsafe fn(
        BindDistortionDirection,

        // Image size
        usize,
        usize,

        // Image sub-window
        usize,
        usize,
        usize,
        usize,

        // Output buffer
        *mut T,
        usize,
        usize,

        // Camera and lens parameters.
        BindCameraParameters,
        f64,
        LensParameter,
    ),
) {
    let out_data_ptr = out_data.as_mut_ptr();
    let out_data_size = out_data.len();

    // SAFETY: This is a C++ function needing to be called as
    // 'unsafe'. We hope/assume that our C++ code stays within the
    // memory bounds given.
    unsafe {
        func(
            direction,
            image_width,
            image_height,
            start_image_width,
            start_image_height,
            end_image_width,
            end_image_height,
            out_data_ptr,
            out_data_size,
            out_data_stride,
            camera_parameters,
            film_back_radius_cm,
            lens_parameters,
        );
    }
}

fn apply_identity_multithread<
    T: Copy + Send + Sync,
    LensParameter: Copy + Sized + Send + Sync,
>(
    direction: BindDistortionDirection,
    image_width: usize,
    image_height: usize,
    num_channels: usize,
    out_data_ptr: *mut T,
    out_data_size: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: LensParameter,
    func: unsafe fn(
        BindDistortionDirection,

        // Image size
        usize,
        usize,

        // Image sub-window
        usize,
        usize,
        usize,
        usize,

        // Output buffer
        *mut T,
        usize,
        usize,

        // Camera and lens parameters.
        BindCameraParameters,
        f64,
        LensParameter,
    ),
) {
    // SAFETY: Reconstructs the original slice from the
    // pointer/size. We assume the values given are good.
    let out_data =
        unsafe { std::slice::from_raw_parts_mut(out_data_ptr, out_data_size) };
    let out_data_ptr_num = out_data_ptr as usize;

    // Number of scanlines to process at once.
    let parallel_scanlines: usize = 1;

    let chunk_size = std::cmp::min(
        out_data_size,
        image_width * num_channels * parallel_scanlines,
    );
    let remainder_count = out_data_size % chunk_size;
    out_data
        .par_chunks_exact_mut(chunk_size)
        .for_each(|out_data_chunk| {
            // Without this workaround we might need to use
            // 'rayon::iter::split()', but that seemed slightly less
            // performant and a little complicated.
            let out_data_chunk_ptr = out_data_chunk.as_ptr();
            let image_height_offset = (out_data_chunk_ptr as usize
                - out_data_ptr_num)
                / (core::mem::size_of::<T>() * chunk_size);

            let start_image_width = 0;
            let start_image_height = image_height_offset * parallel_scanlines;
            let end_image_width = image_width;
            let end_image_height = start_image_height + parallel_scanlines;

            apply_identity_func(
                direction,
                image_width,
                image_height,
                start_image_width,
                start_image_height,
                end_image_width,
                end_image_height,
                out_data_chunk,
                num_channels,
                camera_parameters,
                film_back_radius_cm,
                lens_parameters,
                func,
            );
        });

    // Process the remaining elements
    if remainder_count > 0 {
        let remainder_rows = remainder_count / image_width;

        let start_image_width = 0;
        let start_image_height = image_height - remainder_rows;
        let end_image_width = image_width;
        let end_image_height = image_height;

        apply_identity_func(
            direction,
            image_width,
            image_height,
            start_image_width,
            start_image_height,
            end_image_width,
            end_image_height,
            out_data,
            num_channels,
            camera_parameters,
            film_back_radius_cm,
            lens_parameters,
            func,
        );
    }
}

// "Most" CPUs have a cache line of 64 bytes.
const CPU_CACHE_LINE_NUM_BYTES: usize = 64;

// Number of pixels per CPU cache line.
const CPU_CACHE_LINE_PIXEL_COUNT: usize =
    CPU_CACHE_LINE_NUM_BYTES / std::mem::size_of::<f64>();

// Each parallel task will work on 64 cache lines in a single "task".
//
// This means each task will use 4KB (64 * 64 bytes = 4096 bytes),
// which is about 1/8th of the "average" CPU's L1 cache size (32KB
// per-CPU core).
//
// We probably shouldn't use all of the CPU cache. The operating
// system is running other software on those cores. If we max-out the
// L1 cache then the CPU will be forced to flush our all our data when
// another process wants to run.
//
// TODO: Do tests to confirm if 64 is a reasonable number of cache
// lines to use for maximum performance.
const NUM_CACHE_LINES_PER_TASK: usize = 64;

fn apply_buffer_func<
    T: Copy + Send + Sync,
    LensParameter: Copy + Sized + Send + Sync,
>(
    direction: BindDistortionDirection,
    pixel_num_start: usize,
    pixel_num_end: usize,
    in_data: &[f64],
    in_data_stride: usize,
    out_data: &mut [T],
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: LensParameter,
    func: unsafe fn(
        BindDistortionDirection,

        // Data chunk sub-window.
        usize,
        usize,

        // Input buffer
        *const f64,
        usize,
        usize,

        // Output buffer
        *mut T,
        usize,
        usize,

        // Camera and lens parameters.
        BindCameraParameters,
        f64,
        LensParameter,
    ),
) {
    let in_data_chunk_ptr = in_data.as_ptr();
    let in_data_chunk_size = in_data.len();

    // SAFETY: The slice of data given to this function is the slice
    // of memory offset from the original data. 'out_data' is expected
    // to a subset of the original data. Our 'func' below expects that
    // the pointers given are to the original data memory. Therefore
    // we remove the offset into the original data get a pointer (and
    // size) of the original data to be passed to 'func.'
    let out_num_elements = pixel_num_start * out_data_stride;
    let out_data_ptr = unsafe { out_data.as_mut_ptr().sub(out_num_elements) };
    let out_data_size = out_data.len() + out_num_elements;

    // SAFETY: This is a C++ function needing to be called as
    // 'unsafe'. We hope/assume that our C++ code stays within the
    // memory bounds given.
    unsafe {
        func(
            direction,
            pixel_num_start,
            pixel_num_end,
            in_data_chunk_ptr,
            in_data_chunk_size,
            in_data_stride,
            out_data_ptr,
            out_data_size,
            out_data_stride,
            camera_parameters,
            film_back_radius_cm,
            lens_parameters,
        );
    }
}

fn apply_buffer_multithread<
    T: Copy + Send + Sync,
    LensParameter: Copy + Sized + Send + Sync,
>(
    direction: BindDistortionDirection,
    in_data_ptr: *const f64,
    in_data_size: usize,
    in_data_stride: usize,
    out_data_ptr: *mut T,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: LensParameter,
    func: unsafe fn(
        BindDistortionDirection,

        // Data chunk sub-window.
        usize,
        usize,

        // Input buffer
        *const f64,
        usize,
        usize,

        // Output buffer
        *mut T,
        usize,
        usize,

        // Camera and lens parameters.
        BindCameraParameters,
        f64,
        LensParameter,
    ),
) {
    // SAFETY: Reconstructs the original slice from the
    // pointer/size. We assume the values given are good.
    let in_data =
        unsafe { std::slice::from_raw_parts(in_data_ptr, in_data_size) };
    let out_data =
        unsafe { std::slice::from_raw_parts_mut(out_data_ptr, out_data_size) };
    let out_data_ptr_num = out_data_ptr as usize;

    let reasonable_chunk_size = (CPU_CACHE_LINE_PIXEL_COUNT / out_data_stride)
        * NUM_CACHE_LINES_PER_TASK;
    let chunk_size = if reasonable_chunk_size > out_data_size {
        out_data_size
    } else {
        reasonable_chunk_size
    };
    let remainder_count = out_data_size % chunk_size;

    out_data
        .par_chunks_exact_mut(chunk_size)
        .for_each(|out_data_chunk| {
            // This hack is extremely important to calculating the
            // correct sub-window into the buffer data given only the
            // new and original pointer. This feels kind of dirty.
            // Without this workaround we might need to use
            // 'rayon::iter::split()', but that seemed slightly less
            // performant and a little complicated.
            let out_data_chunk_ptr = out_data_chunk.as_mut_ptr();
            let data_chunk_offset = (out_data_chunk_ptr as usize
                - out_data_ptr_num)
                / (core::mem::size_of::<T>() * chunk_size);

            let chunk_pixel_count = chunk_size / out_data_stride;
            let pixel_num_start = data_chunk_offset * chunk_pixel_count;
            let pixel_num_end = pixel_num_start + chunk_pixel_count;

            apply_buffer_func(
                direction,
                pixel_num_start,
                pixel_num_end,
                in_data,
                in_data_stride,
                out_data_chunk,
                out_data_stride,
                camera_parameters,
                film_back_radius_cm,
                lens_parameters,
                func,
            );
        });

    // Process the remaining elements
    if remainder_count > 0 {
        let pixel_num_start =
            (out_data_size - remainder_count) / out_data_stride;
        let pixel_num_end = out_data_size / out_data_stride;
        let out_data_start = pixel_num_start * out_data_stride;
        let out_data_chunk = &mut out_data[out_data_start..];
        apply_buffer_func(
            direction,
            pixel_num_start,
            pixel_num_end,
            in_data,
            in_data_stride,
            out_data_chunk,
            out_data_stride,
            camera_parameters,
            film_back_radius_cm,
            lens_parameters,
            func,
        );
    }
}

//////////////////////////////////////////////////////////////////////
// 3DE Classic

pub fn apply_identity_to_f64_3de_classic_multithread(
    direction: BindDistortionDirection,
    image_width: usize,
    image_height: usize,
    out_data_ptr: *mut f64,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deClassic,
) {
    apply_identity_multithread::<f64, BindParameters3deClassic>(
        direction,
        image_width,
        image_height,
        out_data_stride,
        out_data_ptr,
        out_data_size,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_identity_to_f64_3de_classic,
    );
}

pub fn apply_identity_to_f32_3de_classic_multithread(
    direction: BindDistortionDirection,
    image_width: usize,
    image_height: usize,
    out_data_ptr: *mut f32,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deClassic,
) {
    apply_identity_multithread::<f32, BindParameters3deClassic>(
        direction,
        image_width,
        image_height,
        out_data_stride,
        out_data_ptr,
        out_data_size,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_identity_to_f32_3de_classic,
    );
}

pub fn apply_f64_to_f32_3de_classic_multithread(
    direction: BindDistortionDirection,
    in_data_ptr: *const f64,
    in_data_size: usize,
    in_data_stride: usize,
    out_data_ptr: *mut f32,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deClassic,
) {
    apply_buffer_multithread::<f32, BindParameters3deClassic>(
        direction,
        in_data_ptr,
        in_data_size,
        in_data_stride,
        out_data_ptr,
        out_data_size,
        out_data_stride,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_f64_to_f32_3de_classic,
    );
}

pub fn apply_f64_to_f64_3de_classic_multithread(
    direction: BindDistortionDirection,
    in_data_ptr: *const f64,
    in_data_size: usize,
    in_data_stride: usize,
    out_data_ptr: *mut f64,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deClassic,
) {
    apply_buffer_multithread::<f64, BindParameters3deClassic>(
        direction,
        in_data_ptr,
        in_data_size,
        in_data_stride,
        out_data_ptr,
        out_data_size,
        out_data_stride,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_f64_to_f64_3de_classic,
    );
}

//////////////////////////////////////////////////////////////////////
// 3DE Radial Decentered Degree 4 Cylindric

pub fn apply_identity_to_f64_3de_radial_std_deg4_multithread(
    direction: BindDistortionDirection,
    image_width: usize,
    image_height: usize,
    out_data_ptr: *mut f64,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deRadialStdDeg4,
) {
    apply_identity_multithread::<f64, BindParameters3deRadialStdDeg4>(
        direction,
        image_width,
        image_height,
        out_data_stride,
        out_data_ptr,
        out_data_size,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_identity_to_f64_3de_radial_std_deg4,
    );
}

pub fn apply_identity_to_f32_3de_radial_std_deg4_multithread(
    direction: BindDistortionDirection,
    image_width: usize,
    image_height: usize,
    out_data_ptr: *mut f32,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deRadialStdDeg4,
) {
    apply_identity_multithread::<f32, BindParameters3deRadialStdDeg4>(
        direction,
        image_width,
        image_height,
        out_data_stride,
        out_data_ptr,
        out_data_size,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_identity_to_f32_3de_radial_std_deg4,
    );
}

pub fn apply_f64_to_f32_3de_radial_std_deg4_multithread(
    direction: BindDistortionDirection,
    in_data_ptr: *const f64,
    in_data_size: usize,
    in_data_stride: usize,
    out_data_ptr: *mut f32,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deRadialStdDeg4,
) {
    apply_buffer_multithread::<f32, BindParameters3deRadialStdDeg4>(
        direction,
        in_data_ptr,
        in_data_size,
        in_data_stride,
        out_data_ptr,
        out_data_size,
        out_data_stride,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_f64_to_f32_3de_radial_std_deg4,
    );
}

pub fn apply_f64_to_f64_3de_radial_std_deg4_multithread(
    direction: BindDistortionDirection,
    in_data_ptr: *const f64,
    in_data_size: usize,
    in_data_stride: usize,
    out_data_ptr: *mut f64,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deRadialStdDeg4,
) {
    apply_buffer_multithread::<f64, BindParameters3deRadialStdDeg4>(
        direction,
        in_data_ptr,
        in_data_size,
        in_data_stride,
        out_data_ptr,
        out_data_size,
        out_data_stride,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_f64_to_f64_3de_radial_std_deg4,
    );
}

//////////////////////////////////////////////////////////////////////
// 3DE Anamorphic Degree 4 Rotate Squeeze XY

pub fn apply_identity_to_f64_3de_anamorphic_std_deg4_multithread(
    direction: BindDistortionDirection,
    image_width: usize,
    image_height: usize,
    out_data_ptr: *mut f64,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deAnamorphicStdDeg4,
) {
    apply_identity_multithread::<f64, BindParameters3deAnamorphicStdDeg4>(
        direction,
        image_width,
        image_height,
        out_data_stride,
        out_data_ptr,
        out_data_size,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_identity_to_f64_3de_anamorphic_std_deg4,
    );
}

pub fn apply_identity_to_f32_3de_anamorphic_std_deg4_multithread(
    direction: BindDistortionDirection,
    image_width: usize,
    image_height: usize,
    out_data_ptr: *mut f32,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deAnamorphicStdDeg4,
) {
    apply_identity_multithread::<f32, BindParameters3deAnamorphicStdDeg4>(
        direction,
        image_width,
        image_height,
        out_data_stride,
        out_data_ptr,
        out_data_size,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_identity_to_f32_3de_anamorphic_std_deg4,
    );
}

pub fn apply_f64_to_f32_3de_anamorphic_std_deg4_multithread(
    direction: BindDistortionDirection,
    in_data_ptr: *const f64,
    in_data_size: usize,
    in_data_stride: usize,
    out_data_ptr: *mut f32,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deAnamorphicStdDeg4,
) {
    apply_buffer_multithread::<f32, BindParameters3deAnamorphicStdDeg4>(
        direction,
        in_data_ptr,
        in_data_size,
        in_data_stride,
        out_data_ptr,
        out_data_size,
        out_data_stride,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_f64_to_f32_3de_anamorphic_std_deg4,
    );
}

pub fn apply_f64_to_f64_3de_anamorphic_std_deg4_multithread(
    direction: BindDistortionDirection,
    in_data_ptr: *const f64,
    in_data_size: usize,
    in_data_stride: usize,
    out_data_ptr: *mut f64,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deAnamorphicStdDeg4,
) {
    apply_buffer_multithread::<f64, BindParameters3deAnamorphicStdDeg4>(
        direction,
        in_data_ptr,
        in_data_size,
        in_data_stride,
        out_data_ptr,
        out_data_size,
        out_data_stride,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_f64_to_f64_3de_anamorphic_std_deg4,
    );
}

//////////////////////////////////////////////////////////////////////
// 3DE Anamorphic Degree 4 Rotate Squeeze XY Rescaled

pub fn apply_identity_to_f64_3de_anamorphic_std_deg4_rescaled_multithread(
    direction: BindDistortionDirection,
    image_width: usize,
    image_height: usize,
    out_data_ptr: *mut f64,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deAnamorphicStdDeg4Rescaled,
) {
    apply_identity_multithread::<f64, BindParameters3deAnamorphicStdDeg4Rescaled>(
        direction,
        image_width,
        image_height,
        out_data_stride,
        out_data_ptr,
        out_data_size,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_identity_to_f64_3de_anamorphic_std_deg4_rescaled,
    );
}

pub fn apply_identity_to_f32_3de_anamorphic_std_deg4_rescaled_multithread(
    direction: BindDistortionDirection,
    image_width: usize,
    image_height: usize,
    out_data_ptr: *mut f32,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deAnamorphicStdDeg4Rescaled,
) {
    apply_identity_multithread::<f32, BindParameters3deAnamorphicStdDeg4Rescaled>(
        direction,
        image_width,
        image_height,
        out_data_stride,
        out_data_ptr,
        out_data_size,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_identity_to_f32_3de_anamorphic_std_deg4_rescaled,
    );
}

pub fn apply_f64_to_f32_3de_anamorphic_std_deg4_rescaled_multithread(
    direction: BindDistortionDirection,
    in_data_ptr: *const f64,
    in_data_size: usize,
    in_data_stride: usize,
    out_data_ptr: *mut f32,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deAnamorphicStdDeg4Rescaled,
) {
    apply_buffer_multithread::<f32, BindParameters3deAnamorphicStdDeg4Rescaled>(
        direction,
        in_data_ptr,
        in_data_size,
        in_data_stride,
        out_data_ptr,
        out_data_size,
        out_data_stride,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_f64_to_f32_3de_anamorphic_std_deg4_rescaled,
    );
}

pub fn apply_f64_to_f64_3de_anamorphic_std_deg4_rescaled_multithread(
    direction: BindDistortionDirection,
    in_data_ptr: *const f64,
    in_data_size: usize,
    in_data_stride: usize,
    out_data_ptr: *mut f64,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deAnamorphicStdDeg4Rescaled,
) {
    apply_buffer_multithread::<f64, BindParameters3deAnamorphicStdDeg4Rescaled>(
        direction,
        in_data_ptr,
        in_data_size,
        in_data_stride,
        out_data_ptr,
        out_data_size,
        out_data_stride,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_f64_to_f64_3de_anamorphic_std_deg4_rescaled,
    );
}

//////////////////////////////////////////////////////////////////////
// 3DE Anamorphic Degree 6 Rotate Squeeze XY

pub fn apply_identity_to_f64_3de_anamorphic_std_deg6_multithread(
    direction: BindDistortionDirection,
    image_width: usize,
    image_height: usize,
    out_data_ptr: *mut f64,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deAnamorphicStdDeg6,
) {
    apply_identity_multithread::<f64, BindParameters3deAnamorphicStdDeg6>(
        direction,
        image_width,
        image_height,
        out_data_stride,
        out_data_ptr,
        out_data_size,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_identity_to_f64_3de_anamorphic_std_deg6,
    );
}

pub fn apply_identity_to_f32_3de_anamorphic_std_deg6_multithread(
    direction: BindDistortionDirection,
    image_width: usize,
    image_height: usize,
    out_data_ptr: *mut f32,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deAnamorphicStdDeg6,
) {
    apply_identity_multithread::<f32, BindParameters3deAnamorphicStdDeg6>(
        direction,
        image_width,
        image_height,
        out_data_stride,
        out_data_ptr,
        out_data_size,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_identity_to_f32_3de_anamorphic_std_deg6,
    );
}

pub fn apply_f64_to_f32_3de_anamorphic_std_deg6_multithread(
    direction: BindDistortionDirection,
    in_data_ptr: *const f64,
    in_data_size: usize,
    in_data_stride: usize,
    out_data_ptr: *mut f32,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deAnamorphicStdDeg6,
) {
    apply_buffer_multithread::<f32, BindParameters3deAnamorphicStdDeg6>(
        direction,
        in_data_ptr,
        in_data_size,
        in_data_stride,
        out_data_ptr,
        out_data_size,
        out_data_stride,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_f64_to_f32_3de_anamorphic_std_deg6,
    );
}

pub fn apply_f64_to_f64_3de_anamorphic_std_deg6_multithread(
    direction: BindDistortionDirection,
    in_data_ptr: *const f64,
    in_data_size: usize,
    in_data_stride: usize,
    out_data_ptr: *mut f64,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deAnamorphicStdDeg6,
) {
    apply_buffer_multithread::<f64, BindParameters3deAnamorphicStdDeg6>(
        direction,
        in_data_ptr,
        in_data_size,
        in_data_stride,
        out_data_ptr,
        out_data_size,
        out_data_stride,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_f64_to_f64_3de_anamorphic_std_deg6,
    );
}

//////////////////////////////////////////////////////////////////////
// 3DE Anamorphic Degree 6 Rotate Squeeze XY Rescaled

pub fn apply_identity_to_f64_3de_anamorphic_std_deg6_rescaled_multithread(
    direction: BindDistortionDirection,
    image_width: usize,
    image_height: usize,
    out_data_ptr: *mut f64,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deAnamorphicStdDeg6Rescaled,
) {
    apply_identity_multithread::<f64, BindParameters3deAnamorphicStdDeg6Rescaled>(
        direction,
        image_width,
        image_height,
        out_data_stride,
        out_data_ptr,
        out_data_size,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_identity_to_f64_3de_anamorphic_std_deg6_rescaled,
    );
}

pub fn apply_identity_to_f32_3de_anamorphic_std_deg6_rescaled_multithread(
    direction: BindDistortionDirection,
    image_width: usize,
    image_height: usize,
    out_data_ptr: *mut f32,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deAnamorphicStdDeg6Rescaled,
) {
    apply_identity_multithread::<f32, BindParameters3deAnamorphicStdDeg6Rescaled>(
        direction,
        image_width,
        image_height,
        out_data_stride,
        out_data_ptr,
        out_data_size,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_identity_to_f32_3de_anamorphic_std_deg6_rescaled,
    );
}

pub fn apply_f64_to_f32_3de_anamorphic_std_deg6_rescaled_multithread(
    direction: BindDistortionDirection,
    in_data_ptr: *const f64,
    in_data_size: usize,
    in_data_stride: usize,
    out_data_ptr: *mut f32,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deAnamorphicStdDeg6Rescaled,
) {
    apply_buffer_multithread::<f32, BindParameters3deAnamorphicStdDeg6Rescaled>(
        direction,
        in_data_ptr,
        in_data_size,
        in_data_stride,
        out_data_ptr,
        out_data_size,
        out_data_stride,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_f64_to_f32_3de_anamorphic_std_deg6_rescaled,
    );
}

pub fn apply_f64_to_f64_3de_anamorphic_std_deg6_rescaled_multithread(
    direction: BindDistortionDirection,
    in_data_ptr: *const f64,
    in_data_size: usize,
    in_data_stride: usize,
    out_data_ptr: *mut f64,
    out_data_size: usize,
    out_data_stride: usize,
    camera_parameters: BindCameraParameters,
    film_back_radius_cm: f64,
    lens_parameters: BindParameters3deAnamorphicStdDeg6Rescaled,
) {
    apply_buffer_multithread::<f64, BindParameters3deAnamorphicStdDeg6Rescaled>(
        direction,
        in_data_ptr,
        in_data_size,
        in_data_stride,
        out_data_ptr,
        out_data_size,
        out_data_stride,
        camera_parameters,
        film_back_radius_cm,
        lens_parameters,
        apply_f64_to_f64_3de_anamorphic_std_deg6_rescaled,
    );
}
