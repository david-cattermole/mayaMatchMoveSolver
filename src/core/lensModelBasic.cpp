/*
 * Copyright (C) 2020 David Cattermole.
 *
 * This file is part of mmSolver.
 *
 * mmSolver is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * mmSolver is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
 * ====================================================================
 *
 * Fanctor class for the basic brownian lens distortion model.
 */


// STL
#include <cmath>

// Utils
#include <utilities/debugUtils.h>

#include <core/lensModelBasic.h>

void LensModelBasic::applyModel(double x,
                                double y,
                                double &out_x,
                                double &out_y) const {
    // TODO: Add Brownian lens distortion model here.
    //
    // xu = xd + ((xd - dc) * ((k1 * r2) + (k2 * r4)));
    //
    // where:
    //   xu = undistorted image point
    //   xd = distorted image point
    //   xc = distortion center
    //   k1, k2, etc = Nth radial distortion coefficent
    //   p1, p2, etc = Nth tangential distortion coefficent
    //   r = sqrt(pow(xd - xc, 2) + pow(yd - yc, 2))
    //
    out_x = x + 0.1;
    out_y = y + 0.1;
    return;
}
