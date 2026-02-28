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

//! mmsfm CLI executable - Structure from Motion camera solver.

use anyhow::{Context, Result};

use mmio::bundle_writer::{write_bundle_file, BundlePoint};
use mmio::kuper_writer::{
    extract_zxy_euler_angles, maya_pose_to_kuper, write_kuper_file,
    KuperFrameData,
};
use mmio::mmcamera_common::{
    MmCameraAttrData, MmCameraData, MmCameraImageData,
};
use mmio::mmcamera_writer::write_mmcamera_file;
use mmio::uvtrack_reader::{FrameRange, MarkersData};
use mmsfm::datatype::common::UnitValue;
use mmsfm::datatype::{
    BundlePositions, CameraFilmBack, CameraIntrinsics, CameraPoses,
};

use crate::cli::CliArgs;

pub fn write_kuper_output(
    kuper_path: &str,
    camera_poses: &CameraPoses,
    focal_length_mm: f64,
) -> Result<()> {
    let frame_list = camera_poses.generate_sorted_frame_list();

    let kuper_frames: Vec<KuperFrameData> = frame_list
        .iter()
        .map(|&frame| {
            let pose = &camera_poses[&frame];
            maya_pose_to_kuper(
                frame,
                pose.center(),
                pose.rotation(),
                focal_length_mm,
            )
        })
        .collect();

    write_kuper_file(kuper_path, &kuper_frames)
        .with_context(|| format!("Failed to write Kuper file: {}", kuper_path))
}

/// Write bundle positions to a file, named by marker index.
pub fn write_bundle_output(
    bundle_path: &str,
    markers: &MarkersData,
    bundle_positions: &BundlePositions,
) -> Result<()> {
    let bundles: Vec<BundlePoint> = bundle_positions
        .iter()
        .map(|(&marker_index, &position)| {
            let name = markers
                .names
                .get(marker_index)
                .cloned()
                .unwrap_or_else(|| marker_index.to_string());
            BundlePoint { name, position }
        })
        .collect();

    write_bundle_file(bundle_path, &bundles).with_context(|| {
        format!("Failed to write bundle file: {}", bundle_path)
    })
}

pub fn write_mmcamera_output(
    mmcamera_path: &str,
    args: &CliArgs,
    camera_poses: &CameraPoses,
    camera_intrinsics: &CameraIntrinsics,
    film_back: &CameraFilmBack<f64>,
    frame_range: &FrameRange,
) -> Result<()> {
    write_mmcamera_output_inner(
        mmcamera_path,
        args.prefix.as_deref().unwrap_or("camera"),
        Some(args.image_width as i64),
        Some(args.image_height as i64),
        camera_poses,
        camera_intrinsics,
        film_back,
        frame_range,
    )
}

/// Write camera poses to an .mmcamera file without needing full CLI args.
pub fn write_mmcamera_output_raw(
    mmcamera_path: &str,
    camera_poses: &CameraPoses,
    camera_intrinsics: &CameraIntrinsics,
    film_back: &CameraFilmBack<f64>,
    frame_range: &FrameRange,
) -> Result<()> {
    write_mmcamera_output_inner(
        mmcamera_path,
        "camera",
        None,
        None,
        camera_poses,
        camera_intrinsics,
        film_back,
        frame_range,
    )
}

fn write_mmcamera_output_inner(
    mmcamera_path: &str,
    camera_name: &str,
    image_width: Option<i64>,
    image_height: Option<i64>,
    camera_poses: &CameraPoses,
    camera_intrinsics: &CameraIntrinsics,
    film_back: &CameraFilmBack<f64>,
    frame_range: &FrameRange,
) -> Result<()> {
    let frame_list = camera_poses.generate_sorted_frame_list();

    let (focal_length_mm, _lens_cx, _lens_cy) =
        camera_intrinsics.to_physical_parameters();
    let focal_length_val = focal_length_mm.value();
    let film_back_width_val = film_back.width.value();
    let film_back_height_val = film_back.height.value();

    let mut translate_x = Vec::with_capacity(frame_list.len());
    let mut translate_y = Vec::with_capacity(frame_list.len());
    let mut translate_z = Vec::with_capacity(frame_list.len());
    let mut rotate_x = Vec::with_capacity(frame_list.len());
    let mut rotate_y = Vec::with_capacity(frame_list.len());
    let mut rotate_z = Vec::with_capacity(frame_list.len());
    let mut focal_length = Vec::with_capacity(frame_list.len());
    let mut fb_width = Vec::with_capacity(frame_list.len());
    let mut fb_height = Vec::with_capacity(frame_list.len());
    let mut fb_offset_x = Vec::with_capacity(frame_list.len());
    let mut fb_offset_y = Vec::with_capacity(frame_list.len());

    for &frame in &frame_list {
        let pose = &camera_poses[&frame];
        let center = pose.center();
        let (rx, ry, rz) = extract_zxy_euler_angles(pose.rotation());
        let f = frame as i64;

        translate_x.push((f, center.x));
        translate_y.push((f, center.y));
        translate_z.push((f, center.z));
        rotate_x.push((f, rx));
        rotate_y.push((f, ry));
        rotate_z.push((f, rz));
        focal_length.push((f, focal_length_val));
        fb_width.push((f, film_back_width_val));
        fb_height.push((f, film_back_height_val));
        fb_offset_x.push((f, 0.0));
        fb_offset_y.push((f, 0.0));
    }

    let data = MmCameraData {
        name: camera_name.to_string(),
        start_frame: frame_range.start_frame as i64,
        end_frame: frame_range.end_frame as i64,
        image: MmCameraImageData {
            file_path: None,
            width: image_width,
            height: image_height,
            pixel_aspect_ratio: Some(1.0),
        },
        attr: MmCameraAttrData {
            translate_x,
            translate_y,
            translate_z,
            rotate_x,
            rotate_y,
            rotate_z,
            focal_length,
            film_back_width: fb_width,
            film_back_height: fb_height,
            film_back_offset_x: fb_offset_x,
            film_back_offset_y: fb_offset_y,
        },
    };

    write_mmcamera_file(std::path::Path::new(mmcamera_path), &data)
        .with_context(|| {
            format!("Failed to write mmcamera file: {}", mmcamera_path)
        })
}
