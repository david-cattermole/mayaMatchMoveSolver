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
//! Custom CLI argument parsing (no external dependencies).

use crate::parser;

use crate::defaults::DEFAULT_FILM_BACK_HEIGHT_MM;
use crate::defaults::DEFAULT_FILM_BACK_WIDTH_MM;
use crate::defaults::DEFAULT_FOCAL_LENGTH_MM;
use crate::defaults::DEFAULT_IMAGE_HEIGHT;
use crate::defaults::DEFAULT_IMAGE_WIDTH;
use crate::defaults::DEFAULT_LENS_CENTER_X_MM;
use crate::defaults::DEFAULT_LENS_CENTER_Y_MM;
use crate::defaults::DEFAULT_OUTPUT_DIR;

// Command-line argument constants
const ARG_UV_FILE: &str = "<UV_FILE>";
const ARG_MMCAMERA: &str = "--mmcamera";
const ARG_SOLVER_SETTINGS: &str = "--solver-settings";
const ARG_HELP_SHORT: &str = "-h";
const ARG_HELP_LONG: &str = "--help";
const ARG_VERSION_SHORT: &str = "-v";
const ARG_VERSION_LONG: &str = "--version";
const ARG_QUIET: &str = "--quiet";
const ARG_FOCAL_LENGTH: &str = "--focal-length";
const ARG_LENS_CENTER_X: &str = "--lens-center-x";
const ARG_LENS_CENTER_Y: &str = "--lens-center-y";
const ARG_IMAGE_WIDTH: &str = "--image-width";
const ARG_IMAGE_HEIGHT: &str = "--image-height";
const ARG_FILM_BACK_WIDTH: &str = "--film-back-width";
const ARG_FILM_BACK_HEIGHT: &str = "--film-back-height";
const ARG_START_FRAME: &str = "--start-frame";
const ARG_END_FRAME: &str = "--end-frame";
const ARG_SOLVER: &str = "--solver";
const ARG_THREADS: &str = "--threads";
const ARG_OUTPUT_DIR: &str = "--output-dir";
const ARG_PREFIX: &str = "--prefix";
const ARG_INTERMEDIATE_OUTPUT: &str = "--with-intermediate-output";
const ARG_NUKE_LENS: &str = "--nuke-lens";

/// Solver type for focal length adjustment
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum SolverType {
    /// Use provided focal length as-is (no adjustment)
    #[default]
    None,
    /// Small refinement around provided focal length (±10%)
    Refine,
    /// Large search range for unknown focal length (10-200mm)
    Unknown,
}

impl std::str::FromStr for SolverType {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "none" => Ok(SolverType::None),
            "refine" => Ok(SolverType::Refine),
            "unknown" => Ok(SolverType::Unknown),
            _ => Err(format!(
                "Invalid solver type '{}'. Valid options: none, refine, unknown",
                s
            )),
        }
    }
}

/// Parsed command-line arguments.
#[derive(Debug)]
pub struct CliArgs {
    /// Path to UV markers file (.uv).
    pub uv_file: String,

    /// Optional path to an `.mmcamera` file for camera defaults.
    pub mmcamera_file: Option<String>,

    /// Optional path to an `.mmsettings` file for solver settings.
    pub solver_settings_file: Option<String>,

    /// Focal length in millimeters.
    pub focal_length_mm: f64,

    /// Lens center X offset in millimeters.
    pub lens_center_x_mm: f64,

    /// Lens center Y offset in millimeters.
    pub lens_center_y_mm: f64,

    /// Image width in pixels.
    pub image_width: u32,

    /// Image height in pixels.
    pub image_height: u32,

    /// Film back width in millimeters.
    pub film_back_width_mm: f64,

    /// Film back height in millimeters.
    pub film_back_height_mm: f64,

    /// Start frame (None = use UV file default).
    pub start_frame: Option<u32>,

    /// End frame (None = use UV file default).
    pub end_frame: Option<u32>,

    /// Solver type for focal length adjustment.
    pub solver: SolverType,

    /// Thread count (None = auto).
    pub threads: Option<usize>,

