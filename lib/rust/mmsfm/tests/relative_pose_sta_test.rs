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

//! Relative pose tests for the stA dataset.

#![allow(unused)]
#![allow(unused_imports)]
#![allow(dead_code)]
#![allow(non_snake_case)]

mod common;

use crate::common::bundle_adjustment_solver_type_to_naming;
use crate::common::DataCondition;
use crate::common::TestType;
use crate::common::VisualizationType;
use crate::common::{test_output_file_naming, OutputFileNaming};
use anyhow::Result;
use common::{
    load_marker_data, run_relative_pose_dataset_test,
    select_optimal_frame_pair, visualization::scene::ViewConfigurationBuilder,
};
use mmsfm_rust::datatype::{
    CameraFilmBack, ImageSize, MillimeterUnit, UnitValue,
};

#[test]
fn test_relative_pose_clean_sta() -> Result<()> {
    let (markers, frame_range) = load_marker_data("stA_v1_format.uv")?;
    let frame_pair = select_optimal_frame_pair(&markers, &frame_range)?;

    let film_back = CameraFilmBack::new(
        MillimeterUnit::new(36.0),
        MillimeterUnit::new(20.25), // 16/9 aspect ratio.
    );
    let focal_length = MillimeterUnit::new(56.4); // ~59.12 degrees FoV.
    let image_size_a = ImageSize::from_pixels(3600.0, 2400.0);
    let image_size_b = ImageSize::from_pixels(3600.0, 2400.0);

    let views = vec![
        ViewConfigurationBuilder::new()
            .view_name("front")
            .rotation_ortho_front()
            .resolution_hd()
            .build(),
        ViewConfigurationBuilder::new()
            .view_name("right")
            .rotation_ortho_right()
            .resolution_hd()
            .build(),
        ViewConfigurationBuilder::new()
            .view_name("top")
            .rotation_ortho_top()
            .resolution_hd()
            .build(),
    ];

    let naming = test_output_file_naming(
        TestType::RelativePose,
        "sta",
        VisualizationType::Scene3d,
    );

    let result = run_relative_pose_dataset_test(
        &markers,
        &frame_pair,
        10, // Expect at least 10 markers.
        "stA (clean)",
        &naming,
        views,
        focal_length,
        film_back,
        image_size_a,
        image_size_b,
    );
    result
}
