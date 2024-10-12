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
use log::info;
use mmimage_rust::image_read_metadata_exr;

mod common;

const FILE_NAMES: &[&str] = &[
    "Beachball/multipart.0001.exr",
    "Beachball/multipart.0008.exr",
    "Beachball/singlepart.0001.exr",
    "Beachball/singlepart.0008.exr",
    "LuminanceChroma/CrissyField.exr",
    "LuminanceChroma/Flowers.exr",
    "LuminanceChroma/Garden.exr",
    "LuminanceChroma/MtTamNorth.exr",
    "LuminanceChroma/StarField.exr",
    "MultiResolution/Bonita.exr",
    "MultiResolution/Kapaa.exr",
    "MultiResolution/StageEnvLatLong.exr",
    "MultiView/Balls.exr",
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
    "TestImages/WideFloatRange.exr",
];

#[test]
fn main() -> Result<()> {
    let base_dir_path = common::find_openexr_images_dir()?;
    let file_paths =
        common::construct_image_file_paths(&base_dir_path, FILE_NAMES)?;

    for file_path in file_paths {
        let file_path_str = file_path.as_path().to_str();
        match file_path_str {
            Some(value) => {
                info!("Reading: {}", value);
                let metadata = image_read_metadata_exr(value)?;
                info!("{:#?}", metadata);

                let attr_names = metadata.all_named_attribute_names();
                info!("Attr Name Count: {}", attr_names.len());
                for attr_name in attr_names {
                    info!("Attr Name: {:#?}", attr_name);
                    let has_attr = metadata.has_named_attribute(&attr_name);
                    let attr_type =
                        metadata.get_named_attribute_type_index(&attr_name);
                    let value = metadata.get_named_attribute_as_f32(&attr_name);
                    info!("Attr Name Exists: {:#?}", has_attr);
                    info!("Attr Type: {:#?}", attr_type);
                    info!("Attr Value: {:#?}", value);
                }

                let attr_name = "focal_length";
                let has_focal_length = metadata.has_named_attribute(&attr_name);
                let focal_length_type =
                    metadata.get_named_attribute_type_index(&attr_name);
                let focal_length =
                    metadata.get_named_attribute_as_f32(&attr_name);
                info!("Focal Length Name Exists: {:#?}", has_focal_length);
                info!("Focal Length Type: {:#?}", focal_length_type);
                info!("Focal Length Value: {:#?}", focal_length);
            }
            _ => (),
        }
    }

    Ok(())
}
