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

use crate::distortion_layers::shim_create_distortion_layers_box;
use crate::distortion_layers::ShimDistortionLayers;
use crate::distortion_process::initialize_global_thread_pool;
use crate::lens_io::shim_read_lens_file;

use crate::distortion_process::apply_f64_to_f32_3de_classic_multithread;
use crate::distortion_process::apply_f64_to_f64_3de_classic_multithread;
use crate::distortion_process::apply_identity_to_f32_3de_classic_multithread;
use crate::distortion_process::apply_identity_to_f64_3de_classic_multithread;

use crate::distortion_process::apply_f64_to_f32_3de_radial_std_deg4_multithread;
use crate::distortion_process::apply_f64_to_f64_3de_radial_std_deg4_multithread;
use crate::distortion_process::apply_identity_to_f32_3de_radial_std_deg4_multithread;
use crate::distortion_process::apply_identity_to_f64_3de_radial_std_deg4_multithread;

use crate::distortion_process::apply_f64_to_f32_3de_anamorphic_std_deg4_multithread;
use crate::distortion_process::apply_f64_to_f64_3de_anamorphic_std_deg4_multithread;
use crate::distortion_process::apply_identity_to_f32_3de_anamorphic_std_deg4_multithread;
use crate::distortion_process::apply_identity_to_f64_3de_anamorphic_std_deg4_multithread;

use crate::distortion_process::apply_f64_to_f32_3de_anamorphic_std_deg4_rescaled_multithread;
use crate::distortion_process::apply_f64_to_f64_3de_anamorphic_std_deg4_rescaled_multithread;
use crate::distortion_process::apply_identity_to_f32_3de_anamorphic_std_deg4_rescaled_multithread;
use crate::distortion_process::apply_identity_to_f64_3de_anamorphic_std_deg4_rescaled_multithread;

use crate::distortion_process::apply_f64_to_f32_3de_anamorphic_std_deg6_multithread;
use crate::distortion_process::apply_f64_to_f64_3de_anamorphic_std_deg6_multithread;
use crate::distortion_process::apply_identity_to_f32_3de_anamorphic_std_deg6_multithread;
use crate::distortion_process::apply_identity_to_f64_3de_anamorphic_std_deg6_multithread;

use crate::distortion_process::apply_f64_to_f32_3de_anamorphic_std_deg6_rescaled_multithread;
use crate::distortion_process::apply_f64_to_f64_3de_anamorphic_std_deg6_rescaled_multithread;
use crate::distortion_process::apply_identity_to_f32_3de_anamorphic_std_deg6_rescaled_multithread;
use crate::distortion_process::apply_identity_to_f64_3de_anamorphic_std_deg6_rescaled_multithread;

#[cxx::bridge(namespace = "mmlens")]
pub mod ffi {

    unsafe extern "C++" {
        // C++ includes needed for all files.
        include!("mmlens/_cxx.h");
        include!("mmlens/_symbol_export.h");
    }

    #[repr(u8)]
    #[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
    pub(crate) enum DistortionDirection {
        #[cxx_name = "kUndistort"]
        Undistort = 0,

        #[cxx_name = "kRedistort"]
        Redistort = 1,

        // Indicates that both directions will be used, and the order
        // is 'undistort' then 'redistort'.
        #[cxx_name = "kUndistortAndRedistort"]
        UndistortAndRedistort = 2,

        // Indicates that both directions will be used, and the order
        // is 'redistort' then 'undistort'.
        #[cxx_name = "kRedistortAndUndistort"]
        RedistortAndUndistort = 3,

        #[cxx_name = "kNumDistortionDirection"]
        NumDistortionDirection,
    }

    #[repr(u8)]
    #[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
    pub(crate) enum LensModelState {
        #[cxx_name = "kUninitialized"]
        None = 0,

        #[cxx_name = "kClean"]
        String = 1,

        #[cxx_name = "kDirty"]
        Dirty = 2,

        #[cxx_name = "kNumLensModelState"]
        NumLensModelState,
    }

    // Warning: Do not change the numbers assigned to the different
    // types. These numbers are exposed to the user via the
    // "mmLensModel3de" node, with attribute 'lensModel'.
    #[repr(u8)]
    #[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
    pub(crate) enum LensModelType {
        #[cxx_name = "kUninitialized"]
        Uninitialized = 0,