    /// Output directory for visualizations.
    pub output_dir: String,

    /// Optional prefix for output filenames.
    pub prefix: Option<String>,

    /// Quiet mode - suppress progress output.
    pub quiet: bool,

    /// Write intermediate results during solve.
    pub intermediate_output: bool,

    /// Optional path to a Nuke .nk lens distortion file.
    pub nuke_lens_file: Option<String>,
}

impl Default for CliArgs {
    fn default() -> Self {
        Self {
            uv_file: String::new(),
            mmcamera_file: None,
            solver_settings_file: None,
            focal_length_mm: DEFAULT_FOCAL_LENGTH_MM,
            lens_center_x_mm: DEFAULT_LENS_CENTER_X_MM,
            lens_center_y_mm: DEFAULT_LENS_CENTER_Y_MM,
            image_width: DEFAULT_IMAGE_WIDTH,
            image_height: DEFAULT_IMAGE_HEIGHT,
            film_back_width_mm: DEFAULT_FILM_BACK_WIDTH_MM,
            film_back_height_mm: DEFAULT_FILM_BACK_HEIGHT_MM,
            start_frame: None,
            end_frame: None,
            solver: SolverType::default(),
            threads: None,
            output_dir: DEFAULT_OUTPUT_DIR.to_string(),
            prefix: None,
            quiet: false,
            intermediate_output: false,
            nuke_lens_file: None,
        }
    }
}

/// Print help message.
pub fn print_help() {
    println!(
        "mmSolver Camera Solver - Structure from Motion camera solver.

USAGE:
    mmsfm <UV_FILE> [OPTIONS]

ARGUMENTS:
    <UV_FILE>    Path to UV markers file (.uv)

INPUT:
    --nuke-lens <PATH>        Path to Nuke .nk lens distortion file
                              Lens distortion data for use by the solver.
    --mmcamera <PATH>         Path to .mmcamera file for camera defaults
                              Overrides default focal length, film back,
                              image size, and frame range values.
                              Explicit flags still take priority.
    --solver-settings <PATH>  Path to .mmsettings file for solver settings
                              Provides solver type, frame range, focal length
                              bounds, and other adjustment parameters.
                              Explicit flags still take priority.

CAMERA PARAMETERS:
    --focal-length <MM>       Focal length in millimeters [default: 35]
    --lens-center-x <MM>      Lens center X offset in mm [default: 0]
    --lens-center-y <MM>      Lens center Y offset in mm [default: 0]
    --image-width <PIXELS>    Image width in pixels [default: 1920]
    --image-height <PIXELS>   Image height in pixels [default: 1080]
    --film-back-width <MM>    Film back width in mm [default: 36]
    --film-back-height <MM>   Film back height in mm [default: 24]

FRAME RANGE:
    --start-frame <FRAME>     Start frame [default: from UV file]
    --end-frame <FRAME>       End frame [default: from UV file]

SOLVER SETTINGS:
    --solver <TYPE>           Solver type [default: none]
                              none    = use provided focal length
                              refine  = small adjustment (+/-10%)
                              unknown = large search (10-200mm)
    --threads <COUNT>         Thread count [default: auto]

OUTPUT:
    --output-dir <PATH>         Output directory for Kuper file [default: ./output]
    --prefix <NAME>             Custom prefix for output files
    --with-intermediate-output  Write intermediate results during solve
    --quiet                     Suppress progress output

HELP:
    -h, --help                Show this help message
    -v, --version             Show version"
    );
}

/// Print version information.
pub fn print_version() {
    println!("mmsfm {}", env!("CARGO_PKG_VERSION"));
}

macro_rules! try_parse {
    ($expr:expr) => {
        match $expr {
            Ok(val) => val,
            Err(e) => return e,
        }
    };
}

/// Result of argument parsing.
pub enum ParseResult {
    /// Successfully parsed arguments.
    Args(CliArgs),
    /// User requested help.
    Help,
    /// User requested version.
    Version,
    /// Parse error with message.
    Error(String),
}

