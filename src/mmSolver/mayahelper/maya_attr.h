/*
 * Copyright (C) 2018, 2019 David Cattermole.
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
 * Attribute class, represents an attribute that could be modified.
 */

#ifndef MM_SOLVER_MAYA_HELPER_MAYA_ATTR_H
#define MM_SOLVER_MAYA_HELPER_MAYA_ATTR_H

#include <maya/MAngle.h>
#include <maya/MAnimControl.h>
#include <maya/MDGModifier.h>
#include <maya/MDistance.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MString.h>
#include <maya/MTime.h>

#include <memory>
#include <vector>

#include "maya_utils.h"

// The underlying attribute data type.
#define ATTR_DATA_TYPE_UNKNOWN (0)
#define ATTR_DATA_TYPE_LINEAR (1)
#define ATTR_DATA_TYPE_ANGLE (2)
#define ATTR_DATA_TYPE_NUMERIC (3)

enum class AttrDataType {
    kUnknown = ATTR_DATA_TYPE_UNKNOWN,
    kLinear = ATTR_DATA_TYPE_LINEAR,
    kAngle = ATTR_DATA_TYPE_ANGLE,
    kNumeric = ATTR_DATA_TYPE_NUMERIC
};

// Solver Types of Attributes.
#define ATTR_SOLVER_TYPE_UNINITIALIZED (0)
#define ATTR_SOLVER_TYPE_UNKNOWN (1)
#define ATTR_SOLVER_TYPE_BUNDLE_TX (2)
#define ATTR_SOLVER_TYPE_BUNDLE_TY (3)
#define ATTR_SOLVER_TYPE_BUNDLE_TZ (4)
#define ATTR_SOLVER_TYPE_CAMERA_TX (5)
#define ATTR_SOLVER_TYPE_CAMERA_TY (6)
#define ATTR_SOLVER_TYPE_CAMERA_TZ (7)
#define ATTR_SOLVER_TYPE_CAMERA_RX (8)
#define ATTR_SOLVER_TYPE_CAMERA_RY (9)
#define ATTR_SOLVER_TYPE_CAMERA_RZ (10)
#define ATTR_SOLVER_TYPE_CAMERA_SX (11)
#define ATTR_SOLVER_TYPE_CAMERA_SY (12)
#define ATTR_SOLVER_TYPE_CAMERA_SZ (13)
#define ATTR_SOLVER_TYPE_CAMERA_FOCAL (14)
#define ATTR_SOLVER_TYPE_TRANSFORM_TX (15)
#define ATTR_SOLVER_TYPE_TRANSFORM_TY (16)
#define ATTR_SOLVER_TYPE_TRANSFORM_TZ (17)
#define ATTR_SOLVER_TYPE_TRANSFORM_RX (18)
#define ATTR_SOLVER_TYPE_TRANSFORM_RY (19)
#define ATTR_SOLVER_TYPE_TRANSFORM_RZ (20)
#define ATTR_SOLVER_TYPE_TRANSFORM_SX (21)
#define ATTR_SOLVER_TYPE_TRANSFORM_SY (22)
#define ATTR_SOLVER_TYPE_TRANSFORM_SZ (23)

// Lens distortion models.
#define ATTR_SOLVER_TYPE_LENS_3DE_CLASSIC_DISTORTION (26)
#define ATTR_SOLVER_TYPE_LENS_3DE_CLASSIC_ANAMORPHIC_SQUEEZE (27)
#define ATTR_SOLVER_TYPE_LENS_3DE_CLASSIC_CURVATURE_X (28)
#define ATTR_SOLVER_TYPE_LENS_3DE_CLASSIC_CURVATURE_Y (29)
#define ATTR_SOLVER_TYPE_LENS_3DE_CLASSIC_QUARTIC_DISTORTION (30)

#define ATTR_SOLVER_TYPE_LENS_3DE_RADIAL_DEG_4_DEGREE_2_DISTORTION (31)
#define ATTR_SOLVER_TYPE_LENS_3DE_RADIAL_DEG_4_DEGREE_2_U (32)
#define ATTR_SOLVER_TYPE_LENS_3DE_RADIAL_DEG_4_DEGREE_2_V (33)
#define ATTR_SOLVER_TYPE_LENS_3DE_RADIAL_DEG_4_DEGREE_4_DISTORTION (34)
#define ATTR_SOLVER_TYPE_LENS_3DE_RADIAL_DEG_4_DEGREE_4_U (35)
#define ATTR_SOLVER_TYPE_LENS_3DE_RADIAL_DEG_4_DEGREE_4_V (36)
#define ATTR_SOLVER_TYPE_LENS_3DE_RADIAL_DEG_4_DIRECTION (37)
#define ATTR_SOLVER_TYPE_LENS_3DE_RADIAL_DEG_4_BENDING (38)