        // Does nothing but passes through to the next lens model (if
        // there is one).
        #[cxx_name = "kPassthrough"]
        Passthrough = 1,

        // "3DE Classic LD Model"
        #[cxx_name = "k3deClassic"]
        TdeClassic = 2,

        // "3DE4 Radial - Standard, Degree 4"
        #[cxx_name = "k3deRadialStdDeg4"]
        TdeRadialStdDeg4 = 3,

        // "3DE4 Anamorphic - Standard, Degree 4"
        #[cxx_name = "k3deAnamorphicStdDeg4"]
        TdeAnamorphicStdDeg4 = 4,

        // "3DE4 Anamorphic - Rescaled, Degree 4"
        #[cxx_name = "k3deAnamorphicStdDeg4Rescaled"]
        TdeAnamorphicStdDeg4Rescaled = 5,

        // "3DE4 Anamorphic - Standard, Degree 6"
        #[cxx_name = "k3deAnamorphicStdDeg6"]
        TdeAnamorphicStdDeg6 = 6,

        // "3DE4 Anamorphic - Rescaled, Degree 6"
        #[cxx_name = "k3deAnamorphicStdDeg6Rescaled"]
        TdeAnamorphicStdDeg6Rescaled = 7,

        // // "3DE4 Anamorphic, Degree 6"
        // #[cxx_name = "k3deAnamorphicDeg6"]
        // TdeAnamorphicDeg6 = 8,

        // Always the last item, so it has the number of elements
        // automatically.
        #[cxx_name = "kNumLensModelType"]
        NumLensModelType,
    }

    // Represents the dimensions and sub-window of an image.
    #[derive(Debug, Default, Copy, Clone, PartialEq, PartialOrd)]
    pub(crate) struct ImageDimensions {
        // Image size
        width: usize,  // Full image width.
        height: usize, // Full image height.

        // Image sub-window
        start_width: usize, // Start of processing window width.
        start_height: usize, // Start of processing window height.
        end_width: usize,   // End of processing window width.
        end_height: usize,  // End of processing window height.
    }

    #[derive(Debug, Default, Copy, Clone, PartialEq, PartialOrd)]
    pub(crate) struct CameraParameters {
        // cm = centimeter, the unit of the value.
        focal_length_cm: f64,
        film_back_width_cm: f64,
        film_back_height_cm: f64,
        pixel_aspect: f64,
        lens_center_offset_x_cm: f64,
        lens_center_offset_y_cm: f64,
    }

    #[derive(Debug, Copy, Clone, PartialEq, PartialOrd)]
    pub(crate) struct Parameters3deClassic {
        distortion: f64,         // "Distortion"
        anamorphic_squeeze: f64, // "Anamorphic Squeeze"
        curvature_x: f64,        // "Curvature X"
        curvature_y: f64,        // "Curvature Y"
        quartic_distortion: f64, // "Quartic Distortion"
    }

    #[derive(Debug, Copy, Clone, PartialEq, PartialOrd)]
    pub(crate) struct Parameters3deRadialStdDeg4 {
        degree2_distortion: f64, // "Distortion - Degree 2"
        degree2_u: f64,          // "U - Degree 2"
        degree2_v: f64,          // "V - Degree 2"

        degree4_distortion: f64, // "Quartic Distortion - Degree 4"
        degree4_u: f64,          // "U - Degree 4"
        degree4_v: f64,          // "V - Degree 4"

        cylindric_direction: f64, // "Phi - Cylindric Direction"
        cylindric_bending: f64,   // "B - Cylindric Bending"
    }

    #[derive(Debug, Copy, Clone, PartialEq, PartialOrd)]
    pub(crate) struct Parameters3deAnamorphicStdDeg4 {
        degree2_cx02: f64, // "Cx02 - Degree 2"
        degree2_cy02: f64, // "Cy02 - Degree 2"
        degree2_cx22: f64, // "Cx22 - Degree 2"
        degree2_cy22: f64, // "Cy22 - Degree 2"

        degree4_cx04: f64, // "Cx04 - Degree 4"
        degree4_cy04: f64, // "Cy04 - Degree 4"
        degree4_cx24: f64, // "Cx24 - Degree 4"
        degree4_cy24: f64, // "Cy24 - Degree 4"
        degree4_cx44: f64, // "Cx44 - Degree 4"
        degree4_cy44: f64, // "Cy44 - Degree 4"

