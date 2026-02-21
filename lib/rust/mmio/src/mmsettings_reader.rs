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

//! Reader for `.mmsettings` JSON-with-comments file format.

use crate::json_parser::parse_json_with_comments;

/// Adjustment solver type.
#[derive(Debug, Clone, PartialEq)]
pub enum AdjustmentSolverType {
    /// Differential Evolution with refinement.
    EvolutionRefine,
    /// Differential Evolution with uniform sampling.
    EvolutionUniform,
    /// Uniform grid search.
    UniformGrid,
}

/// Per-attribute settings for adjustment solvers.
#[derive(Debug, Clone)]
pub struct AdjustmentAttribute {
    /// Attribute name (e.g. "camera.focal_length_mm").
    pub name: String,
    /// Minimum value the solver can set.
    pub value_min: f64,
    /// Maximum value the solver can set.
    pub value_max: f64,
    /// Number of samples for uniform grid solver.
    pub sample_count: Option<u32>,
}

/// Adjustment solver settings.
#[derive(Debug, Clone)]
pub struct AdjustmentSolverSettings {
    /// Type of adjustment solver.
    pub solver_type: AdjustmentSolverType,
    /// Number of CPU threads (None = all).
    pub thread_count: Option<usize>,
    /// Enable automatic value range estimation for evolution solvers.
    pub evolution_value_range_estimate: bool,
    /// Number of generations for evolution solvers (None = default).
    pub evolution_generation_count: Option<usize>,
    /// Population count per generation (None = default).
    pub evolution_population_count: Option<usize>,
}

/// Top-level mmsettings data.
#[derive(Debug, Clone)]
pub struct MmSettingsData {
    /// File format version.
    pub version: u32,
    /// The frame used as origin.
    pub origin_frame: u32,
    /// Start frame to solve.
    pub start_frame: Option<u32>,
    /// End frame to solve.
    pub end_frame: Option<u32>,
    /// Adjustment solver settings.
    pub adjustment_solver: Option<AdjustmentSolverSettings>,
    /// Per-attribute adjustment settings.
    pub adjustment_attributes: Vec<AdjustmentAttribute>,
}

impl Default for MmSettingsData {
    fn default() -> Self {
        Self {
            version: 1,
            origin_frame: 0,
            start_frame: None,
            end_frame: None,
            adjustment_solver: None,
            adjustment_attributes: Vec::new(),
        }
    }
}

/// Parse an `.mmsettings` file from a file path.
pub fn parse_mmsettings_file(path: &str) -> Result<MmSettingsData, String> {
    let content = std::fs::read_to_string(path).map_err(|e| {
        format!("Failed to read mmsettings file '{}': {}", path, e)
    })?;
    parse_mmsettings_string(&content)
}

