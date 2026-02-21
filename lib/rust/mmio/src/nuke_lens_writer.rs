//
// Copyright (C) 2025, 2026 David Cattermole.
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

use anyhow::{bail, Result};
use std::fmt::Write as FmtWrite;
use std::io::Write;

use crate::nuke_lens_common::lens_model_knob_definitions;
use crate::nuke_lens_common::lookup_nuke_node_type_str;
use crate::nuke_lens_common::FrameNumber;
use crate::nuke_lens_common::NukeLensData;
use crate::nuke_lens_common::STATIC_FRAME_NUMBER;

/// Format a knob value as a Nuke curve string or static value.
///
/// If there is only one frame (static), write the value directly.
/// If animated, write as `{{curve x<frame> <value> ... }}`.
fn format_knob_value(
    data: &NukeLensData,
    layer_index: u8,
    param_index: usize,
    min_frame: FrameNumber,
    max_frame: FrameNumber,
) -> String {
    let is_static =
        min_frame == STATIC_FRAME_NUMBER && max_frame == STATIC_FRAME_NUMBER;

    if is_static {
        let block = data
            .lens_parameters
            .get(&(layer_index, STATIC_FRAME_NUMBER));
        let value = match block {
            Some(b) => b[param_index],
            None => 0.0,
        };
        format!("{:.7}", value)
    } else {
        let mut s = String::from("{{curve");
        for frame in min_frame..=max_frame {
            if let Some(block) = data.lens_parameters.get(&(layer_index, frame))
            {
                let _ = write!(s, " x{} {:.7}", frame, block[param_index]);
            }
        }
        s.push_str(" }}");
        s
    }
}

/// Write NukeLensData to a Nuke .nk format string.
pub fn write_nuke_lens_string(data: &NukeLensData) -> Result<String> {
    let mut output = String::new();

    for layer_idx in 0..data.layer_count {
        let lens_model_type = data.layer_lens_model_types[layer_idx as usize];
        let node_type_str = match lookup_nuke_node_type_str(lens_model_type) {
            Some(s) => s,
            None => bail!("Unsupported lens model type: {:?}", lens_model_type),
        };

        let (min_frame, max_frame) = data.layer_frame_range[layer_idx as usize];
        let cam = &data.camera_parameters;

        writeln!(output, "{} {{", node_type_str)?;
        writeln!(output, " tde4_focal_length_cm {:.7}", cam.focal_length_cm)?;
        writeln!(
            output,
            " tde4_filmback_width_cm {:.7}",
            cam.film_back_width_cm
        )?;
        writeln!(
            output,
            " tde4_filmback_height_cm {:.7}",
            cam.film_back_height_cm
        )?;
        writeln!(
            output,
            " tde4_lens_center_offset_x_cm {:.7}",
            cam.lens_center_offset_x_cm
        )?;
        writeln!(
            output,
            " tde4_lens_center_offset_y_cm {:.7}",
            cam.lens_center_offset_y_cm
        )?;
        writeln!(output, " tde4_pixel_aspect {:.7}", cam.pixel_aspect)?;

        let knob_defs = lens_model_knob_definitions(lens_model_type);
        for &(knob_name, param_index, _default) in knob_defs {
            let value_str = format_knob_value(
                data,
                layer_idx,
                param_index,
                min_frame,
                max_frame,
            );
            writeln!(output, " {} {}", knob_name, value_str)?;
        }

        writeln!(output, "}}")?;
    }

    Ok(output)
}

