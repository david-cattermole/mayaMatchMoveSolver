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

use mmio::uvtrack_reader::{FrameData, FrameRange, MarkersData};

// Pre-computed deterministic noise table with 100 values in range [-1.0, 1.0].
const NOISE_TABLE: [f64; 100] = [
    0.309016994374947,
    0.587785252292473,
    0.809016994374947,
    0.951056516295154,
    0.999999999999999,
    0.951056516295154,
    0.809016994374947,
    0.587785252292473,
    0.309016994374947,
    -0.000000000000001,
    -0.309016994374948,
    -0.587785252292474,
    -0.809016994374948,
    -0.951056516295154,
    -1.000000000000000,
    -0.951056516295154,
    -0.809016994374947,
    -0.587785252292473,
    -0.309016994374947,
    0.000000000000002,
    0.587785252292473,
    0.951056516295154,
    0.951056516295154,
    0.587785252292473,
    -0.000000000000001,
    -0.587785252292474,
    -0.951056516295154,
    -0.951056516295154,
    -0.587785252292473,
    0.000000000000002,
    0.809016994374947,
    0.309016994374947,
    -0.587785252292473,
    -0.999999999999999,
    -0.587785252292473,
    0.309016994374948,
    0.809016994374948,
    0.309016994374947,
    -0.587785252292474,
    -1.000000000000000,
    -0.587785252292473,
    0.309016994374947,
    0.809016994374947,
    0.309016994374947,
    -0.587785252292473,
    -0.999999999999999,
    -0.587785252292473,
    0.309016994374948,
    0.809016994374948,
    0.309016994374947,
    0.951056516295154,
    -0.000000000000001,
    -0.951056516295154,
    -0.587785252292474,
    0.587785252292473,
    0.951056516295154,
    -0.000000000000001,
    -0.951056516295154,
    -0.587785252292473,
    0.587785252292473,
    0.951056516295154,
    -0.000000000000001,
    -0.951056516295154,
    -0.587785252292474,
    0.587785252292473,
    0.951056516295154,
    -0.000000000000001,
    -0.951056516295154,
    -0.587785252292473,
    0.587785252292473,
    0.999999999999999,
    -0.587785252292473,
    -0.587785252292473,
    0.999999999999999,
    -0.587785252292473,
    -0.587785252292474,
    1.000000000000000,
    -0.587785252292473,
    -0.587785252292473,
    0.999999999999999,
    0.309016994374947,
    -0.951056516295154,
    0.809016994374947,
    0.309016994374947,
    -0.951056516295154,
    0.809016994374948,
    0.309016994374947,
    -0.951056516295154,
    0.809016994374947,
    0.309016994374947,
    -0.951056516295154,
    0.809016994374948,
    0.309016994374947,
    -0.951056516295154,
    0.809016994374947,
    0.309016994374947,
    -0.951056516295154,
    0.809016994374948,
    0.309016994374947,
    -0.951056516295154,
];

