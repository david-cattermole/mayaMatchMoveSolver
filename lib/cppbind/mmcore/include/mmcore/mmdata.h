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
 * Data types for use in mmSolver.
 */

#ifndef MM_CORE_MM_DATA_H
#define MM_CORE_MM_DATA_H

namespace mmdata {

struct Point2D {
public:
    double x_;
    double y_;
    double z_;

    Point2D() : x_(0.0), y_(0.0), z_(1.0) {}

    Point2D(double x, double y) : x_(x), y_(y), z_(1.0) {}

    Point2D(double x, double y, double z) : x_(x), y_(y), z_(z) {}
};

struct Point3D {
public:
    double x_;
    double y_;
    double z_;
    double w_;

    Point3D() : x_(0.0), y_(0.0), z_(0.0), w_(1.0) {}

    Point3D(double x, double y, double z) : x_(x), y_(y), z_(z), w_(1.0) {}

    Point3D(double x, double y, double z, double w)
        : x_(x), y_(y), z_(z), w_(w) {}
};

struct Vector2D {
public:
    double x_, y_;

    Vector2D() : x_(0.0), y_(0.0) {}

    // Converting constructor.
    explicit Vector2D(double f) : x_(f), y_(f) {}

    Vector2D(double x, double y) : x_(x), y_(y) {}
};

struct Vector3D {
public:
    double x_, y_, z_;

    Vector3D() : x_(0.0), y_(0.0), z_(0.0) {}

    // Converting constructor.
    explicit Vector3D(double f) : x_(f), y_(f), z_(f) {}

    Vector3D(double x, double y) : x_(x), y_(y), z_(0.0) {}

    Vector3D(double x, double y, double z) : x_(x), y_(y), z_(z) {}
};

struct Line2D {
    Point2D pointA_;
    Point2D pointB_;

    Line2D() : pointA_(), pointB_() {}

    Line2D(Point2D pointA, Point2D pointB) : pointA_(pointA), pointB_(pointB) {}
};

struct LinePair2D {
    Line2D lineA_;
    Line2D lineB_;

    LinePair2D() : lineA_(), lineB_() {}

    LinePair2D(Line2D lineA, Line2D lineB) : lineA_(lineA), lineB_(lineB) {}

    LinePair2D(double aax, double aay,  // Line A Point A
               double abx, double aby,  // Line A Point B
               double bax, double bay,  // Line B Point A
               double bbx, double bby)  // Line B Point B
    {
        auto aa = Point2D(aax, aay);
        auto ab = Point2D(abx, aby);
        auto ba = Point2D(bax, bay);
        auto bb = Point2D(bbx, bby);
        lineA_ = Line2D(aa, ab);
        lineB_ = Line2D(ba, bb);
    }
};

struct Matrix4x4 {
public:
    double m00_, m01_, m02_, m03_;
    double m10_, m11_, m12_, m13_;
    double m20_, m21_, m22_, m23_;
    double m30_, m31_, m32_, m33_;

    Matrix4x4()
        : m00_(1.0)
        , m01_(0.0)
        , m02_(0.0)
        , m03_(0.0)
        //
        , m10_(0.0)
        , m11_(1.0)
        , m12_(0.0)
        , m13_(0.0)
        //
        , m20_(0.0)
        , m21_(0.0)
        , m22_(1.0)
        , m23_(0.0)
        //
        , m30_(0.0)
        , m31_(0.0)
        , m32_(0.0)
        , m33_(1.0){};

    Matrix4x4(double m00, double m01, double m02, double m03, double m10,
              double m11, double m12, double m13, double m20, double m21,
              double m22, double m23, double m30, double m31, double m32,
              double m33)
        : m00_(m00)
        , m01_(m01)
        , m02_(m02)
        , m03_(m03)
        //
        , m10_(m10)
        , m11_(m11)
        , m12_(m12)
        , m13_(m13)
        //
        , m20_(m20)
        , m21_(m21)
        , m22_(m22)
        , m23_(m23)
        //
        , m30_(m30)
        , m31_(m31)
        , m32_(m32)
        , m33_(m33) {}

    Matrix4x4(const Matrix4x4 &m)
        : m00_(m.m00_)
        , m01_(m.m01_)
        , m02_(m.m02_)
        , m03_(m.m03_)
        //
        , m10_(m.m10_)
        , m11_(m.m11_)
        , m12_(m.m12_)
        , m13_(m.m13_)
        //
        , m20_(m.m20_)
        , m21_(m.m21_)
        , m22_(m.m22_)
        , m23_(m.m23_)
        //
        , m30_(m.m30_)
        , m31_(m.m31_)
        , m32_(m.m32_)
        , m33_(m.m33_){};
};

}  // namespace mmdata

#endif  // MM_CORE_MM_DATA_H