/// Write NukeLensData to a file in Nuke .nk format.
pub fn write_nuke_lens_file(
    file_path: &str,
    data: &NukeLensData,
) -> Result<()> {
    let content = write_nuke_lens_string(data)?;
    let mut file = std::fs::File::create(file_path)?;
    file.write_all(content.as_bytes())?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::nuke_lens_common::{
        CameraParameters, LensModelType, MAX_LENS_PARAMETER_COUNT,
    };
    use crate::nuke_lens_reader::read_nuke_lens_file;
    use std::collections::HashMap;

    fn test_data_dir() -> std::path::PathBuf {
        let mut path = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        path.pop();
        path.pop();
        path.pop();
        path.push("tests");
        path.push("data");
        path.push("lens_example_files");
        path
    }

    /// Read a file, write it out, read it back, compare data.
    fn roundtrip_test(file_name: &str) {
        let path = test_data_dir().join(file_name);
        if !path.exists() {
            return;
        }

        let original = read_nuke_lens_file(path.to_str().unwrap()).unwrap();
        if original.layer_count == 0 {
            // No supported layers to roundtrip.
            return;
        }

        let tmp_dir = std::env::temp_dir();
        let tmp_path = tmp_dir.join(format!("roundtrip_{}", file_name));
        write_nuke_lens_file(tmp_path.to_str().unwrap(), &original).unwrap();

        let reloaded = read_nuke_lens_file(tmp_path.to_str().unwrap()).unwrap();

        assert_eq!(original.layer_count, reloaded.layer_count);
        assert_eq!(
            original.layer_lens_model_types,
            reloaded.layer_lens_model_types
        );
        assert_eq!(original.layer_frame_range, reloaded.layer_frame_range);

        let cam_orig = &original.camera_parameters;
        let cam_new = &reloaded.camera_parameters;
        assert!(
            (cam_orig.focal_length_cm - cam_new.focal_length_cm).abs() < 1e-6
        );
        assert!(
            (cam_orig.film_back_width_cm - cam_new.film_back_width_cm).abs()
                < 1e-6
        );
        assert!(
            (cam_orig.film_back_height_cm - cam_new.film_back_height_cm).abs()
                < 1e-6
        );
        assert!(
            (cam_orig.lens_center_offset_x_cm
                - cam_new.lens_center_offset_x_cm)
                .abs()
                < 1e-6
        );
        assert!(
            (cam_orig.lens_center_offset_y_cm
                - cam_new.lens_center_offset_y_cm)
                .abs()
                < 1e-6
        );
        assert!((cam_orig.pixel_aspect - cam_new.pixel_aspect).abs() < 1e-6);

        // Compare all lens parameter blocks.
        for (&key, orig_block) in &original.lens_parameters {
            let new_block = reloaded
                .lens_parameters
                .get(&key)
                .expect("Missing parameter block after roundtrip");
            for i in 0..MAX_LENS_PARAMETER_COUNT {
                assert!(
                    (orig_block[i] - new_block[i]).abs() < 1e-6,
                    "Mismatch at key {:?} param index {}: {} vs {}",
                    key,
                    i,
                    orig_block[i],
                    new_block[i]
                );
            }
        }

        // Clean up.
        let _ = std::fs::remove_file(&tmp_path);
    }

    #[test]
    fn test_roundtrip_classic_v003() {
        roundtrip_test("ldpk_nuke_distortion_classic_v003.nk");
    }

    #[test]
    fn test_roundtrip_classic_v004() {
        roundtrip_test("ldpk_nuke_distortion_classic_v004.nk");
    }

    #[test]
    fn test_roundtrip_v001() {
        roundtrip_test("ldpk_nuke_distortion_v001.nk");
    }

    #[test]
    fn test_roundtrip_v002() {
        roundtrip_test("ldpk_nuke_distortion_v002.nk");
    }

    #[test]
    fn test_write_static_classic() {
        let mut lens_parameters = HashMap::new();
        let mut block = [0.0_f64; MAX_LENS_PARAMETER_COUNT];
        block[0] = 0.05; // Distortion
        block[1] = 1.0; // Anamorphic_Squeeze
        block[2] = 0.01; // Curvature_X
        block[3] = -0.02; // Curvature_Y
        block[4] = 0.03; // Quartic_Distortion
        lens_parameters.insert((0_u8, STATIC_FRAME_NUMBER), block);

        let data = NukeLensData {
            layer_count: 1,
            layer_lens_model_types: vec![LensModelType::TdeClassic],
            layer_frame_range: vec![(STATIC_FRAME_NUMBER, STATIC_FRAME_NUMBER)],
            camera_parameters: CameraParameters {
                focal_length_cm: 5.0,
                film_back_width_cm: 3.6,
                film_back_height_cm: 2.4,
                pixel_aspect: 1.0,
                lens_center_offset_x_cm: 0.0,
                lens_center_offset_y_cm: 0.0,
            },
            lens_parameters,
        };

        let output = write_nuke_lens_string(&data).unwrap();
        assert!(output.contains("LD_3DE_Classic_LD_Model {"));
        assert!(output.contains("Distortion 0.0500000"));
        assert!(output.contains("Anamorphic_Squeeze 1.0000000"));
        assert!(output.contains("tde4_focal_length_cm 5.0000000"));

        // Roundtrip through reader.
        let tmp_path =
            std::env::temp_dir().join("test_write_static_classic.nk");
        write_nuke_lens_file(tmp_path.to_str().unwrap(), &data).unwrap();
        let reloaded = read_nuke_lens_file(tmp_path.to_str().unwrap()).unwrap();
        assert_eq!(reloaded.layer_count, 1);
        assert_eq!(
            reloaded.layer_lens_model_types[0],
            LensModelType::TdeClassic
        );
        let rb = reloaded
            .lens_parameters
            .get(&(0, STATIC_FRAME_NUMBER))
            .unwrap();
        assert!((rb[0] - 0.05).abs() < 1e-7);
        assert!((rb[1] - 1.0).abs() < 1e-7);
        let _ = std::fs::remove_file(&tmp_path);
    }

    #[test]
    fn test_write_animated_radial_std_deg4() {
        let mut lens_parameters = HashMap::new();
        for frame in 1_u16..=3 {
            let mut block = [0.0_f64; MAX_LENS_PARAMETER_COUNT];
            block[0] = 0.1 * frame as f64; // Distortion_Degree_2
            lens_parameters.insert((0_u8, frame), block);
        }

        let data = NukeLensData {
            layer_count: 1,
            layer_lens_model_types: vec![LensModelType::TdeRadialStdDeg4],
            layer_frame_range: vec![(1, 3)],
            camera_parameters: CameraParameters::default(),
            lens_parameters,
        };

        let output = write_nuke_lens_string(&data).unwrap();
        assert!(output.contains("{{curve x1"));
        assert!(output.contains("x2"));
        assert!(output.contains("x3"));

        // Roundtrip.
        let tmp_path =
            std::env::temp_dir().join("test_write_animated_radial.nk");
        write_nuke_lens_file(tmp_path.to_str().unwrap(), &data).unwrap();
        let reloaded = read_nuke_lens_file(tmp_path.to_str().unwrap()).unwrap();
        assert_eq!(reloaded.layer_count, 1);
        assert_eq!(reloaded.layer_frame_range[0], (1, 3));
        let b2 = reloaded.lens_parameters.get(&(0, 2)).unwrap();
        assert!((b2[0] - 0.2).abs() < 1e-6);
        let _ = std::fs::remove_file(&tmp_path);
    }
}
