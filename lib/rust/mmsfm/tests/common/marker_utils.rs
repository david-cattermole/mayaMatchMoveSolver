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

use mmio::uvtrack_reader::MarkersData;
use mmsfm_rust::datatype::{UvPoint2, UvValue};

use crate::common::FramePair;

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

/// Extracts UV point correspondences between two specific frames.
pub fn extract_specific_frame_correspondences(
    markers: &MarkersData,
    frame_a: u32,
    frame_b: u32,
) -> Result<(Vec<UvPoint2<f64>>, Vec<UvPoint2<f64>>)> {
    let mut uv_coords_a = Vec::new();
    let mut uv_coords_b = Vec::new();

    for frame_data in &markers.frame_data {
        let idx_a = frame_data.frames.iter().position(|&f| f == frame_a);
        let idx_b = frame_data.frames.iter().position(|&f| f == frame_b);

        if let (Some(idx_a), Some(idx_b)) = (idx_a, idx_b) {
            let u_a = frame_data.u_coords[idx_a];
            let v_a = frame_data.v_coords[idx_a];
            let weight_a = frame_data.weights[idx_a];

            let u_b = frame_data.u_coords[idx_b];
            let v_b = frame_data.v_coords[idx_b];
            let weight_b = frame_data.weights[idx_b];

            if weight_a > 0.1 && weight_b > 0.1 {
                uv_coords_a.push(UvValue::point2(u_a, v_a));
                uv_coords_b.push(UvValue::point2(u_b, v_b));
            }
        }
    }

    if uv_coords_a.len() < 5 {
        anyhow::bail!(
            "Insufficient point correspondences: found {} but need at least 5",
            uv_coords_a.len()
        );
    }

    if DEBUG {
        println!(
            "Extracted {} point correspondences between frames {} and {}",
            uv_coords_a.len(),
            frame_a,
            frame_b
        );
    }

    Ok((uv_coords_a, uv_coords_b))
}

/// Extracts UV point correspondences between two frames, with optional index filtering.
pub fn extract_point_correspondences(
    markers: &MarkersData,
    frame_pair: FramePair,
    point_indices: Option<Vec<usize>>,
) -> Result<(Vec<UvPoint2<f64>>, Vec<UvPoint2<f64>>)> {
    let mut all_uv_coords_a = Vec::new();
    let mut all_uv_coords_b = Vec::new();

    for frame_data in &markers.frame_data {
        let idx_a = frame_data
            .frames
            .iter()
            .position(|&f| f == frame_pair.frame_a);
        let idx_b = frame_data
            .frames
            .iter()
            .position(|&f| f == frame_pair.frame_b);

        if let (Some(idx_a), Some(idx_b)) = (idx_a, idx_b) {
            let u_a = frame_data.u_coords[idx_a];
            let v_a = frame_data.v_coords[idx_a];
            let weight_a = frame_data.weights[idx_a];

            let u_b = frame_data.u_coords[idx_b];
            let v_b = frame_data.v_coords[idx_b];
            let weight_b = frame_data.weights[idx_b];

            if weight_a > 0.1 && weight_b > 0.1 {
                all_uv_coords_a.push(UvValue::point2(u_a, v_a));
                all_uv_coords_b.push(UvValue::point2(u_b, v_b));
            }
        }
    }

    let (uv_coords_a, uv_coords_b) = if let Some(indices) = point_indices {
        let mut selected_a = Vec::new();
        let mut selected_b = Vec::new();

        for &idx in &indices {
            if idx < all_uv_coords_a.len() {
                selected_a.push(all_uv_coords_a[idx]);
                selected_b.push(all_uv_coords_b[idx]);
            } else {
                anyhow::bail!(
                    "Point index {} is out of range. Available points: {}",
                    idx,
                    all_uv_coords_a.len()
                );
            }
        }
        (selected_a, selected_b)
    } else {
        (all_uv_coords_a, all_uv_coords_b)
    };

    if uv_coords_a.len() < 5 {
        anyhow::bail!(
            "Insufficient point correspondences: found {} but need at least 5",
            uv_coords_a.len()
        );
    }

    Ok((uv_coords_a, uv_coords_b))
}
