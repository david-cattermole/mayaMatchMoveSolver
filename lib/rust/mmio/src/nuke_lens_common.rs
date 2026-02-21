//
// Copyright (C) 2023, 2025, 2026 David Cattermole.
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

use std::collections::HashMap;

/// Frame numbers 0 to 65534 are valid.
/// Frame number 65535 is reserved to indicate a static value.
pub type FrameNumber = u16;
pub type LayerSize = u8;

/// Represents a static frame number.
pub const STATIC_FRAME_NUMBER: FrameNumber = u16::MAX;

/// The maximum lens parameter count.
pub const MAX_LENS_PARAMETER_COUNT: usize = 22;

// Nuke node types.
pub const NUKE_3DE4_CLASSIC: &str = "LD_3DE_Classic_LD_Model";
pub const NUKE_3DE4_RADIAL_STD_DEG4: &str = "LD_3DE4_Radial_Standard_Degree_4";
pub const NUKE_3DE4_ANAMORPHIC_STD_DEG4: &str =
    "LD_3DE4_Anamorphic_Standard_Degree_4";
pub const NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED: &str =
    "LD_3DE4_Anamorphic_Rescaled_Degree_4";
pub const NUKE_3DE4_ANAMORPHIC_STD_DEG6: &str =
    "LD_3DE4_Anamorphic_Standard_Degree_6";
pub const NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED: &str =
    "LD_3DE4_Anamorphic_Rescaled_Degree_6";
pub const NUKE_3DE4_ANAMORPHIC_DEG6: &str = "LD_3DE4_Anamorphic_Degree_6";

#[derive(Debug, Copy, Clone, Hash, Eq, PartialEq, Ord, PartialOrd)]
#[repr(u8)]
pub enum LensModelType {
    Uninitialized = 0,
    Passthrough = 1,
    TdeClassic = 2,
    TdeRadialStdDeg4 = 3,
    TdeAnamorphicStdDeg4 = 4,
    TdeAnamorphicStdDeg4Rescaled = 5,
    TdeAnamorphicStdDeg6 = 6,
    TdeAnamorphicStdDeg6Rescaled = 7,
}

#[derive(Debug, Copy, Clone, PartialEq, PartialOrd)]
pub struct CameraParameters {
    pub focal_length_cm: f64,
    pub film_back_width_cm: f64,
    pub film_back_height_cm: f64,
    pub pixel_aspect: f64,
    pub lens_center_offset_x_cm: f64,
    pub lens_center_offset_y_cm: f64,
}

impl Default for CameraParameters {
    fn default() -> Self {
        CameraParameters {
            focal_length_cm: 3.5,
            film_back_width_cm: 3.6,
            film_back_height_cm: 2.4,
            pixel_aspect: 1.0,
            lens_center_offset_x_cm: 0.0,
            lens_center_offset_y_cm: 0.0,
        }
    }
}

pub type ParameterBlock = [f64; MAX_LENS_PARAMETER_COUNT];

/// Parsed Nuke lens distortion data.
#[derive(Debug, Clone)]
pub struct NukeLensData {
    pub layer_count: LayerSize,
    pub layer_lens_model_types: Vec<LensModelType>,
    pub layer_frame_range: Vec<(FrameNumber, FrameNumber)>,
    pub camera_parameters: CameraParameters,
    pub lens_parameters: HashMap<(LayerSize, FrameNumber), ParameterBlock>,
}

pub fn lookup_lens_model_type(value: &str) -> LensModelType {
    match value {
        NUKE_3DE4_CLASSIC => LensModelType::TdeClassic,
        NUKE_3DE4_RADIAL_STD_DEG4 => LensModelType::TdeRadialStdDeg4,
        NUKE_3DE4_ANAMORPHIC_STD_DEG4 => LensModelType::TdeAnamorphicStdDeg4,
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED => {
            LensModelType::TdeAnamorphicStdDeg4Rescaled
        }
        NUKE_3DE4_ANAMORPHIC_STD_DEG6 => LensModelType::TdeAnamorphicStdDeg6,
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED => {
            LensModelType::TdeAnamorphicStdDeg6Rescaled
        }
        _ => LensModelType::Uninitialized,
    }
}

pub fn lookup_nuke_node_type_str(
    lens_model_type: LensModelType,
) -> Option<&'static str> {
    match lens_model_type {
        LensModelType::TdeClassic => Some(NUKE_3DE4_CLASSIC),
        LensModelType::TdeRadialStdDeg4 => Some(NUKE_3DE4_RADIAL_STD_DEG4),
        LensModelType::TdeAnamorphicStdDeg4 => {
            Some(NUKE_3DE4_ANAMORPHIC_STD_DEG4)
        }
        LensModelType::TdeAnamorphicStdDeg4Rescaled => {
            Some(NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED)
        }
        LensModelType::TdeAnamorphicStdDeg6 => {
            Some(NUKE_3DE4_ANAMORPHIC_STD_DEG6)
        }
        LensModelType::TdeAnamorphicStdDeg6Rescaled => {
            Some(NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED)
        }
        _ => None,
    }
}

