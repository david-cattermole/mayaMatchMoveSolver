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
 *
 * This module provides basic mathematical operations for working with
 * 2D/3D vectors, points, lines and 4x4 matrices.
 */

#ifndef MM_CORE_MM_MATH_H
#define MM_CORE_MM_MATH_H

#include "mmdata.h"

namespace mmmath {

/**
 * Linear interpolation between two values.
 *
 * @param min_value The start value when mix=0.0
 * @param max_value The end value when mix=1.0
 * @param mix Interpolation factor between 0.0 and 1.0
 * @return Interpolated value
 */
float lerp(const float min_value, const float max_value, const float mix);
double lerp(const double min_value, const double max_value, const double mix);

/**
 * Inverse linear interpolation - returns where a value falls between two
 * bounds.
 *
 * @param from Lower bound value
 * @param to Upper bound value
 * @param value Input value to map
 * @return Factor between 0.0 and 1.0 representing position between bounds
 */
float inverse_lerp(const float from, const float to, const float value);
double inverse_lerp(const double from, const double to, const double value);

/**
 * Remaps a value from one range to another using linear
 * interpolation.
 *
 * @param original_from Original range start
 * @param original_to Original range end
 * @param target_from Target range start
 * @param target_to Target range end
 * @param value Value to remap
 * @return Remapped value in target range
 */
float remap(const float original_from, const float original_to,
            const float target_from, const float target_to, const float value);
double remap(const double original_from, const double original_to,
             const double target_from, const double target_to,
             const double value);

/**
 * Clamps a value between minimum and maximum bounds.
 *
 * @param v Value to clamp
 * @param min Minimum allowed value
 * @param max Maximum allowed value
 * @return Clamped value
 */
inline float clamp(const float v, const float min, const float max) {
    const float x = v < min ? min : v;
    return x > max ? max : x;
}

/**
 * Fast approximation of pow() function.
 * Less accurate but much faster than std::pow().
 *
 * https://martin.ankerl.com/2007/10/04/optimized-pow-approximation-for-java-and-c-c/
 *
 * @param a Base value
 * @param b Exponent value
 * @return Approximated power result
 */
inline double fast_pow(const double a, const double b) {
    union {
        double d;
        int x[2];
    } u = {a};
    u.x[1] = static_cast<int>(b * (u.x[1] - 1072632447) + 1072632447);
    u.x[0] = 0;
    return u.d;
}

inline float fast_pow(const float a, const float b) {
    union {
        float f;
        int i;
    } u = {a};
    u.i = static_cast<int>(b * (u.i - 1065307417) + 1065307417);
    return u.f;
}

/**
 * Calculate length/magnitude of a 2D point vector.
 *
 * @param a Input point
 * @return Length of vector from origin to point
 */
double length(mmdata::Point2D a);
double length(mmdata::Vector3D a);

/**
 * Calculate Euclidean distance between two 2D points.
 *
 * @param a First point
 * @param b Second point
 * @return Distance between points
 */
double distance(mmdata::Point2D a, mmdata::Point2D b);
double distance(mmdata::Vector3D a, mmdata::Vector3D b);

/**
 * Normalize a 2D point vector to unit length.
 *
 * Returns zero vector if input has zero length.
 *
 * @param vector Input vector to normalize
 * @return Normalized vector with length 1.0
 */
mmdata::Point2D normalize(mmdata::Point2D vector);
mmdata::Vector3D normalize(mmdata::Vector3D vector);

// Difference between A and B points.
mmdata::Point2D subtract(mmdata::Point2D a, mmdata::Point2D b);

/**
 * Calculate dot product between two 2D points as vectors.
 *
 * @param a First point vector
 * @param b Second point vector
 * @return Dot product result
 */
double dot(mmdata::Point2D a, mmdata::Point2D b);
double dot(mmdata::Vector3D a, mmdata::Vector3D b);
double dot(mmdata::Matrix4x4 a, mmdata::Matrix4x4 b);

/**
 * Calculate cross product between two 3D vectors.
 *
 * Result is perpendicular to input vectors.
 *
 * @param a First vector
 * @param b Second vector
 * @return Cross product vector
 */
mmdata::Vector3D cross(mmdata::Vector3D a, mmdata::Vector3D b);

/**
 * Calculate determinant of 4x4 matrix.
 *
 * @param m Input matrix
 * @return Determinant value
 */
double determinant(mmdata::Matrix4x4 m);

/**
 * Calculate inverse of 4x4 matrix. Assumes matrix is invertible.
 *
 * @param m Input matrix to invert
 * @return Inverse matrix
 */
mmdata::Matrix4x4 inverse(mmdata::Matrix4x4 m);

/**
 * Multiply two 4x4 matrices.
 *
 * Result is equivalent to applying transformations in right-to-left
 * order.
 *
 * @param a First matrix
 * @param b Second matrix
 * @return Result of a * b
 */
mmdata::Matrix4x4 matrixMultiply(mmdata::Matrix4x4 a, mmdata::Matrix4x4 b);

/**
 * Transform a 3D point by a 4x4 matrix.
 *
 * @param m Transform matrix
 * @param point Input point
 * @param outPoint Transformed point result
 */
void transform(mmdata::Matrix4x4 m, mmdata::Point3D point,
               mmdata::Point3D &outPoint);

/**
 * Find intersection point of two infinite 2D lines.
 *
 * The point at which 2 2D lines intersect, assuming the lines
 * continue into infinity.
 *
 * @param pointA First point on line 1
 * @param pointB Second point on line 1
 * @param pointC First point on line 2
 * @param pointD Second point on line 2
 * @param outPoint Intersection point result
 * @return true if lines intersect, false if parallel or coincident
 */
bool infiniteLineIntersection(mmdata::Point2D pointA, mmdata::Point2D pointB,
                              mmdata::Point2D pointC, mmdata::Point2D pointD,
                              mmdata::Point2D &outPoint);

/**
 * Calculate cosine of angle between two 2D lines.
 *
 * Result near 1.0 indicates nearly parallel lines.
 *
 * @param linePair Pair of lines to compare
 * @return Cosine of angle between lines
 */
double cosineAngleBetweenLines(mmdata::LinePair2D linePair);

/**
 * Create look-at matrix from direction vector.
 *
 * Result aligns Z axis with direction and maintains Y axis up where
 * possible.
 *
 * @param dir Direction vector to look at
 * @param out_matrix Resulting orientation matrix
 */
void createLookAtMatrix(const mmdata::Vector3D &dir,
                        mmdata::Matrix4x4 &out_matrix);

}  // namespace mmmath

#endif  // MM_CORE_MM_MATH_H
