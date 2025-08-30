//
// Copyright (C) 2024 David Cattermole.
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

use anyhow::bail;
use anyhow::Result;
use std::path::Path;
use std::path::PathBuf;

#[allow(dead_code)]
pub fn find_data_dir() -> Result<PathBuf> {
    // // "<project_root>/lib/rust/mmscenegraph/tests/common/mod.rs"
    // let this_file = file!();

    // "<project_root>/target/debug/deps/curve_curvature-a1543a4f123cfc9f"
    let mut directory = PathBuf::from(std::env::current_exe().unwrap());

    // "<project_root>/target/debug/deps"
    assert!(directory.pop());

    // "<project_root>/target/debug"
    assert!(directory.pop());

    // "<project_root>/target"
    assert!(directory.pop());

    // "<project_root>"
    assert!(directory.pop());

    // "<project_root>/lib/rust/mmscenegraph/tests/data"
    directory.push("lib");
    directory.push("rust");
    directory.push("mmscenegraph");
    directory.push("tests");
    directory.push("data");

    if directory.is_dir() {
        Ok(directory)
    } else {
        bail!("Could not find data directory {:?}.", directory)
    }
}

#[allow(dead_code)]
pub fn find_output_dir() -> Result<PathBuf> {
    // "<project_root>/target/debug/deps/curve_curvature-a1543a4f123cfc9f"
    let mut directory = PathBuf::from(std::env::current_exe().unwrap());

    // "<project_root>/target/debug/deps"
    assert!(directory.pop());

    // "<project_root>/target/debug"
    assert!(directory.pop());

    // "<project_root>/target"
    assert!(directory.pop());

    // "<project_root>"
    assert!(directory.pop());

    // "<project_root>/lib/rust/mmscenegraph/tests/output"
    directory.push("lib");
    directory.push("rust");
    directory.push("mmscenegraph");
    directory.push("tests");
    directory.push("output");

    // Create the output directory if it doesn't exist
    if !directory.exists() {
        std::fs::create_dir_all(&directory).map_err(|e| {
            anyhow::anyhow!(
                "Failed to create output directory {:?}: {}",
                directory,
                e
            )
        })?;
    }

    Ok(directory)
}

#[allow(dead_code)]
pub fn construct_input_file_path(
    base_dir: &Path,
    file_name: &str,
) -> Result<PathBuf> {
    let mut file_path = PathBuf::new();
    file_path.push(base_dir);
    file_path.push(file_name);
    if !file_path.is_file() {
        bail!("Could not find file name {:?}", file_path);
    }
    Ok(file_path)
}

#[allow(dead_code)]
pub fn construct_output_file_path(
    base_dir: &Path,
    file_name: &str,
) -> Result<PathBuf> {
    let mut file_path = PathBuf::new();
    file_path.push(base_dir);
    file_path.push(file_name);
    Ok(file_path)
}
