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
/// 3D Euler Rotation mathematics.

use crate::constant::Matrix33;
use crate::constant::Matrix44;
use crate::constant::Real;

#[derive(Debug, Default, Copy, Clone)]
pub struct EulerAngles {
    pub x: Real,
    pub y: Real,
    pub z: Real,
    pub w: Real,
}

// const EULER_REP_NO: usize = 0; // Repetition No
// const EULER_PAR_EVEN: usize = 0; // Parity Even
// const EULER_FRM_S: usize = 0; // Rotating Axis Frame
const EULER_REP_YES: usize = 1; // Repetition Yes
const EULER_PAR_ODD: usize = 1; // Parity Odd
const EULER_FRM_R: usize = 1; // Static Axis Frame

/// unpacks all useful information about order simultaneously.
fn euler_get_order<'a>(
    order: u8,
    i: &'a mut usize,
    j: &'a mut usize,
    k: &'a mut usize,
    h: &'a mut usize,
    n: &'a mut usize,
    s: &'a mut usize,
    f: &'a mut usize,
) {
    let euler_safe = &[0, 1, 2, 0];
    let euler_next = &[1, 2, 0, 1];
    let o: usize = order as usize;
    *f = o & 1;
    let o = o >> 1;
    *s = o & 1;
    let o = o >> 1;
    *n = o & 1;
    let o = o >> 1;
    *i = euler_safe[o & 3];
    *j = euler_next[*i + *n];
    *k = euler_next[*i + 1 - *n];
    if *s != 0 {
        *h = *k
    } else {
        *h = *i
    };
}

// /// creates an order value between 0 and 23 from 4-tuple choices. */
// fn euler_order(i: usize, p: usize, r: usize, f: usize) -> usize {
//     // ((((((i) << 1) + (p)) << 1) + (r)) << 1) + (f)
//     let i = (i << 1) + p;
//     let i = (i << 1) + r;
//     let i = (i << 1) + f;
//     i
// }

/// Construct matrix from Euler angles (in radians).
pub fn euler_to_matrix4(mut ea: EulerAngles) -> Matrix44 {
    let mut matrix = Matrix44::identity();

    let mut i: usize = 0;
    let mut j: usize = 0;
    let mut k: usize = 0;
    let mut h: usize = 0;
    let mut n: usize = 0;
    let mut s: usize = 0;
    let mut f: usize = 0;
    euler_get_order(
        ea.w as u8, &mut i, &mut j, &mut k, &mut h, &mut n, &mut s, &mut f,
    );

    if f == EULER_FRM_R {
        // Swap X and Z
        let t = ea.x;
        ea.x = ea.z;
        ea.z = t;
    }

    if n == EULER_PAR_ODD {
        // Negate the euler angles.
        ea.x = -ea.x;
        ea.y = -ea.y;
        ea.z = -ea.z;
    }

    let ti = ea.x;
    let tj = ea.y;
    let th = ea.z;

    let (si, ci) = ti.sin_cos();
    let (sj, cj) = tj.sin_cos();
    let (sh, ch) = th.sin_cos();

    let cc = ci * ch;
    let cs = ci * sh;
    let sc = si * ch;
    let ss = si * sh;

    if s == EULER_REP_YES {
        matrix[(i, i)] = cj;
        matrix[(i, j)] = sj * si;
        matrix[(i, k)] = sj * ci;

        matrix[(j, i)] = sj * sh;
        matrix[(j, j)] = -cj * ss + cc;
        matrix[(j, k)] = -cj * cs - sc;

        matrix[(k, i)] = -sj * ch;
        matrix[(k, j)] = cj * sc + cs;
        matrix[(k, k)] = cj * cc - ss;
    } else {
        matrix[(i, i)] = cj * ch;
        matrix[(i, j)] = sj * sc - cs;
        matrix[(i, k)] = sj * cc + ss;

        matrix[(j, i)] = cj * sh;
        matrix[(j, j)] = sj * ss + cc;
        matrix[(j, k)] = sj * cs - sc;

        matrix[(k, i)] = -sj;
        matrix[(k, j)] = cj * si;
        matrix[(k, k)] = cj * ci;
    }

    // Fill in last matrix column/row (for 4x4 matrix)
    matrix[(3, 0)] = 0.0;
    matrix[(3, 1)] = 0.0;
    matrix[(3, 2)] = 0.0;
    matrix[(0, 3)] = 0.0;
    matrix[(1, 3)] = 0.0;
    matrix[(2, 3)] = 0.0;
    matrix[(3, 3)] = 1.0;

    matrix
}

