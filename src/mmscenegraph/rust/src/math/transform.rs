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
/// 3D Transformation mathematics.
use nalgebra as na;

use crate::constant::Matrix44;
use crate::constant::Real;
use crate::constant::DEGREES_TO_RADIANS;
use crate::constant::RADIANS_TO_DEGREES;
use crate::math::rotate::euler::EulerAngles;
use crate::math::rotate::euler::RotateOrder;
use crate::math::rotate::quaternion::matrix3_to_quaternion;
use crate::math::rotate::quaternion::quaternion_to_euler;

#[derive(Debug, Copy, Clone)]
pub struct Transform {
    // Scale
    pub sx: Real,
    pub sy: Real,
    pub sz: Real,

    // Scale Pivot
    pub spx: Real,
    pub spy: Real,
    pub spz: Real,

    // Scale Pivot Translation
    pub sptx: Real,
    pub spty: Real,
    pub sptz: Real,

    // Shear
    pub shxy: Real,
    pub shxz: Real,
    pub shyz: Real,

    // Rotate Order
    pub roo: RotateOrder,

    // Rotate
    pub rx: Real,
    pub ry: Real,
    pub rz: Real,

    // Rotate Axis
    pub rax: Real,
    pub ray: Real,
    pub raz: Real,

    // Rotate Pivot
    pub rpx: Real,
    pub rpy: Real,
    pub rpz: Real,

    // Rotate Pivot Translation
    pub rptx: Real,
    pub rpty: Real,
    pub rptz: Real,

    // Translate
    pub tx: Real,
    pub ty: Real,
    pub tz: Real,
}

impl Transform {
    pub fn new() -> Transform {
        Transform {
            sx: 1.0,
            sy: 1.0,
            sz: 1.0,
            spx: 0.0,
            spy: 0.0,
            spz: 0.0,
            sptx: 0.0,
            spty: 0.0,
            sptz: 0.0,
            shxy: 0.0,
            shxz: 0.0,
            shyz: 0.0,
            roo: RotateOrder::XYZ,
            rx: 0.0,
            ry: 0.0,
            rz: 0.0,
            rax: 0.0,
            ray: 0.0,
            raz: 0.0,
            rpx: 0.0,
            rpy: 0.0,
            rpz: 0.0,
            rptx: 0.0,
            rpty: 0.0,
            rptz: 0.0,
            tx: 0.0,
            ty: 0.0,
            tz: 0.0,
        }
    }

    pub fn from_txyz_rxyz_sxyz(
        tx: Real,
        ty: Real,
        tz: Real,
        rx: Real,
        ry: Real,
        rz: Real,
        roo: RotateOrder,
        sx: Real,
        sy: Real,
        sz: Real,
    ) -> Transform {
        Transform {
            sx: sx,
            sy: sy,
            sz: sz,
            spx: 0.0,
            spy: 0.0,
            spz: 0.0,
            sptx: 0.0,
            spty: 0.0,
            sptz: 0.0,
            shxy: 0.0,
            shxz: 0.0,
            shyz: 0.0,
            roo: RotateOrder::XYZ,
            rx: rx,
            ry: ry,
            rz: rz,
            rax: 0.0,
            ray: 0.0,
            raz: 0.0,
            rpx: 0.0,
            rpy: 0.0,
            rpz: 0.0,
            rptx: 0.0,
            rpty: 0.0,
            rptz: 0.0,
            tx: tx,
            ty: ty,
            tz: tz,
        }
    }

    pub fn from_txyz_rxyz(
        tx: Real,
        ty: Real,
        tz: Real,
        rx: Real,
        ry: Real,
        rz: Real,
        roo: RotateOrder,
    ) -> Transform {
        Transform {
            sx: 1.0,
            sy: 1.0,
            sz: 1.0,
            spx: 0.0,
            spy: 0.0,
            spz: 0.0,
            sptx: 0.0,
            spty: 0.0,
            sptz: 0.0,
            shxy: 0.0,
            shxz: 0.0,
            shyz: 0.0,
            roo: roo,
            rx: rx,
            ry: ry,
            rz: rz,
            rax: 0.0,
            ray: 0.0,
            raz: 0.0,
            rpx: 0.0,
            rpy: 0.0,
            rpz: 0.0,
            rptx: 0.0,
            rpty: 0.0,
            rptz: 0.0,
            tx: tx,
            ty: ty,
            tz: tz,
        }
    }

