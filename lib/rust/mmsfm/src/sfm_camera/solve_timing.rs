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

//! Timing data structures and reporting for camera solving

use std::time::Duration;

/// Timing data for a single round in Phase 3.
#[allow(dead_code)]
#[derive(Debug, Clone)]
pub struct RoundTimingData {
    pub round_number: usize,
    pub total_cameras: usize,
    pub cameras_added: u32,
    pub camera_pnp_duration: Duration,
    pub ba_duration: Duration,
    pub marker_expansion_duration: Duration,
    pub round_duration: Duration,
}

/// Comprehensive timing data for the entire solve.
#[allow(dead_code)]
#[derive(Debug, Clone)]
pub struct TimingData {
    pub solve_total_duration: Duration,
    pub phase1_duration: Duration,
    pub frame_pair_duration: Duration,
    pub phase2_duration: Duration,
    pub relative_pose_duration: Duration,
    pub fixed_depth_phase2_duration: Duration,
    pub initial_ba_duration: Duration,
    pub phase3_duration: Duration,
    pub total_camera_pnp_duration: Duration,
    pub total_phase3_ba_duration: Duration,
    pub total_phase3_marker_expansion_duration: Duration,
    pub round_timings: Vec<RoundTimingData>,
    pub phase4_duration: Duration,
    pub phase4_pre_fixed_depth_duration: Duration,
    pub phase4_ba_duration: Duration,
    pub phase4_post_fixed_depth_duration: Duration,
    pub phase5_duration: Duration,
    pub origin_transform_duration: Duration,
}