/// Convert matrix to Euler angles (as radians).
pub fn euler_from_matrix3(matrix: Matrix33, order: u8) -> EulerAngles {
    let mut ea = EulerAngles {
        x: 0.0,
        y: 0.0,
        z: 0.0,
        w: 1.0,
    };

    let mut i: usize = 0;
    let mut j: usize = 0;
    let mut k: usize = 0;
    let mut h: usize = 0;
    let mut n: usize = 0;
    let mut s: usize = 0;
    let mut f: usize = 0;
    euler_get_order(
        order, &mut i, &mut j, &mut k, &mut h, &mut n, &mut s, &mut f,
    );

    if s == EULER_REP_YES {
        let sy: Real = (matrix[(i, j)] * matrix[(i, j)]
            + matrix[(i, k)] * matrix[(i, k)])
            .sqrt();
        if sy > (16.0 * Real::EPSILON) {
            ea.x = matrix[(i, j)].atan2(matrix[(i, k)]);
            ea.y = sy.atan2(matrix[(i, i)]);
            ea.z = matrix[(j, i)].atan2(-matrix[(k, i)]);
        } else {
            ea.x = (-matrix[(j, k)]).atan2(matrix[(j, j)]);
            ea.y = sy.atan2(matrix[(i, i)]);
            ea.z = 0.0;
        }
    } else {
        let cy: Real = (matrix[(i, i)] * matrix[(i, i)]
            + matrix[(j, i)] * matrix[(j, i)])
            .sqrt();
        if cy > (16.0 * Real::EPSILON) {
            ea.x = matrix[(k, j)].atan2(matrix[(k, k)]);
            ea.y = (-matrix[(k, i)]).atan2(cy);
            ea.z = matrix[(j, i)].atan2(matrix[(i, i)]);
        } else {
            ea.x = (-matrix[(j, k)]).atan2(matrix[(j, j)]);
            ea.y = (-matrix[(k, i)]).atan2(cy);
            ea.z = 0.0;
        }
    }
    if n == EULER_PAR_ODD {
        // Negate angles.
        ea.x = -ea.x;
        ea.y = -ea.y;
        ea.z = -ea.z;
    }
    if f == EULER_FRM_R {
        // Swap X axis and Z axis.
        let t = ea.x;
        ea.x = ea.z;
        ea.z = t;
    }
    ea.w = order as Real;
    ea
}

// http://bediyap.com/programming/convert-quaternion-to-euler-rotations/

// Supported Rotation Orders.
#[derive(Debug, Copy, Clone, Eq, PartialEq, Hash, Ord, PartialOrd)]
pub enum RotateOrder {
    XYZ = 0, // XYZ
    YXZ = 4, // YXZ
    ZXY = 2, // ZXY
    XZY = 3, // XZY
    ZYX = 5, // ZYX
    YZX = 1, // YZX
}

impl From<u8> for RotateOrder {
    fn from(index: u8) -> Self {
        match index {
            0 => RotateOrder::XYZ,
            1 => RotateOrder::YZX,
            2 => RotateOrder::ZXY,
            3 => RotateOrder::XZY,
            4 => RotateOrder::YXZ,
            5 => RotateOrder::ZYX,
            _ => panic!("Invalid Rotate Order index"),
        }
    }
}

#[inline]
pub fn rotate_order_from_index(index: u8) -> RotateOrder {
    match index {
        0 => RotateOrder::XYZ,
        1 => RotateOrder::YZX,
        2 => RotateOrder::ZXY,
        3 => RotateOrder::XZY,
        4 => RotateOrder::YXZ,
        5 => RotateOrder::ZYX,
        _ => panic!("This rotate order index is invalid."),
    }
}