    pub fn from_txyz(tx: Real, ty: Real, tz: Real) -> Transform {
        Transform {
            sx: 1.0,
            sy: 1.0,
            sz: 1.0,
            spx: 0.0,
            spy: 0.0,
            spz: 0.0,
            sptx: 0.0,
            spty: 0.0,
            sptz: 0.0,
            shxy: 0.0,
            shxz: 0.0,
            shyz: 0.0,
            roo: RotateOrder::XYZ,
            rx: 0.0,
            ry: 0.0,
            rz: 0.0,
            rax: 0.0,
            ray: 0.0,
            raz: 0.0,
            rpx: 0.0,
            rpy: 0.0,
            rpz: 0.0,
            rptx: 0.0,
            rpty: 0.0,
            rptz: 0.0,
            tx: tx,
            ty: ty,
            tz: tz,
        }
    }

    pub fn from_rxyz(rx: Real, ry: Real, rz: Real, roo: RotateOrder) -> Transform {
        Transform {
            sx: 1.0,
            sy: 1.0,
            sz: 1.0,
            spx: 0.0,
            spy: 0.0,
            spz: 0.0,
            sptx: 0.0,
            spty: 0.0,
            sptz: 0.0,
            shxy: 0.0,
            shxz: 0.0,
            shyz: 0.0,
            roo: roo,
            rx: rx,
            ry: ry,
            rz: rz,
            rax: 0.0,
            ray: 0.0,
            raz: 0.0,
            rpx: 0.0,
            rpy: 0.0,
            rpz: 0.0,
            rptx: 0.0,
            rpty: 0.0,
            rptz: 0.0,
            tx: 0.0,
            ty: 0.0,
            tz: 0.0,
        }
    }

    pub fn from_sxyz(sx: Real, sy: Real, sz: Real) -> Transform {
        Transform {
            sx: sx,
            sy: sy,
            sz: sz,
            spx: 0.0,
            spy: 0.0,
            spz: 0.0,
            sptx: 0.0,
            spty: 0.0,
            sptz: 0.0,
            shxy: 0.0,
            shxz: 0.0,
            shyz: 0.0,
            roo: RotateOrder::XYZ,
            rx: 0.0,
            ry: 0.0,
            rz: 0.0,
            rax: 0.0,
            ray: 0.0,
            raz: 0.0,
            rpx: 0.0,
            rpy: 0.0,
            rpz: 0.0,
            rptx: 0.0,
            rpty: 0.0,
            rptz: 0.0,
            tx: 0.0,
            ty: 0.0,
            tz: 0.0,
        }
    }

    pub fn from_s(s: Real) -> Transform {
        Transform {
            sx: s,
            sy: s,
            sz: s,
            spx: 0.0,
            spy: 0.0,
            spz: 0.0,
            sptx: 0.0,
            spty: 0.0,
            sptz: 0.0,
            shxy: 0.0,
            shxz: 0.0,
            shyz: 0.0,
            roo: RotateOrder::XYZ,
            rx: 0.0,
            ry: 0.0,
            rz: 0.0,
            rax: 0.0,
            ray: 0.0,
            raz: 0.0,
            rpx: 0.0,
            rpy: 0.0,
            rpz: 0.0,
            rptx: 0.0,
            rpty: 0.0,
            rptz: 0.0,
            tx: 0.0,
            ty: 0.0,
            tz: 0.0,
        }
    }
}

pub fn calculate_matrix_with_values(
    tx: Real,
    ty: Real,
    tz: Real,
    rx: Real,
    ry: Real,
    rz: Real,
    sx: Real,
    sy: Real,
    sz: Real,
    roo: RotateOrder,
) -> Matrix44 {
    // Scale
    let s = na::Matrix4::<Real>::new(
        sx, 0.0, 0.0, 0.0, //
        0.0, sy, 0.0, 0.0, //
        0.0, 0.0, sz, 0.0, //
        0.0, 0.0, 0.0, 1.0, //
    );
    // println!("s {}", s);

    // Rotate
    let (srx, crx) = (rx * DEGREES_TO_RADIANS).sin_cos();
    let (sry, cry) = (ry * DEGREES_TO_RADIANS).sin_cos();
    let (srz, crz) = (rz * DEGREES_TO_RADIANS).sin_cos();
    let rotx = na::Matrix4::<Real>::new(
        1.0, 0.0, 0.0, 0.0, //
        0.0, crx, -srx, 0.0, //
        0.0, srx, crx, 0.0, //
        0.0, 0.0, 0.0, 1.0, //
    );
    let roty = na::Matrix4::<Real>::new(
        cry, 0.0, sry, 0.0, //
        0.0, 1.0, 0.0, 0.0, //
        -sry, 0.0, cry, 0.0, //
        0.0, 0.0, 0.0, 1.0, //
    );
    let rotz = na::Matrix4::<Real>::new(
        crz, -srz, 0.0, 0.0, //
        srz, crz, 0.0, 0.0, //
        0.0, 0.0, 1.0, 0.0, //
        0.0, 0.0, 0.0, 1.0, //
    );

    // Rotate Order
    //
    // Note: rotation order is reversed because nalgebra stores
    // matrixes as column-major.
    let r = match roo {
        RotateOrder::XYZ => rotz * roty * rotx, // XYZ
        RotateOrder::YZX => rotx * rotz * roty, // YZX
        RotateOrder::ZXY => roty * rotx * rotz, // ZXY
        RotateOrder::XZY => roty * rotz * rotx, // XZY
        RotateOrder::YXZ => rotz * rotx * roty, // YXZ
        RotateOrder::ZYX => rotx * roty * rotz, // ZYX
    };
    // println!("r {}", r);

    // Translate
    let t = na::Matrix4::<Real>::new(
        1.0, 0.0, 0.0, tx, //
        0.0, 1.0, 0.0, ty, //
        0.0, 0.0, 1.0, tz, //
        0.0, 0.0, 0.0, 1.0, //
    );
    // println!("t {}", t);

    t * r * s
}

