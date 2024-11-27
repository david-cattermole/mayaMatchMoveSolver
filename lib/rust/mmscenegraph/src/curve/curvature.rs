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

use anyhow::bail;
use anyhow::Result;

use crate::constant::Real;

/// Allocate vectors for 1st order derivatives.
pub fn allocate_curvature(num: usize) -> Result<Vec<Real>> {
    let curvature = vec![0.0; num];
    Ok(curvature)
}

/// Compute curvature with protection against numerical
/// instability.
fn curvature(velocity: Real, acceleration: Real) -> Real {
    let denom = (1.0 + velocity * velocity).powf(1.5);
    let curvature = if denom < 1e-10 {
        0.0
    } else {
        acceleration / denom
    };

    curvature
}

pub fn calculate_curvature(
    velocity: &[Real],
    acceleration: &[Real],
    out_curvature: &mut [Real],
) -> Result<()> {
    // Verify slice lengths match
    if velocity.len() != acceleration.len()
        || velocity.len() != out_curvature.len()
    {
        bail!("Input and output slices must have equal length; velocity.len()={} acceleration.len()={} out_curvature.len()={}",
              velocity.len(),
              acceleration.len(),
              out_curvature.len())
    }

    for i in 0..out_curvature.len() {
        out_curvature[i] = curvature(velocity[i], acceleration[i]);
    }

    Ok(())
}
