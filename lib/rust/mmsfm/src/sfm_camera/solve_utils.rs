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

//! Shared utility functions for the SfM camera solver.

use std::time::Instant;

use mmio::uvtrack_reader::FrameNumber;
use mmlogger::Logger;

/// Format a list of frame numbers as ranges
///
/// Examples:
/// - [1, 2, 3, 5, 7, 8, 9] -> "1-3, 5, 7-9"
/// - [1, 10, 20] -> "1, 10, 20"
pub(crate) fn format_frame_list(frames: &[FrameNumber]) -> String {
    if frames.is_empty() {
        return String::from("none");
    }

    let mut result = Vec::new();
    let mut range_start = frames[0];
    let mut range_end = frames[0];

    for &frame in &frames[1..] {
        if frame == range_end + 1 {
            // Continue the current range
            range_end = frame;
        } else {
            // End current range and start a new one
            if range_start == range_end {
                result.push(format!("{}", range_start));
            } else if range_end == range_start + 1 {
                result.push(format!("{}, {}", range_start, range_end));
            } else {
                result.push(format!("{}-{}", range_start, range_end));
            }
            range_start = frame;
            range_end = frame;
        }
    }

    // Add the last range
    if range_start == range_end {
        result.push(format!("{}", range_start));
    } else if range_end == range_start + 1 {
        result.push(format!("{}, {}", range_start, range_end));
    } else {
        result.push(format!("{}-{}", range_start, range_end));
    }

    result.join(", ")
}

/// Print a free-text progress line (no numeric columns).
pub(super) fn progress_text<L: Logger>(
    logger: &mut L,
    phase: u8,
    solve_start: Instant,
    text: &str,
) {
    let time_str = format!("{:.1}s", solve_start.elapsed().as_secs_f64());
    mm_info_log!(logger, "[Phase {}] {:>5} | {}", phase, time_str, text);
}

/// Print the numeric-column header and its separator row.
#[allow(dead_code)]
pub(super) fn progress_table_header<L: Logger>(
    logger: &mut L,
    phase: u8,
    solve_start: Instant,
) {
    let time_str = format!("{:.1}s", solve_start.elapsed().as_secs_f64());
    mm_info_log!(
        logger,
        "[Phase {}] {:>5} | {:>7} | {:>9} | {:>6} | {:>7} | {}",
        phase,
        time_str,
        "Mean px",
        "Median px",
        "Frames",
        "Bundles",
        "Stage"
    );
    mm_info_log!(
        logger,
        "[Phase {}] {:>5} | {:>7} | {:>9} | {:>6} | {:>7} | {}",
        phase,
        "-----",
        "-------",
        "---------",
        "------",
        "-------",
        "-----"
    );
}

/// Print one row of the progress table.
#[allow(dead_code)]
pub(super) fn progress_row<L: Logger>(
    logger: &mut L,
    phase: u8,
    solve_start: Instant,
    mean: f64,
    median: f64,
    frames: usize,
    bundles: usize,
    stage: &str,
) {
    let time_str = format!("{:.1}s", solve_start.elapsed().as_secs_f64());
    mm_info_log!(
        logger,
        "[Phase {}] {:>5} | {:>7.3} | {:>9.3} | {:>6} | {:>7} | {}",
        phase,
        time_str,
        mean,
        median,
        frames,
        bundles,
        stage
    );
}