pub fn calculate_matrix(transform: &Transform) -> Matrix44 {
    // Scale
    let sx = transform.sx;
    let sy = transform.sy;
    let sz = transform.sz;
    let s = na::Matrix4::<Real>::new(
        sx, 0.0, 0.0, 0.0, //
        0.0, sy, 0.0, 0.0, //
        0.0, 0.0, sz, 0.0, //
        0.0, 0.0, 0.0, 1.0,
    );

    // Rotate
    //
    // http://www.gregslabaugh.net/publications/euler.pdf
    //
    // TODO: combine all rotation functions into a single 4x4 matrix.
    let rx = transform.rx * DEGREES_TO_RADIANS;
    let ry = transform.ry * DEGREES_TO_RADIANS;
    let rz = transform.rz * DEGREES_TO_RADIANS;
    let sin_rx = rx.sin();
    let sin_ry = ry.sin();
    let sin_rz = rz.sin();
    let cos_rx = rx.cos();
    let cos_ry = ry.cos();
    let cos_rz = rz.cos();
    let rotx = na::Matrix4::<Real>::new(
        1.0, 0.0, 0.0, 0.0, //
        0.0, cos_rx, -sin_rx, 0.0, //
        0.0, sin_rx, cos_rx, 0.0, //
        0.0, 0.0, 0.0, 1.0, //
    );
    let roty = na::Matrix4::<Real>::new(
        cos_ry, 0.0, sin_ry, 0.0, //
        0.0, 1.0, 0.0, 0.0, //
        -sin_ry, 0.0, cos_ry, 0.0, //
        0.0, 0.0, 0.0, 1.0, //
    );
    let rotz = na::Matrix4::<Real>::new(
        cos_rz, -sin_rz, 0.0, 0.0, //
        sin_rz, cos_rz, 0.0, 0.0, //
        0.0, 0.0, 1.0, 0.0, //
        0.0, 0.0, 0.0, 1.0, //
    );

    // Rotate Order (XYZ)
    //
    // Note: rotation order is reversed because nalgebra stores
    // matrixes as column-major.
    let r = match transform.roo {
        RotateOrder::XYZ => rotz * roty * rotx, // XYZ
        RotateOrder::YZX => rotx * rotz * roty, // YZX
        RotateOrder::ZXY => roty * rotx * rotz, // ZXY
        RotateOrder::XZY => roty * rotz * rotx, // XZY
        RotateOrder::YXZ => rotz * rotx * roty, // YXZ
        RotateOrder::ZYX => rotx * roty * rotz, // ZYX
        _ => panic!(
            "Error; Invalid rotate order value: roo={0:?}",
            transform.roo
        ),
    };

    // Translate
    let tx = transform.tx;
    let ty = transform.ty;
    let tz = transform.tz;
    let t = na::Matrix4::<Real>::new(
        1.0, 0.0, 0.0, tx, //
        0.0, 1.0, 0.0, ty, //
        0.0, 0.0, 1.0, tz, //
        0.0, 0.0, 0.0, 1.0, //
    );

    // NOTE: Only Translate, Rotate and Scale is supported
    t * r * s
}

pub fn multiply(tfm_a: &Transform, tfm_b: &Transform) -> Matrix44 {
    println!("Multiply!");
    let mat_a = calculate_matrix(tfm_a);
    let mat_b = calculate_matrix(tfm_b);
    mat_a * mat_b
}

