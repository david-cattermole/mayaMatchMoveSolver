//
// Copyright (C) 2023, 2024 David Cattermole.
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

use crate::shim_expand_file_path_string;

#[cxx::bridge(namespace = "mmcore")]
pub mod ffi {
    unsafe extern "C++" {
        // C++ includes needed for all files.
        include!("mmcore/_cxx.h");
        include!("mmcore/_symbol_export.h");
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

    extern "Rust" {
        pub fn shim_expand_file_path_string(value: &str, frame: i32) -> String;
    }
}
