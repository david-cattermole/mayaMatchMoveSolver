/*
 * Copyright (C) 2021 David Cattermole.
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
 */

#include <mmcore/mmcoord.h>

// STL
#include <cmath>

// MM Core
#include <mmcore/mmdata.h>

namespace mmcoord {

mmdata::Point2D convertCoordPointMarkerToImageNormalized(mmdata::Point2D point,
                                                         double width,
                                                         double height) {
    // Get the reciprocal of the aspect ratio ("aspect = width /
    // height") to avoid needing to perform another divide.
    auto aspect = height / width;
    return mmdata::Point2D(point.x_ * 2.0, point.y_ * 2.0 * aspect);
}

mmdata::Point2D convertPoint2DImageNormalizedToMarker(mmdata::Point2D point,
                                                      double width,
                                                      double height) {
    // Get the aspect ratio ("aspect = width / height") to avoid
    // needing to perform another divide.
    auto aspect = width / height;
    return mmdata::Point2D(0.5 * point.x_, 0.5 * (point.y_ * aspect));
}

mmdata::Point2D convertCoordPointMarkerToCameraFilmBackInches(
    mmdata::Point2D point, double width_inches, double height_inches) {
    return mmdata::Point2D(point.x_ * width_inches, point.y_ * height_inches);
}

}  // namespace mmcoord
