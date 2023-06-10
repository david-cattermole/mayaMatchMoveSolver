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

// use crate::imagemetadata::shim_create_image_meta_data_box;
// use crate::imagemetadata::ShimImageMetaData;
// use crate::imagepixeldata::shim_create_image_pixel_data_rgba_f32_box;
// use crate::imagepixeldata::ShimImagePixelDataRgbaF32;
// use crate::shim_image_read_metadata_exr;
// use crate::shim_image_read_pixels_exr_rgba_f32;
// use crate::shim_image_write_pixels_exr_rgba_f32;

// use crate::constants::MAX_LENS_PARAMETER_COUNT;

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

        // // "3DE4 Anamorphic - Standard, Degree 6"
        // #[cxx_name = "k3deAnamorphicStdDeg4"]
        // TdeAnamorphicStdDeg4 = 6,

        // // "3DE4 Anamorphic - Rescaled, Degree 6"
        // #[cxx_name = "k3deAnamorphicStdDeg4Rescaled"]
        // TdeAnamorphicStdDeg4Rescaled = 7,

        // // "3DE4 Anamorphic, Degree 6"
        // #[cxx_name = "k3deAnamorphicDeg6"]
        // TdeAnamorphicDeg6 = 8,

        // Always the last item, so it has the number of elements
        // automatically.
        #[cxx_name = "kNumLensModelType"]
        NumLensModelType,
    }

    #[derive(Debug, Copy, Clone, PartialEq, PartialOrd)]
    pub(crate) struct CameraParameters {
        // cm = centimeter, the unit of the value.
        focal_length_cm: f64,
        film_back_width_cm: f64,
        film_back_height_cm: f64,
        pixel_aspect: f64,
        lens_center_offset_x_cm: f64,
        lens_center_offset_y_cm: f64,
    }

    pub(crate) struct LensParameters {
        mode: LensModelType,
        values: [f64; 5], // MAX_LENS_PARAMETER_COUNT
    }

    #[derive(Debug, Copy, Clone, PartialEq, PartialOrd)]
    pub(crate) struct TdeClassicParameters {
        distortion: f64,         // Distortion
        anamorphic_squeeze: f64, // Anamorphic squeeze
        curvature_x: f64,        // Curvature X
        curvature_y: f64,        // Curvature Y
        quartic_distortion: f64, // Quartic Distortion
    }

    #[derive(Debug, Copy, Clone, PartialEq, PartialOrd)]
    pub(crate) struct TdeRadialDecenteredDeg4CylindricParameters {
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
    pub(crate) struct TdeAnamorphicDeg4RotateSqueezeXYParameters {
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
    pub(crate) struct TdeAnamorphicDeg4RotateSqueezeXYRescaledParameters {
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
}
