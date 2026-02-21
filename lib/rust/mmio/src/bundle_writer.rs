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

//! ASCII file format writer for 3D bundle point data.
//!
//! Each bundle is a named 3D point in Maya world-space coordinates
//! (right-handed, +Y up, camera looks down -Z).
//!
//! ## File Format
//!
//! The bundle ASCII format is:
//! - Line 1: integer count of bundles
//! - For each bundle, two lines:
//!   - Name line: the marker / bundle name (one name per line)
//!   - Position line: three space-separated f64 values `x y z`
//!
//! Example:
//! ```text
//! 3
//! TopLeft
//! 10.123456 20.654321 -5.111111
//! TopRight
//! 30.000000 20.654321 -5.111111
//! Center
//! 20.061728 15.327160 -5.111111
//! ```
//!
//! Names may contain spaces and any non-newline characters.  An empty
//! name is valid and written as an empty line.

use anyhow::{Context, Result};
use nalgebra::Point3;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::path::Path;

/// A single named 3D bundle point.
#[derive(Debug, Clone)]
pub struct BundlePoint {
    /// Marker / bundle name.
    pub name: String,
    /// 3D position in Maya world coordinates.
    pub position: Point3<f64>,
}

/// Write bundle points to an ASCII file.
///
/// # Arguments
/// * `path`   – output file path
/// * `bundles` – slice of BundlePoint, written in order
pub fn write_bundle_file<P: AsRef<Path>>(
    path: P,
    bundles: &[BundlePoint],
) -> Result<()> {
    let path = path.as_ref();
    let file = File::create(path).with_context(|| {
        format!("Failed to create bundle file: {}", path.display())
    })?;
    let mut w = BufWriter::new(file);

    // Header: number of bundles.
    writeln!(w, "{}", bundles.len())
        .with_context(|| "Failed to write bundle count")?;

    for bundle in bundles {
        writeln!(w, "{}", bundle.name).with_context(|| {
            format!("Failed to write bundle name: {:?}", bundle.name)
        })?;

        writeln!(
            w,
            "{:.6} {:.6} {:.6}",
            bundle.position.x, bundle.position.y, bundle.position.z
        )
        .with_context(|| {
            format!("Failed to write position for bundle: {:?}", bundle.name)
        })?;
    }

    w.flush().with_context(|| "Failed to flush bundle file")?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;
    use nalgebra::Point3;

    /// Round-trip helper: write then read back raw text.
    ///
    /// Each test passes a unique `tag` to avoid parallel-test races.
    fn write_and_read(tag: &str, bundles: &[BundlePoint]) -> Result<String> {
        let temp_dir = std::env::temp_dir();
        let temp_file = temp_dir.join(format!("test_bundle_{}.mmbundles", tag));
        write_bundle_file(&temp_file, bundles)?;
        let content = std::fs::read_to_string(&temp_file)?;
        let _ = std::fs::remove_file(&temp_file);
        Ok(content)
    }

    /// Parse the text produced by write_bundle_file back into a Vec<BundlePoint>.
    fn parse_bundle_text(text: &str) -> Vec<BundlePoint> {
        let mut lines = text.lines();
        let count: usize = lines.next().unwrap().trim().parse().unwrap();
        let mut out = Vec::with_capacity(count);
        for _ in 0..count {
            let name = lines.next().unwrap().to_string();
            let pos_line = lines.next().unwrap();
            let parts: Vec<f64> = pos_line
                .split_whitespace()
                .map(|s| s.parse().unwrap())
                .collect();
            out.push(BundlePoint {
                name,
                position: Point3::new(parts[0], parts[1], parts[2]),
            });
        }
        out
    }

    #[test]
    fn test_write_empty() {
        let content = write_and_read("empty", &[]).unwrap();
        let lines: Vec<&str> = content.lines().collect();
        assert_eq!(lines.len(), 1);
        assert_eq!(lines[0], "0");
    }

    #[test]
    fn test_write_single_bundle() {
        let bundles = vec![BundlePoint {
            name: "MyMarker".to_string(),
            position: Point3::new(1.0, 2.0, -3.0),
        }];

        let content = write_and_read("single", &bundles).unwrap();
        let lines: Vec<&str> = content.lines().collect();

        assert_eq!(lines[0], "1");
        assert_eq!(lines[1], "MyMarker");
        assert!(lines[2].starts_with("1.000000 2.000000 -3.000000"));
    }

    #[test]
    fn test_write_multiple_bundles() {
        let bundles = vec![
            BundlePoint {
                name: "A".to_string(),
                position: Point3::new(10.0, 20.0, -30.0),
            },
            BundlePoint {
                name: "B".to_string(),
                position: Point3::new(-5.5, 0.0, 100.25),
            },
            BundlePoint {
                name: "C".to_string(),
                position: Point3::new(0.0, 0.0, 0.0),
            },
        ];

        let content = write_and_read("multiple", &bundles).unwrap();
        let parsed = parse_bundle_text(&content);

        assert_eq!(parsed.len(), 3);

        assert_eq!(parsed[0].name, "A");
        assert_relative_eq!(parsed[0].position.x, 10.0, epsilon = 1e-5);
        assert_relative_eq!(parsed[0].position.y, 20.0, epsilon = 1e-5);
        assert_relative_eq!(parsed[0].position.z, -30.0, epsilon = 1e-5);

        assert_eq!(parsed[1].name, "B");
        assert_relative_eq!(parsed[1].position.x, -5.5, epsilon = 1e-5);
        assert_relative_eq!(parsed[1].position.y, 0.0, epsilon = 1e-5);
        assert_relative_eq!(parsed[1].position.z, 100.25, epsilon = 1e-5);

        assert_eq!(parsed[2].name, "C");
        assert_relative_eq!(parsed[2].position.x, 0.0, epsilon = 1e-5);
        assert_relative_eq!(parsed[2].position.y, 0.0, epsilon = 1e-5);
        assert_relative_eq!(parsed[2].position.z, 0.0, epsilon = 1e-5);
    }

    #[test]
    fn test_roundtrip_preserves_precision() {
        let bundles = vec![BundlePoint {
            name: "Precise".to_string(),
            position: Point3::new(123.456789012345, -98.765432109876, 0.000001),
        }];

        let content = write_and_read("precision", &bundles).unwrap();
        let parsed = parse_bundle_text(&content);

        // 6 decimal places of precision expected from {:.6}.
        assert_relative_eq!(parsed[0].position.x, 123.456789, epsilon = 1e-6);
        assert_relative_eq!(parsed[0].position.y, -98.765432, epsilon = 1e-6);
        assert_relative_eq!(parsed[0].position.z, 0.000001, epsilon = 1e-6);
    }

    #[test]
    fn test_name_with_spaces() {
        let bundles = vec![BundlePoint {
            name: "Top Left Corner".to_string(),
            position: Point3::new(0.0, 1.0, -1.0),
        }];

        let content = write_and_read("spaces", &bundles).unwrap();
        let parsed = parse_bundle_text(&content);

        assert_eq!(parsed[0].name, "Top Left Corner");
    }

    #[test]
    fn test_empty_name() {
        let bundles = vec![BundlePoint {
            name: String::new(),
            position: Point3::new(5.0, 6.0, 7.0),
        }];

        let content = write_and_read("emptyname", &bundles).unwrap();
        let parsed = parse_bundle_text(&content);

        assert_eq!(parsed[0].name, "");
        assert_relative_eq!(parsed[0].position.x, 5.0, epsilon = 1e-5);
    }
}
