//
// Copyright (C) 2024 David Cattermole.
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

mod common;

use anyhow::Result;
use approx::assert_relative_eq;

use mmscenegraph_rust::math::curve_analysis::calculate_derivatives;

fn print_arrays(velocity: &[f64], acceleration: &[f64], jerk: &[f64]) {
    println!("Found {} velocity:", velocity.len());
    for (i, v) in velocity.iter().enumerate() {
        println!("i={i} v={v}");
    }

    println!("Found {} acceleration:", acceleration.len());
    for (i, v) in acceleration.iter().enumerate() {
        println!("i={i} v={v}");
    }

    println!("Found {} jerk:", jerk.len());
    for (i, v) in jerk.iter().enumerate() {
        println!("i={i} v={v}");
    }
}

#[test]
fn calculate_derivatives1() -> Result<()> {
    // Constant speed, upwards.
    let times = vec![0.0, 1.0, 2.0, 3.0, 4.0, 5.0];
    let heights = vec![1.0, 1.1, 1.2, 1.3, 1.4, 1.5];

    let (velocity, acceleration, jerk) =
        calculate_derivatives(&times, &heights)?;

    print_arrays(&velocity, &acceleration, &jerk);

    assert_eq!(velocity.len(), 6);
    assert_eq!(acceleration.len(), 6);
    assert_eq!(jerk.len(), 6);

    assert_relative_eq!(velocity[0], 0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[1], 0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[2], 0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[3], 0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[4], 0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[5], 0.1, epsilon = 1.0e-9);

    assert_relative_eq!(acceleration[0], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[1], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[2], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[3], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[4], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[5], 0.0, epsilon = 1.0e-9);

    assert_relative_eq!(jerk[0], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[1], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[2], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[3], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[4], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[5], 0.0, epsilon = 1.0e-9);

    Ok(())
}

#[test]
fn calculate_derivatives2() -> Result<()> {
    // Constant velocity, downwards.
    let times = vec![0.0, 1.0, 2.0, 3.0, 4.0, 5.0];
    let heights = vec![-1.0, -1.1, -1.2, -1.3, -1.4, -1.5];

    let (velocity, acceleration, jerk) =
        calculate_derivatives(&times, &heights)?;

    print_arrays(&velocity, &acceleration, &jerk);

    assert_eq!(velocity.len(), 6);
    assert_eq!(acceleration.len(), 6);
    assert_eq!(jerk.len(), 6);

    assert_relative_eq!(velocity[0], -0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[1], -0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[2], -0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[3], -0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[4], -0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[5], -0.1, epsilon = 1.0e-9);

    assert_relative_eq!(acceleration[0], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[1], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[2], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[3], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[4], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[5], 0.0, epsilon = 1.0e-9);

    assert_relative_eq!(jerk[0], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[1], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[2], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[3], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[4], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[5], 0.0, epsilon = 1.0e-9);

    Ok(())
}

#[test]
fn calculate_derivatives3() -> Result<()> {
    // Variable velocity.
    let times = vec![0.0, 1.0, 2.0, 3.0, 4.0, 5.0];
    let heights = vec![1.0, 1.1, 1.25, 1.5, 2.0, 4.0];

    let (velocity, acceleration, jerk) =
        calculate_derivatives(&times, &heights)?;

    print_arrays(&velocity, &acceleration, &jerk);

    assert_eq!(velocity.len(), 6);
    assert_eq!(acceleration.len(), 6);
    assert_eq!(jerk.len(), 6);

    assert_relative_eq!(velocity[0], 0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[1], 0.125, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[2], 0.2, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[3], 0.375, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[4], 1.25, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[5], 2.0, epsilon = 1.0e-9);

    Ok(())
}

#[test]
fn calculate_derivatives4() -> Result<()> {
    let times = vec![0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0];
    let heights = vec![0.0, 1.0, 4.0, 9.0, 16.0, 25.0, 36.0]; // f(x) = x^2

    let (velocity, acceleration, jerk) =
        calculate_derivatives(&times, &heights)?;

    print_arrays(&velocity, &acceleration, &jerk);

    assert_eq!(velocity.len(), 7);
    assert_eq!(acceleration.len(), 7);
    assert_eq!(jerk.len(), 7);

    // Expected derivatives of x^2;
    assert_relative_eq!(velocity[0], 1.0, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[1], 2.0, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[2], 4.0, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[3], 6.0, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[4], 8.0, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[5], 10.0, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[6], 11.0, epsilon = 1.0e-9);

    assert_relative_eq!(acceleration[0], 1.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[1], 1.5, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[2], 2.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[3], 2.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[4], 2.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[5], 1.5, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[6], 1.0, epsilon = 1.0e-9);

    assert_relative_eq!(jerk[0], 0.5, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[1], 0.5, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[2], 0.25, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[3], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[4], -0.25, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[5], -0.5, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[6], -0.5, epsilon = 1.0e-9);

    Ok(())
}