#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_DEGREE_2_CX02 (39)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_DEGREE_2_CY02 (40)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_DEGREE_2_CX22 (41)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_DEGREE_2_CY22 (42)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_DEGREE_4_CX04 (43)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_DEGREE_4_CY04 (44)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_DEGREE_4_CX24 (45)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_DEGREE_4_CY24 (46)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_DEGREE_4_CX44 (47)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_DEGREE_4_CY44 (48)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_LENS_ROTATION (49)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_SQUEEZE_X (50)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_SQUEEZE_Y (51)

#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_2_CX02 (52)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_2_CY02 (53)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_2_CX22 (54)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_2_CY22 (55)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_4_CX04 (56)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_4_CY04 (57)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_4_CX24 (58)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_4_CY24 (59)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_4_CX44 (60)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_4_CY44 (61)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_6_CX06 (62)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_6_CY06 (63)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_6_CX26 (64)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_6_CY26 (65)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_6_CX46 (66)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_6_CY46 (67)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_6_CX66 (68)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_6_CY66 (69)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_LENS_ROTATION (70)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_SQUEEZE_X (71)
#define ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_SQUEEZE_Y (72)

enum class AttrSolverType {
    kUninitialized = ATTR_SOLVER_TYPE_UNINITIALIZED,
    kUnknown = ATTR_SOLVER_TYPE_UNKNOWN,

    kBundleTx = ATTR_SOLVER_TYPE_BUNDLE_TX,
    kBundleTy = ATTR_SOLVER_TYPE_BUNDLE_TY,
    kBundleTz = ATTR_SOLVER_TYPE_BUNDLE_TZ,

    kCameraTx = ATTR_SOLVER_TYPE_CAMERA_TX,
    kCameraTy = ATTR_SOLVER_TYPE_CAMERA_TY,
    kCameraTz = ATTR_SOLVER_TYPE_CAMERA_TZ,
    kCameraRx = ATTR_SOLVER_TYPE_CAMERA_RX,
    kCameraRy = ATTR_SOLVER_TYPE_CAMERA_RY,
    kCameraRz = ATTR_SOLVER_TYPE_CAMERA_RZ,
    kCameraSx = ATTR_SOLVER_TYPE_CAMERA_SX,
    kCameraSy = ATTR_SOLVER_TYPE_CAMERA_SY,
    kCameraSz = ATTR_SOLVER_TYPE_CAMERA_SZ,
    kCameraFocal = ATTR_SOLVER_TYPE_CAMERA_FOCAL,

    kTransformTx = ATTR_SOLVER_TYPE_TRANSFORM_TX,
    kTransformTy = ATTR_SOLVER_TYPE_TRANSFORM_TY,
    kTransformTz = ATTR_SOLVER_TYPE_TRANSFORM_TZ,
    kTransformRx = ATTR_SOLVER_TYPE_TRANSFORM_RX,
    kTransformRy = ATTR_SOLVER_TYPE_TRANSFORM_RY,
    kTransformRz = ATTR_SOLVER_TYPE_TRANSFORM_RZ,
    kTransformSx = ATTR_SOLVER_TYPE_TRANSFORM_SX,
    kTransformSy = ATTR_SOLVER_TYPE_TRANSFORM_SY,
    kTransformSz = ATTR_SOLVER_TYPE_TRANSFORM_SZ,

    kLens3deClassicDistortion = ATTR_SOLVER_TYPE_LENS_3DE_CLASSIC_DISTORTION,
    kLens3deClassicAnamorphicSqueeze =
        ATTR_SOLVER_TYPE_LENS_3DE_CLASSIC_ANAMORPHIC_SQUEEZE,
    kLens3deClassicCurvatureX = ATTR_SOLVER_TYPE_LENS_3DE_CLASSIC_CURVATURE_X,
    kLens3deClassicCurvatureY = ATTR_SOLVER_TYPE_LENS_3DE_CLASSIC_CURVATURE_Y,
    kLens3deClassicQuarticDistortion =
        ATTR_SOLVER_TYPE_LENS_3DE_CLASSIC_QUARTIC_DISTORTION,

