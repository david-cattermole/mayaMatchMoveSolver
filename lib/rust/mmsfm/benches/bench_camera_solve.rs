//
// Copyright (C) 2026 David Cattermole.
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

//! Benchmarks comparing SparseLM vs SchurComplementLM bundle adjustment
//! backends on real camera solve datasets.

use std::hint::black_box;
use std::path::PathBuf;
use std::time::Duration;

use criterion::{criterion_group, criterion_main, BenchmarkId, Criterion};

use mmio::uvtrack_reader::{parse_file, FrameRange, MarkersData};
use mmsfm_rust::datatype::common::UnitValue;
use mmsfm_rust::datatype::{
    BundlePositions, CameraFilmBack, CameraIntrinsics, CameraPoses, ImageSize,
    MillimeterUnit,
};
use mmsfm_rust::sfm_camera::{
    camera_solve, BundleAdjustmentSolverType, CameraSolveConfig,
    SolveQualityMetrics,
};

/// Find the project test data directory relative to the crate manifest.
fn find_data_dir() -> PathBuf {
    let manifest_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    // lib/rust/mmsfm -> project root
    let project_root = manifest_dir
        .parent()
        .unwrap()
        .parent()
        .unwrap()
        .parent()
        .unwrap();
    project_root.join("tests").join("data")
}

/// Load marker data from a UV track file, applying the same
/// data-quality fixes as the test suite.
fn load_marker_data(file_name: &str) -> (MarkersData, FrameRange) {
    let data_dir = find_data_dir();
    let file_path = data_dir.join("uvtrack").join(file_name);
    assert!(
        file_path.is_file(),
        "Benchmark data file not found: {:?}",
        file_path
    );

    let (_file_info, mut markers) = parse_file(&file_path).unwrap();

    // Promote distorted coords when primary coords are all-zero.
    for frame_data in &mut markers.frame_data {
        let all_zero = frame_data.u_coords.iter().all(|&u| u == 0.0)
            && frame_data.v_coords.iter().all(|&v| v == 0.0);
        let has_dist = !frame_data.u_coords_dist.is_empty()
            && frame_data.u_coords_dist.len() == frame_data.u_coords.len();
        if all_zero && has_dist {
            frame_data
                .u_coords
                .copy_from_slice(&frame_data.u_coords_dist);
            frame_data
                .v_coords
                .copy_from_slice(&frame_data.v_coords_dist);
        }
    }

    // Remove single-frame markers.
    let keep: Vec<bool> = markers
        .frame_data
        .iter()
        .map(|fd| fd.frames.len() > 1)
        .collect();
    if keep.iter().any(|&k| !k) {
        let mut new_markers =
            MarkersData::with_capacity(keep.iter().filter(|&&k| k).count());
        for (i, &keep_i) in keep.iter().enumerate() {
            if keep_i {
                new_markers.push_marker_full(
                    markers.names[i].clone(),
                    markers.frame_data[i].clone(),
                    markers.set_names[i].clone(),
                    markers.ids[i].clone(),
                    markers.point_3d[i].clone(),
                );
            }
        }
        markers = new_markers;
    }

    let mut min_frame = u32::MAX;
    let mut max_frame = 0;
    for frame_data in &markers.frame_data {
        if let (Some(&first), Some(&last)) =
            (frame_data.frames.first(), frame_data.frames.last())
        {
            min_frame = min_frame.min(first);
            max_frame = max_frame.max(last);
        }
    }
    let frame_range = FrameRange::new(min_frame, max_frame);

    (markers, frame_range)
}

/// Run a full camera solve with the given solver type.
fn run_camera_solve(
    markers: &MarkersData,
    frame_range: FrameRange,
    focal_length_mm: f64,
    film_back_width_mm: f64,
    film_back_height_mm: f64,
    image_width: f64,
    image_height: f64,
    solver_type: BundleAdjustmentSolverType,
) {
    let focal_length = MillimeterUnit::new(focal_length_mm);
    let film_back = CameraFilmBack::from_millimeters(
        film_back_width_mm,
        film_back_height_mm,
    );
    let image_size = ImageSize::from_pixels(image_width, image_height);
    let intrinsics =
        CameraIntrinsics::from_centered_lens(focal_length, film_back);

    let config = CameraSolveConfig {
        origin_frame: 1,
        bundle_solver_type: solver_type,
        ..Default::default()
    };

    let mut poses = CameraPoses::new();
    let mut bundles = BundlePositions::new();
    let mut metrics = SolveQualityMetrics::default();

    let mut noop_logger = mmlogger::NoOpLogger;
    camera_solve(
        &mut noop_logger,
        frame_range,
        markers,
        &intrinsics,
        &film_back,
        &image_size,
        &config,
        None,
        None,
        &mut poses,
        &mut bundles,
        &mut metrics,
    )
    .unwrap();

    // Prevent the compiler from optimizing away the solve.
    black_box(&poses);
    black_box(&bundles);
}

/// Dataset configuration for benchmarking.
struct DatasetConfig {
    name: &'static str,
    file_name: &'static str,
    focal_length_mm: f64,
    film_back_width_mm: f64,
    film_back_height_mm: f64,
    image_width: f64,
    image_height: f64,
}

const DATASETS: &[DatasetConfig] = &[
    DatasetConfig {
        name: "stA",
        file_name: "stA_v1_format.uv",
        focal_length_mm: 41.6,
        film_back_width_mm: 36.0,
        film_back_height_mm: 24.0,
        image_width: 3600.0,
        image_height: 2400.0,
    },
    DatasetConfig {
        name: "cube_a",
        file_name: "test_cube_a_markers_v1_fmt.uv",
        focal_length_mm: 35.0,
        film_back_width_mm: 36.0,
        film_back_height_mm: 24.0,
        image_width: 3600.0,
        image_height: 2400.0,
    },
    DatasetConfig {
        name: "cube_b",
        file_name: "test_cube_b_markers_v1_fmt.uv",
        focal_length_mm: 35.0,
        film_back_width_mm: 36.0,
        film_back_height_mm: 24.0,
        image_width: 3600.0,
        image_height: 2400.0,
    },
];

const SOLVER_TYPES: &[(&str, BundleAdjustmentSolverType)] = &[
    (
        "sparse_lm",
        BundleAdjustmentSolverType::SparseLevenbergMarquardt,
    ),
    ("schur_lm", BundleAdjustmentSolverType::SchurComplementLM),
];

fn bench_camera_solve(c: &mut Criterion) {
    let mut group = c.benchmark_group("camera_solve");
    // Each camera solve takes seconds, so use fewer samples.
    group.sample_size(10);
    group.measurement_time(Duration::from_secs(30));

    for dataset in DATASETS {
        let (markers, frame_range) = load_marker_data(dataset.file_name);

        for &(solver_name, ref solver_type) in SOLVER_TYPES {
            let id = BenchmarkId::new(dataset.name, solver_name);
            let solver_type = solver_type.clone();
            group.bench_with_input(id, &(), |b, _| {
                b.iter(|| {
                    run_camera_solve(
                        &markers,
                        frame_range,
                        dataset.focal_length_mm,
                        dataset.film_back_width_mm,
                        dataset.film_back_height_mm,
                        dataset.image_width,
                        dataset.image_height,
                        solver_type.clone(),
                    );
                });
            });
        }
    }

    group.finish();
}

criterion_group!(benches, bench_camera_solve);
criterion_main!(benches);
