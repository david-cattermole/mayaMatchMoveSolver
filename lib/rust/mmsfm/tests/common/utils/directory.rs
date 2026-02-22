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

use anyhow::Result;
use std::path::{Path, PathBuf};

/// Finds the project's test data directory.
pub fn find_data_dir() -> Result<PathBuf> {
    // "<project_root>/target/debug/deps/mmsfm_rust-xxx"
    let mut directory = PathBuf::from(std::env::current_exe().unwrap());

    // "<project_root>/target/debug/deps"
    assert!(directory.pop());

    // "<project_root>/target/debug"
    assert!(directory.pop());

    // "<project_root>/target"
    assert!(directory.pop());

    // "<project_root>"
    assert!(directory.pop());

    // "<project_root>/tests/data"
    directory.push("tests");
    directory.push("data");

    if directory.is_dir() {
        Ok(directory)
    } else {
        anyhow::bail!("Could not find data directory {:?}.", directory)
    }
}

/// Finds or creates the project's test output directory.
pub fn find_output_dir() -> Result<PathBuf> {
    // "<project_root>/target/debug/deps/mmsfm_rust-xxx"
    let mut directory = PathBuf::from(std::env::current_exe().unwrap());

    // "<project_root>/target/debug/deps"
    assert!(directory.pop());

    // "<project_root>/target/debug"
    assert!(directory.pop());

    // "<project_root>/target"
    assert!(directory.pop());

    // "<project_root>"
    assert!(directory.pop());

    // "<project_root>/lib/rust/mmsfm/tests/output"
    directory.push("lib");
    directory.push("rust");
    directory.push("mmsfm");
    directory.push("tests");
    directory.push("output");

    Ok(directory)
}

/// Constructs a path to a uvtrack input file in the test data directory.
pub fn construct_uvtrack_input_file_path(
    base_dir: &Path,
    file_name: &str,
) -> Result<PathBuf> {
    let mut file_path = PathBuf::new();
    file_path.push(base_dir);
    file_path.push("uvtrack");
    file_path.push(file_name);
    if !file_path.is_file() {
        anyhow::bail!("Could not find file name {:?}", file_path);
    }
    Ok(file_path)
}

/// Constructs a path to an output file in the given base directory.
pub fn construct_output_file_path(base_dir: &Path, file_name: &str) -> PathBuf {
    let mut file_path = PathBuf::new();
    file_path.push(base_dir);
    file_path.push(file_name);

    // Create the parent directory if it doesn't exist.
    if let Some(parent) = file_path.parent() {
        if !parent.exists() {
            std::fs::create_dir_all(parent).unwrap_or_else(|e| {
                eprintln!("Failed to create directory {:?}: {}", parent, e)
            });
        }
    }

    file_path
}