        lens_rotation: f64, // "Lens Rotation"
        squeeze_x: f64,     // "Squeeze-X"
        squeeze_y: f64,     // "Squeeze-Y"
    }

    #[derive(Debug, Copy, Clone, PartialEq, PartialOrd)]
    pub(crate) struct Parameters3deAnamorphicStdDeg4Rescaled {
        degree2_cx02: f64, // "Cx02 - Degree 2"
        degree2_cy02: f64, // "Cy02 - Degree 2"
        degree2_cx22: f64, // "Cx22 - Degree 2"
        degree2_cy22: f64, // "Cy22 - Degree 2"

        degree4_cx04: f64, // "Cx04 - Degree 4"
        degree4_cy04: f64, // "Cy04 - Degree 4"
        degree4_cx24: f64, // "Cx24 - Degree 4"
        degree4_cy24: f64, // "Cy24 - Degree 4"
        degree4_cx44: f64, // "Cx44 - Degree 4"
        degree4_cy44: f64, // "Cy44 - Degree 4"

        lens_rotation: f64, // "Lens Rotation"
        squeeze_x: f64,     // "Squeeze-X"
        squeeze_y: f64,     // "Squeeze-Y"
        rescale: f64,       // "Rescale"
    }

    #[derive(Debug, Copy, Clone, PartialEq, PartialOrd)]
    pub(crate) struct Parameters3deAnamorphicStdDeg6 {
        degree2_cx02: f64, // "Cx02 - Degree 2"
        degree2_cy02: f64, // "Cy02 - Degree 2"
        degree2_cx22: f64, // "Cx22 - Degree 2"
        degree2_cy22: f64, // "Cy22 - Degree 2"

        degree4_cx04: f64, // "Cx04 - Degree 4"
        degree4_cy04: f64, // "Cy04 - Degree 4"
        degree4_cx24: f64, // "Cx24 - Degree 4"
        degree4_cy24: f64, // "Cy24 - Degree 4"
        degree4_cx44: f64, // "Cx44 - Degree 4"
        degree4_cy44: f64, // "Cy44 - Degree 4"

        degree6_cx06: f64, // "Cx06 - Degree 6"
        degree6_cy06: f64, // "Cy06 - Degree 6"
        degree6_cx26: f64, // "Cx26 - Degree 6"
        degree6_cy26: f64, // "Cy26 - Degree 6"
        degree6_cx46: f64, // "Cx46 - Degree 6"
        degree6_cy46: f64, // "Cy46 - Degree 6"
        degree6_cx66: f64, // "Cx66 - Degree 6"
        degree6_cy66: f64, // "Cy66 - Degree 6"

        lens_rotation: f64, // "Lens Rotation"
        squeeze_x: f64,     // "Squeeze-X"
        squeeze_y: f64,     // "Squeeze-Y"
    }

    #[derive(Debug, Copy, Clone, PartialEq, PartialOrd)]
    pub(crate) struct Parameters3deAnamorphicStdDeg6Rescaled {
        degree2_cx02: f64, // "Cx02 - Degree 2"
        degree2_cy02: f64, // "Cy02 - Degree 2"
        degree2_cx22: f64, // "Cx22 - Degree 2"
        degree2_cy22: f64, // "Cy22 - Degree 2"

        degree4_cx04: f64, // "Cx04 - Degree 4"
        degree4_cy04: f64, // "Cy04 - Degree 4"
        degree4_cx24: f64, // "Cx24 - Degree 4"
        degree4_cy24: f64, // "Cy24 - Degree 4"
        degree4_cx44: f64, // "Cx44 - Degree 4"
        degree4_cy44: f64, // "Cy44 - Degree 4"

        degree6_cx06: f64, // "Cx06 - Degree 6"
        degree6_cy06: f64, // "Cy06 - Degree 6"
        degree6_cx26: f64, // "Cx26 - Degree 6"
        degree6_cy26: f64, // "Cy26 - Degree 6"
        degree6_cx46: f64, // "Cx46 - Degree 6"
        degree6_cy46: f64, // "Cy46 - Degree 6"
        degree6_cx66: f64, // "Cx66 - Degree 6"
        degree6_cy66: f64, // "Cy66 - Degree 6"

