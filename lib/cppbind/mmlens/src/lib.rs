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

// use crate::constants::MIN_DISTORT_SAMPLES;
// use crate::constants::THREAD_TASK_BREAK_UP_FACTOR;
// use crate::cxxbridge::ffi::CameraParameters as BindCameraParameters;
// use crate::cxxbridge::ffi::LensModelType as BindLensModelType;
// use crate::cxxbridge::ffi::LensParameters as BindLensParameters;
// use crate::cxxbridge::ffi::Parameters3deClassic as BindParameters3deClassic;

// use rayon::prelude::*;

// use mmlens_rust::image_read_metadata_exr as core_image_read_metadata_exr;
// use mmlens_rust::image_read_pixels_exr_rgba_f32 as core_image_read_pixels_exr_rgba_f32;
// use mmlens_rust::image_write_pixels_exr_rgba_f32 as core_image_write_pixels_exr_rgba_f32;

mod constants;
pub mod cxxbridge;
mod lens_parameters;

// fn multi_thread_sample_chunk_size(
//     num_threads: usize,
//     image_width: usize,
//     image_height: usize,
//     data_stride: usize,
// ) -> usize {
//     let sample_count = image_width * image_height;
//     let one_sample_line_size = image_width * data_stride;
//     let min_sample_lines = 1;
//     let sample_line_chunks = std::cmp::max(
//         min_sample_lines,
//         image_height / (num_threads * THREAD_TASK_BREAK_UP_FACTOR),
//     );
//     let sample_line_data_size = one_sample_line_size * sample_line_chunks;
//     sample_line_data_size
// }

// fn should_use_multi_threading(
//     num_threads: usize,
//     image_width: usize,
//     image_height: usize,
//     data_stride: usize,
// ) -> bool {
//     if num_threads == 1 {
//         return false;
//     }

//     let sample_count = image_width * image_height;
//     sample_count > MIN_DISTORT_SAMPLES
// }

// // Undistorts the input 'working_data' coordinates, and overrides the
// // 'working_data' memory with the newly computed values.
// fn apply_intermediate_undistort_classic(
//     image_width: usize,
//     image_height: usize,
//     working_data: &mut [f64],
//     camera_parameters: BindCameraParameters,
//     lens_parameters: BindParameters3deClassic,
// ) -> bool {
//     let mut ok = false;

//     let total_sample_count = image_width * image_height;
//     let num_threads = rayon::current_num_threads();
//     let data_stride = 2; // Each sample is a 2D coordinate.
//     let use_multi_threading = should_use_multi_threading(
//         num_threads,
//         image_width,
//         image_height,
//         data_stride,
//     );

//     // TODO: Construct a 3DE Classic lens distortion plug-in with
//     // parameters.
//     //
//     // TODO: Can we pass this across threads? The underlying LDPK
//     // implementation says that it's thread safe, so we should be able
//     // to. We do NOT want to create one LDPK Plug-in per-task, because
//     // that would be very costly. We also cannot duplicate/copy the
//     // lens model plug-in and then send the copies across threads,
//     // which is annoying.
//     let lens = Lens::new(camera_parameters, lens_parameters);

//     if use_multi_threading == false {
//         // TODO: Call C++ code to do undistortion on all samples.
//         ok = cpp_apply_undistort_3de_classic_f64_f64(
//             working_data,
//             data_stride,
//             total_sample_count,
//             working_data,
//             data_stride,
//             total_sample_count,
//             lens,
//         );
//     } else {
//         // TODO: Use Rayon.

//         // TODO: Construct a 3DE Classic lens distortion plug-in with
//         // parameters.
//         let lens = Lens::new(camera_parameters, lens_parameters);

//         let sample_line_data_size = multi_thread_sample_chunk_size(
//             num_threads,
//             image_width,
//             image_height,
//             data_stride,
//         );

//         working_data
//             .par_chunks_mut(sample_line_data_size)
//             .for_each(|slice| {
//                 ok = cpp_apply_undistort_3de_classic_f64_f64(
//                     slice,
//                     data_stride,
//                     slice.size(),
//                     slice,
//                     data_stride,
//                     slice.size(),
//                     lens,
//                 );
//             });
//     }
//     ok
// }

// // Converts the input f64 data into f32 data as the final data
// // representation, ready to be written to an EXR file.
// fn apply_pixels_undistort_classic(
//     image_width: usize,
//     image_height: usize,
//     image_num_channels: usize,
//     working_data: &mut [f64],
//     pixel_data: &mut [f32],
//     camera_parameters: BindCameraParameters,
//     lens_parameters: BindParameters3deClassic,
// ) -> bool {
//     true
// }

// pub fn shim_initialize_thread_pool(num_threads: i32) -> bool {
//     // TODO: Use 'rayon::ThreadPoolBuilder::build_global()' to
//     // initialize a thread pool to be used by mmLens.
//     //
//     // https://docs.rs/rayon/latest/rayon/struct.ThreadPoolBuilder.html#method.build_global

//     true
// }

// pub fn shim_apply_undistort_stmap(
//     pixel_data: &mut [f32],
//     working_data: &mut [f64],
//     image_width: usize,
//     image_height: usize,
//     image_num_channels: usize,
//     camera_parameters: BindCameraParameters,
//     lens_parameters: Vec<BindLensParameters>,
// ) -> bool {
//     assert!(
//         pixel_data.length()
//             == (image_width * image_height * image_num_channels)
//     );
//     // 'working_data' is expected to only contain 2 values (X and Y)
//     // for each pixel. That's all we need and we don't want to waste
//     // memory.
//     assert!(working_data.length() == (image_width * image_height * 2));

//     // TODO: Initialize the input working data to be 'identity' ST-Map?

//     let lens_count = lens_parameters.length();
//     let mut ok = false;
//     for (i, lens_param) in lens_parameters.enumerate() {
//         let is_last_lens = i >= lens_count;
//         ok = match lens_param.mode {
//             BindLensModelType::TdeClassic => {
//                 let lens_classic_parameters = lens_parameters.as_tde_classic();
//                 if !is_last_lens {
//                     apply_intermediate_undistort_classic(
//                         image_width,
//                         image_height,
//                         image_num_channels,
//                         working_data,
//                         camera_parameters,
//                         lens_classic_parameters,
//                     )
//                 } else {
//                     apply_pixels_undistort_classic(
//                         image_width,
//                         image_height,
//                         image_num_channels,
//                         working_data,
//                         pixel_data,
//                         camera_parameters,
//                         lens_classic_parameters,
//                     )
//                 }
//             }
//             _ => panic!("Unsupported LensModelType."),
//         };
//         if ok == false {
//             break;
//         }
//     }

//     // for row in 0..image_height {
//     //     for column in 0..image_width {
//     //         let index = (row * image_width) + (column * image_num_channels);
//     //         pixel_data[index]
//     //     }
//     // }

//     ok
// }
