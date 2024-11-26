//
// Copyright (C) 2023 David Cattermole.
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
use log::{debug, info};
use mmimage_rust::image_read_pixels_exr_f16x4;
use mmimage_rust::image_read_pixels_exr_f32x4;

mod common;

const FILE_NAMES: &[&str] = &[
    "Beachball/multipart.0001.exr",
    "Beachball/multipart.0008.exr",
    "Beachball/singlepart.0001.exr",
    "Beachball/singlepart.0008.exr",
    "ScanLines/Blobbies.exr",
    "ScanLines/CandleGlass.exr",
    "ScanLines/Cannon.exr",
    "ScanLines/Desk.exr",
    "ScanLines/MtTamWest.exr",
    "ScanLines/PrismsLenses.exr",
    "ScanLines/StillLife.exr",
    "ScanLines/Tree.exr",
    "TestImages/AllHalfValues.exr",
    "TestImages/BrightRings.exr",
];

#[test]
fn read_as_f32x4() -> Result<()> {
    let base_dir_path = common::find_openexr_images_dir()?;
    let file_paths =
        common::construct_image_file_paths(&base_dir_path, FILE_NAMES)?;

    let vertical_flip = false;
    for file_path in file_paths {
        let file_path_str = file_path.as_path().to_str();
        match file_path_str {
            Some(value) => {
                info!("Reading: {}", value);
                let (meta_data, pixel_data) =
                    image_read_pixels_exr_f32x4(value, vertical_flip)?;
                debug!("Metadata: {:?}", meta_data);
                debug!("PixelData: {:?}", pixel_data);
            }
            _ => (),
        }
    }

    Ok(())
}

#[test]
fn read_as_f16x4() -> Result<()> {
    let base_dir_path = common::find_openexr_images_dir()?;
    let file_paths =
        common::construct_image_file_paths(&base_dir_path, FILE_NAMES)?;

    let vertical_flip = false;
    for file_path in file_paths {
        let file_path_str = file_path.as_path().to_str();
        match file_path_str {
            Some(value) => {
                info!("Reading: {}", value);
                let (meta_data, pixel_data) =
                    image_read_pixels_exr_f16x4(value, vertical_flip)?;
                debug!("Metadata: {:?}", meta_data);
                debug!("PixelData: {:?}", pixel_data);
            }
            _ => (),
        }
    }

    Ok(())
}