        lens_rotation: f64, // "Lens Rotation"
        squeeze_x: f64,     // "Squeeze-X"
        squeeze_y: f64,     // "Squeeze-Y"
        rescale: f64,       // "Rescale"
    }

    #[derive(Debug, Default, Copy, Clone, PartialEq, PartialOrd)]
    struct OptionParameters3deClassic {
        exists: bool,
        value: Parameters3deClassic,
    }

    #[derive(Debug, Default, Copy, Clone, PartialEq, PartialOrd)]
    struct OptionParameters3deRadialStdDeg4 {
        exists: bool,
        value: Parameters3deRadialStdDeg4,
    }

    #[derive(Debug, Default, Copy, Clone, PartialEq, PartialOrd)]
    struct OptionParameters3deAnamorphicStdDeg4 {
        exists: bool,
        value: Parameters3deAnamorphicStdDeg4,
    }

    #[derive(Debug, Default, Copy, Clone, PartialEq, PartialOrd)]
    struct OptionParameters3deAnamorphicStdDeg4Rescaled {
        exists: bool,
        value: Parameters3deAnamorphicStdDeg4Rescaled,
    }

    #[derive(Debug, Default, Copy, Clone, PartialEq, PartialOrd)]
    struct OptionParameters3deAnamorphicStdDeg6 {
        exists: bool,
        value: Parameters3deAnamorphicStdDeg6,
    }

    #[derive(Debug, Default, Copy, Clone, PartialEq, PartialOrd)]
    struct OptionParameters3deAnamorphicStdDeg6Rescaled {
        exists: bool,
        value: Parameters3deAnamorphicStdDeg6Rescaled,
    }

    extern "Rust" {
        type ShimDistortionLayers;

        fn is_static(&self) -> bool;
        fn frame_range(
            &self,
            out_start_frame: &mut u16,
            out_end_frame: &mut u16,
        );
        fn frame_count(&self) -> u16;
        fn frame_hash(&self, frame: u16) -> u64;
        fn camera_parameters(&self) -> CameraParameters;
        fn layer_count(&self) -> u8;
        fn layer_lens_model_type(&self, layer_num: u8) -> LensModelType;
        fn layer_lens_parameters_3de_classic(
            &self,
            layer_num: u8,
            frame: u16,
        ) -> OptionParameters3deClassic;
        fn layer_lens_parameters_3de_radial_std_deg4(
            &self,
            layer_num: u8,
            frame: u16,
        ) -> OptionParameters3deRadialStdDeg4;
        fn layer_lens_parameters_3de_anamorphic_std_deg4(
            &self,
            layer_num: u8,
            frame: u16,
        ) -> OptionParameters3deAnamorphicStdDeg4;
        fn layer_lens_parameters_3de_anamorphic_std_deg4_rescaled(
            &self,
            layer_num: u8,
            frame: u16,
        ) -> OptionParameters3deAnamorphicStdDeg4Rescaled;
        fn layer_lens_parameters_3de_anamorphic_std_deg6(
            &self,
            layer_num: u8,
            frame: u16,
        ) -> OptionParameters3deAnamorphicStdDeg6;
        fn layer_lens_parameters_3de_anamorphic_std_deg6_rescaled(
            &self,
            layer_num: u8,
            frame: u16,
        ) -> OptionParameters3deAnamorphicStdDeg6Rescaled;

        fn as_string(&self) -> String;

        fn shim_create_distortion_layers_box() -> Box<ShimDistortionLayers>;

        fn shim_read_lens_file(file_path: &str) -> Box<ShimDistortionLayers>;
    }