    kLens3deRadialDeg4Degree2Distortion =
        ATTR_SOLVER_TYPE_LENS_3DE_RADIAL_DEG_4_DEGREE_2_DISTORTION,
    kLens3deRadialDeg4Degree2U =
        ATTR_SOLVER_TYPE_LENS_3DE_RADIAL_DEG_4_DEGREE_2_U,
    kLens3deRadialDeg4Degree2V =
        ATTR_SOLVER_TYPE_LENS_3DE_RADIAL_DEG_4_DEGREE_2_V,
    kLens3deRadialDeg4Degree4Distortion =
        ATTR_SOLVER_TYPE_LENS_3DE_RADIAL_DEG_4_DEGREE_4_DISTORTION,
    kLens3deRadialDeg4Degree4U =
        ATTR_SOLVER_TYPE_LENS_3DE_RADIAL_DEG_4_DEGREE_4_U,
    kLens3deRadialDeg4Degree4V =
        ATTR_SOLVER_TYPE_LENS_3DE_RADIAL_DEG_4_DEGREE_4_V,
    kLens3deRadialDeg4Direction =
        ATTR_SOLVER_TYPE_LENS_3DE_RADIAL_DEG_4_DIRECTION,
    kLens3deRadialDeg4Bending = ATTR_SOLVER_TYPE_LENS_3DE_RADIAL_DEG_4_BENDING,

    kLens3deAnamorphicDeg4Degree2Cx02 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_DEGREE_2_CX02,
    kLens3deAnamorphicDeg4Degree2Cy02 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_DEGREE_2_CY02,
    kLens3deAnamorphicDeg4Degree2Cx22 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_DEGREE_2_CX22,
    kLens3deAnamorphicDeg4Degree2Cy22 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_DEGREE_2_CY22,
    kLens3deAnamorphicDeg4Degree4Cx04 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_DEGREE_4_CX04,
    kLens3deAnamorphicDeg4Degree4Cy04 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_DEGREE_4_CY04,
    kLens3deAnamorphicDeg4Degree4Cx24 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_DEGREE_4_CX24,
    kLens3deAnamorphicDeg4Degree4Cy24 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_DEGREE_4_CY24,
    kLens3deAnamorphicDeg4Degree4Cx44 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_DEGREE_4_CX44,
    kLens3deAnamorphicDeg4Degree4Cy44 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_DEGREE_4_CY44,
    kLens3deAnamorphicDeg4LensRotation =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_LENS_ROTATION,
    kLens3deAnamorphicDeg4SqueezeX =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_SQUEEZE_X,
    kLens3deAnamorphicDeg4SqueezeY =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_4_SQUEEZE_Y,

    kLens3deAnamorphicDeg6Degree2Cx02 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_2_CX02,
    kLens3deAnamorphicDeg6Degree2Cy02 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_2_CY02,
    kLens3deAnamorphicDeg6Degree2Cx22 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_2_CX22,
    kLens3deAnamorphicDeg6Degree2Cy22 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_2_CY22,
    kLens3deAnamorphicDeg6Degree4Cx04 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_4_CX04,
    kLens3deAnamorphicDeg6Degree4Cy04 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_4_CY04,
    kLens3deAnamorphicDeg6Degree4Cx24 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_4_CX24,
    kLens3deAnamorphicDeg6Degree4Cy24 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_4_CY24,
    kLens3deAnamorphicDeg6Degree4Cx44 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_4_CX44,
    kLens3deAnamorphicDeg6Degree4Cy44 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_4_CY44,
    kLens3deAnamorphicDeg6Degree6Cx06 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_6_CX06,
    kLens3deAnamorphicDeg6Degree6Cy06 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_6_CY06,
    kLens3deAnamorphicDeg6Degree6Cx26 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_6_CX26,
    kLens3deAnamorphicDeg6Degree6Cy26 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_6_CY26,
    kLens3deAnamorphicDeg6Degree6Cx46 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_6_CX46,
    kLens3deAnamorphicDeg6Degree6Cy46 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_6_CY46,
    kLens3deAnamorphicDeg6Degree6Cx66 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_6_CX66,
    kLens3deAnamorphicDeg6Degree6Cy66 =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_DEGREE_6_CY66,
    kLens3deAnamorphicDeg6LensRotation =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_LENS_ROTATION,
    kLens3deAnamorphicDeg6SqueezeX =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_SQUEEZE_X,
    kLens3deAnamorphicDeg6SqueezeY =
        ATTR_SOLVER_TYPE_LENS_3DE_ANAMORPHIC_DEG_6_SQUEEZE_Y,
};

