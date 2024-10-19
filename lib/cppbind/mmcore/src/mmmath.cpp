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
 * The mathematical functions are unrolled (for speed), and are
 * generally hoped to be inlined by the compiler. The functions are
 * also overloaded and will work with different arguments.
 *
 * See https://www.euclideanspace.com/ as reference for these
 * functions.
 *
 * For conventions we follow the standards here:
 * https://www.euclideanspace.com/maths/standards/index.htm
 */

#include <mmcore/mmmath.h>

// STL
#include <cmath>
#include <cstdint>
#include <cstdlib>

// MM Core
#include <mmcore/mmdata.h>

namespace mmmath {

// Return 'min_value' to 'max_value' linearly, for a 'mix' value
// between 0.0 and 1.0.
float lerp(const float min_value, const float max_value, const float mix) {
    return ((1 - mix) * min_value) + (mix * max_value);
}

double lerp(const double min_value, const double max_value, const double mix) {
    return ((1 - mix) * min_value) + (mix * max_value);
}

// Return a value between 0.0 and 1.0 for a value in an input range
// 'from' to 'to'.
float inverse_lerp(const float from, const float to, const float value) {
    return (value - from) / (to - from);
}

double inverse_lerp(const double from, const double to, const double value) {
    return (value - from) / (to - from);
}

// Remap from an 'original' value range to a 'target' value range.
float remap(const float original_from, const float original_to,
            const float target_from, const float target_to, const float value) {
    float map_to_original_range =
        inverse_lerp(original_from, original_to, value);
    return lerp(target_from, target_to, map_to_original_range);
}

double remap(const double original_from, const double original_to,
             const double target_from, const double target_to,
             const double value) {
    double map_to_original_range =
        inverse_lerp(original_from, original_to, value);
    return lerp(target_from, target_to, map_to_original_range);
}

double length(mmdata::Point2D a) {
    return std::sqrt(a.x_ * a.x_ + a.y_ * a.y_);
}

double length(mmdata::Vector3D a) {
    return std::sqrt(a.x_ * a.x_ + a.y_ * a.y_ + a.z_ * a.z_);
}

double distance(mmdata::Point2D a, mmdata::Point2D b) {
    auto dx = a.x_ - b.x_;
    auto dy = a.y_ - b.y_;
    return std::sqrt(dx * dx + dy * dy);
}

double distance(mmdata::Vector3D a, mmdata::Vector3D b) {
    auto dx = a.x_ - b.x_;
    auto dy = a.y_ - b.y_;
    auto dz = a.z_ - b.z_;
    return std::sqrt(dx * dx + dy * dy + dz * dz);
}

// https://www.euclideanspace.com/maths/vectors/normals/index.htm
mmdata::Point2D normalize(mmdata::Point2D vector) {
    auto mag = mmmath::length(vector);
    // Avoid dividing by zero.
    if (mag == 0.0) {
        return mmdata::Point2D(0.0, 0.0);
    }
    return mmdata::Point2D(vector.x_ / mag, vector.y_ / mag);
}

// https://www.euclideanspace.com/maths/vectors/normals/index.htm
mmdata::Vector3D normalize(mmdata::Vector3D vector) {
    auto mag = mmmath::length(vector);
    // Avoid dividing by zero.
    if (mag == 0.0) {
        return mmdata::Vector3D(0.0, 0.0, 0.0);
    }
    return mmdata::Vector3D(vector.x_ / mag, vector.y_ / mag, vector.z_ / mag);
}

mmdata::Point2D subtract(mmdata::Point2D a, mmdata::Point2D b) {
    return mmdata::Point2D(a.x_ - b.x_, a.y_ - b.y_);
}

double dot(mmdata::Point2D a, mmdata::Point2D b) {
    return a.x_ * b.x_ + a.y_ * b.y_;
}

double dot(mmdata::Vector3D a, mmdata::Vector3D b) {
    return a.x_ * b.x_ + a.y_ * b.y_ + a.z_ * b.z_;
}

double dot(mmdata::Matrix4x4 a, mmdata::Matrix4x4 b) {
    double r = 0.0;

    r += a.m00_ * b.m00_;
    r += a.m01_ * b.m01_;
    r += a.m02_ * b.m02_;
    r += a.m03_ * b.m03_;

    r += a.m10_ * b.m10_;
    r += a.m11_ * b.m11_;
    r += a.m12_ * b.m12_;
    r += a.m13_ * b.m13_;

    r += a.m20_ * b.m20_;
    r += a.m21_ * b.m21_;
    r += a.m22_ * b.m22_;
    r += a.m23_ * b.m23_;

    r += a.m30_ * b.m30_;
    r += a.m31_ * b.m31_;
    r += a.m32_ * b.m32_;
    r += a.m33_ * b.m33_;

    return r;
}

mmdata::Vector3D cross(mmdata::Vector3D a, mmdata::Vector3D b) {
    return mmdata::Vector3D(a.y_ * b.z_ - a.z_ * b.y_,
                            a.z_ * b.x_ - a.x_ * b.z_,
                            a.x_ * b.y_ - a.y_ * b.x_);
}

// http://www.euclideanspace.com/maths/algebra/matrix/functions/determinant/fourD/index.htm
double determinant(mmdata::Matrix4x4 m) {
    auto m00 = m.m00_;
    auto m01 = m.m01_;
    auto m02 = m.m02_;
    auto m03 = m.m03_;

    auto m10 = m.m10_;
    auto m11 = m.m11_;
    auto m12 = m.m12_;
    auto m13 = m.m13_;

    auto m20 = m.m20_;
    auto m21 = m.m21_;
    auto m22 = m.m22_;
    auto m23 = m.m23_;

    auto m30 = m.m30_;
    auto m31 = m.m31_;
    auto m32 = m.m32_;
    auto m33 = m.m33_;

    auto r0 = m03 * m12 * m21 * m30 - m02 * m13 * m21 * m30 -
              m03 * m11 * m22 * m30 + m01 * m13 * m22 * m30;
    auto r1 = m02 * m11 * m23 * m30 - m01 * m12 * m23 * m30 -
              m03 * m12 * m20 * m31 + m02 * m13 * m20 * m31;
    auto r2 = m03 * m10 * m22 * m31 - m00 * m13 * m22 * m31 -
              m02 * m10 * m23 * m31 + m00 * m12 * m23 * m31;
    auto r3 = m03 * m11 * m20 * m32 - m01 * m13 * m20 * m32 -
              m03 * m10 * m21 * m32 + m00 * m13 * m21 * m32;
    auto r4 = m01 * m10 * m23 * m32 - m00 * m11 * m23 * m32 -
              m02 * m11 * m20 * m33 + m01 * m12 * m20 * m33;
    auto r5 = m02 * m10 * m21 * m33 - m00 * m12 * m21 * m33 -
              m01 * m10 * m22 * m33 + m00 * m11 * m22 * m33;
    return r0 + r1 + r2 + r3 + r4 + r5;
}

// http://www.euclideanspace.com/maths/algebra/matrix/functions/inverse/fourD/index.htm
mmdata::Matrix4x4 inverse(mmdata::Matrix4x4 m) {
    auto s = 1.0 / determinant(m);

    auto m00 = m.m00_;
    auto m01 = m.m01_;
    auto m02 = m.m02_;
    auto m03 = m.m03_;

    auto m10 = m.m10_;
    auto m11 = m.m11_;
    auto m12 = m.m12_;
    auto m13 = m.m13_;

    auto m20 = m.m20_;
    auto m21 = m.m21_;
    auto m22 = m.m22_;
    auto m23 = m.m23_;

    auto m30 = m.m30_;
    auto m31 = m.m31_;
    auto m32 = m.m32_;
    auto m33 = m.m33_;

    auto r = mmdata::Matrix4x4();
    r.m00_ = m12 * m23 * m31 - m13 * m22 * m31 + m13 * m21 * m32 -
             m11 * m23 * m32 - m12 * m21 * m33 + m11 * m22 * m33;
    r.m01_ = m03 * m22 * m31 - m02 * m23 * m31 - m03 * m21 * m32 +
             m01 * m23 * m32 + m02 * m21 * m33 - m01 * m22 * m33;
    r.m02_ = m02 * m13 * m31 - m03 * m12 * m31 + m03 * m11 * m32 -
             m01 * m13 * m32 - m02 * m11 * m33 + m01 * m12 * m33;
    r.m03_ = m03 * m12 * m21 - m02 * m13 * m21 - m03 * m11 * m22 +
             m01 * m13 * m22 + m02 * m11 * m23 - m01 * m12 * m23;
    r.m10_ = m13 * m22 * m30 - m12 * m23 * m30 - m13 * m20 * m32 +
             m10 * m23 * m32 + m12 * m20 * m33 - m10 * m22 * m33;
    r.m11_ = m02 * m23 * m30 - m03 * m22 * m30 + m03 * m20 * m32 -
             m00 * m23 * m32 - m02 * m20 * m33 + m00 * m22 * m33;
    r.m12_ = m03 * m12 * m30 - m02 * m13 * m30 - m03 * m10 * m32 +
             m00 * m13 * m32 + m02 * m10 * m33 - m00 * m12 * m33;
    r.m13_ = m02 * m13 * m20 - m03 * m12 * m20 + m03 * m10 * m22 -
             m00 * m13 * m22 - m02 * m10 * m23 + m00 * m12 * m23;
    r.m20_ = m11 * m23 * m30 - m13 * m21 * m30 + m13 * m20 * m31 -
             m10 * m23 * m31 - m11 * m20 * m33 + m10 * m21 * m33;
    r.m21_ = m03 * m21 * m30 - m01 * m23 * m30 - m03 * m20 * m31 +
             m00 * m23 * m31 + m01 * m20 * m33 - m00 * m21 * m33;
    r.m22_ = m01 * m13 * m30 - m03 * m11 * m30 + m03 * m10 * m31 -
             m00 * m13 * m31 - m01 * m10 * m33 + m00 * m11 * m33;
    r.m23_ = m03 * m11 * m20 - m01 * m13 * m20 - m03 * m10 * m21 +
             m00 * m13 * m21 + m01 * m10 * m23 - m00 * m11 * m23;
    r.m30_ = m12 * m21 * m30 - m11 * m22 * m30 - m12 * m20 * m31 +
             m10 * m22 * m31 + m11 * m20 * m32 - m10 * m21 * m32;
    r.m31_ = m01 * m22 * m30 - m02 * m21 * m30 + m02 * m20 * m31 -
             m00 * m22 * m31 - m01 * m20 * m32 + m00 * m21 * m32;
    r.m32_ = m02 * m11 * m30 - m01 * m12 * m30 - m02 * m10 * m31 +
             m00 * m12 * m31 + m01 * m10 * m32 - m00 * m11 * m32;
    r.m33_ = m01 * m12 * m20 - m02 * m11 * m20 + m02 * m10 * m21 -
             m00 * m12 * m21 - m01 * m10 * m22 + m00 * m11 * m22;

    r.m00_ *= s;
    r.m01_ *= s;
    r.m02_ *= s;
    r.m03_ *= s;
    r.m10_ *= s;
    r.m11_ *= s;
    r.m12_ *= s;
    r.m13_ *= s;
    r.m20_ *= s;
    r.m21_ *= s;
    r.m22_ *= s;
    r.m23_ *= s;
    r.m30_ *= s;
    r.m31_ *= s;
    r.m32_ *= s;
    r.m33_ *= s;
    return r;
}

// Matrix multiplication: Matrix4x4 X Matrix4x4
//
// https://www.euclideanspace.com/maths/algebra/matrix/arithmetic/fourD/index.htm
//
// The implementation is long, because it has all loops unrolled.
mmdata::Matrix4x4 matrixMultiply(mmdata::Matrix4x4 a, mmdata::Matrix4x4 b) {
    auto r = mmdata::Matrix4x4();

    // Column 0, Row 0
    r.m00_ = 0.0;
    r.m00_ += a.m00_ * b.m00_;
    r.m00_ += a.m10_ * b.m01_;
    r.m00_ += a.m20_ * b.m02_;
    r.m00_ += a.m30_ * b.m03_;

    // Column 1, Row 0
    r.m01_ = 0.0;
    r.m01_ += a.m01_ * b.m00_;
    r.m01_ += a.m11_ * b.m01_;
    r.m01_ += a.m21_ * b.m02_;
    r.m01_ += a.m31_ * b.m03_;

    // Column 2, Row 0
    r.m02_ = 0.0;
    r.m02_ += a.m02_ * b.m00_;
    r.m02_ += a.m12_ * b.m01_;
    r.m02_ += a.m22_ * b.m02_;
    r.m02_ += a.m32_ * b.m03_;

    // Column 3, Row 0
    r.m03_ = 0.0;
    r.m03_ += a.m03_ * b.m10_;
    r.m03_ += a.m13_ * b.m11_;
    r.m03_ += a.m23_ * b.m12_;
    r.m03_ += a.m33_ * b.m13_;
    ////////////////////////////////

    // Column 0, Row 1
    r.m10_ = 0.0;
    r.m10_ += a.m00_ * b.m10_;
    r.m10_ += a.m10_ * b.m11_;
    r.m10_ += a.m20_ * b.m12_;
    r.m10_ += a.m30_ * b.m13_;

    // Column 1, Row 1
    r.m11_ = 0.0;
    r.m11_ += a.m01_ * b.m10_;
    r.m11_ += a.m11_ * b.m11_;
    r.m11_ += a.m21_ * b.m12_;
    r.m11_ += a.m31_ * b.m13_;

    // Column 2, Row 1
    r.m12_ = 0.0;
    r.m12_ += a.m02_ * b.m10_;
    r.m12_ += a.m12_ * b.m11_;
    r.m12_ += a.m22_ * b.m12_;
    r.m12_ += a.m32_ * b.m13_;

    // Column 3, Row 1
    r.m13_ = 0.0;
    r.m13_ += a.m03_ * b.m10_;
    r.m13_ += a.m13_ * b.m11_;
    r.m13_ += a.m23_ * b.m12_;
    r.m13_ += a.m33_ * b.m13_;
    ////////////////////////////////

    // Column 0, Row 2
    r.m20_ = 0.0;
    r.m20_ += a.m00_ * b.m20_;
    r.m20_ += a.m10_ * b.m21_;
    r.m20_ += a.m20_ * b.m22_;
    r.m20_ += a.m30_ * b.m23_;

    // Column 1, Row 2
    r.m21_ = 0.0;
    r.m21_ += a.m01_ * b.m20_;
    r.m21_ += a.m11_ * b.m21_;
    r.m21_ += a.m21_ * b.m22_;
    r.m21_ += a.m31_ * b.m23_;

    // Column 2, Row 2
    r.m22_ = 0.0;
    r.m22_ += a.m02_ * b.m20_;
    r.m22_ += a.m12_ * b.m21_;
    r.m22_ += a.m22_ * b.m22_;
    r.m22_ += a.m32_ * b.m23_;

    // Column 3, Row 2
    r.m23_ = 0.0;
    r.m23_ += a.m03_ * b.m20_;
    r.m23_ += a.m13_ * b.m21_;
    r.m23_ += a.m23_ * b.m22_;
    r.m23_ += a.m33_ * b.m23_;
    ////////////////////////////////

    // Column 0, Row 3
    r.m30_ = 0.0;
    r.m30_ += a.m00_ * b.m30_;
    r.m30_ += a.m10_ * b.m31_;
    r.m30_ += a.m20_ * b.m32_;
    r.m30_ += a.m30_ * b.m33_;

    // Column 1, Row 3
    r.m31_ = 0.0;
    r.m31_ += a.m01_ * b.m30_;
    r.m31_ += a.m11_ * b.m31_;
    r.m31_ += a.m21_ * b.m32_;
    r.m31_ += a.m31_ * b.m33_;

    // Column 2, Row 3
    r.m32_ = 0.0;
    r.m32_ += a.m02_ * b.m30_;
    r.m32_ += a.m12_ * b.m31_;
    r.m32_ += a.m22_ * b.m32_;
    r.m32_ += a.m32_ * b.m33_;

    // Column 3, Row 3
    r.m33_ = 0.0;
    r.m33_ += a.m03_ * b.m30_;
    r.m33_ += a.m13_ * b.m31_;
    r.m33_ += a.m23_ * b.m32_;
    r.m33_ += a.m33_ * b.m33_;
    ////////////////////////////////

    return r;
}

// https://www.euclideanspace.com/maths/geometry/transform/index.htm
void transform(mmdata::Matrix4x4 m, mmdata::Point3D point,
               mmdata::Point3D &outPoint) {
    // Column 0
    outPoint.x_ = 0.0;
    outPoint.x_ += m.m00_ * point.x_;
    outPoint.x_ += m.m01_ * point.y_;
    outPoint.x_ += m.m02_ * point.z_;
    outPoint.x_ += m.m03_ * point.w_;

    // Column 1
    outPoint.y_ = 0.0;
    outPoint.y_ += m.m10_ * point.x_;
    outPoint.y_ += m.m11_ * point.y_;
    outPoint.y_ += m.m12_ * point.z_;
    outPoint.y_ += m.m13_ * point.w_;

    // Column 2
    outPoint.z_ = 0.0;
    outPoint.z_ += m.m20_ * point.x_;
    outPoint.z_ += m.m21_ * point.y_;
    outPoint.z_ += m.m22_ * point.z_;
    outPoint.z_ += m.m23_ * point.w_;

    // Column 3
    outPoint.w_ = 0.0;
    outPoint.w_ += m.m30_ * point.x_;
    outPoint.w_ += m.m31_ * point.y_;
    outPoint.w_ += m.m32_ * point.z_;
    outPoint.w_ += m.m33_ * point.w_;
    return;
}

// See "Intersection point of two line segments in 2 dimensions" in
// http://paulbourke.net/geometry/pointlineplane/
bool infiniteLineIntersection(
    // Line 1
    mmdata::Point2D pointA, mmdata::Point2D pointB,

    // Line 2
    mmdata::Point2D pointC, mmdata::Point2D pointD,

    // Output
    mmdata::Point2D &outPoint) {
    auto x1 = pointA.x_;
    auto y1 = pointA.y_;

    auto x2 = pointB.x_;
    auto y2 = pointB.y_;

    auto x3 = pointC.x_;
    auto y3 = pointC.y_;

    auto x4 = pointD.x_;
    auto y4 = pointD.y_;

    double denom = ((y4 - y3) * (x2 - x1)) - ((x4 - x3) * (y2 - y1));
    double nume_a = ((x4 - x3) * (y1 - y3)) - ((y4 - y3) * (x1 - x3));
    double nume_b = ((x2 - x1) * (y1 - y3)) - ((y2 - y1) * (x1 - x3));

    if (denom == 0.0) {
        if (nume_a == 0.0 && nume_b == 0.0) {
            // Coincident lines.
            outPoint.x_ = (x1 + x2) / 2;
            outPoint.y_ = (y1 + y2) / 2;
            return false;
        }
        // Parallel lines.
        outPoint.x_ = 0.0;
        outPoint.y_ = 0.0;
        return false;
    }

    // Intersecting.
    double ua = nume_a / denom;
    outPoint.x_ = x1 + ua * (x2 - x1);
    outPoint.y_ = y1 + ua * (y2 - y1);
    return true;
}

// Compute the cosine of the angle between 2 2D lines.
// When the cosine of the angle is near 1.0, the lines are almost parallel.
double cosineAngleBetweenLines(mmdata::LinePair2D linePair) {
    mmdata::Line2D lineA = linePair.lineA_;
    mmdata::Line2D lineB = linePair.lineB_;
    auto directionA =
        mmmath::normalize(mmmath::subtract(lineA.pointA_, lineA.pointB_));
    auto directionB =
        mmmath::normalize(mmmath::subtract(lineB.pointA_, lineB.pointB_));
    auto angle_cosine = std::abs(mmmath::dot(directionA, directionB));
    return angle_cosine;
}

}  // namespace mmmath
