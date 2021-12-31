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

use mmscenegraph_rust::constant::Matrix44;
use mmscenegraph_rust::constant::Real;
use mmscenegraph_rust::constant::DEGREES_TO_RADIANS;
use mmscenegraph_rust::constant::RADIANS_TO_DEGREES;
use mmscenegraph_rust::math::rotate::euler::euler_to_matrix4;
use mmscenegraph_rust::math::rotate::euler::EulerAngles;
use mmscenegraph_rust::math::rotate::euler::RotateOrder;
use mmscenegraph_rust::math::rotate::quaternion::matrix4_to_quaternion;
use mmscenegraph_rust::math::rotate::quaternion::quaternion_to_euler;

fn main() {
    /* Matrix for reference.
     *
     * RX = 45.0
     * RY = 15.0
     * RZ = 5.0
     * Rotation Order = XYZ = 0
     */
    let example = Matrix44::new(
        0.96225, 0.084186, -0.258819, 0.0, //
        0.120688, 0.720367, 0.683013, 0.0, //
        0.243945, -0.688465, 0.683013, 0.0, //
        0.0, 0.0, 0.0, 1.0, //
    );

    // Create Matrix
    let mut min_index = 0;
    let mut min_sum = 99999.0;
    for i in 0..24 {
        let in_angles = EulerAngles {
            x: 45.2277951 * DEGREES_TO_RADIANS,  // X
            y: 14.11947737 * DEGREES_TO_RADIANS, // Y
            z: -7.14885265 * DEGREES_TO_RADIANS, // Z
            w: i as Real,
        }; // ZYX == 21

        println!(
            "order: {} X: {} Y: {} Z: {}",
            in_angles.w,
            in_angles.x * RADIANS_TO_DEGREES,
            in_angles.y * RADIANS_TO_DEGREES,
            in_angles.z * RADIANS_TO_DEGREES
        );

        println!("Matrix: {}", in_angles.w);

        // 0 = XYZ
        // 21 = ZYX
        let final_matrix = euler_to_matrix4(in_angles);

        let q = matrix4_to_quaternion(final_matrix);
        println!("Quart X: {0} Y: {1} Z: {2} W: {3}", q[0], q[1], q[2], q[3]);
        let order = RotateOrder::YZX;
        let quat_angles = quaternion_to_euler(q, order);
        println!(
            "Angles X: {} Y: {} Z: {} W: {}\n",
            quat_angles.x * RADIANS_TO_DEGREES,
            quat_angles.y * RADIANS_TO_DEGREES,
            quat_angles.z * RADIANS_TO_DEGREES,
            quat_angles.w * RADIANS_TO_DEGREES,
        );

        println!("final_matrix:");
        for j in 0..4 {
            println!(
                "{} {} {} {}",
                final_matrix[(j, 0)],
                final_matrix[(j, 1)],
                final_matrix[(j, 2)],
                final_matrix[(j, 3)]
            );
        }
        println!("");

        // println!("example matrix:");
        // for j in 0..4 {
        //     println!(
        //         "{} {} {} {}",
        //         example[(j, 0)],
        //         example[(j, 1)],
        //         example[(j, 2)],
        //         example[(j, 3)]
        //     );
        // }
        // println!("");

        // println!("Compare final_matrix - example matrix:");
        let mut sum: Real = 0.0;
        for j in 0..4 {
            sum += (final_matrix[(j, 0)].abs() - example[(j, 0)].abs()).abs();
            sum += (final_matrix[(j, 1)].abs() - example[(j, 1)].abs()).abs();
            sum += (final_matrix[(j, 2)].abs() - example[(j, 2)].abs()).abs();
            sum += (final_matrix[(j, 3)].abs() - example[(j, 3)].abs()).abs();
            println!(
                "{} {} {} {}",
                (final_matrix[(j, 0)].abs() - example[(j, 0)].abs()).abs(),
                (final_matrix[(j, 1)].abs() - example[(j, 1)].abs()).abs(),
                (final_matrix[(j, 2)].abs() - example[(j, 2)].abs()).abs(),
                (final_matrix[(j, 3)].abs() - example[(j, 3)].abs()).abs(),
            );
        }
        sum = sum.abs();
        println!("compare: {}", sum);
        if sum < min_sum {
            min_sum = sum;
            min_index = i;
        }

        println!("");
    }

    println!("min sum: value={} index={}", min_sum, min_index);
}
