//
// Copyright (C) 2020, 2021 David Cattermole.
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


pub mod attr;
pub mod constant;
pub mod core;
pub mod math;
pub mod node;
pub mod scene;

pub struct Camera {
    pub sensor_width_mm: f64,
    pub focal_length_mm: f64,
}

pub fn make_camera(width: f64, focal: f64) -> Camera {
    println!("Make camera. width={} focal={}", width, focal);
    Camera {
        sensor_width_mm: width,
        focal_length_mm: focal,
    }
}

pub fn make_camera_default() -> Camera {
    println!("Make default camera.");
    let width = 36.0;
    let focal = 50.0;
    make_camera(width, focal)
}