    unsafe extern "C++" {
        include!("mmlens/distortion_process.h");

        //////////////////////////////////////////////////////////////////////
        // 3DE Classic

        #[rust_name = "apply_identity_to_f64_3de_classic"]
        unsafe fn apply_identity_to_f64(
            direction: DistortionDirection,
            image_dimensions: ImageDimensions,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deClassic,
        );

        #[rust_name = "apply_identity_to_f32_3de_classic"]
        unsafe fn apply_identity_to_f32(
            direction: DistortionDirection,
            image_dimensions: ImageDimensions,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deClassic,
        );

        #[rust_name = "apply_f64_to_f64_3de_classic"]
        unsafe fn apply_f64_to_f64(
            direction: DistortionDirection,
            data_chunk_start: usize,
            data_chunk_end: usize,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deClassic,
        );

        #[rust_name = "apply_f64_to_f32_3de_classic"]
        unsafe fn apply_f64_to_f32(
            direction: DistortionDirection,
            data_chunk_start: usize,
            data_chunk_end: usize,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deClassic,
        );

        //////////////////////////////////////////////////////////////////////
        // 3DE Radial Decentered Degree 4 Cylindric

        #[rust_name = "apply_identity_to_f64_3de_radial_std_deg4"]
        unsafe fn apply_identity_to_f64(
            direction: DistortionDirection,
            image_dimensions: ImageDimensions,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deRadialStdDeg4,
        );

        #[rust_name = "apply_identity_to_f32_3de_radial_std_deg4"]
        unsafe fn apply_identity_to_f32(
            direction: DistortionDirection,
            image_dimensions: ImageDimensions,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deRadialStdDeg4,
        );

        #[rust_name = "apply_f64_to_f64_3de_radial_std_deg4"]
        unsafe fn apply_f64_to_f64(
            direction: DistortionDirection,
            data_chunk_start: usize,
            data_chunk_end: usize,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deRadialStdDeg4,
        );

        #[rust_name = "apply_f64_to_f32_3de_radial_std_deg4"]
        unsafe fn apply_f64_to_f32(
            direction: DistortionDirection,
            data_chunk_start: usize,
            data_chunk_end: usize,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deRadialStdDeg4,
        );

        //////////////////////////////////////////////////////////////////////
        // 3DE Anamorphic Degree 4 Rotate Squeeze XY

        #[rust_name = "apply_identity_to_f64_3de_anamorphic_std_deg4"]
        unsafe fn apply_identity_to_f64(
            direction: DistortionDirection,
            image_dimensions: ImageDimensions,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg4,
        );

        #[rust_name = "apply_identity_to_f32_3de_anamorphic_std_deg4"]
        unsafe fn apply_identity_to_f32(
            direction: DistortionDirection,
            image_dimensions: ImageDimensions,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg4,
        );

        #[rust_name = "apply_f64_to_f64_3de_anamorphic_std_deg4"]
        unsafe fn apply_f64_to_f64(
            direction: DistortionDirection,
            data_chunk_start: usize,
            data_chunk_end: usize,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg4,
        );

        #[rust_name = "apply_f64_to_f32_3de_anamorphic_std_deg4"]
        unsafe fn apply_f64_to_f32(
            direction: DistortionDirection,
            data_chunk_start: usize,
            data_chunk_end: usize,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg4,
        );

        //////////////////////////////////////////////////////////////////////
        // 3DE Anamorphic Degree 4 Rotate Squeeze XY Rescaled

        #[rust_name = "apply_identity_to_f64_3de_anamorphic_std_deg4_rescaled"]
        unsafe fn apply_identity_to_f64(
            direction: DistortionDirection,
            image_dimensions: ImageDimensions,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg4Rescaled,
        );

        #[rust_name = "apply_identity_to_f32_3de_anamorphic_std_deg4_rescaled"]
        unsafe fn apply_identity_to_f32(
            direction: DistortionDirection,
            image_dimensions: ImageDimensions,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg4Rescaled,
        );

        #[rust_name = "apply_f64_to_f64_3de_anamorphic_std_deg4_rescaled"]
        unsafe fn apply_f64_to_f64(
            direction: DistortionDirection,
            data_chunk_start: usize,
            data_chunk_end: usize,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg4Rescaled,
        );

        #[rust_name = "apply_f64_to_f32_3de_anamorphic_std_deg4_rescaled"]
        unsafe fn apply_f64_to_f32(
            direction: DistortionDirection,
            data_chunk_start: usize,
            data_chunk_end: usize,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg4Rescaled,
        );

        //////////////////////////////////////////////////////////////////////
        // 3DE Anamorphic degree 6 Rotate Squeeze XY

        #[rust_name = "apply_identity_to_f64_3de_anamorphic_std_deg6"]
        unsafe fn apply_identity_to_f64(
            direction: DistortionDirection,
            image_dimensions: ImageDimensions,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg6,
        );

        #[rust_name = "apply_identity_to_f32_3de_anamorphic_std_deg6"]
        unsafe fn apply_identity_to_f32(
            direction: DistortionDirection,
            image_dimensions: ImageDimensions,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg6,
        );

        #[rust_name = "apply_f64_to_f64_3de_anamorphic_std_deg6"]
        unsafe fn apply_f64_to_f64(
            direction: DistortionDirection,
            data_chunk_start: usize,
            data_chunk_end: usize,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg6,
        );

        #[rust_name = "apply_f64_to_f32_3de_anamorphic_std_deg6"]
        unsafe fn apply_f64_to_f32(
            direction: DistortionDirection,
            data_chunk_start: usize,
            data_chunk_end: usize,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg6,
        );

        //////////////////////////////////////////////////////////////////////
        // 3DE Anamorphic degree 6 Rotate Squeeze XY Rescaled

        #[rust_name = "apply_identity_to_f64_3de_anamorphic_std_deg6_rescaled"]
        unsafe fn apply_identity_to_f64(
            direction: DistortionDirection,
            image_dimensions: ImageDimensions,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg6Rescaled,
        );

        #[rust_name = "apply_identity_to_f32_3de_anamorphic_std_deg6_rescaled"]
        unsafe fn apply_identity_to_f32(
            direction: DistortionDirection,
            image_dimensions: ImageDimensions,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg6Rescaled,
        );

        #[rust_name = "apply_f64_to_f64_3de_anamorphic_std_deg6_rescaled"]
        unsafe fn apply_f64_to_f64(
            direction: DistortionDirection,
            data_chunk_start: usize,
            data_chunk_end: usize,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg6Rescaled,
        );

        #[rust_name = "apply_f64_to_f32_3de_anamorphic_std_deg6_rescaled"]
        unsafe fn apply_f64_to_f32(
            direction: DistortionDirection,
            data_chunk_start: usize,
            data_chunk_end: usize,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg6Rescaled,
        );

    }

