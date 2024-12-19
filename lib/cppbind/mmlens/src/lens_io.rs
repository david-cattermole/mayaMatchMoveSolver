//
// Copyright (C) 2023 David Cattermole.
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

use crate::constants::MAX_LENS_PARAMETER_COUNT;
use crate::constants::NUKE_3DE4_ANAMORPHIC_STD_DEG4;
use crate::constants::NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED;
use crate::constants::NUKE_3DE4_ANAMORPHIC_STD_DEG6;
use crate::constants::NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED;
use crate::constants::NUKE_3DE4_CLASSIC;
use crate::constants::NUKE_3DE4_RADIAL_STD_DEG4;
use crate::constants::STATIC_FRAME_NUMBER;
use crate::cxxbridge::ffi::CameraParameters as BindCameraParameters;
use crate::cxxbridge::ffi::LensModelType as BindLensModelType;
use crate::data::FrameNumber;
use crate::data::LayerSize;
use crate::distortion_layers::ShimDistortionLayers;
use smallvec::SmallVec;

use anyhow::Result;
use std::collections::HashMap;

fn lookup_lens_model_type(value: &str) -> BindLensModelType {
    match value {
        NUKE_3DE4_CLASSIC => BindLensModelType::TdeClassic,
        NUKE_3DE4_RADIAL_STD_DEG4 => BindLensModelType::TdeRadialStdDeg4,
        NUKE_3DE4_ANAMORPHIC_STD_DEG4 => {
            BindLensModelType::TdeAnamorphicStdDeg4
        }
        NUKE_3DE4_ANAMORPHIC_STD_DEG4_RESCALED => {
            BindLensModelType::TdeAnamorphicStdDeg4Rescaled
        }
        NUKE_3DE4_ANAMORPHIC_STD_DEG6 => {
            BindLensModelType::TdeAnamorphicStdDeg6
        }
        NUKE_3DE4_ANAMORPHIC_STD_DEG6_RESCALED => {
            BindLensModelType::TdeAnamorphicStdDeg6Rescaled
        }
        _ => BindLensModelType::Uninitialized,
    }
}

// The possible "trivially copyable" values used that can be parsed
// from a string.
#[derive(Copy, Clone, Debug, PartialEq, PartialOrd)]
#[repr(u8)]
enum TrivialValue {
    None,
    F64(f64),
    I32(i32),
}

fn parse_str_to_trivial_value(str_value: &str) -> TrivialValue {
    if let Ok(f64_value) = str_value.parse::<f64>() {
        TrivialValue::F64(f64_value)
    } else if let Ok(i32_value) = str_value.parse::<i32>() {
        TrivialValue::I32(i32_value)
    } else {
        TrivialValue::None
    }
}

type F64CurveData = HashMap<FrameNumber, f64>;
type I32CurveData = HashMap<FrameNumber, i32>;

#[derive(Clone, Debug)]
#[repr(u8)]
enum KnobValue {
    None,
    F64(f64),
    #[allow(dead_code)]
    I32(i32),
    F64Curve(F64CurveData),
    I32Curve(I32CurveData),
}

#[derive(Clone, Debug)]
struct Node {
    pub lens_model_type: BindLensModelType,
    pub node_name: String,
    pub node_type: String,
    pub knobs: HashMap<String, KnobValue>,
    pub min_frame: FrameNumber,
    pub max_frame: FrameNumber,
}

impl Node {
    fn new() -> Node {
        Node {
            lens_model_type: BindLensModelType::Uninitialized,
            node_name: "".to_string(),
            node_type: "".to_string(),
            knobs: HashMap::new(),
            min_frame: FrameNumber::MAX,
            max_frame: FrameNumber::MIN,
        }
    }
}

/// Frame numbers in the Nuke curve format starts with an x, such as
/// x1, x2, x3, etc.
const FRAME_NUMBER_TOKEN_PREFIX: char = 'x';

/// Use this Knob name as the node's name.
const KNOB_NAME_NODE_NAME_VALUE: &str = "name";

/// How to tell a knob's value is an animated curve?
const KNOB_START_CURVE_TOKEN: &str = "{{curve";
/// The token at the end of a knob value curve.
const KNOB_END_CURVE_TOKEN: &str = "}}";

const BRACE_START_TOKEN: char = '{';
const BRACE_END_TOKEN: char = '}';