/// Returns the knob names and default values for a given lens model type.
/// Each entry is (knob_name, parameter_index, default_value).
pub fn lens_model_knob_definitions(
    lens_model_type: LensModelType,
) -> &'static [(&'static str, usize, f64)] {
    match lens_model_type {
        LensModelType::TdeClassic => &[
            ("Distortion", 0, 0.0),
            ("Anamorphic_Squeeze", 1, 1.0),
            ("Curvature_X", 2, 0.0),
            ("Curvature_Y", 3, 0.0),
            ("Quartic_Distortion", 4, 0.0),
        ],
        LensModelType::TdeRadialStdDeg4 => &[
            ("Distortion_Degree_2", 0, 0.0),
            ("U_Degree_2", 1, 0.0),
            ("V_Degree_2", 2, 0.0),
            ("Quartic_Distortion_Degree_4", 3, 0.0),
            ("U_Degree_4", 4, 0.0),
            ("V_Degree_4", 5, 0.0),
            ("Phi_Cylindric_Direction", 6, 0.0),
            ("B_Cylindric_Bending", 7, 0.0),
        ],
        LensModelType::TdeAnamorphicStdDeg4 => &[
            ("Cx02_Degree_2", 0, 0.0),
            ("Cy02_Degree_2", 1, 0.0),
            ("Cx22_Degree_2", 2, 0.0),
            ("Cy22_Degree_2", 3, 0.0),
            ("Cx04_Degree_4", 4, 0.0),
            ("Cy04_Degree_4", 5, 0.0),
            ("Cx24_Degree_4", 6, 0.0),
            ("Cy24_Degree_4", 7, 0.0),
            ("Cx44_Degree_4", 8, 0.0),
            ("Cy44_Degree_4", 9, 0.0),
            ("Lens_Rotation", 10, 0.0),
            ("Squeeze_X", 11, 1.0),
            ("Squeeze_Y", 12, 1.0),
        ],
        LensModelType::TdeAnamorphicStdDeg4Rescaled => &[
            ("Cx02_Degree_2", 0, 0.0),
            ("Cy02_Degree_2", 1, 0.0),
            ("Cx22_Degree_2", 2, 0.0),
            ("Cy22_Degree_2", 3, 0.0),
            ("Cx04_Degree_4", 4, 0.0),
            ("Cy04_Degree_4", 5, 0.0),
            ("Cx24_Degree_4", 6, 0.0),
            ("Cy24_Degree_4", 7, 0.0),
            ("Cx44_Degree_4", 8, 0.0),
            ("Cy44_Degree_4", 9, 0.0),
            ("Lens_Rotation", 10, 0.0),
            ("Squeeze_X", 11, 1.0),
            ("Squeeze_Y", 12, 1.0),
            ("Rescale", 13, 1.0),
        ],
        LensModelType::TdeAnamorphicStdDeg6 => &[
            ("Cx02_Degree_2", 0, 0.0),
            ("Cy02_Degree_2", 1, 0.0),
            ("Cx22_Degree_2", 2, 0.0),
            ("Cy22_Degree_2", 3, 0.0),
            ("Cx04_Degree_4", 4, 0.0),
            ("Cy04_Degree_4", 5, 0.0),
            ("Cx24_Degree_4", 6, 0.0),
            ("Cy24_Degree_4", 7, 0.0),
            ("Cx44_Degree_4", 8, 0.0),
            ("Cy44_Degree_4", 9, 0.0),
            ("Cx06_Degree_6", 10, 0.0),
            ("Cy06_Degree_6", 11, 0.0),
            ("Cx26_Degree_6", 12, 0.0),
            ("Cy26_Degree_6", 13, 0.0),
            ("Cx46_Degree_6", 14, 0.0),
            ("Cy46_Degree_6", 15, 0.0),
            ("Cx66_Degree_6", 16, 0.0),
            ("Cy66_Degree_6", 17, 0.0),
            ("Lens_Rotation", 18, 0.0),
            ("Squeeze_X", 19, 1.0),
            ("Squeeze_Y", 20, 1.0),
        ],
        LensModelType::TdeAnamorphicStdDeg6Rescaled => &[
            ("Cx02_Degree_2", 0, 0.0),
            ("Cy02_Degree_2", 1, 0.0),
            ("Cx22_Degree_2", 2, 0.0),
            ("Cy22_Degree_2", 3, 0.0),
            ("Cx04_Degree_4", 4, 0.0),
            ("Cy04_Degree_4", 5, 0.0),
            ("Cx24_Degree_4", 6, 0.0),
            ("Cy24_Degree_4", 7, 0.0),
            ("Cx44_Degree_4", 8, 0.0),
            ("Cy44_Degree_4", 9, 0.0),
            ("Cx06_Degree_6", 10, 0.0),
            ("Cy06_Degree_6", 11, 0.0),
            ("Cx26_Degree_6", 12, 0.0),
            ("Cy26_Degree_6", 13, 0.0),
            ("Cx46_Degree_6", 14, 0.0),
            ("Cy46_Degree_6", 15, 0.0),
            ("Cx66_Degree_6", 16, 0.0),
            ("Cy66_Degree_6", 17, 0.0),
            ("Lens_Rotation", 18, 0.0),
            ("Squeeze_X", 19, 1.0),
            ("Squeeze_Y", 20, 1.0),
            ("Rescale", 21, 1.0),
        ],
        _ => &[],
    }
}
