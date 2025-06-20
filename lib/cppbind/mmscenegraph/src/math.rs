//
// Copyright (C) 2020, 2021 David Cattermole.
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

use crate::cxxbridge::ffi::ControlPointDistribution as BindControlPointDistribution;
use crate::cxxbridge::ffi::FilmFit as BindFilmFit;
use crate::cxxbridge::ffi::InterpolationMethod as BindInterpolationMethod;
use crate::cxxbridge::ffi::RotateOrder as BindRotateOrder;
use mmscenegraph_rust::curve::simplify::ControlPointDistribution as CoreControlPointDistribution;
use mmscenegraph_rust::math::camera::FilmFit as CoreFilmFit;
use mmscenegraph_rust::math::interpolate::InterpolationMethod as CoreInterpolationMethod;
use mmscenegraph_rust::math::rotate::euler::RotateOrder as CoreRotateOrder;

pub fn bind_to_core_rotate_order(value: BindRotateOrder) -> CoreRotateOrder {
    match value {
        BindRotateOrder::XYZ => CoreRotateOrder::XYZ,
        BindRotateOrder::YXZ => CoreRotateOrder::YXZ,
        BindRotateOrder::ZXY => CoreRotateOrder::ZXY,
        BindRotateOrder::XZY => CoreRotateOrder::XZY,
        BindRotateOrder::ZYX => CoreRotateOrder::ZYX,
        BindRotateOrder::YZX => CoreRotateOrder::YZX,
        _ => panic!("Invalid rotate order: {:?}", value),
    }
}

pub fn core_to_bind_rotate_order(value: CoreRotateOrder) -> BindRotateOrder {
    match value {
        CoreRotateOrder::XYZ => BindRotateOrder::XYZ,
        CoreRotateOrder::YXZ => BindRotateOrder::YXZ,
        CoreRotateOrder::ZXY => BindRotateOrder::ZXY,
        CoreRotateOrder::XZY => BindRotateOrder::XZY,
        CoreRotateOrder::ZYX => BindRotateOrder::ZYX,
        CoreRotateOrder::YZX => BindRotateOrder::YZX,
    }
}

pub fn bind_to_core_film_fit(value: BindFilmFit) -> CoreFilmFit {
    match value {
        BindFilmFit::Fill => CoreFilmFit::Fill,
        BindFilmFit::Horizontal => CoreFilmFit::Horizontal,
        BindFilmFit::Vertical => CoreFilmFit::Vertical,
        BindFilmFit::Overscan => CoreFilmFit::Overscan,
        _ => panic!("Invalid film fit: {:?}", value),
    }
}

pub fn core_to_bind_film_fit(value: CoreFilmFit) -> BindFilmFit {
    match value {
        CoreFilmFit::Fill => BindFilmFit::Fill,
        CoreFilmFit::Horizontal => BindFilmFit::Horizontal,
        CoreFilmFit::Vertical => BindFilmFit::Vertical,
        CoreFilmFit::Overscan => BindFilmFit::Overscan,
    }
}

pub fn bind_to_core_control_point_distribution(
    value: BindControlPointDistribution,
) -> CoreControlPointDistribution {
    match value {
        BindControlPointDistribution::Uniform => {
            CoreControlPointDistribution::Uniform
        }
        BindControlPointDistribution::AutoKeypoints => {
            CoreControlPointDistribution::AutoKeypoints
        }
        _ => panic!("Invalid control point distribution: {:?}", value),
    }
}

pub fn core_to_bind_control_point_distribution(
    value: CoreControlPointDistribution,
) -> BindControlPointDistribution {
    match value {
        CoreControlPointDistribution::Uniform => {
            BindControlPointDistribution::Uniform
        }
        CoreControlPointDistribution::AutoKeypoints => {
            BindControlPointDistribution::AutoKeypoints
        }
    }
}

pub fn bind_to_core_interpolation_method(
    value: BindInterpolationMethod,
) -> CoreInterpolationMethod {
    match value {
        // BindInterpolationMethod::Nearest => CoreInterpolationMethod::Nearest,
        BindInterpolationMethod::Linear => CoreInterpolationMethod::Linear,
        BindInterpolationMethod::CubicNUBS => {
            CoreInterpolationMethod::CubicNUBS
        }
        BindInterpolationMethod::CubicSpline => {
            CoreInterpolationMethod::CubicSpline
        }
        _ => panic!("Invalid interpolation method: {:?}", value),
    }
}

pub fn core_to_bind_interpolation_method(
    value: CoreInterpolationMethod,
) -> BindInterpolationMethod {
    match value {
        // CoreInterpolationMethod::Nearest => BindInterpolationMethod::Nearest,
        CoreInterpolationMethod::Linear => BindInterpolationMethod::Linear,
        CoreInterpolationMethod::CubicNUBS => {
            BindInterpolationMethod::CubicNUBS
        }
        CoreInterpolationMethod::CubicSpline => {
            BindInterpolationMethod::CubicSpline
        }
    }
}