/// Adds deterministic noise to marker UV coordinates, varying per marker and per frame.
pub fn add_noise_to_markers(markers: &mut MarkersData, noise_scale: f64) {
    for (marker_id, frame_data) in markers.frame_data.iter_mut().enumerate() {
        for (idx, &frame_number) in frame_data.frames.iter().enumerate() {
            let u_noise_index =
                (marker_id + frame_number as usize) % NOISE_TABLE.len();
            let v_noise_index =
                (marker_id * 2 + frame_number as usize) % NOISE_TABLE.len();

            frame_data.u_coords[idx] +=
                NOISE_TABLE[u_noise_index] * noise_scale;
            frame_data.v_coords[idx] +=
                NOISE_TABLE[v_noise_index] * noise_scale;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_noise_table_range() {
        // All noise values must be in the valid range.
        for &value in NOISE_TABLE.iter() {
            assert!(
                value >= -1.0 && value <= 1.0,
                "Noise value {} out of range",
                value
            );
        }
    }

    #[test]
    fn test_noise_table_has_variation() {
        // The table must have both positive and negative values.
        let has_positive = NOISE_TABLE.iter().any(|&v| v > 0.5);
        let has_negative = NOISE_TABLE.iter().any(|&v| v < -0.5);
        assert!(has_positive, "Noise table should have positive values");
        assert!(has_negative, "Noise table should have negative values");
    }

    #[test]
    fn test_add_noise_to_markers() {
        // Create test marker data.
        let mut markers = MarkersData {
            names: vec!["marker1".to_string(), "marker2".to_string()],
            frame_data: vec![
                FrameData {
                    frame_range: FrameRange {
                        start_frame: 1,
                        end_frame: 3,
                    },
                    frames: vec![1, 2, 3],
                    u_coords: vec![0.5, 0.5, 0.5],
                    v_coords: vec![0.5, 0.5, 0.5],
                    weights: vec![1.0, 1.0, 1.0],
                    u_coords_dist: Vec::new(),
                    v_coords_dist: Vec::new(),
                },
                FrameData {
                    frame_range: FrameRange {
                        start_frame: 1,
                        end_frame: 3,
                    },
                    frames: vec![1, 2, 3],
                    u_coords: vec![0.3, 0.3, 0.3],
                    v_coords: vec![0.7, 0.7, 0.7],
                    weights: vec![1.0, 1.0, 1.0],
                    u_coords_dist: Vec::new(),
                    v_coords_dist: Vec::new(),
                },
            ],
            frame_range: FrameRange {
                start_frame: 1,
                end_frame: 3,
            },
            set_names: Vec::new(),
            ids: Vec::new(),
            point_3d: Vec::new(),
        };

        // Store original values before adding noise.
        let original_u_0_0 = markers.frame_data[0].u_coords[0];
        let original_v_0_0 = markers.frame_data[0].v_coords[0];

        // Add noise to the markers.
        add_noise_to_markers(&mut markers, 0.01);

        // Values must have changed.
        assert_ne!(
            markers.frame_data[0].u_coords[0], original_u_0_0,
            "U coordinate should change"
        );
        assert_ne!(
            markers.frame_data[0].v_coords[0], original_v_0_0,
            "V coordinate should change"
        );

        // Noise must be scaled correctly.
        let u_delta =
            (markers.frame_data[0].u_coords[0] - original_u_0_0).abs();
        let v_delta =
            (markers.frame_data[0].v_coords[0] - original_v_0_0).abs();
        assert!(u_delta <= 0.01, "U noise should be scaled by noise_scale");
        assert!(v_delta <= 0.01, "V noise should be scaled by noise_scale");
    }

    #[test]
    fn test_noise_is_deterministic() {
        // Create test marker data.
        let mut markers1 = MarkersData {
            names: vec!["marker1".to_string()],
            frame_data: vec![FrameData {
                frame_range: FrameRange {
                    start_frame: 1,
                    end_frame: 3,
                },
                frames: vec![1, 2, 3],
                u_coords: vec![0.5, 0.5, 0.5],
                v_coords: vec![0.5, 0.5, 0.5],
                weights: vec![1.0, 1.0, 1.0],
                u_coords_dist: Vec::new(),
                v_coords_dist: Vec::new(),
            }],
            frame_range: FrameRange {
                start_frame: 1,
                end_frame: 3,
            },
            set_names: Vec::new(),
            ids: Vec::new(),
            point_3d: Vec::new(),
        };

        let mut markers2 = markers1.clone();

        // Add the same noise to both.
        add_noise_to_markers(&mut markers1, 0.005);
        add_noise_to_markers(&mut markers2, 0.005);

        // Both must match exactly.
        for (fd1, fd2) in
            markers1.frame_data.iter().zip(markers2.frame_data.iter())
        {
            assert_eq!(fd1.u_coords, fd2.u_coords, "U coords should match");
            assert_eq!(fd1.v_coords, fd2.v_coords, "V coords should match");
        }
    }

    #[test]
    fn test_noise_varies_per_marker() {
        // Two markers at the same frame.
        let mut markers = MarkersData {
            names: vec!["marker1".to_string(), "marker2".to_string()],
            frame_data: vec![
                FrameData {
                    frame_range: FrameRange {
                        start_frame: 1,
                        end_frame: 1,
                    },
                    frames: vec![1],
                    u_coords: vec![0.5],
                    v_coords: vec![0.5],
                    weights: vec![1.0],
                    u_coords_dist: Vec::new(),
                    v_coords_dist: Vec::new(),
                },
                FrameData {
                    frame_range: FrameRange {
                        start_frame: 1,
                        end_frame: 1,
                    },
                    frames: vec![1],
                    u_coords: vec![0.5],
                    v_coords: vec![0.5],
                    weights: vec![1.0],
                    u_coords_dist: Vec::new(),
                    v_coords_dist: Vec::new(),
                },
            ],
            frame_range: FrameRange {
                start_frame: 1,
                end_frame: 1,
            },
            set_names: Vec::new(),
            ids: Vec::new(),
            point_3d: Vec::new(),
        };

        add_noise_to_markers(&mut markers, 0.01);

        // Different markers must get different noise.
        assert_ne!(
            markers.frame_data[0].u_coords[0],
            markers.frame_data[1].u_coords[0],
            "Different markers should have different u noise"
        );
    }

    #[test]
    fn test_noise_varies_per_frame() {
        // One marker across multiple frames.
        let mut markers = MarkersData {
            names: vec!["marker1".to_string()],
            frame_data: vec![FrameData {
                frame_range: FrameRange {
                    start_frame: 1,
                    end_frame: 3,
                },
                frames: vec![1, 2, 3],
                u_coords: vec![0.5, 0.5, 0.5],
                v_coords: vec![0.5, 0.5, 0.5],
                weights: vec![1.0, 1.0, 1.0],
                u_coords_dist: Vec::new(),
                v_coords_dist: Vec::new(),
            }],
            frame_range: FrameRange {
                start_frame: 1,
                end_frame: 3,
            },
            set_names: Vec::new(),
            ids: Vec::new(),
            point_3d: Vec::new(),
        };

        add_noise_to_markers(&mut markers, 0.01);

        // Different frames must get different noise.
        assert_ne!(
            markers.frame_data[0].u_coords[0],
            markers.frame_data[0].u_coords[1],
            "Different frames should have different u noise"
        );
        assert_ne!(
            markers.frame_data[0].u_coords[1],
            markers.frame_data[0].u_coords[2],
            "Different frames should have different u noise"
        );
    }
}
