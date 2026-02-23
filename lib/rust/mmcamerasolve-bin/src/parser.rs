//
// Copyright (C) 2025 David Cattermole.
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

//! Re-usable parser functions for CLI arguments.

use crate::cli::{ParseResult, SolverType};

fn parse_value<'a>(
    args: &'a [String],
    i: &mut usize,
    arg_name: &str,
) -> Result<&'a str, ParseResult> {
    *i += 1;
    if *i >= args.len() {
        return Err(ParseResult::Error(format!(
            "{} requires a value",
            arg_name
        )));
    }
    let val_str = &args[*i];
    *i += 1;
    Ok(val_str)
}

pub fn parse_f64_arg(
    args: &[String],
    i: &mut usize,
    arg_name: &str,
    error_name: &str,
) -> Result<f64, ParseResult> {
    let val_str = parse_value(args, i, arg_name)?;
    val_str.parse::<f64>().map_err(|_| {
        ParseResult::Error(format!("Invalid {}: {}", error_name, val_str))
    })
}

pub fn parse_positive_f64_arg(
    args: &[String],
    i: &mut usize,
    arg_name: &str,
    error_name: &str,
) -> Result<f64, ParseResult> {
    let val_str = parse_value(args, i, arg_name)?;
    let value = val_str.parse::<f64>().map_err(|_| {
        ParseResult::Error(format!("Invalid {}: {}", error_name, val_str))
    })?;

    if value <= 0.0 {
        return Err(ParseResult::Error(format!(
            "{} must be positive",
            arg_name
        )));
    }
    Ok(value)
}

pub fn parse_u32_arg(
    args: &[String],
    i: &mut usize,
    arg_name: &str,
    error_name: &str,
) -> Result<u32, ParseResult> {
    let val_str = parse_value(args, i, arg_name)?;
    val_str.parse::<u32>().map_err(|_| {
        ParseResult::Error(format!("Invalid {}: {}", error_name, val_str))
    })
}

pub fn parse_positive_u32_arg(
    args: &[String],
    i: &mut usize,
    arg_name: &str,
    error_name: &str,
) -> Result<u32, ParseResult> {
    let val_str = parse_value(args, i, arg_name)?;
    let value = val_str.parse::<u32>().map_err(|_| {
        ParseResult::Error(format!("Invalid {}: {}", error_name, val_str))
    })?;

    if value == 0 {
        return Err(ParseResult::Error(format!(
            "{} must be positive",
            arg_name
        )));
    }
    Ok(value)
}

pub fn parse_positive_usize_arg(
    args: &[String],
    i: &mut usize,
    arg_name: &str,
    error_name: &str,
) -> Result<usize, ParseResult> {
    let val_str = parse_value(args, i, arg_name)?;
    let value = val_str.parse::<usize>().map_err(|_| {
        ParseResult::Error(format!("Invalid {}: {}", error_name, val_str))
    })?;

    if value == 0 {
        return Err(ParseResult::Error(format!(
            "{} must be positive",
            arg_name
        )));
    }
    Ok(value)
}

pub fn parse_solver_type_arg(
    args: &[String],
    i: &mut usize,
    arg_name: &str,
) -> Result<SolverType, ParseResult> {
    let val_str = parse_value(args, i, arg_name)?;
    val_str.parse::<SolverType>().map_err(ParseResult::Error)
}

pub fn parse_string_arg(
    args: &[String],
    i: &mut usize,
    arg_name: &str,
) -> Result<String, ParseResult> {
    let val_str = parse_value(args, i, arg_name)?;
    Ok(val_str.to_string())
}