#[derive(Copy, Clone, Debug)]
struct ParserState {
    pub scope_level: u8,
    pub expect_brace_start: bool,
    pub expect_brace_end: bool,
}

impl ParserState {
    fn new() -> ParserState {
        ParserState {
            scope_level: 0,
            expect_brace_start: true,
            expect_brace_end: false,
        }
    }
}

/// Parse the outer scope of a Nuke script file format.
///
/// The "outer" scope of the file format looks like this:
/// Node_Type {
///    "... knob definitions..."
/// }
///
/// The parser currently assumes that nodes cannot be defined inside
/// of other nodes - which is an accurate assumption, so far.
fn parse_node_definitions(
    line: &str,
    state: &mut ParserState,
    current_node: &mut Node,
) {
    // Looking for node type definitions.
    for word in line.split_whitespace() {
        let lens_model_type = lookup_lens_model_type(word);
        if lens_model_type != BindLensModelType::Uninitialized {
            // Got the node type! Save it.
            current_node.node_type = word.to_string();
            current_node.lens_model_type = lens_model_type;
            continue;
        }
        if state.expect_brace_start == true {
            if word.starts_with(BRACE_START_TOKEN) {
                state.scope_level += 1;
                state.expect_brace_end = true;
                state.expect_brace_start = false;
            }
        }
    }
}