    extern "Rust" {
        fn initialize_global_thread_pool(num_threads: i32) -> i32;

        //////////////////////////////////////////////////////////////////////
        // 3DE Classic

        #[cxx_name = "apply_identity_to_f64_multithread"]
        unsafe fn apply_identity_to_f64_3de_classic_multithread(
            direction: DistortionDirection,
            image_width: usize,
            image_height: usize,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deClassic,
        );

        #[cxx_name = "apply_identity_to_f32_multithread"]
        unsafe fn apply_identity_to_f32_3de_classic_multithread(
            direction: DistortionDirection,
            image_width: usize,
            image_height: usize,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deClassic,
        );

        #[cxx_name = "apply_f64_to_f64_multithread"]
        unsafe fn apply_f64_to_f64_3de_classic_multithread(
            direction: DistortionDirection,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deClassic,
        );

        #[cxx_name = "apply_f64_to_f32_multithread"]
        unsafe fn apply_f64_to_f32_3de_classic_multithread(
            direction: DistortionDirection,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deClassic,
        );

        //////////////////////////////////////////////////////////////////////
        // 3DE Radial Decentered Degree 4 Cylindric

        #[cxx_name = "apply_identity_to_f64_multithread"]
        unsafe fn apply_identity_to_f64_3de_radial_std_deg4_multithread(
            direction: DistortionDirection,
            image_width: usize,
            image_height: usize,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deRadialStdDeg4,
        );

        #[cxx_name = "apply_identity_to_f32_multithread"]
        unsafe fn apply_identity_to_f32_3de_radial_std_deg4_multithread(
            direction: DistortionDirection,
            image_width: usize,
            image_height: usize,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deRadialStdDeg4,
        );

        #[cxx_name = "apply_f64_to_f64_multithread"]
        unsafe fn apply_f64_to_f64_3de_radial_std_deg4_multithread(
            direction: DistortionDirection,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deRadialStdDeg4,
        );

        #[cxx_name = "apply_f64_to_f32_multithread"]
        unsafe fn apply_f64_to_f32_3de_radial_std_deg4_multithread(
            direction: DistortionDirection,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deRadialStdDeg4,
        );

        //////////////////////////////////////////////////////////////////////
        // 3DE Anamorphic Degree 4 Rotate Squeeze XY

        #[cxx_name = "apply_identity_to_f64_multithread"]
        unsafe fn apply_identity_to_f64_3de_anamorphic_std_deg4_multithread(
            direction: DistortionDirection,
            image_width: usize,
            image_height: usize,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg4,
        );

        #[cxx_name = "apply_identity_to_f32_multithread"]
        unsafe fn apply_identity_to_f32_3de_anamorphic_std_deg4_multithread(
            direction: DistortionDirection,
            image_width: usize,
            image_height: usize,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg4,
        );

        #[cxx_name = "apply_f64_to_f64_multithread"]
        unsafe fn apply_f64_to_f64_3de_anamorphic_std_deg4_multithread(
            direction: DistortionDirection,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg4,
        );

        #[cxx_name = "apply_f64_to_f32_multithread"]
        unsafe fn apply_f64_to_f32_3de_anamorphic_std_deg4_multithread(
            direction: DistortionDirection,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg4,
        );

        //////////////////////////////////////////////////////////////////////
        // 3DE Anamorphic Degree 4 Rotate Squeeze XY Rescaled

        #[cxx_name = "apply_identity_to_f64_multithread"]
        unsafe fn apply_identity_to_f64_3de_anamorphic_std_deg4_rescaled_multithread(
            direction: DistortionDirection,
            image_width: usize,
            image_height: usize,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg4Rescaled,
        );

        #[cxx_name = "apply_identity_to_f32_multithread"]
        unsafe fn apply_identity_to_f32_3de_anamorphic_std_deg4_rescaled_multithread(
            direction: DistortionDirection,
            image_width: usize,
            image_height: usize,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg4Rescaled,
        );

        #[cxx_name = "apply_f64_to_f64_multithread"]
        unsafe fn apply_f64_to_f64_3de_anamorphic_std_deg4_rescaled_multithread(
            direction: DistortionDirection,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg4Rescaled,
        );

        #[cxx_name = "apply_f64_to_f32_multithread"]
        unsafe fn apply_f64_to_f32_3de_anamorphic_std_deg4_rescaled_multithread(
            direction: DistortionDirection,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg4Rescaled,
        );

        //////////////////////////////////////////////////////////////////////
        // 3DE Anamorphic degree 6 Rotate Squeeze XY

        #[cxx_name = "apply_identity_to_f64_multithread"]
        unsafe fn apply_identity_to_f64_3de_anamorphic_std_deg6_multithread(
            direction: DistortionDirection,
            image_width: usize,
            image_height: usize,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg6,
        );

        #[cxx_name = "apply_identity_to_f32_multithread"]
        unsafe fn apply_identity_to_f32_3de_anamorphic_std_deg6_multithread(
            direction: DistortionDirection,
            image_width: usize,
            image_height: usize,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg6,
        );

        #[cxx_name = "apply_f64_to_f64_multithread"]
        unsafe fn apply_f64_to_f64_3de_anamorphic_std_deg6_multithread(
            direction: DistortionDirection,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg6,
        );

        #[cxx_name = "apply_f64_to_f32_multithread"]
        unsafe fn apply_f64_to_f32_3de_anamorphic_std_deg6_multithread(
            direction: DistortionDirection,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg6,
        );

        //////////////////////////////////////////////////////////////////////
        // 3DE Anamorphic degree 6 Rotate Squeeze XY Rescaled

        #[cxx_name = "apply_identity_to_f64_multithread"]
        unsafe fn apply_identity_to_f64_3de_anamorphic_std_deg6_rescaled_multithread(
            direction: DistortionDirection,
            image_width: usize,
            image_height: usize,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg6Rescaled,
        );

        #[cxx_name = "apply_identity_to_f32_multithread"]
        unsafe fn apply_identity_to_f32_3de_anamorphic_std_deg6_rescaled_multithread(
            direction: DistortionDirection,
            image_width: usize,
            image_height: usize,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg6Rescaled,
        );

        #[cxx_name = "apply_f64_to_f64_multithread"]
        unsafe fn apply_f64_to_f64_3de_anamorphic_std_deg6_rescaled_multithread(
            direction: DistortionDirection,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f64,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg6Rescaled,
        );

        #[cxx_name = "apply_f64_to_f32_multithread"]
        unsafe fn apply_f64_to_f32_3de_anamorphic_std_deg6_rescaled_multithread(
            direction: DistortionDirection,
            in_data_ptr: *const f64,
            in_data_size: usize,
            in_data_stride: usize,
            out_data_ptr: *mut f32,
            out_data_size: usize,
            out_data_stride: usize,
            camera_parameters: CameraParameters,
            film_back_radius_cm: f64,
            lens_parameters: Parameters3deAnamorphicStdDeg6Rescaled,
        );

    }
}
