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

use crate::cxxbridge::ffi::CameraParameters as BindCameraParameters;
use crate::cxxbridge::ffi::LensModelType as BindLensModelType;
use crate::distortion_layers::ShimDistortionLayers;
use mmio_rust::nuke_lens_common::CameraParameters as IoCameraParameters;
use mmio_rust::nuke_lens_common::LensModelType as IoLensModelType;
use mmio_rust::nuke_lens_reader;
use smallvec::SmallVec;
use std::collections::HashMap;

use crate::data::FrameNumber;
use crate::data::LayerSize;
use crate::data::ParameterBlock;

fn convert_lens_model_type(value: IoLensModelType) -> BindLensModelType {
    match value {
        IoLensModelType::TdeClassic => BindLensModelType::TdeClassic,
        IoLensModelType::TdeRadialStdDeg4 => {
            BindLensModelType::TdeRadialStdDeg4
        }
        IoLensModelType::TdeAnamorphicStdDeg4 => {
            BindLensModelType::TdeAnamorphicStdDeg4
        }
        IoLensModelType::TdeAnamorphicStdDeg4Rescaled => {
            BindLensModelType::TdeAnamorphicStdDeg4Rescaled
        }
        IoLensModelType::TdeAnamorphicStdDeg6 => {
            BindLensModelType::TdeAnamorphicStdDeg6
        }
        IoLensModelType::TdeAnamorphicStdDeg6Rescaled => {
            BindLensModelType::TdeAnamorphicStdDeg6Rescaled
        }
        _ => BindLensModelType::Uninitialized,
    }
}

fn convert_camera_parameters(
    value: IoCameraParameters,
) -> BindCameraParameters {
    BindCameraParameters {
        focal_length_cm: value.focal_length_cm,
        film_back_width_cm: value.film_back_width_cm,
        film_back_height_cm: value.film_back_height_cm,
        pixel_aspect: value.pixel_aspect,
        lens_center_offset_x_cm: value.lens_center_offset_x_cm,
        lens_center_offset_y_cm: value.lens_center_offset_y_cm,
    }
}

pub fn shim_read_lens_file(file_path: &str) -> Box<ShimDistortionLayers> {
    let data = nuke_lens_reader::read_nuke_lens_file(file_path)
        .expect("should get distortion layers");

    let layer_lens_model_types: SmallVec<[BindLensModelType; 4]> = data
        .layer_lens_model_types
        .iter()
        .map(|t| convert_lens_model_type(*t))
        .collect();

    let layer_frame_range: SmallVec<[(FrameNumber, FrameNumber); 4]> =
        data.layer_frame_range.iter().copied().collect();

    let camera_parameters = convert_camera_parameters(data.camera_parameters);

    let lens_parameters: HashMap<(LayerSize, FrameNumber), ParameterBlock> =
        data.lens_parameters;

    Box::new(ShimDistortionLayers::from_parts(
        data.layer_count,
        &layer_lens_model_types,
        &layer_frame_range,
        camera_parameters,
        &lens_parameters,
    ))
}
