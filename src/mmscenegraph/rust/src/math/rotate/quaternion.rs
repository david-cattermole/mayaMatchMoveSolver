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
/// 3D Quaternion Rotation mathematics.
use crate::constant::Matrix33;
use crate::constant::Matrix44;
use crate::constant::Quaternion;
use crate::constant::Real;
use crate::math::rotate::euler::EulerAngles;
use crate::math::rotate::euler::RotateOrder;

#[inline]
fn three_axis_rotation(r11: Real, r12: Real, r21: Real, r31: Real, r32: Real) -> EulerAngles {
    EulerAngles {
        x: r11.atan2(r12),
        y: r31.atan2(r32),
        z: r21.asin(),
        w: 0.0,
    }
}

#[inline]
pub fn quaternion_to_euler(q: Quaternion, order: RotateOrder) -> EulerAngles {
    match order {
        RotateOrder::XYZ => {
            let mut res = three_axis_rotation(
                2.0 * (q[0] * q[1] + q.w * q[2]),
                q.w * q.w + q[0] * q[0] - q[1] * q[1] - q[2] * q[2],
                -2.0 * (q[0] * q[2] - q.w * q[1]),
                2.0 * (q[1] * q[2] + q.w * q[0]),
                q.w * q.w - q[0] * q[0] - q[1] * q[1] + q[2] * q[2],
            );

            // Reorder X, Y and Z.
            let tmp1 = res.x;
            let tmp2 = res.y;
            let tmp3 = res.z;
            res.x = tmp2;
            res.y = tmp3;
            res.z = tmp1;

            res
        }

        RotateOrder::YXZ => {
            let mut res = three_axis_rotation(
                -2.0 * (q[0] * q[1] - q.w * q[2]),
                q.w * q.w - q[0] * q[0] + q[1] * q[1] - q[2] * q[2],
                2.0 * (q[1] * q[2] + q.w * q[0]),
                -2.0 * (q[0] * q[2] - q.w * q[1]),
                q.w * q.w - q[0] * q[0] - q[1] * q[1] + q[2] * q[2],
            );

            // Swap X and Z.
            let tmp1 = res.x;
            res.x = res.z;
            res.z = tmp1;

            res
        }

        RotateOrder::ZXY => {
            let mut res = three_axis_rotation(
                2.0 * (q[0] * q[2] + q.w * q[1]),
                q.w * q.w - q[0] * q[0] - q[1] * q[1] + q[2] * q[2],
                -2.0 * (q[1] * q[2] - q.w * q[0]),
                2.0 * (q[0] * q[1] + q.w * q[2]),
                q.w * q.w - q[0] * q[0] + q[1] * q[1] - q[2] * q[2],
            );

            // Reorder X, Y and Z.
            let tmp1 = res.x;
            let tmp2 = res.y;
            let tmp3 = res.z;
            res.x = tmp3;
            res.y = tmp1;
            res.z = tmp2;

            res
        }

        RotateOrder::XZY => {
            let mut res = three_axis_rotation(
                -2.0 * (q[0] * q[2] - q.w * q[1]),
                q.w * q.w + q[0] * q[0] - q[1] * q[1] - q[2] * q[2],
                2.0 * (q[0] * q[1] + q.w * q[2]),
                -2.0 * (q[1] * q[2] - q.w * q[0]),
                q.w * q.w - q[0] * q[0] + q[1] * q[1] - q[2] * q[2],
            );

            // Swap X and Y.
            let tmp1 = res.x;
            res.x = res.y;
            res.y = tmp1;

            res
        }

        RotateOrder::ZYX => {
            let mut res = three_axis_rotation(
                -2.0 * (q[1] * q[2] - q.w * q[0]),
                q.w * q.w - q[0] * q[0] - q[1] * q[1] + q[2] * q[2],
                2.0 * (q[0] * q[2] + q.w * q[1]),
                -2.0 * (q[0] * q[1] - q.w * q[2]),
                q.w * q.w + q[0] * q[0] - q[1] * q[1] - q[2] * q[2],
            );

            // Swap Y and Z.
            let tmp1 = res.y;
            res.y = res.z;
            res.z = tmp1;

            res
        }

        RotateOrder::YZX => three_axis_rotation(
            2.0 * (q[1] * q[2] + q.w * q[0]),
            q.w * q.w - q[0] * q[0] + q[1] * q[1] - q[2] * q[2],
            -2.0 * (q[0] * q[1] - q.w * q[2]),
            2.0 * (q[0] * q[2] + q.w * q[1]),
            q.w * q.w + q[0] * q[0] - q[1] * q[1] - q[2] * q[2],
        ),
    }
}