/// Parse an `.mmsettings` string.
pub fn parse_mmsettings_string(
    content: &str,
) -> Result<MmSettingsData, String> {
    let root = parse_json_with_comments(content)
        .map_err(|e| format!("Failed to parse mmsettings JSON: {}", e))?;

    let version =
        root.get("version").and_then(|v| v.as_i64()).unwrap_or(1) as u32;

    let data = match root.get("data") {
        Some(d) => d,
        None => return Err("Missing 'data' field in mmsettings".to_string()),
    };

    let origin_frame = data
        .get("origin_frame")
        .and_then(|v| v.as_i64())
        .unwrap_or(0) as u32;

    let (start_frame, end_frame) = if let Some(frames) = data.get("frames") {
        let sf = frames
            .get("start_frame")
            .and_then(|v| v.as_i64())
            .map(|v| v as u32);
        let ef = frames
            .get("end_frame")
            .and_then(|v| v.as_i64())
            .map(|v| v as u32);
        (sf, ef)
    } else {
        (None, None)
    };

    let adjustment_solver = if let Some(adj) = data.get("adjustment_solver") {
        let solver_type = match adj
            .get("type")
            .and_then(|v| v.as_str())
            .unwrap_or("evolution_refine")
        {
            "evolution_refine" => AdjustmentSolverType::EvolutionRefine,
            "evolution_uniform" => AdjustmentSolverType::EvolutionUniform,
            "uniform_grid" => AdjustmentSolverType::UniformGrid,
            other => {
                return Err(format!(
                    "Unknown adjustment solver type: '{}'",
                    other
                ))
            }
        };

        let thread_count = adj
            .get("thread_count")
            .and_then(|v| if v.is_null() { None } else { v.as_i64() })
            .map(|v| v as usize);

        let evolution_value_range_estimate = adj
            .get("evolution_value_range_estimate")
            .and_then(|v| v.as_bool())
            .unwrap_or(true);

        let evolution_generation_count = adj
            .get("evolution_generation_count")
            .and_then(|v| if v.is_null() { None } else { v.as_i64() })
            .map(|v| v as usize);

        let evolution_population_count = adj
            .get("evolution_population_count")
            .and_then(|v| if v.is_null() { None } else { v.as_i64() })
            .map(|v| v as usize);

        Some(AdjustmentSolverSettings {
            solver_type,
            thread_count,
            evolution_value_range_estimate,
            evolution_generation_count,
            evolution_population_count,
        })
    } else {
        None
    };

    let mut adjustment_attributes = Vec::new();
    if let Some(attrs) = data.get("adjustment_attributes") {
        if let Some(arr) = attrs.as_array() {
            for attr_val in arr {
                let name = attr_val
                    .get("name")
                    .and_then(|v| v.as_str())
                    .unwrap_or("")
                    .to_string();
                let value_min = attr_val
                    .get("value_min")
                    .and_then(|v| v.as_f64())
                    .unwrap_or(0.0);
                let value_max = attr_val
                    .get("value_max")
                    .and_then(|v| v.as_f64())
                    .unwrap_or(200.0);
                let sample_count = attr_val
                    .get("sample_count")
                    .and_then(|v| v.as_i64())
                    .map(|v| v as u32);

                adjustment_attributes.push(AdjustmentAttribute {
                    name,
                    value_min,
                    value_max,
                    sample_count,
                });
            }
        }
    }

    Ok(MmSettingsData {
        version,
        origin_frame,
        start_frame,
        end_frame,
        adjustment_solver,
        adjustment_attributes,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_mmsettings() {
        let input = r#"{
            // Version of the mmsettings file format structure.
            "version": 1,
            "data": {
                "origin_frame": 0,
                "frames": {
                    "start_frame": 1,
                    "end_frame": 10
                },
                "adjustment_solver": {
                    "type": "evolution_refine",
                    "thread_count": null,
                    "evolution_value_range_estimate": true,
                    "evolution_generation_count": null,
                    "evolution_population_count": null
                },
                "adjustment_attributes": [
                    {
                        "name": "camera.focal_length_mm",
                        "value_min": 0.1,
                        "value_max": 120.0,
                        "sample_count": 8
                    }
                ]
            }
        }"#;

        let settings = parse_mmsettings_string(input).unwrap();
        assert_eq!(settings.version, 1);
        assert_eq!(settings.origin_frame, 0);
        assert_eq!(settings.start_frame, Some(1));
        assert_eq!(settings.end_frame, Some(10));

        let adj = settings.adjustment_solver.unwrap();
        assert_eq!(adj.solver_type, AdjustmentSolverType::EvolutionRefine);
        assert_eq!(adj.thread_count, None);
        assert!(adj.evolution_value_range_estimate);

        assert_eq!(settings.adjustment_attributes.len(), 1);
        let attr = &settings.adjustment_attributes[0];
        assert_eq!(attr.name, "camera.focal_length_mm");
        assert_eq!(attr.value_min, 0.1);
        assert_eq!(attr.value_max, 120.0);
        assert_eq!(attr.sample_count, Some(8));
    }
}
