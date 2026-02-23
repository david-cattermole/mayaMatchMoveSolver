//
// Copyright (C) 2026 David Cattermole.
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

//! Lens undistortion of marker UV positions.

use anyhow::Result;

use mmio::nuke_lens_common::{
    LensModelType, NukeLensData, STATIC_FRAME_NUMBER,
};
use mmio::uvtrack_reader::MarkersData;
use mmlens::cxxbridge::ffi::{
    apply_f64_to_f64_3de_anamorphic_std_deg4,
    apply_f64_to_f64_3de_anamorphic_std_deg4_rescaled,
    apply_f64_to_f64_3de_anamorphic_std_deg6,
    apply_f64_to_f64_3de_anamorphic_std_deg6_rescaled,
    apply_f64_to_f64_3de_classic, apply_f64_to_f64_3de_radial_std_deg4,
    CameraParameters as BindCameraParameters, DistortionDirection,
    Parameters3deAnamorphicStdDeg4, Parameters3deAnamorphicStdDeg4Rescaled,
    Parameters3deAnamorphicStdDeg6, Parameters3deAnamorphicStdDeg6Rescaled,
    Parameters3deClassic, Parameters3deRadialStdDeg4,
};

pub fn undistort_markers_with_lens(
    markers: &mut MarkersData,
    nuke_lens: &NukeLensData,
    has_explicit_distorted: bool,
) -> Result<()> {
    let cam = &nuke_lens.camera_parameters;
    let bind_cam = BindCameraParameters {
        focal_length_cm: cam.focal_length_cm,
        film_back_width_cm: cam.film_back_width_cm,
        film_back_height_cm: cam.film_back_height_cm,
        pixel_aspect: cam.pixel_aspect,
        lens_center_offset_x_cm: cam.lens_center_offset_x_cm,
        lens_center_offset_y_cm: cam.lens_center_offset_y_cm,
    };

    let film_back_radius_cm = (cam.film_back_width_cm * cam.film_back_width_cm
        + cam.film_back_height_cm * cam.film_back_height_cm)
        .sqrt()
        * 0.5;

    for fd in markers.frame_data.iter_mut() {
        let num_points = fd.u_coords.len();
        if num_points == 0 {
            continue;
        }

        // Determine source coordinates for undistortion.
        //
        // If explicit distorted data exists, use u_coords_dist.
        // Otherwise, u_coords/v_coords hold the distorted positions.
        let (src_u, src_v) = if has_explicit_distorted && fd.has_distorted() {
            (&fd.u_coords_dist, &fd.v_coords_dist)
        } else {
            (&fd.u_coords, &fd.v_coords)
        };

        let src_len = src_u.len();

        // Convert distorted UV coordinates from 0-1 range to the
        // -0.5 to +0.5 centered range expected by the mmlens
        // apply_f64_to_f64 functions.
        let mut in_data: Vec<f64> = Vec::with_capacity(src_len * 2);
        for i in 0..src_len {
            in_data.push(src_u[i] - 0.5);
            in_data.push(src_v[i] - 0.5);
        }

        let mut out_data: Vec<f64> = vec![0.0; src_len * 2];

        for layer_idx in 0..nuke_lens.layer_count {
            let model_type =
                nuke_lens.layer_lens_model_types[layer_idx as usize];

            // Try frame-specific lens parameters first, then fall back to static.
            let frame_num = if !fd.frames.is_empty() {
                fd.frames[0] as u16
            } else {
                STATIC_FRAME_NUMBER
            };

            let params = nuke_lens
                .lens_parameters
                .get(&(layer_idx, frame_num))
                .or_else(|| {
                    nuke_lens
                        .lens_parameters
                        .get(&(layer_idx, STATIC_FRAME_NUMBER))
                })
                .ok_or_else(|| {
                    anyhow::anyhow!(
                        "No lens parameters found for layer {}",
                        layer_idx
                    )
                })?;

            let direction = DistortionDirection::Undistort;
            let data_chunk_start = 0;
            let data_chunk_end = src_len;
            let stride = 2;

            unsafe {
                match model_type {
                    LensModelType::TdeClassic => {
                        let lens_params = Parameters3deClassic {
                            distortion: params[0],
                            anamorphic_squeeze: params[1],
                            curvature_x: params[2],
                            curvature_y: params[3],
                            quartic_distortion: params[4],
                        };
                        apply_f64_to_f64_3de_classic(
                            direction,
                            data_chunk_start,
                            data_chunk_end,
                            in_data.as_ptr(),
                            in_data.len(),
                            stride,
                            out_data.as_mut_ptr(),
                            out_data.len(),
                            stride,
                            bind_cam,
                            film_back_radius_cm,
                            lens_params,
                        );
                    }
                    LensModelType::TdeRadialStdDeg4 => {
                        let lens_params = Parameters3deRadialStdDeg4 {
                            degree2_distortion: params[0],
                            degree2_u: params[1],
                            degree2_v: params[2],
                            degree4_distortion: params[3],
                            degree4_u: params[4],
                            degree4_v: params[5],
                            cylindric_direction: params[6],
                            cylindric_bending: params[7],
                        };
                        apply_f64_to_f64_3de_radial_std_deg4(
                            direction,
                            data_chunk_start,
                            data_chunk_end,
                            in_data.as_ptr(),
                            in_data.len(),
                            stride,
                            out_data.as_mut_ptr(),
                            out_data.len(),
                            stride,
                            bind_cam,
                            film_back_radius_cm,
                            lens_params,
                        );
                    }
                    LensModelType::TdeAnamorphicStdDeg4 => {
                        let lens_params = Parameters3deAnamorphicStdDeg4 {
                            degree2_cx02: params[0],
                            degree2_cy02: params[1],
                            degree2_cx22: params[2],
                            degree2_cy22: params[3],
                            degree4_cx04: params[4],
                            degree4_cy04: params[5],
                            degree4_cx24: params[6],
                            degree4_cy24: params[7],
                            degree4_cx44: params[8],
                            degree4_cy44: params[9],
                            lens_rotation: params[10],
                            squeeze_x: params[11],
                            squeeze_y: params[12],
                        };
                        apply_f64_to_f64_3de_anamorphic_std_deg4(
                            direction,
                            data_chunk_start,
                            data_chunk_end,
                            in_data.as_ptr(),
                            in_data.len(),
                            stride,
                            out_data.as_mut_ptr(),
                            out_data.len(),
                            stride,
                            bind_cam,
                            film_back_radius_cm,
                            lens_params,
                        );
                    }
                    LensModelType::TdeAnamorphicStdDeg4Rescaled => {
                        let lens_params =
                            Parameters3deAnamorphicStdDeg4Rescaled {
                                degree2_cx02: params[0],
                                degree2_cy02: params[1],
                                degree2_cx22: params[2],
                                degree2_cy22: params[3],
                                degree4_cx04: params[4],
                                degree4_cy04: params[5],
                                degree4_cx24: params[6],
                                degree4_cy24: params[7],
                                degree4_cx44: params[8],
                                degree4_cy44: params[9],
                                lens_rotation: params[10],
                                squeeze_x: params[11],
                                squeeze_y: params[12],
                                rescale: params[13],
                            };
                        apply_f64_to_f64_3de_anamorphic_std_deg4_rescaled(
                            direction,
                            data_chunk_start,
                            data_chunk_end,
                            in_data.as_ptr(),
                            in_data.len(),
                            stride,
                            out_data.as_mut_ptr(),
                            out_data.len(),
                            stride,
                            bind_cam,
                            film_back_radius_cm,
                            lens_params,
                        );
                    }
                    LensModelType::TdeAnamorphicStdDeg6 => {
                        let lens_params = Parameters3deAnamorphicStdDeg6 {
                            degree2_cx02: params[0],
                            degree2_cy02: params[1],
                            degree2_cx22: params[2],
                            degree2_cy22: params[3],
                            degree4_cx04: params[4],
                            degree4_cy04: params[5],
                            degree4_cx24: params[6],
                            degree4_cy24: params[7],
                            degree4_cx44: params[8],
                            degree4_cy44: params[9],
                            degree6_cx06: params[10],
                            degree6_cy06: params[11],
                            degree6_cx26: params[12],
                            degree6_cy26: params[13],
                            degree6_cx46: params[14],
                            degree6_cy46: params[15],
                            degree6_cx66: params[16],
                            degree6_cy66: params[17],
                            lens_rotation: params[18],
                            squeeze_x: params[19],
                            squeeze_y: params[20],
                        };
                        apply_f64_to_f64_3de_anamorphic_std_deg6(
                            direction,
                            data_chunk_start,
                            data_chunk_end,
                            in_data.as_ptr(),
                            in_data.len(),
                            stride,
                            out_data.as_mut_ptr(),
                            out_data.len(),
                            stride,
                            bind_cam,
                            film_back_radius_cm,
                            lens_params,
                        );
                    }
                    LensModelType::TdeAnamorphicStdDeg6Rescaled => {
                        let lens_params =
                            Parameters3deAnamorphicStdDeg6Rescaled {
                                degree2_cx02: params[0],
                                degree2_cy02: params[1],
                                degree2_cx22: params[2],
                                degree2_cy22: params[3],
                                degree4_cx04: params[4],
                                degree4_cy04: params[5],
                                degree4_cx24: params[6],
                                degree4_cy24: params[7],
                                degree4_cx44: params[8],
                                degree4_cy44: params[9],
                                degree6_cx06: params[10],
                                degree6_cy06: params[11],
                                degree6_cx26: params[12],
                                degree6_cy26: params[13],
                                degree6_cx46: params[14],
                                degree6_cy46: params[15],
                                degree6_cx66: params[16],
                                degree6_cy66: params[17],
                                lens_rotation: params[18],
                                squeeze_x: params[19],
                                squeeze_y: params[20],
                                rescale: params[21],
                            };
                        apply_f64_to_f64_3de_anamorphic_std_deg6_rescaled(
                            direction,
                            data_chunk_start,
                            data_chunk_end,
                            in_data.as_ptr(),
                            in_data.len(),
                            stride,
                            out_data.as_mut_ptr(),
                            out_data.len(),
                            stride,
                            bind_cam,
                            film_back_radius_cm,
                            lens_params,
                        );
                    }
                    _ => {
                        anyhow::bail!(
                            "Unsupported lens model type: {:?}",
                            model_type
                        );
                    }
                }
            }

            // Use output as input for next layer.
            in_data.copy_from_slice(&out_data);
        }

        // Write undistorted coordinates back out, converting from
        // -0.5 to +0.5 centered range back to 0-1 UV range.
        for i in 0..src_len {
            fd.u_coords[i] = out_data[i * 2] + 0.5;
            fd.v_coords[i] = out_data[i * 2 + 1] + 0.5;
        }
    }

    Ok(())
}
