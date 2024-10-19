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
 * Mathematical functions for vectors, points, lines and matrices.
 */

#ifndef MM_CORE_MM_MATH_H
#define MM_CORE_MM_MATH_H

#include "mmdata.h"

namespace mmmath {

// Return 'min_value' to 'max_value' linearly, for a 'mix' value
// between 0.0 and 1.0.
float lerp(const float min_value, const float max_value, const float mix);
double lerp(const double min_value, const double max_value, const double mix);

// Return a value between 0.0 and 1.0 for a value in an input range
// 'from' to 'to'.
float inverse_lerp(const float from, const float to, const float value);
double inverse_lerp(const double from, const double to, const double value);

// Remap from an 'original' value range to a 'target' value range.
float remap(const float original_from, const float original_to,
            const float target_from, const float target_to, const float value);
double remap(const double original_from, const double original_to,
             const double target_from, const double target_to,
             const double value);

inline float clamp(const float v, const float min, const float max) {
    const float x = v < min ? min : v;
    return x > max ? max : x;
}

// https://martin.ankerl.com/2007/10/04/optimized-pow-approximation-for-java-and-c-c/
inline double fast_pow(const double a, const double b) {
    union {
        double d;
        int x[2];
    } u = {a};
    u.x[1] = static_cast<int>(b * (u.x[1] - 1072632447) + 1072632447);
    u.x[0] = 0;
    return u.d;
}

// https://martin.ankerl.com/2007/10/04/optimized-pow-approximation-for-java-and-c-c/
inline float fast_pow(const float a, const float b) {
    union {
        float f;
        int i;
    } u = {a};
    u.i = static_cast<int>(b * (u.i - 1065307417) + 1065307417);
    return u.f;
}

double length(mmdata::Point2D a);
double length(mmdata::Vector3D a);

// Distance between A and B.
double distance(mmdata::Point2D a, mmdata::Point2D b);
double distance(mmdata::Vector3D a, mmdata::Vector3D b);

mmdata::Point2D normalize(mmdata::Point2D vector);
mmdata::Vector3D normalize(mmdata::Vector3D vector);

// Difference between A and B points.
mmdata::Point2D subtract(mmdata::Point2D a, mmdata::Point2D b);

// Dot product.
double dot(mmdata::Point2D a, mmdata::Point2D b);
double dot(mmdata::Vector3D a, mmdata::Vector3D b);
double dot(mmdata::Matrix4x4 a, mmdata::Matrix4x4 b);

// Cross product.
mmdata::Vector3D cross(mmdata::Vector3D a, mmdata::Vector3D b);

double determinant(mmdata::Matrix4x4 m);

mmdata::Matrix4x4 inverse(mmdata::Matrix4x4 m);

mmdata::Matrix4x4 matrixMultiply(mmdata::Matrix4x4 a, mmdata::Matrix4x4 b);

void transform(mmdata::Matrix4x4 m, mmdata::Point3D point,
               mmdata::Point3D &outPoint);

// The point at which 2 2D lines intersect, assuming the lines continue into
// infinity.
bool infiniteLineIntersection(mmdata::Point2D pointA, mmdata::Point2D pointB,
                              mmdata::Point2D pointC, mmdata::Point2D pointD,
                              mmdata::Point2D &outPoint);

double cosineAngleBetweenLines(mmdata::LinePair2D linePair);

}  // namespace mmmath

#endif  // MM_CORE_MM_MATH_H
