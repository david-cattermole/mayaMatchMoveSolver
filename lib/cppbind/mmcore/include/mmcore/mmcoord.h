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
 * Convert between different coordinate spaces, for points.
 */

#ifndef MM_CORE_MM_COORD_H
#define MM_CORE_MM_COORD_H

// MM Solver Libs
#include <mmsolverlibs/assert.h>

#include "mmdata.h"

namespace mmcoord {

// Defines the different coordinate spaces.
enum class Point2DSpace {
    // Image Normalized space.
    //
    // lower-left:  [-1.0, -1.0 / aspect]
    // upper-right: [1.0, 1.0 / aspect]
    // range x:     [-1.0 to 1.0]
    // range y:     [-1.0 / aspect to 1.0 / aspect]
    //
    // Where: aspect = width / height;
    //
    ImageNormalized,

    // Marker space.
    //
    // lower-left:  [-0.5, -0.5]
    // upper-right: [0.5, 0.5]
    // range x:     [-0.5 to 0.5]
    // range y:     [-0.5 to 0.5]
    //
    Marker,

    // Camera Film Back space (inches).
    //
    // lower-left:  [-width * 0.5, -height * 0.5]
    // upper-right: [width * 0.5, height * 0.5]
    // range x:     [-width * 0.5 to width * 0.5]
    // range y:     [-height * 0.5 to height * 0.5]
    //
    // Where: width is the camera film back width in inches, and
    // height is the camera film back height in inches.
    //
    CameraFilmBackInches,
};

mmdata::Point2D convertCoordPointMarkerToImageNormalized(mmdata::Point2D point,
                                                         double width,
                                                         double height);

mmdata::Point2D convertPoint2DImageNormalizedToMarker(mmdata::Point2D point,
                                                      double width,
                                                      double height);

mmdata::Point2D convertCoordPointMarkerToCameraFilmBackInches(
    mmdata::Point2D point, double width_inches, double height_inches);

inline mmdata::Point2D convertPoint2D(const Point2DSpace from,
                                      const Point2DSpace to,
                                      mmdata::Point2D point, double width = 100,
                                      double height = 100) {
    auto result = mmdata::Point2D();

    switch (from) {
        case Point2DSpace::Marker:
            switch (to) {
                case Point2DSpace::ImageNormalized: {
                    result = convertCoordPointMarkerToImageNormalized(
                        point, width, height);
                    break;
                }
                case Point2DSpace::CameraFilmBackInches: {
                    result = convertCoordPointMarkerToCameraFilmBackInches(
                        point, width, height);
                    break;
                }
                default: {
                    MMSOLVER_CORE_PANIC(
                        "Point2DSpace enum value combination is not valid.");
                }
            }
        case Point2DSpace::ImageNormalized:
            switch (to) {
                case Point2DSpace::Marker: {
                    result = convertPoint2DImageNormalizedToMarker(point, width,
                                                                   height);
                    break;
                }
                default: {
                    MMSOLVER_CORE_PANIC(
                        "Point2DSpace enum value combination is not valid.");
                }
            }
        default: {
            MMSOLVER_CORE_PANIC(
                "Point2DSpace enum value combination is not valid.");
        }
    }

    return result;
}

}  // namespace mmcoord

#endif  // MM_CORE_MM_COORD_H