/// Parse command-line arguments.
pub fn parse_args() -> ParseResult {
    let args: Vec<String> = std::env::args().collect();

    if args.len() < 2 {
        return ParseResult::Error(format!(
            "Missing required argument: {}",
            ARG_UV_FILE
        ));
    }

    let mut cli = CliArgs::default();
    let mut i = 1;

    // Track which fields were explicitly set on the command line,
    // so that mmcamera defaults don't override them.
    let mut explicit = ExplicitFlags::default();

    while i < args.len() {
        let arg = &args[i];

        match arg.as_str() {
            ARG_HELP_SHORT | ARG_HELP_LONG => return ParseResult::Help,
            ARG_VERSION_SHORT | ARG_VERSION_LONG => {
                return ParseResult::Version
            }
            ARG_QUIET => {
                cli.quiet = true;
                i += 1;
            }
            ARG_INTERMEDIATE_OUTPUT => {
                cli.intermediate_output = true;
                i += 1;
            }
            ARG_MMCAMERA => {
                cli.mmcamera_file = Some(try_parse!(parser::parse_string_arg(
                    &args,
                    &mut i,
                    ARG_MMCAMERA
                )));
            }
            ARG_SOLVER_SETTINGS => {
                cli.solver_settings_file =
                    Some(try_parse!(parser::parse_string_arg(
                        &args,
                        &mut i,
                        ARG_SOLVER_SETTINGS
                    )));
            }
            ARG_NUKE_LENS => {
                cli.nuke_lens_file = Some(try_parse!(
                    parser::parse_string_arg(&args, &mut i, ARG_NUKE_LENS)
                ));
            }
            ARG_FOCAL_LENGTH => {
                cli.focal_length_mm =
                    try_parse!(parser::parse_positive_f64_arg(
                        &args,
                        &mut i,
                        ARG_FOCAL_LENGTH,
                        "focal length"
                    ));
                explicit.focal_length = true;
            }
            ARG_LENS_CENTER_X => {
                cli.lens_center_x_mm = try_parse!(parser::parse_f64_arg(
                    &args,
                    &mut i,
                    ARG_LENS_CENTER_X,
                    "lens center X"
                ));
                explicit.lens_center_x = true;
            }
            ARG_LENS_CENTER_Y => {
                cli.lens_center_y_mm = try_parse!(parser::parse_f64_arg(
                    &args,
                    &mut i,
                    ARG_LENS_CENTER_Y,
                    "lens center Y"
                ));
                explicit.lens_center_y = true;
            }
            ARG_IMAGE_WIDTH => {
                cli.image_width = try_parse!(parser::parse_positive_u32_arg(
                    &args,
                    &mut i,
                    ARG_IMAGE_WIDTH,
                    "image width"
                ));
                explicit.image_width = true;
            }
            ARG_IMAGE_HEIGHT => {
                cli.image_height = try_parse!(parser::parse_positive_u32_arg(
                    &args,
                    &mut i,
                    ARG_IMAGE_HEIGHT,
                    "image height"
                ));
                explicit.image_height = true;
            }
            ARG_FILM_BACK_WIDTH => {
                cli.film_back_width_mm =
                    try_parse!(parser::parse_positive_f64_arg(
                        &args,
                        &mut i,
                        ARG_FILM_BACK_WIDTH,
                        "film back width"
                    ));
                explicit.film_back_width = true;
            }
            ARG_FILM_BACK_HEIGHT => {
                cli.film_back_height_mm =
                    try_parse!(parser::parse_positive_f64_arg(
                        &args,
                        &mut i,
                        ARG_FILM_BACK_HEIGHT,
                        "film back height"
                    ));
                explicit.film_back_height = true;
            }
            ARG_START_FRAME => {
                cli.start_frame = Some(try_parse!(parser::parse_u32_arg(
                    &args,
                    &mut i,
                    ARG_START_FRAME,
                    "start frame"
                )));
                explicit.start_frame = true;
            }
            ARG_END_FRAME => {
                cli.end_frame = Some(try_parse!(parser::parse_u32_arg(
                    &args,
                    &mut i,
                    ARG_END_FRAME,
                    "end frame"
                )));
                explicit.end_frame = true;
            }
            ARG_SOLVER => {
                cli.solver = try_parse!(parser::parse_solver_type_arg(
                    &args, &mut i, ARG_SOLVER
                ));
            }
            ARG_THREADS => {
                cli.threads =
                    Some(try_parse!(parser::parse_positive_usize_arg(
                        &args,
                        &mut i,
                        ARG_THREADS,
                        "thread count"
                    )));
            }
            ARG_OUTPUT_DIR => {
                cli.output_dir = try_parse!(parser::parse_string_arg(
                    &args,
                    &mut i,
                    ARG_OUTPUT_DIR
                ));
            }
            ARG_PREFIX => {
                cli.prefix = Some(try_parse!(parser::parse_string_arg(
                    &args, &mut i, ARG_PREFIX
                )));
            }
            _ if arg.starts_with('-') => {
                return ParseResult::Error(format!("Unknown option: {}", arg));
            }
            _ => {
                // Positional argument (UV file)
                if cli.uv_file.is_empty() {
                    cli.uv_file = arg.clone();
                } else {
                    return ParseResult::Error(format!(
                        "Unexpected argument: {}",
                        arg
                    ));
                }
                i += 1;
            }
        }
    }

    if cli.uv_file.is_empty() {
        return ParseResult::Error(format!(
            "Missing required argument: {}",
            ARG_UV_FILE
        ));
    }

    // Apply mmcamera defaults for fields not explicitly set.
    if let Some(mmcamera_path) = cli.mmcamera_file.clone() {
        match apply_mmcamera_defaults(&mut cli, &mmcamera_path, &explicit) {
            Ok(()) => {}
            Err(msg) => return ParseResult::Error(msg),
        }
    }

    ParseResult::Args(cli)
}