inline AttrSolverType computeSolverAttrType(ObjectType objectType,
                                            const MString &attrName) {
    auto attr_type = AttrSolverType::kUnknown;
    if (objectType == ObjectType::kBundle) {
        // A bundle node.
        if (attrName == "translateX" || attrName == "tx") {
            attr_type = AttrSolverType::kBundleTx;
        } else if (attrName == "translateY" || attrName == "ty") {
            attr_type = AttrSolverType::kBundleTy;
        } else if (attrName == "translateZ" || attrName == "tz") {
            attr_type = AttrSolverType::kBundleTz;
        }
    } else if (objectType == ObjectType::kCamera) {
        // A camera node.
        if (attrName == "translateX" || attrName == "tx") {
            attr_type = AttrSolverType::kCameraTx;
        } else if (attrName == "translateY" || attrName == "ty") {
            attr_type = AttrSolverType::kCameraTy;
        } else if (attrName == "translateZ" || attrName == "tz") {
            attr_type = AttrSolverType::kCameraTz;
        } else if (attrName == "rotateX" || attrName == "rx") {
            attr_type = AttrSolverType::kCameraRx;
        } else if (attrName == "rotateY" || attrName == "ry") {
            attr_type = AttrSolverType::kCameraRy;
        } else if (attrName == "rotateZ" || attrName == "rx") {
            attr_type = AttrSolverType::kCameraRz;
        } else if (attrName == "scaleX" || attrName == "sx") {
            attr_type = AttrSolverType::kCameraSx;
        } else if (attrName == "scaleY" || attrName == "sy") {
            attr_type = AttrSolverType::kCameraSy;
        } else if (attrName == "scaleZ" || attrName == "sz") {
            attr_type = AttrSolverType::kCameraSz;
        } else if (attrName == "focalLength" || attrName == "fl") {
            attr_type = AttrSolverType::kCameraFocal;
        }
    } else if (objectType == ObjectType::kLens) {
        // A lens model node.
        if (attrName == "tdeClassic_distortion") {
            attr_type = AttrSolverType::kLens3deClassicDistortion;
        } else if (attrName == "tdeClassic_anamorphicSqueeze") {
            attr_type = AttrSolverType::kLens3deClassicAnamorphicSqueeze;
        } else if (attrName == "tdeClassic_curvatureX") {
            attr_type = AttrSolverType::kLens3deClassicCurvatureX;
        } else if (attrName == "tdeClassic_curvatureY") {
            attr_type = AttrSolverType::kLens3deClassicCurvatureY;
        } else if (attrName == "tdeClassic_quarticDistortion") {
            attr_type = AttrSolverType::kLens3deClassicQuarticDistortion;
        } else if (attrName == "tdeRadialStdDeg4_degree2_distortion") {
            attr_type = AttrSolverType::kLens3deRadialDeg4Degree2Distortion;
        } else if (attrName == "tdeRadialStdDeg4_degree2_u") {
            attr_type = AttrSolverType::kLens3deRadialDeg4Degree2U;
        } else if (attrName == "tdeRadialStdDeg4_degree2_v") {
            attr_type = AttrSolverType::kLens3deRadialDeg4Degree2V;
        } else if (attrName == "tdeRadialStdDeg4_degree4_distortion") {
            attr_type = AttrSolverType::kLens3deRadialDeg4Degree4Distortion;
        } else if (attrName == "tdeRadialStdDeg4_degree4_u") {
            attr_type = AttrSolverType::kLens3deRadialDeg4Degree4U;
        } else if (attrName == "tdeRadialStdDeg4_degree4_v") {
            attr_type = AttrSolverType::kLens3deRadialDeg4Degree4V;
        } else if (attrName == "tdeRadialStdDeg4_cylindricDirection") {
            attr_type = AttrSolverType::kLens3deRadialDeg4Direction;
        } else if (attrName == "tdeRadialStdDeg4_cylindricBending") {
            attr_type = AttrSolverType::kLens3deRadialDeg4Bending;
        } else if (attrName == "tdeAnamorphicStdDeg4_degree2_cx02") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg4Degree2Cx02;
        } else if (attrName == "tdeAnamorphicStdDeg4_degree2_cy02") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg4Degree2Cy02;
        } else if (attrName == "tdeAnamorphicStdDeg4_degree2_cx22") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg4Degree2Cx22;
        } else if (attrName == "tdeAnamorphicStdDeg4_degree2_cy22") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg4Degree2Cy22;
        } else if (attrName == "tdeAnamorphicStdDeg4_degree4_cx04") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg4Degree4Cx04;
        } else if (attrName == "tdeAnamorphicStdDeg4_degree4_cy04") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg4Degree4Cy04;
        } else if (attrName == "tdeAnamorphicStdDeg4_degree4_cx24") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg4Degree4Cx24;
        } else if (attrName == "tdeAnamorphicStdDeg4_degree4_cy24") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg4Degree4Cy24;
        } else if (attrName == "tdeAnamorphicStdDeg4_degree4_cx44") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg4Degree4Cx44;
        } else if (attrName == "tdeAnamorphicStdDeg4_degree4_cy44") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg4Degree4Cy44;
        } else if (attrName == "tdeAnamorphicStdDeg4_lensRotation") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg4LensRotation;
        } else if (attrName == "tdeAnamorphicStdDeg4_squeeze_x") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg4SqueezeX;
        } else if (attrName == "tdeAnamorphicStdDeg4_squeeze_y") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg4SqueezeY;
        } else if (attrName == "tdeAnamorphicStdDeg6_degree2_cx02") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6Degree2Cx02;
        } else if (attrName == "tdeAnamorphicStdDeg6_degree2_cy02") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6Degree2Cy02;
        } else if (attrName == "tdeAnamorphicStdDeg6_degree2_cx22") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6Degree2Cx22;
        } else if (attrName == "tdeAnamorphicStdDeg6_degree2_cy22") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6Degree2Cy22;
        } else if (attrName == "tdeAnamorphicStdDeg6_degree4_cx04") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6Degree4Cx04;
        } else if (attrName == "tdeAnamorphicStdDeg6_degree4_cy04") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6Degree4Cy04;
        } else if (attrName == "tdeAnamorphicStdDeg6_degree4_cx24") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6Degree4Cx24;
        } else if (attrName == "tdeAnamorphicStdDeg6_degree4_cy24") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6Degree4Cy24;
        } else if (attrName == "tdeAnamorphicStdDeg6_degree4_cx44") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6Degree4Cx44;
        } else if (attrName == "tdeAnamorphicStdDeg6_degree4_cy44") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6Degree4Cy44;
        } else if (attrName == "tdeAnamorphicStdDeg6_degree6_cx06") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6Degree6Cx06;
        } else if (attrName == "tdeAnamorphicStdDeg6_degree6_cy06") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6Degree6Cy06;
        } else if (attrName == "tdeAnamorphicStdDeg6_degree6_cx26") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6Degree6Cx26;
        } else if (attrName == "tdeAnamorphicStdDeg6_degree6_cy26") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6Degree6Cy26;
        } else if (attrName == "tdeAnamorphicStdDeg6_degree6_cx46") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6Degree6Cx46;
        } else if (attrName == "tdeAnamorphicStdDeg6_degree6_cy46") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6Degree6Cy46;
        } else if (attrName == "tdeAnamorphicStdDeg6_degree6_cx66") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6Degree6Cx66;
        } else if (attrName == "tdeAnamorphicStdDeg6_degree6_cy66") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6Degree6Cy66;
        } else if (attrName == "tdeAnamorphicStdDeg6_lensRotation") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6LensRotation;
        } else if (attrName == "tdeAnamorphicStdDeg6_squeeze_x") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6SqueezeX;
        } else if (attrName == "tdeAnamorphicStdDeg6_squeeze_y") {
            attr_type = AttrSolverType::kLens3deAnamorphicDeg6SqueezeY;
        }

    } else {
        // A normal transform node.
        if (attrName == "translateX" || attrName == "tx") {
            attr_type = AttrSolverType::kTransformTx;
        } else if (attrName == "translateY" || attrName == "ty") {
            attr_type = AttrSolverType::kTransformTy;
        } else if (attrName == "translateZ" || attrName == "tz") {
            attr_type = AttrSolverType::kTransformTz;
        } else if (attrName == "rotateX" || attrName == "rx") {
            attr_type = AttrSolverType::kTransformRx;
        } else if (attrName == "rotateY" || attrName == "ry") {
            attr_type = AttrSolverType::kTransformRy;
        } else if (attrName == "rotateZ" || attrName == "rx") {
            attr_type = AttrSolverType::kTransformRz;
        } else if (attrName == "scaleX" || attrName == "sx") {
            attr_type = AttrSolverType::kTransformSx;
        } else if (attrName == "scaleY" || attrName == "sy") {
            attr_type = AttrSolverType::kTransformSy;
        } else if (attrName == "scaleZ" || attrName == "sz") {
            attr_type = AttrSolverType::kTransformSz;
        }
    }
    return attr_type;
}

