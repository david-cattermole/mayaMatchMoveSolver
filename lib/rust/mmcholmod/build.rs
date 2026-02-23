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

fn main() {
    // SuiteSparse CHOLMOD library configuration.
    //
    // Environment variables can override default paths:
    //   CHOLMOD_INCLUDE_DIR - path to directory containing suitesparse/cholmod.h
    //   CHOLMOD_LIB_DIR     - path to directory containing library files

    let mut inc_dirs: Vec<String> = Vec::new();
    let mut lib_dirs: Vec<String> = Vec::new();

    // Check for environment variable overrides.
    if let Ok(inc) = std::env::var("CHOLMOD_INCLUDE_DIR") {
        println!("cargo:rerun-if-env-changed=CHOLMOD_INCLUDE_DIR");
        inc_dirs.push(inc);
    }
    if let Ok(lib) = std::env::var("CHOLMOD_LIB_DIR") {
        println!("cargo:rerun-if-env-changed=CHOLMOD_LIB_DIR");
        lib_dirs.push(lib);
    }

    // Fall back to system paths if no overrides given.
    if inc_dirs.is_empty() {
        inc_dirs.push("/usr/include".to_string());
        inc_dirs.push("/usr/local/include".to_string());
    }
    if lib_dirs.is_empty() {
        lib_dirs.push("/usr/lib/x86_64-linux-gnu".to_string()); // Debian/Ubuntu
        lib_dirs.push("/usr/lib".to_string()); // Arch
        lib_dirs.push("/usr/lib64".to_string()); // Rocky/RHEL
    }

    // Build C wrapper interface.
    cc::Build::new()
        .file("c_code/interface_cholmod.c")
        .includes(&inc_dirs)
        .compile("c_code_cholmod");

    // Link SuiteSparse libraries dynamically (required by the LGPL).
    let libs = vec![
        "cholmod",
        "amd",
        "camd",
        "colamd",
        "ccolamd",
        "suitesparseconfig",
    ];

    for d in &lib_dirs {
        println!("cargo:rustc-link-search=native={}", d);
    }
    for l in &libs {
        println!("cargo:rustc-link-lib=dylib={}", l);
    }
}