/// Tracks which CLI fields were explicitly provided by the user.
#[derive(Debug, Default)]
struct ExplicitFlags {
    focal_length: bool,
    lens_center_x: bool,
    lens_center_y: bool,
    image_width: bool,
    image_height: bool,
    film_back_width: bool,
    film_back_height: bool,
    start_frame: bool,
    end_frame: bool,
}

/// Read an `.mmcamera` file and apply its values as defaults for any
/// fields that were not explicitly set on the command line.
fn apply_mmcamera_defaults(
    cli: &mut CliArgs,
    mmcamera_path: &str,
    explicit: &ExplicitFlags,
) -> Result<(), String> {
    use mmio::mmcamera_reader::parse_mmcamera_file;
    use std::path::Path;

    let path = Path::new(mmcamera_path);
    let (_version, data) = parse_mmcamera_file(path)
        .map_err(|e| format!("Failed to read mmcamera file: {}", e))?;

    // Use the first frame's value for per-frame attributes.
    if !explicit.focal_length {
        if let Some(&(_frame, val)) = data.attr.focal_length.first() {
            cli.focal_length_mm = val;
        }
    }

    if !explicit.film_back_width {
        if let Some(&(_frame, val)) = data.attr.film_back_width.first() {
            cli.film_back_width_mm = val;
        }
    }

    if !explicit.film_back_height {
        if let Some(&(_frame, val)) = data.attr.film_back_height.first() {
            cli.film_back_height_mm = val;
        }
    }

    if !explicit.lens_center_x {
        if let Some(&(_frame, val)) = data.attr.film_back_offset_x.first() {
            cli.lens_center_x_mm = val;
        }
    }

    if !explicit.lens_center_y {
        if let Some(&(_frame, val)) = data.attr.film_back_offset_y.first() {
            cli.lens_center_y_mm = val;
        }
    }

    if !explicit.image_width {
        if let Some(w) = data.image.width {
            cli.image_width = w as u32;
        }
    }

    if !explicit.image_height {
        if let Some(h) = data.image.height {
            cli.image_height = h as u32;
        }
    }

    if !explicit.start_frame {
        cli.start_frame = Some(data.start_frame as u32);
    }

    if !explicit.end_frame {
        cli.end_frame = Some(data.end_frame as u32);
    }

    Ok(())
}