class Attr {
public:
    Attr();

    MString getName() const;
    MStatus setName(MString value);

    MString getNodeName() const;
    MStatus setNodeName(const MString &value);

    MString getAttrName() const;
    MStatus setAttrName(const MString &value);

    MObject getObject();
    MPlug getPlug();
    MObject getAttribute();
    MString getAnimCurveName();
    AttrDataType getAttrType();

    bool isFreeToChange();
    bool isAnimated();
    bool isConnected();

    MStatus getValue(bool &value, const MTime &time, const int timeEvalMode);
    MStatus getValue(int &value, const MTime &time, const int timeEvalMode);
    MStatus getValue(short &value, const MTime &time, const int timeEvalMode);
    MStatus getValue(double &value, const MTime &time, const int timeEvalMode);
    MStatus getValue(MMatrix &value, const MTime &time, const int timeEvalMode);

    MStatus getValue(bool &value, const int timeEvalMode);
    MStatus getValue(int &value, const int timeEvalMode);
    MStatus getValue(short &value, const int timeEvalMode);
    MStatus getValue(double &value, const int timeEvalMode);
    MStatus getValue(MMatrix &value, const int timeEvalMode);

    MStatus setValue(const double value, const MTime &time, MDGModifier &dgmod,
                     MAnimCurveChange &animChange);