/// Convert 4x4 rotation matrix to a quaternion.
#[inline]
pub fn matrix4_to_quaternion(a: Matrix44) -> Quaternion {
    let x;
    let y;
    let z;
    let w;
    let trace = a[(0, 0)] + a[(1, 1)] + a[(2, 2)];
    if trace > 0.0 {
        let s = 0.5 / (trace + 1.0).sqrt();
        w = 0.25 / s;
        x = (a[(2, 1)] - a[(1, 2)]) * s;
        y = (a[(0, 2)] - a[(2, 0)]) * s;
        z = (a[(1, 0)] - a[(0, 1)]) * s;
    } else {
        if a[(0, 0)] > a[(1, 1)] && a[(0, 0)] > a[(2, 2)] {
            let s = 2.0 * (1.0 + a[(0, 0)] - a[(1, 1)] - a[(2, 2)]).sqrt();
            w = (a[(2, 1)] - a[(1, 2)]) / s;
            x = 0.25 * s;
            y = (a[(0, 1)] + a[(1, 0)]) / s;
            z = (a[(0, 2)] + a[(2, 0)]) / s;
        } else if a[(1, 1)] > a[(2, 2)] {
            let s = 2.0 * (1.0 + a[(1, 1)] - a[(0, 0)] - a[(2, 2)]).sqrt();
            w = (a[(0, 2)] - a[(2, 0)]) / s;
            x = (a[(0, 1)] + a[(1, 0)]) / s;
            y = 0.25 * s;
            z = (a[(1, 2)] + a[(2, 1)]) / s;
        } else {
            let s = 2.0 * (1.0 + a[(2, 2)] - a[(0, 0)] - a[(1, 1)]).sqrt();
            w = (a[(1, 0)] - a[(0, 1)]) / s;
            x = (a[(0, 2)] + a[(2, 0)]) / s;
            y = (a[(1, 2)] + a[(2, 1)]) / s;
            z = 0.25 * s;
        }
    }
    Quaternion::new(w, x, y, z)
}

pub fn matrix3_to_quaternion(a: Matrix33) -> Quaternion {
    let x;
    let y;
    let z;
    let w;
    let trace = a[(0, 0)] + a[(1, 1)] + a[(2, 2)];
    if trace > 0.0 {
        let s = 0.5 / (trace + 1.0).sqrt();
        w = 0.25 / s;
        x = (a[(2, 1)] - a[(1, 2)]) * s;
        y = (a[(0, 2)] - a[(2, 0)]) * s;
        z = (a[(1, 0)] - a[(0, 1)]) * s;
    } else {
        if a[(0, 0)] > a[(1, 1)] && a[(0, 0)] > a[(2, 2)] {
            let s = 2.0 * (1.0 + a[(0, 0)] - a[(1, 1)] - a[(2, 2)]).sqrt();
            w = (a[(2, 1)] - a[(1, 2)]) / s;
            x = 0.25 * s;
            y = (a[(0, 1)] + a[(1, 0)]) / s;
            z = (a[(0, 2)] + a[(2, 0)]) / s;
        } else if a[(1, 1)] > a[(2, 2)] {
            let s = 2.0 * (1.0 + a[(1, 1)] - a[(0, 0)] - a[(2, 2)]).sqrt();
            w = (a[(0, 2)] - a[(2, 0)]) / s;
            x = (a[(0, 1)] + a[(1, 0)]) / s;
            y = 0.25 * s;
            z = (a[(1, 2)] + a[(2, 1)]) / s;
        } else {
            let s = 2.0 * (1.0 + a[(2, 2)] - a[(0, 0)] - a[(1, 1)]).sqrt();
            w = (a[(1, 0)] - a[(0, 1)]) / s;
            x = (a[(0, 2)] + a[(2, 0)]) / s;
            y = (a[(1, 2)] + a[(2, 1)]) / s;
            z = 0.25 * s;
        }
    }
    Quaternion::new(w, x, y, z)
}
