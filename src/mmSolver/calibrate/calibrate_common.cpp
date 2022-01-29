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
 * The functions are derived from the following papers:
 *
 * - "Using vanishing points for camera calibration and coarse 3D
 *   reconstruction from a single image" (2000), E. Guillou,
 *   D. Meneveaux, E. Maisel, K. Bouatouch.
 *
 * - "Camera calibration using two or three vanishing points" (2012),
 *   Radu Orghidan, Joaquim Salvi, Mihaela Gordan and Bogdan Orza.
 */

#include "calibrate_common.h"

// STL
#include <cmath>
#include <cstdint>
#include <cstdlib>

// MM Solver
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/core/mmdata.h"
#include "mmSolver/core/mmmath.h"
#include "mmSolver/core/mmcoord.h"
#include "mmSolver/core/mmcamera.h"


namespace calibrate {

#define EPSILON (1e-7)

bool
calcVanishingPointFromLinePair(
    mmdata::LinePair2D linePair,
    mmdata::Point2D &outPoint)
{
    mmdata::Line2D lineA = linePair.lineA_;
    mmdata::Line2D lineB = linePair.lineB_;

    mmdata::Point2D pointAA = lineA.pointA_;
    mmdata::Point2D pointAB = lineA.pointB_;
    mmdata::Point2D pointBA = lineB.pointA_;
    mmdata::Point2D pointBB = lineB.pointB_;

    auto vanishingPoint = mmdata::Point2D();
    auto success = mmmath::infiniteLineIntersection(
        pointAA,
        pointAB,
        pointBA,
        pointBB,
        vanishingPoint
    );
    if (success) {
        outPoint = vanishingPoint;
    } else {
        MMSOLVER_INFO("ERROR: Failed to calculate vanishing point.");
    }
    return success;
}

// With a single vanishing point (vpA), and a direction of the horizon
// line, and the focal length we can re-arrange and estimate a second
// vanishing point.
//
// The second vanishing point is found, using the focal length finds
// the position from the first vanishing point (vpA) along the horizon
// direction.
//
mmdata::Point2D
estimateSecondVanishingPoint(
    mmdata::Point2D vpA,
    mmdata::Point2D principalPoint,
    mmdata::Point2D horizonDirection,
    double focalLengthFactor)
{
    auto result = mmdata::Point2D();
    if (mmmath::distance(vpA, principalPoint) > EPSILON) {
        auto upPoint = mmdata::Point2D(
            vpA.x_ - principalPoint.x_,
            vpA.y_ - principalPoint.y_);

        auto k = -(upPoint.x_ * upPoint.x_ + upPoint.y_ * upPoint.y_ + focalLengthFactor * focalLengthFactor) / (upPoint.x_ * horizonDirection.x_ + upPoint.y_ * horizonDirection.y_);

        result = mmdata::Point2D(
            upPoint.x_ + k * horizonDirection.x_ + principalPoint.x_,
            upPoint.y_ + k * horizonDirection.y_ + principalPoint.y_);
    };
    return result;
}

// Calculates the focal length based on two vanishing points and a
// center of projection.
//
// See paper "Using vanishing points for camera calibration and coarse
// 3D reconstruction from a single image" (2000), section "3.2
// Determining the focal length from a single image".
//
// See paper "Camera calibration using two or three vanishing points"
// (2012), section "2.A. Intrinsic parameters calculation" for
// reference.
bool
calcFocalLength(
    mmdata::Point2D vpA,             // Variable 'Fu' in the paper.
    mmdata::Point2D vpB,             // Variable 'Fv' in the paper.
    mmdata::Point2D principalPoint,  // Variable 'P' in the paper.
    double &outFocalLength)
{
    auto vpA_vpB = mmdata::Vector3D(
        vpA.x_ - vpB.x_,
        vpA.y_ - vpB.y_);
    auto vpA_vpB_direction = mmmath::normalize(vpA_vpB);

    auto P_vpB = mmdata::Vector3D(
        principalPoint.x_ - vpB.x_,
        principalPoint.y_ - vpB.y_);
    auto projection = mmmath::dot(vpA_vpB_direction, P_vpB);

    // Let 'Puv' be the orthogonal projection of 'P' on the line 'vpA_vpB_direction'.
    auto Puv = mmdata::Point2D(
        projection * vpA_vpB_direction.x_ + vpB.x_,
        projection * vpA_vpB_direction.y_ + vpB.y_);

    auto PPuv = mmmath::length(
        mmdata::Vector3D(
            principalPoint.x_ - Puv.x_,
            principalPoint.y_ - Puv.y_));
    auto vpA_Puv = mmmath::length(
        mmdata::Vector3D(
            vpB.x_ - Puv.x_,
            vpB.y_ - Puv.y_));
    auto vpB_Puv = mmmath::length(
        mmdata::Vector3D(
            vpA.x_ - Puv.x_,
            vpA.y_ - Puv.y_));

    auto focalLengthSquared = (vpA_Puv * vpB_Puv) - (PPuv * PPuv);
    auto ok = focalLengthSquared > 0;
    if (ok) {
        outFocalLength = std::sqrt(focalLengthSquared);
    }
    return ok;
}

// Calculate the camera rotation matrix from two vanishing points and
// a (assumed to be) known focal length.
//
// See paper "Camera calibration using two or three vanishing points"
// (2012), section "2.B. Extrinsic parameters calculation" for
// reference.
//
// See paper "Using vanishing points for camera calibration and coarse
// 3D reconstruction from a single image" (2000), section "3.3
// Computing the rotation matrix".
bool
calcCameraRotationMatrix(
    mmdata::Point2D vpA,            // Variable 'Fu' in the paper.
    mmdata::Point2D vpB,            // Variable 'Fv' in the paper.
    mmdata::Point2D principalPoint, // Variable 'P' in the paper.
    double focalLengthFactor,       // Relative focal length.
    mmdata::Matrix4x4 &outMatrix)
{
    // vpA projected into camera depth, centered around principalPoint.
    auto O_vpA = mmdata::Vector3D(
        vpA.x_ - principalPoint.x_,
        vpA.y_ - principalPoint.y_,
        -focalLengthFactor);

    // vpB projected into camera depth, centered around principalPoint.
    auto O_vpB = mmdata::Vector3D(
        vpB.x_ - principalPoint.x_,
        vpB.y_ - principalPoint.y_,
        -focalLengthFactor);

    auto O_vpA_magnitude = mmmath::length(O_vpA);
    auto O_vpB_magnitude = mmmath::length(O_vpB);

    auto O_vpA_direction = mmmath::normalize(O_vpA);
    auto O_vpB_direction = mmmath::normalize(O_vpB);
    auto w = mmmath::cross(O_vpA_direction, O_vpB_direction);

    outMatrix = mmdata::Matrix4x4();
    //
    outMatrix.m00_ = O_vpA.x_ / O_vpA_magnitude;
    outMatrix.m01_ = O_vpB.x_ / O_vpB_magnitude;
    outMatrix.m02_ = w.x_;
    //
    outMatrix.m10_ = O_vpA.y_ / O_vpA_magnitude;
    outMatrix.m11_ = O_vpB.y_ / O_vpB_magnitude;
    outMatrix.m12_ = w.y_;
    //
    outMatrix.m20_ = -focalLengthFactor / O_vpA_magnitude;
    outMatrix.m21_ = -focalLengthFactor / O_vpB_magnitude;
    outMatrix.m22_ = w.z_;

    auto det = mmmath::determinant(outMatrix);
    auto ok = std::abs(det - 1.0) > EPSILON;
    return ok;
}

mmdata::Matrix4x4
createOrientationMatrix(
    OrientationPlane orientPlane,
    bool flipX,
    bool flipY,
    bool flipZ)
{
    // This is essentially a look-at matrix.
    auto forward = mmdata::Vector3D();
    auto side = mmdata::Vector3D();
    if (orientPlane == OrientationPlane::ZX)
    {
        forward = mmdata::Vector3D(0, 0, -1);
        side = mmdata::Vector3D(1, 0, 0);
    }
    else if (orientPlane == OrientationPlane::ZY)
    {
        forward = mmdata::Vector3D(0, 0, -1);
        side = mmdata::Vector3D(0, -1, 0);
    }
    else if (orientPlane == OrientationPlane::XZ)
    {
        forward = mmdata::Vector3D(1, 0, 0);
        side = mmdata::Vector3D(0, 0, 1);
    }
    else if (orientPlane == OrientationPlane::XY)
    {
        forward = mmdata::Vector3D(-1, 0, 0);
        side = mmdata::Vector3D(0, 1, 0);
    }
    else if (orientPlane == OrientationPlane::YZ)
    {
        forward = mmdata::Vector3D(0, -1, 0);
        side = mmdata::Vector3D(0, 0, 1);
    }
    else if (orientPlane == OrientationPlane::YX)
    {
        forward = mmdata::Vector3D(0, -1, 0);
        side = mmdata::Vector3D(-1, 0, 0);
    }
    else {
        MMSOLVER_INFO("ERROR: Invalid OrientationPlane: "
             << static_cast<int>(orientPlane));
        return mmdata::Matrix4x4();;
    }
    auto up = mmmath::cross(forward, side);

    auto orientMatrix = mmdata::Matrix4x4();
    orientMatrix.m00_ = forward.x_;
    orientMatrix.m01_ = forward.y_;
    orientMatrix.m02_ = forward.z_;
    orientMatrix.m10_ = side.x_;
    orientMatrix.m11_ = side.y_;
    orientMatrix.m12_ = side.z_;
    orientMatrix.m20_ = up.x_;
    orientMatrix.m21_ = up.y_;
    orientMatrix.m22_ = up.z_;

    if (flipX) {
        orientMatrix.m00_ *= -1;
        orientMatrix.m10_ *= -1;
        orientMatrix.m20_ *= -1;
    }
    if (flipY) {
        orientMatrix.m01_ *= -1;
        orientMatrix.m11_ *= -1;
        orientMatrix.m21_ *= -1;
    }
    if (flipZ) {
        orientMatrix.m02_ *= -1;
        orientMatrix.m12_ *= -1;
        orientMatrix.m22_ *= -1;
    }

    return orientMatrix;
}


// The translations are computed by projecting a 2D point into 3D
// space (2.5D point), and using the value to offset the camera away
// from that point. The given point (originPoint) becomes the origin
// of the 3D world.
//
// See paper "Using vanishing points for camera calibration and coarse
// 3D reconstruction from a single image" (2000), section "3.4
// Computing the translation vector".
//
// See paper "Camera calibration using two or three vanishing points"
// (2012), section "2.B. Extrinsic parameters calculation" for
// reference.
//
bool
calcTranslationVector(
    mmdata::Point2D originPoint,
    mmdata::Point2D principalPoint,
    double angleOfView_radians,
    mmdata::Vector3D &outVector)
{
    auto focalLength = std::tan(0.5 * angleOfView_radians);
    auto originInCameraSpace = mmdata::Vector3D(
        focalLength * (originPoint.x_ - principalPoint.x_),
        focalLength * (originPoint.y_ - principalPoint.y_),
        -1
    );

    // Set camera translation values.
    outVector.x_ = originInCameraSpace.x_;
    outVector.y_ = originInCameraSpace.y_;
    outVector.z_ = originInCameraSpace.z_;
    return true;
}

// The logic of the scale is intrinsic to the camera and a distance
// factor. No other data is required.
bool
applySceneScale(
    mmdata::Matrix4x4 cameraTransform,
    SceneScaleMode sceneScaleMode,
    double distance_cm,
    mmdata::Matrix4x4 &outCameraTransform) {
    auto translation = mmdata::Vector3D(
        cameraTransform.m03_,
        cameraTransform.m13_,
        cameraTransform.m23_);
    if (sceneScaleMode == SceneScaleMode::UniformScale) {
        translation.x_ *= distance_cm;
        translation.y_ *= distance_cm;
        translation.z_ *= distance_cm;
    } else if (sceneScaleMode == SceneScaleMode::CameraHeight) {
        // The camera height from the origin will be exactly
        // 'distance_cm'.
        auto scaleFactor = distance_cm / std::abs(translation.y_);
        translation.x_ *= scaleFactor;
        translation.y_ *= scaleFactor;
        translation.z_ *= scaleFactor;
    } else {
        MMSOLVER_INFO("ERROR: Invalid SceneScaleMode: "
             << static_cast<int>(sceneScaleMode));
        return false;
    }
    outCameraTransform = mmdata::Matrix4x4(cameraTransform);
    outCameraTransform.m03_ = translation.x_;
    outCameraTransform.m13_ = translation.y_;
    outCameraTransform.m23_ = translation.z_;
    return true;
}

// Combines multiple calculations such as scale, rotation and
// translation into a single function.
bool
calcCameraParameters(
    mmdata::Point2D originPoint,
    mmdata::Point2D principalPoint,
    mmdata::Point2D vanishingPointA,
    mmdata::Point2D vanishingPointB,
    SceneScaleMode sceneScaleMode,
    double sceneScaleDistance_cm,
    double focalLengthFactor,
    double filmBackWidth_mm,
    double filmBackHeight_mm,
    CameraParameters &outCameraParameters)
{
    auto transformInverse = mmdata::Matrix4x4();
    auto ok = calcCameraRotationMatrix(
        vanishingPointA,
        vanishingPointB,
        principalPoint,
        focalLengthFactor,
        transformInverse);
    if (ok) {
        MMSOLVER_INFO("ERROR: Camera Rotation calculation is invalid. ");
        return false;
    }

    auto angleOfView_radians = mmcamera::angleOfViewFromFocalLengthFactor(focalLengthFactor);
    auto translation = mmdata::Vector3D();
    ok = calcTranslationVector(
        originPoint,
        principalPoint,
        angleOfView_radians,
        translation
    );
    if (!ok) {
        MMSOLVER_INFO("ERROR: Invalid translation vector.");
        return false;
    }

    // Orient the "ground" plane.
    bool axisFlipX = false;
    bool axisFlipY = false;
    bool axisFlipZ = false;
    auto orientPlane = OrientationPlane::XZ;
    auto orientMatrix = createOrientationMatrix(
        orientPlane,
        axisFlipX,
        axisFlipY,
        axisFlipZ);
    transformInverse = mmmath::matrixMultiply(
        orientMatrix,
        transformInverse);

    // Set camera translation values.
    transformInverse.m03_ = translation.x_;
    transformInverse.m13_ = translation.y_;
    transformInverse.m23_ = translation.z_;
    auto transform = mmmath::inverse(transformInverse);

    // Apply scale.
    //
    // We have made sure to align the world before scaling the camera
    // so that our "camera height" setting make sense.
    auto transformScaled = mmdata::Matrix4x4();
    ok = applySceneScale(
        transform,
        sceneScaleMode,
        sceneScaleDistance_cm,
        transformScaled);
    if (!ok) {
        MMSOLVER_INFO("ERROR: Invalid scene scale. "
             << "sceneScaleDistance_cm=" << sceneScaleDistance_cm
             << "sceneScaleMode" << static_cast<int>(sceneScaleMode));
        return false;
    }

    // Set Camera parameters.
    outCameraParameters.filmBackWidth_mm_ = filmBackWidth_mm;
    outCameraParameters.filmBackHeight_mm_ = filmBackHeight_mm;
    outCameraParameters.principalPoint_ =
        mmcoord::convertPoint2D(
            mmcoord::Point2DSpace::ImageNormalized,
            mmcoord::Point2DSpace::Marker,
            principalPoint,
            filmBackWidth_mm,
            filmBackHeight_mm);
    outCameraParameters.focalLength_mm_ = mmcamera::focalLengthFromAngleOfView(
        angleOfView_radians,
        filmBackWidth_mm);
    outCameraParameters.transformMatrix_ = transformScaled;
    outCameraParameters.vanishingPointA_ =
        mmcoord::convertPoint2D(
            mmcoord::Point2DSpace::ImageNormalized,
            mmcoord::Point2DSpace::Marker,
            vanishingPointA,
            filmBackWidth_mm,
            filmBackHeight_mm);
    outCameraParameters.vanishingPointB_ =
        mmcoord::convertPoint2D(
            mmcoord::Point2DSpace::ImageNormalized,
            mmcoord::Point2DSpace::Marker,
            vanishingPointB,
            filmBackWidth_mm,
            filmBackHeight_mm);
    return true;
}

#undef EPSILON

} // namespace calibrate