/// Parse a Knob value curve.
///
/// The `words_iter` is expected to return &str values from an input
/// file line like this:
///
///    my_float {{curve x1 0.3 x2 0.4 x3 0.5 }}
///
/// Where "x1", "x2" and "x3" represent the frame numbers 1, 2 and 3.
/// And "0.3", "0.4" and "0.5" represents the values at frames 1, 2
/// and 3.
///
/// But this function has already reached the 'x1' word in the
/// 'word_iter' iterator when this function states, and returns the
/// values after that point; "x1", "0.3", "x2", "0.4", etc.
///
fn parse_knob_value_curve<
    'a,
    WordsIterator: Iterator<Item = (Index, &'a str)>,
    Index,
>(
    words_iter: &mut WordsIterator,
    _state: &mut ParserState,
    current_knob_name: &str,
    current_node: &mut Node,
) {
    // Parse the curve data, until we find the end
    // of the curve (or run off the end of the
    // current line).
    let mut current_knob_curve = KnobValue::None;
    while let Some((_, curve_word)) = words_iter.next() {
        if curve_word == KNOB_END_CURVE_TOKEN {
            break;
        }
        if let Some(frame_string) =
            curve_word.strip_prefix(FRAME_NUMBER_TOKEN_PREFIX)
        {
            if let Ok(frame_number) = frame_string.parse::<u16>() {
                let knob_value_word = words_iter.next();
                if let Some((_, value_string)) = knob_value_word {
                    let knob_value = parse_str_to_trivial_value(value_string);
                    match knob_value {
                        TrivialValue::I32(i32_value) => {
                            match current_knob_curve {
                                KnobValue::None => {
                                    current_node.min_frame = std::cmp::min(
                                        current_node.min_frame,
                                        frame_number,
                                    );
                                    current_node.max_frame = std::cmp::max(
                                        current_node.max_frame,
                                        frame_number,
                                    );

                                    let mut curve_data = I32CurveData::new();
                                    curve_data.insert(frame_number, i32_value);
                                    current_knob_curve =
                                        KnobValue::I32Curve(curve_data);
                                }
                                KnobValue::I32Curve(ref mut curve_data) => {
                                    current_node.min_frame = std::cmp::min(
                                        current_node.min_frame,
                                        frame_number,
                                    );
                                    current_node.max_frame = std::cmp::max(
                                        current_node.max_frame,
                                        frame_number,
                                    );

                                    curve_data.insert(frame_number, i32_value);
                                }
                                _ => (),
                            }
                        }
                        TrivialValue::F64(f64_value) => {
                            match current_knob_curve {
                                KnobValue::None => {
                                    current_node.min_frame = std::cmp::min(
                                        current_node.min_frame,
                                        frame_number,
                                    );
                                    current_node.max_frame = std::cmp::max(
                                        current_node.max_frame,
                                        frame_number,
                                    );

                                    let mut curve_data = F64CurveData::new();
                                    curve_data.insert(frame_number, f64_value);
                                    current_knob_curve =
                                        KnobValue::F64Curve(curve_data);
                                }
                                KnobValue::F64Curve(ref mut curve_data) => {
                                    current_node.min_frame = std::cmp::min(
                                        current_node.min_frame,
                                        frame_number,
                                    );
                                    current_node.max_frame = std::cmp::max(
                                        current_node.max_frame,
                                        frame_number,
                                    );

                                    curve_data.insert(frame_number, f64_value);
                                }
                                _ => (),
                            }
                        }
                        _ => (),
                    }
                }
            }
        }
    }

    // TODO: Before adding the curve we should ensure the curve does
    // not have any frame number gaps. If there are gaps we must fill
    // them with interpolated neighboring values or error out.

    current_node
        .knobs
        .insert(current_knob_name.to_string(), current_knob_curve);
}

/// Parse the interior of a Nuke node definition.
///
/// 'Knobs' in Nuke terms is an attribute or parameter of a node.
///
/// Knob definitions look like:
///    knob_name knob_value
///
/// Such as:
///    name MyNode1
///
/// Where the special knob "name" defines the name of the Node.
///
/// Other examples include:
///    my_float 0.3
///    my_int 1
///    my_enum value_name
///
/// Knobs can also have animated values, such as:
///    my_float {{curve x1 0.3 x2 0.4 x3 0.5 }}
///
fn parse_knob_definition(
    line: &str,
    state: &mut ParserState,
    current_node: &mut Node,
    nodes: &mut Vec<Node>,
) {
    // Looking for knob name/value pairs.
    let mut words_iter = line.split_whitespace().enumerate();
    while let Some((word_number, word)) = words_iter.next() {
        if word_number == 0 {
            if state.expect_brace_end == true {
                if word.starts_with(BRACE_END_TOKEN) {
                    state.expect_brace_start = true;
                    state.expect_brace_end = false;

                    // If no curve was used, the frame range is static.
                    if current_node.min_frame == FrameNumber::MAX
                        || current_node.max_frame == FrameNumber::MIN
                    {
                        current_node.min_frame = STATIC_FRAME_NUMBER;
                        current_node.max_frame = STATIC_FRAME_NUMBER;
                    }

                    nodes.push(current_node.clone());

                    // Reset the "current_" state variables.
                    state.scope_level -= 1;

                    *current_node = Node::new();
                    continue;
                }
            }

            // Knob name.
            if word == KNOB_NAME_NODE_NAME_VALUE {
                if let Some((_, node_name)) = words_iter.next() {
                    current_node.node_name = node_name.to_string();
                };
                // After we got the name value, we expect to
                // go to the next line. The name knob cannot
                // be animated, so there is no more data
                // expected.
                break;
            }

            let current_knob_name = word;

            // Knob value.
            if let Some((_, word)) = words_iter.next() {
                if word == KNOB_START_CURVE_TOKEN {
                    // Animated knob, with a curve.
                    parse_knob_value_curve(
                        &mut words_iter,
                        state,
                        current_knob_name,
                        current_node,
                    );
                } else {
                    // A regular knob value.
                    let knob_value = match parse_str_to_trivial_value(word) {
                        TrivialValue::I32(value) => KnobValue::I32(value),
                        TrivialValue::F64(value) => KnobValue::F64(value),
                        _ => KnobValue::None,
                    };

                    current_node
                        .knobs
                        .insert(current_knob_name.to_string(), knob_value);
                }
            }
        }
    }
}

fn get_static_knob_value_f64(
    knob_name: &str,
    knobs: &HashMap<String, KnobValue>,
    default_value: f64,
) -> f64 {
    match knobs.get(knob_name) {
        Some(knob_value) => match knob_value {
            KnobValue::F64(value) => *value,
            KnobValue::F64Curve(curve) => match curve.iter().next() {
                Some((_frame_number, value)) => *value,
                None => default_value,
            },
            _ => default_value,
        },
        None => default_value,
    }
}

fn get_animated_knob_value_f64(
    knob_name: &str,
    knobs: &HashMap<String, KnobValue>,
    default_value: f64,
    frame_number: FrameNumber,
) -> f64 {
    match knobs.get(knob_name) {
        Some(knob_value) => match knob_value {
            KnobValue::F64(value) => *value,
            KnobValue::F64Curve(curve) => match curve.get(&frame_number) {
                Some(value) => *value,
                None => default_value,
            },
            _ => default_value,
        },
        None => default_value,
    }
}

/// A very simple Nuke file parser.
///
/// The implementation is a line-by-line top-down approach.
///
/// This parser supports knobs with floating point or integer values,
/// and the values can be animated or not.
///
/// The parser supports multiple nodes, one after the
/// other. Connections between nodes is not supported.
fn parse_nuke_file_lines(
    lines: Vec<String>,
) -> Result<Box<ShimDistortionLayers>> {
    let mut state = ParserState::new();

    let mut current_node = Node::new();
    let mut nodes = Vec::new();

    let mut lines_iter = lines.iter();
    while let Some(line) = lines_iter.next() {
        match state.scope_level {
            0 => parse_node_definitions(line, &mut state, &mut current_node),
            _ => parse_knob_definition(
                line,
                &mut state,
                &mut current_node,
                &mut nodes,
            ),
        }
    }

    let mut layer_count: LayerSize = 0;
    let mut layer_lens_model_types = SmallVec::new();
    let mut layer_frame_range = SmallVec::new();
    let mut camera_parameters = BindCameraParameters::default();
    let mut lens_parameters = HashMap::new();
    for node in nodes {
        let min_frame = node.min_frame;
        let max_frame = node.max_frame;
        match node.lens_model_type {
            BindLensModelType::TdeClassic => {
                for frame_number in min_frame..=max_frame {
                    let distortion = get_animated_knob_value_f64(
                        "Distortion",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let anamorphic_squeeze = get_animated_knob_value_f64(
                        "Anamorphic_Squeeze",
                        &node.knobs,
                        1.0,
                        frame_number,
                    );
                    let curvature_x = get_animated_knob_value_f64(
                        "Curvature_X",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let curvature_y = get_animated_knob_value_f64(
                        "Curvature_Y",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let quartic_distortion = get_animated_knob_value_f64(
                        "Quartic_Distortion",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let mut parameter_block =
                        [0.0 as f64; MAX_LENS_PARAMETER_COUNT];
                    parameter_block[0] = distortion;
                    parameter_block[1] = anamorphic_squeeze;
                    parameter_block[2] = curvature_x;
                    parameter_block[3] = curvature_y;
                    parameter_block[4] = quartic_distortion;
                    lens_parameters
                        .insert((layer_count, frame_number), parameter_block);
                }
                layer_count += 1;
            }
            BindLensModelType::TdeRadialStdDeg4 => {
                for frame_number in min_frame..=max_frame {
                    let distortion_deg2 = get_animated_knob_value_f64(
                        "Distortion_Degree_2",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let u_deg2 = get_animated_knob_value_f64(
                        "U_Degree_2",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let v_deg2 = get_animated_knob_value_f64(
                        "V_Degree_2",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let quartic_distortion_deg4 = get_animated_knob_value_f64(
                        "Quartic_Distortion_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let u_deg4 = get_animated_knob_value_f64(
                        "U_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let v_deg4 = get_animated_knob_value_f64(
                        "V_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let cylindric_direction = get_animated_knob_value_f64(
                        "Phi_Cylindric_Direction",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let cylindric_bending = get_animated_knob_value_f64(
                        "B_Cylindric_Bending",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let mut parameter_block =
                        [0.0 as f64; MAX_LENS_PARAMETER_COUNT];
                    parameter_block[0] = distortion_deg2;
                    parameter_block[1] = u_deg2;
                    parameter_block[2] = v_deg2;
                    parameter_block[3] = quartic_distortion_deg4;
                    parameter_block[4] = u_deg4;
                    parameter_block[5] = v_deg4;
                    parameter_block[6] = cylindric_direction;
                    parameter_block[7] = cylindric_bending;
                    lens_parameters
                        .insert((layer_count, frame_number), parameter_block);
                }
                layer_count += 1;
            }
            BindLensModelType::TdeAnamorphicStdDeg4 => {
                for frame_number in min_frame..=max_frame {
                    let degree2_cx02 = get_animated_knob_value_f64(
                        "Cx02_Degree_2",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree2_cy02 = get_animated_knob_value_f64(
                        "Cy02_Degree_2",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree2_cx22 = get_animated_knob_value_f64(
                        "Cx22_Degree_2",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree2_cy22 = get_animated_knob_value_f64(
                        "Cy22_Degree_2",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree4_cx04 = get_animated_knob_value_f64(
                        "Cx04_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree4_cy04 = get_animated_knob_value_f64(
                        "Cy04_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree4_cx24 = get_animated_knob_value_f64(
                        "Cx24_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree4_cy24 = get_animated_knob_value_f64(
                        "Cy24_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree4_cx44 = get_animated_knob_value_f64(
                        "Cx44_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree4_cy44 = get_animated_knob_value_f64(
                        "Cx44_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let lens_rotation = get_animated_knob_value_f64(
                        "Lens_Rotation",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let squeeze_x = get_animated_knob_value_f64(
                        "Squeeze_X",
                        &node.knobs,
                        1.0,
                        frame_number,
                    );
                    let squeeze_y = get_animated_knob_value_f64(
                        "Squeeze_Y",
                        &node.knobs,
                        1.0,
                        frame_number,
                    );

                    let mut parameter_block =
                        [0.0 as f64; MAX_LENS_PARAMETER_COUNT];
                    parameter_block[0] = degree2_cx02;
                    parameter_block[1] = degree2_cy02;
                    parameter_block[2] = degree2_cx22;
                    parameter_block[3] = degree2_cy22;
                    parameter_block[4] = degree4_cx04;
                    parameter_block[5] = degree4_cy04;
                    parameter_block[6] = degree4_cx24;
                    parameter_block[7] = degree4_cy24;
                    parameter_block[8] = degree4_cx44;
                    parameter_block[9] = degree4_cy44;
                    parameter_block[10] = lens_rotation;
                    parameter_block[11] = squeeze_x;
                    parameter_block[12] = squeeze_y;
                    lens_parameters
                        .insert((layer_count, frame_number), parameter_block);
                }
                layer_count += 1;
            }
            BindLensModelType::TdeAnamorphicStdDeg4Rescaled => {
                for frame_number in min_frame..=max_frame {
                    let degree2_cx02 = get_animated_knob_value_f64(
                        "Cx02_Degree_2",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree2_cy02 = get_animated_knob_value_f64(
                        "Cy02_Degree_2",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree2_cx22 = get_animated_knob_value_f64(
                        "Cx22_Degree_2",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree2_cy22 = get_animated_knob_value_f64(
                        "Cy22_Degree_2",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree4_cx04 = get_animated_knob_value_f64(
                        "Cx04_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree4_cy04 = get_animated_knob_value_f64(
                        "Cy04_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree4_cx24 = get_animated_knob_value_f64(
                        "Cx24_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree4_cy24 = get_animated_knob_value_f64(
                        "Cy24_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree4_cx44 = get_animated_knob_value_f64(
                        "Cx44_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree4_cy44 = get_animated_knob_value_f64(
                        "Cx44_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let lens_rotation = get_animated_knob_value_f64(
                        "Lens_Rotation",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let squeeze_x = get_animated_knob_value_f64(
                        "Squeeze_X",
                        &node.knobs,
                        1.0,
                        frame_number,
                    );
                    let squeeze_y = get_animated_knob_value_f64(
                        "Squeeze_Y",
                        &node.knobs,
                        1.0,
                        frame_number,
                    );

                    let rescale = get_animated_knob_value_f64(
                        "Rescale",
                        &node.knobs,
                        1.0,
                        frame_number,
                    );

                    let mut parameter_block =
                        [0.0 as f64; MAX_LENS_PARAMETER_COUNT];
                    parameter_block[0] = degree2_cx02;
                    parameter_block[1] = degree2_cy02;
                    parameter_block[2] = degree2_cx22;
                    parameter_block[3] = degree2_cy22;
                    parameter_block[4] = degree4_cx04;
                    parameter_block[5] = degree4_cy04;
                    parameter_block[6] = degree4_cx24;
                    parameter_block[7] = degree4_cy24;
                    parameter_block[8] = degree4_cx44;
                    parameter_block[9] = degree4_cy44;
                    parameter_block[10] = lens_rotation;
                    parameter_block[11] = squeeze_x;
                    parameter_block[12] = squeeze_y;
                    parameter_block[13] = rescale;
                    lens_parameters
                        .insert((layer_count, frame_number), parameter_block);
                }
                layer_count += 1;
            }

            BindLensModelType::TdeAnamorphicStdDeg6 => {
                for frame_number in min_frame..=max_frame {
                    let degree2_cx02 = get_animated_knob_value_f64(
                        "Cx02_Degree_2",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree2_cy02 = get_animated_knob_value_f64(
                        "Cy02_Degree_2",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree2_cx22 = get_animated_knob_value_f64(
                        "Cx22_Degree_2",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree2_cy22 = get_animated_knob_value_f64(
                        "Cy22_Degree_2",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree4_cx04 = get_animated_knob_value_f64(
                        "Cx04_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree4_cy04 = get_animated_knob_value_f64(
                        "Cy04_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree4_cx24 = get_animated_knob_value_f64(
                        "Cx24_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree4_cy24 = get_animated_knob_value_f64(
                        "Cy24_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree4_cx44 = get_animated_knob_value_f64(
                        "Cx44_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree4_cy44 = get_animated_knob_value_f64(
                        "Cx44_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree6_cx06 = get_animated_knob_value_f64(
                        "Cx06_Degree_6",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree6_cy06 = get_animated_knob_value_f64(
                        "Cy06_Degree_6",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree6_cx26 = get_animated_knob_value_f64(
                        "Cx26_Degree_6",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree6_cy26 = get_animated_knob_value_f64(
                        "Cy26_Degree_6",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree6_cx46 = get_animated_knob_value_f64(
                        "Cx46_Degree_6",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree6_cy46 = get_animated_knob_value_f64(
                        "Cy46_Degree_6",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree6_cx66 = get_animated_knob_value_f64(
                        "Cx66_Degree_6",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree6_cy66 = get_animated_knob_value_f64(
                        "Cx66_Degree_6",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let lens_rotation = get_animated_knob_value_f64(
                        "Lens_Rotation",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let squeeze_x = get_animated_knob_value_f64(
                        "Squeeze_X",
                        &node.knobs,
                        1.0,
                        frame_number,
                    );
                    let squeeze_y = get_animated_knob_value_f64(
                        "Squeeze_Y",
                        &node.knobs,
                        1.0,
                        frame_number,
                    );

                    let mut parameter_block =
                        [0.0 as f64; MAX_LENS_PARAMETER_COUNT];
                    parameter_block[0] = degree2_cx02;
                    parameter_block[1] = degree2_cy02;
                    parameter_block[2] = degree2_cx22;
                    parameter_block[3] = degree2_cy22;
                    parameter_block[4] = degree4_cx04;
                    parameter_block[5] = degree4_cy04;
                    parameter_block[6] = degree4_cx24;
                    parameter_block[7] = degree4_cy24;
                    parameter_block[8] = degree4_cx44;
                    parameter_block[9] = degree4_cy44;
                    parameter_block[10] = degree6_cx06;
                    parameter_block[11] = degree6_cy06;
                    parameter_block[12] = degree6_cx26;
                    parameter_block[13] = degree6_cy26;
                    parameter_block[14] = degree6_cx46;
                    parameter_block[15] = degree6_cy46;
                    parameter_block[16] = degree6_cx66;
                    parameter_block[17] = degree6_cy66;
                    parameter_block[18] = lens_rotation;
                    parameter_block[19] = squeeze_x;
                    parameter_block[20] = squeeze_y;
                    lens_parameters
                        .insert((layer_count, frame_number), parameter_block);
                }
                layer_count += 1;
            }
            BindLensModelType::TdeAnamorphicStdDeg6Rescaled => {
                for frame_number in min_frame..=max_frame {
                    let degree2_cx02 = get_animated_knob_value_f64(
                        "Cx02_Degree_2",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree2_cy02 = get_animated_knob_value_f64(
                        "Cy02_Degree_2",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree2_cx22 = get_animated_knob_value_f64(
                        "Cx22_Degree_2",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree2_cy22 = get_animated_knob_value_f64(
                        "Cy22_Degree_2",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree4_cx04 = get_animated_knob_value_f64(
                        "Cx04_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree4_cy04 = get_animated_knob_value_f64(
                        "Cy04_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree4_cx24 = get_animated_knob_value_f64(
                        "Cx24_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree4_cy24 = get_animated_knob_value_f64(
                        "Cy24_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree4_cx44 = get_animated_knob_value_f64(
                        "Cx44_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree4_cy44 = get_animated_knob_value_f64(
                        "Cx44_Degree_4",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree6_cx06 = get_animated_knob_value_f64(
                        "Cx06_Degree_6",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree6_cy06 = get_animated_knob_value_f64(
                        "Cy06_Degree_6",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree6_cx26 = get_animated_knob_value_f64(
                        "Cx26_Degree_6",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree6_cy26 = get_animated_knob_value_f64(
                        "Cy26_Degree_6",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree6_cx46 = get_animated_knob_value_f64(
                        "Cx46_Degree_6",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree6_cy46 = get_animated_knob_value_f64(
                        "Cy46_Degree_6",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let degree6_cx66 = get_animated_knob_value_f64(
                        "Cx66_Degree_6",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let degree6_cy66 = get_animated_knob_value_f64(
                        "Cx66_Degree_6",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );

                    let lens_rotation = get_animated_knob_value_f64(
                        "Lens_Rotation",
                        &node.knobs,
                        0.0,
                        frame_number,
                    );
                    let squeeze_x = get_animated_knob_value_f64(
                        "Squeeze_X",
                        &node.knobs,
                        1.0,
                        frame_number,
                    );
                    let squeeze_y = get_animated_knob_value_f64(
                        "Squeeze_Y",
                        &node.knobs,
                        1.0,
                        frame_number,
                    );

                    let rescale = get_animated_knob_value_f64(
                        "Rescale",
                        &node.knobs,
                        1.0,
                        frame_number,
                    );

                    let mut parameter_block =
                        [0.0 as f64; MAX_LENS_PARAMETER_COUNT];
                    parameter_block[0] = degree2_cx02;
                    parameter_block[1] = degree2_cy02;
                    parameter_block[2] = degree2_cx22;
                    parameter_block[3] = degree2_cy22;
                    parameter_block[4] = degree4_cx04;
                    parameter_block[5] = degree4_cy04;
                    parameter_block[6] = degree4_cx24;
                    parameter_block[7] = degree4_cy24;
                    parameter_block[8] = degree4_cx44;
                    parameter_block[9] = degree4_cy44;
                    parameter_block[10] = degree6_cx06;
                    parameter_block[11] = degree6_cy06;
                    parameter_block[12] = degree6_cx26;
                    parameter_block[13] = degree6_cy26;
                    parameter_block[14] = degree6_cx46;
                    parameter_block[15] = degree6_cy46;
                    parameter_block[16] = degree6_cx66;
                    parameter_block[17] = degree6_cy66;
                    parameter_block[18] = lens_rotation;
                    parameter_block[19] = squeeze_x;
                    parameter_block[20] = squeeze_y;
                    parameter_block[21] = rescale;
                    lens_parameters
                        .insert((layer_count, frame_number), parameter_block);
                }
                layer_count += 1;
            }

            _ => continue,
        }

        // Common knob names for all valid lens distortion nodes.
        camera_parameters.focal_length_cm =
            get_static_knob_value_f64("tde4_focal_length_cm", &node.knobs, 3.5);
        camera_parameters.film_back_width_cm = get_static_knob_value_f64(
            "tde4_filmback_width_cm",
            &node.knobs,
            3.6,
        );
        camera_parameters.film_back_height_cm = get_static_knob_value_f64(
            "tde4_filmback_height_cm",
            &node.knobs,
            2.4,
        );
        camera_parameters.lens_center_offset_x_cm = get_static_knob_value_f64(
            "tde4_lens_center_offset_x_cm",
            &node.knobs,
            0.0,
        );
        camera_parameters.lens_center_offset_y_cm = get_static_knob_value_f64(
            "tde4_lens_center_offset_y_cm",
            &node.knobs,
            0.0,
        );
        camera_parameters.pixel_aspect =
            get_static_knob_value_f64("tde4_pixel_aspect", &node.knobs, 1.0);

        layer_frame_range.push((min_frame, max_frame));
        layer_lens_model_types.push(node.lens_model_type);
    }

    Ok(Box::new(ShimDistortionLayers::from_parts(
        layer_count,
        &layer_lens_model_types,
        &layer_frame_range,
        camera_parameters,
        &lens_parameters,
    )))
}

fn read_nuke_file_lines(file_path: &str) -> Vec<String> {
    std::fs::read_to_string(file_path)
        .expect("Could not open file.")
        .lines()
        .filter_map(|x| {
            let x = x.trim();
            let is_comment = x.starts_with('#');
            if is_comment {
                None
            } else {
                Some(x.to_string())
            }
        })
        .collect()
}

pub fn shim_read_lens_file(file_path: &str) -> Box<ShimDistortionLayers> {
    let lines = read_nuke_file_lines(file_path);
    parse_nuke_file_lines(lines).expect("should get distortion layers")
}