/// Print comprehensive timing breakdown for the solve.
#[allow(dead_code)]
pub fn print_timing_breakdown(timing: &TimingData) {
    eprintln!("\n=== Timing Breakdown ===");
    eprintln!(
        "Total solve time: {:.3}s ({:.1}ms)",
        timing.solve_total_duration.as_secs_f64(),
        timing.solve_total_duration.as_secs_f64() * 1000.0
    );
    eprintln!("");
    eprintln!(
        "Phase 1 - Frame Analysis & Selection: {:.1}ms ({:.1}%)",
        timing.phase1_duration.as_secs_f64() * 1000.0,
        (timing.phase1_duration.as_secs_f64()
            / timing.solve_total_duration.as_secs_f64())
            * 100.0
    );
    eprintln!(
        "  Frame analysis: {:.1}ms",
        timing.phase1_duration.as_secs_f64() * 1000.0
    );
    eprintln!(
        "  Best frame pair selection: {:.1}ms",
        timing.frame_pair_duration.as_secs_f64() * 1000.0
    );
    eprintln!("");
    eprintln!(
        "Phase 2 - Initial Reconstruction: {:.1}ms ({:.1}%)",
        timing.phase2_duration.as_secs_f64() * 1000.0,
        (timing.phase2_duration.as_secs_f64()
            / timing.solve_total_duration.as_secs_f64())
            * 100.0
    );
    eprintln!(
        "  Relative pose computation: {:.1}ms",
        timing.relative_pose_duration.as_secs_f64() * 1000.0
    );
    eprintln!(
        "  Fixed depth triangulation: {:.1}ms",
        timing.fixed_depth_phase2_duration.as_secs_f64() * 1000.0
    );
    eprintln!(
        "  Initial bundle adjustment: {:.1}ms",
        timing.initial_ba_duration.as_secs_f64() * 1000.0
    );
    eprintln!("");
    eprintln!(
        "Phase 3 - Multi-Round Camera Addition: {:.1}ms ({:.1}%)",
        timing.phase3_duration.as_secs_f64() * 1000.0,
        (timing.phase3_duration.as_secs_f64()
            / timing.solve_total_duration.as_secs_f64())
            * 100.0
    );
    eprintln!(
        "  Total camera PnP time: {:.1}ms ({:.1}% of Phase 3)",
        timing.total_camera_pnp_duration.as_secs_f64() * 1000.0,
        (timing.total_camera_pnp_duration.as_secs_f64()
            / timing.phase3_duration.as_secs_f64())
            * 100.0
    );
    eprintln!(
        "  Total bundle adjustment time: {:.1}ms ({:.1}% of Phase 3)",
        timing.total_phase3_ba_duration.as_secs_f64() * 1000.0,
        (timing.total_phase3_ba_duration.as_secs_f64()
            / timing.phase3_duration.as_secs_f64())
            * 100.0
    );
    eprintln!(
        "  Total marker expansion: {:.1}ms",
        timing.total_phase3_marker_expansion_duration.as_secs_f64() * 1000.0
    );
    eprintln!("");

    // Print per-round timing breakdowns.
    eprintln!("  Phase 3 Per-Round Breakdown:");
    for round_timing in &timing.round_timings {
        let num_cameras = round_timing.total_cameras;
        let round_total_ms = round_timing.round_duration.as_secs_f64() * 1000.0;

        eprintln!("");
        eprintln!(
            "    Round {}: {} cameras ({} added)",
            round_timing.round_number, num_cameras, round_timing.cameras_added
        );

        let pnp_ms = round_timing.camera_pnp_duration.as_secs_f64() * 1000.0;
        let pnp_per_frame = pnp_ms / num_cameras as f64;
        let pnp_pct = (pnp_ms / round_total_ms) * 100.0;
        eprintln!(
            "      Camera PnP: {:.1}ms ({:.2}ms/frame, {:.1}%)",
            pnp_ms, pnp_per_frame, pnp_pct
        );

        let ba_ms = round_timing.ba_duration.as_secs_f64() * 1000.0;
        let ba_per_frame = ba_ms / num_cameras as f64;
        let ba_pct = (ba_ms / round_total_ms) * 100.0;
        eprintln!(
            "      Bundle adjustment: {:.1}ms ({:.2}ms/frame, {:.1}%)",
            ba_ms, ba_per_frame, ba_pct
        );

        let me_ms =
            round_timing.marker_expansion_duration.as_secs_f64() * 1000.0;
        let me_per_frame = me_ms / num_cameras as f64;
        let me_pct = (me_ms / round_total_ms) * 100.0;
        eprintln!(
            "      Marker expansion: {:.1}ms ({:.2}ms/frame, {:.1}%)",
            me_ms, me_per_frame, me_pct
        );

        let total_per_frame = round_total_ms / num_cameras as f64;
        eprintln!(
            "      Round total: {:.1}ms ({:.2}ms/frame)",
            round_total_ms, total_per_frame
        );
    }
    eprintln!("");
    eprintln!(
        "Phase 4 - Final General BA: {:.1}ms ({:.1}%)",
        timing.phase4_duration.as_secs_f64() * 1000.0,
        (timing.phase4_duration.as_secs_f64()
            / timing.solve_total_duration.as_secs_f64())
            * 100.0
    );
    eprintln!(
        "  Fixed depth pre-triangulation: {:.1}ms",
        timing.phase4_pre_fixed_depth_duration.as_secs_f64() * 1000.0
    );
    eprintln!(
        "  General bundle adjustment: {:.1}ms",
        timing.phase4_ba_duration.as_secs_f64() * 1000.0
    );
    eprintln!(
        "  Fixed depth post-triangulation: {:.1}ms",
        timing.phase4_post_fixed_depth_duration.as_secs_f64() * 1000.0
    );
    eprintln!("");
    eprintln!(
        "Phase 5 - Final Summary & Transform: {:.1}ms ({:.1}%)",
        timing.phase5_duration.as_secs_f64() * 1000.0,
        (timing.phase5_duration.as_secs_f64()
            / timing.solve_total_duration.as_secs_f64())
            * 100.0
    );
    eprintln!(
        "  Origin frame transformation: {:.1}ms",
        timing.origin_transform_duration.as_secs_f64() * 1000.0
    );
    eprintln!("========================");
}
