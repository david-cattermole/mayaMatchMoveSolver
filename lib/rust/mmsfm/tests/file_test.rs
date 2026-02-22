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

#![allow(unused)]
#![allow(unused_imports)]
#![allow(dead_code)]
#![allow(non_snake_case)]

mod common;

use crate::common::data_utils::load_marker_data;
use crate::common::visualization::scene::ViewConfigurationBuilder;
use crate::common::{
    test_output_file_naming, OutputFileNaming, TestType, VisualizationType,
};
use anyhow::Result;
use mmsfm_rust::datatype::{
    CameraFilmBack, CameraIntrinsics, ImageSize, MillimeterUnit, UnitValue,
};
use std::ffi::OsStr;
use std::fs::File;
use std::io::Read;
use std::path::Path;
use std::path::PathBuf;

use mmio::uvtrack_reader::UVTrackV1Parser;

fn construct_input_file_path(
    base_dir: &Path,
    file_name: &str,
) -> Result<PathBuf> {
    // This function is specific to this test - it looks directly in the data dir
    // rather than the uvtrack subdirectory like construct_uvtrack_input_file_path
    let mut file_path = PathBuf::new();
    file_path.push(base_dir);
    file_path.push(file_name);
    if !file_path.is_file() {
        anyhow::bail!("Could not find file name {:?}", file_path);
    }
    Ok(file_path)
}

fn read_ascii_file(file_name: &OsStr) -> Result<String> {
    let mut file = File::open(file_name)?;
    let mut buffer = String::new();
    file.read_to_string(&mut buffer)?;
    Ok(buffer)
}

#[test]
fn test_parse_v1_simple() -> Result<()> {
    let content = r#"1
My Point Name
1
1 0.0 1.0 1.0
        "#;

    println!("File data:");
    println!("{}", content);

    let (file_info, markers) = UVTrackV1Parser::parse_string(content)?;

    assert!(file_info.marker_undistorted);
    assert!(!file_info.marker_distorted);
    assert_eq!(markers.len(), 1);

    assert_eq!(markers.names[0], "My Point Name");

    let frame_data = &markers.frame_data[0];
    assert_eq!(frame_data.frames[0], 1);
    assert_eq!(frame_data.u_coords[0], 0.0);
    assert_eq!(frame_data.v_coords[0], 1.0);
    assert_eq!(frame_data.weights[0], 1.0);

    Ok(())
}