    MStatus setValue(const double value, MDGModifier &dgmod,
                     MAnimCurveChange &animChange);

    double getMinimumValue() const;
    double getMaximumValue() const;
    double getOffsetValue() const;
    double getScaleValue() const;
    ObjectType getObjectType() const;
    AttrSolverType getSolverAttrType() const;

    void setMinimumValue(const double value);
    void setMaximumValue(const double value);
    void setOffsetValue(const double value);
    void setScaleValue(const double value);
    void setObjectType(const ObjectType value);
    void setSolverAttrType(const AttrSolverType value);

    MString getLongNodeName();
    MString getLongAttributeName();
    MString getLongName();

private:
    MString m_nodeName;
    MString m_attrName;
    MObject m_object;
    MPlug m_plug;
    MString m_animCurveName;
    int m_animated;
    int m_connected;
    int m_isFreeToChange;
    double m_minValue;
    double m_maxValue;
    double m_offsetValue;
    double m_scaleValue;
    ObjectType m_objectType;
    AttrSolverType m_solverAttrType;

    double m_linearFactor;
    double m_linearFactorInv;
    double m_angularFactor;
    double m_angularFactorInv;
};

typedef std::vector<Attr> AttrList;
typedef AttrList::iterator AttrListIt;

typedef std::shared_ptr<Attr> AttrPtr;
typedef std::vector<std::shared_ptr<Attr> > AttrPtrList;
typedef AttrPtrList::iterator AttrPtrListIt;
typedef AttrPtrList::const_iterator AttrPtrListCIt;

struct SmoothAttrs {
    int attrIndex;
    AttrPtr weightAttr;
    AttrPtr varianceAttr;
    AttrPtr valueAttr;
};

typedef std::vector<SmoothAttrs> SmoothAttrsList;
typedef SmoothAttrsList::iterator SmoothAttrsListIt;

typedef std::shared_ptr<SmoothAttrs> SmoothAttrsPtr;
typedef std::vector<std::shared_ptr<SmoothAttrs> > SmoothAttrsPtrList;
typedef SmoothAttrsPtrList::iterator SmoothAttrsPtrListIt;
typedef SmoothAttrsPtrList::const_iterator SmoothAttrsPtrListCIt;

struct StiffAttrs {
    int attrIndex;
    AttrPtr weightAttr;
    AttrPtr varianceAttr;
    AttrPtr valueAttr;
};

typedef std::vector<StiffAttrs> StiffAttrsList;
typedef StiffAttrsList::iterator StiffAttrsListIt;

typedef std::shared_ptr<StiffAttrs> StiffAttrsPtr;
typedef std::vector<std::shared_ptr<StiffAttrs> > StiffAttrsPtrList;
typedef StiffAttrsPtrList::iterator StiffAttrsPtrListIt;
typedef StiffAttrsPtrList::const_iterator StiffAttrsPtrListCIt;

#endif  // MM_SOLVER_MAYA_HELPER_MAYA_ATTR_H
