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

use anyhow::Result;
use std::ffi::OsStr;
use std::fs::File;
use std::io::Read;

use mmscenegraph_rust::constant::FrameTime;
use mmscenegraph_rust::constant::Real;

#[allow(dead_code)]
pub fn read_chan_file(file_name: &OsStr) -> Result<Vec<(FrameTime, Real)>> {
    let mut file = File::open(file_name)?;
    let mut buffer = String::new();
    file.read_to_string(&mut buffer)?;

    let mut data = Vec::new();
    for line in buffer.lines() {
        let mut line_iter = line.split_ascii_whitespace();
        let line_start = line_iter.next().expect("First frame number.");
        let line_end = line_iter.next().expect("Second value.");

        let frame = line_start
            .parse::<FrameTime>()
            .expect("Frame number must be integer.");
        let value = line_end
            .parse::<Real>()
            .expect("Value must be floating-point.");
        data.push((frame, value));
    }

    Ok(data)
}

#[allow(dead_code)]
pub fn print_chan_data(data: &[(FrameTime, Real)]) {
    for pair in data {
        let frame: FrameTime = pair.0;
        let value: Real = pair.1;
        println!("frame={frame} value={value}");
    }
}
