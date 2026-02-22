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

//! Triangulation test using the test cube dataset with known camera poses.

#![allow(unused)]
#![allow(unused_imports)]
#![allow(dead_code)]
#![allow(non_snake_case)]

mod common;

use crate::common::data_utils::load_marker_data;
use crate::common::marker_noise::add_noise_to_markers;
use crate::common::triangulation_utils::run_triangulation_test_from_file;
use crate::common::{
    test_output_file_naming, DataCondition, OutputFileNaming, TestType,
    VisualizationType,
};
use anyhow::Result;
use mmio::uvtrack_reader::FrameRange;
use mmsfm_rust::datatype::{CameraFilmBack, MillimeterUnit, UnitValue};
use nalgebra::Vector3;

fn run_triangulation_cube_b(is_noisy: bool) -> Result<()> {
    let (mut markers, frame_range) =
        load_marker_data("test_cube_b_markers_v1_fmt.uv")?;

    let (test_base_name, condition, threshold) = if is_noisy {
        add_noise_to_markers(&mut markers, 0.005);
        ("Triangulation Cube - B (noisy)", DataCondition::Noisy, 5.0)
    } else {
        ("Triangulation Cube - B (clean)", DataCondition::Clean, 1.0)
    };

    // Create output file naming.
    let naming = test_output_file_naming(
        TestType::Triangulation,
        "cube_b",
        VisualizationType::Scene3d,
    )
    .with_condition(condition);

    let expected_frame_range = FrameRange {
        start_frame: 1,
        end_frame: 101,
    };
    let correspondence_frames = (1, 101);
    let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
    let focal_length = MillimeterUnit::new(35.0);

    run_triangulation_test_from_file(
        &markers,
        &frame_range,
        expected_frame_range,
        correspondence_frames,
        film_back,
        focal_length,
        Vector3::new(-10.0, 0.0, 0.0),
        Vector3::new(0.0, -45.0, 0.0),
        test_base_name,
        &naming,
        false,
        threshold,
    )
}

#[test]
fn test_triangulation_clean_cube_b() -> Result<()> {
    run_triangulation_cube_b(false)
}

#[test]
fn test_triangulation_noisy_cube_b() -> Result<()> {
    run_triangulation_cube_b(true)
}
