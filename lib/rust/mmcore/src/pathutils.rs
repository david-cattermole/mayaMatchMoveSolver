/*
 * Copyright (C) 2020, 2021, 2024 David Cattermole.
 *
 * This file is part of mmSolver.
 *
 * mmSolver is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * mmSolver is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
 * ====================================================================
 *
 */

use log::{debug, warn};
use shellexpand;

struct FramePaddingIndexRange {
    start_index: usize,
    end_index: usize,
    padding_count: usize,
}

fn find_frame_padding_index_range(value: &String) -> FramePaddingIndexRange {
    debug!("find_frame_padding_index: {}", value);
    let mut start_index = 0;
    let mut end_index = 0;
    let mut last_char_valid = false;
    for (i, byte) in value.bytes().enumerate() {
        if byte == b'#' {
            if last_char_valid == false {
                // This is the first time we see a '#' character.
                start_index = i;
                end_index = i + 1;
            } else {
                // This might be the last time we see a '#' character.
                end_index = i + 1;
            }
            last_char_valid = true;
        } else {
            if last_char_valid == true {
                // The previous character was the last time we saw
                // '#'.
                break;
            }
        }
    }
    let padding_count = end_index - start_index;
    FramePaddingIndexRange {
        start_index,
        end_index,
        padding_count,
    }
}

fn create_expanded_string(
    value: &String,
    index_range: FramePaddingIndexRange,
    frame: i32,
) -> String {
    let mut expanded_string = value.clone();
    debug!(
        "index: start={} end={} pad={}",
        index_range.start_index,
        index_range.end_index,
        index_range.padding_count
    );

    // FIXME: Create a way to use the padding_count to dynamically
    // change the number formatted into the string. "format!" is a
    // compile time creation. This is a pretty bad hack.
    let frame_string = match index_range.padding_count {
        0 => "".to_string(),
        1 => format!("{:01}", frame),
        2 => format!("{:02}", frame),
        3 => format!("{:03}", frame),
        4 => format!("{:04}", frame),
        5 => format!("{:05}", frame),
        6 => format!("{:06}", frame),
        7 => format!("{:07}", frame),
        8 => format!("{:08}", frame),
        9 => format!("{:09}", frame),
        _ => "".to_string(),
    };
    expanded_string.replace_range(
        index_range.start_index..index_range.end_index,
        &frame_string,
    );
    expanded_string
}

fn expand_file_path(value: &str) -> String {
    let expanded_path = match shellexpand::full(value) {
        Ok(v) => (*v).to_string(),
        Err(e) => {
            warn!(
                "Environment variable unknown: name={} cause={}",
                e.var_name, e.cause
            );
            value.to_string()
        }
    };
    expanded_path.to_string()
}

pub fn expand_file_path_string(value: &str, frame: i32) -> String {
    debug!("expand_string: {} frame={}", value, frame);
    let expanded_path = expand_file_path(&value);
    let index_range = find_frame_padding_index_range(&expanded_path);
    if index_range.padding_count > 0 {
        create_expanded_string(&expanded_path, index_range, frame)
    } else {
        // No expansion needed.
        expanded_path
    }
}