#[inline]
pub fn decompose_matrix(
    matrix: Matrix44,
    rotate_order: RotateOrder,
) -> (Real, Real, Real, Real, Real, Real, Real, Real, Real) {
    // Translation
    let tx = matrix[(0, 3)];
    let ty = matrix[(1, 3)];
    let tz = matrix[(2, 3)];

    // Scale
    let sx_x1 = matrix[(0, 0)];
    let sx_y1 = matrix[(1, 0)];
    let sx_z1 = matrix[(2, 0)];
    let sx = ((sx_x1 * sx_x1) + (sx_y1 * sx_y1) + (sx_z1 * sx_z1)).sqrt();

    let sy_x1 = matrix[(0, 1)];
    let sy_y1 = matrix[(1, 1)];
    let sy_z1 = matrix[(2, 1)];
    let sy = ((sy_x1 * sy_x1) + (sy_y1 * sy_y1) + (sy_z1 * sy_z1)).sqrt();

    let sz_x1 = matrix[(0, 2)];
    let sz_y1 = matrix[(1, 2)];
    let sz_z1 = matrix[(2, 2)];
    let sz = ((sz_x1 * sz_x1) + (sz_y1 * sz_y1) + (sz_z1 * sz_z1)).sqrt();

    // Rotate
    let matrix3 = na::Matrix3::<Real>::new(
        matrix[(0, 0)] / sx,
        matrix[(0, 1)] / sy,
        matrix[(0, 2)] / sz,
        matrix[(1, 0)] / sx,
        matrix[(1, 1)] / sy,
        matrix[(1, 2)] / sz,
        matrix[(2, 0)] / sx,
        matrix[(2, 1)] / sy,
        matrix[(2, 2)] / sz,
    );
    let q = matrix3_to_quaternion(matrix3);
    let angles = quaternion_to_euler(q, rotate_order);
    let rx = angles.x * RADIANS_TO_DEGREES;
    let ry = angles.y * RADIANS_TO_DEGREES;
    let rz = angles.z * RADIANS_TO_DEGREES;

    (tx, ty, tz, rx, ry, rz, sx, sy, sz)
}

#[cfg(test)]
mod tests {
    use super::*;

    const EPSILON: Real = 1.0e-5;

    #[test]
    fn test_decompose_matrix() {
        // Test all the rotation orders.
        for roo_index in 0..6 {
            let tx = 0.0;
            let ty = 42.0;
            let tz = 0.0;
            let rx = 45.0;
            let ry = 15.0;
            let rz = 5.0;
            let sx = 2.0;
            let sy = 3.0;
            let sz = 4.0;
            let roo = RotateOrder::from(roo_index);
            println!("tx: {} ty: {} tz: {}", tx, ty, tz);
            println!("rx: {} ry: {} rz: {}", rx, ry, rz);
            println!("sx: {} sy: {} sz: {}", sx, sy, sz);
            println!("rotate order: {:?}", roo);
            let matrix = calculate_matrix_with_values(tx, ty, tz, rx, ry, rz, sx, sy, sz, roo);
            println!("matrix: {}", matrix);

            let (wtx, wty, wtz, wrx, wry, wrz, wsx, wsy, wsz) = decompose_matrix(matrix, roo);
            println!("wtx: {} wty: {} wtz: {}", wtx, wty, wtz);
            println!("wrx: {} wry: {} wrz: {}", wrx, wry, wrz);
            println!("wsx: {} wsy: {} wsz: {}", wsx, wsy, wsz);
            let new_matrix =
                calculate_matrix_with_values(wtx, wty, wtz, wrx, wry, wrz, wsx, wsy, wsz, roo);
            println!("new_matrix: {}", new_matrix);

            // Translate
            assert_relative_eq!(tx, wtx, epsilon = EPSILON);
            assert_relative_eq!(ty, wty, epsilon = EPSILON);
            assert_relative_eq!(tz, wtz, epsilon = EPSILON);

            // Rotate
            assert_relative_eq!(rx, wrx, epsilon = EPSILON);
            assert_relative_eq!(ry, wry, epsilon = EPSILON);
            assert_relative_eq!(rz, wrz, epsilon = EPSILON);

            // Scale
            assert_relative_eq!(sx, wsx, epsilon = EPSILON);
            assert_relative_eq!(sy, wsy, epsilon = EPSILON);
            assert_relative_eq!(sz, wsz, epsilon = EPSILON);

            // Matrix
            let eq = matrix.relative_eq(&new_matrix, EPSILON, EPSILON);
            assert_eq!(eq, true);
            println!("---------------------------------");
        }
    }
}
