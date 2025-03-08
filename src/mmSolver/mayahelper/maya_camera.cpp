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
 * An object for the camera.
 */

#include "maya_camera.h"

// Maya
#include <maya/MDataHandle.h>
#include <maya/MEulerRotation.h>
#include <maya/MFloatMatrix.h>
#include <maya/MFnCamera.h>
#include <maya/MFnMatrixData.h>
#include <maya/MMatrix.h>
#include <maya/MObject.h>
#include <maya/MPoint.h>

// MM Solver
#include "maya_marker.h"
#include "maya_utils.h"
#include "mmSolver/adjust/adjust_defines.h"
#include "mmSolver/utilities/assert_utils.h"
#include "mmSolver/utilities/number_utils.h"

// NOTE: Turning this on will slow down the solve a lot, since
// Maya seems to switch the current time when computing the
// camera projection matrix internally, even when given
// only a DGContext.
#define USE_MAYA_PROJECTION_MATRIX 0

// The node in the Maya scene which contains the render resolution.
#define RENDER_RES_NODE "defaultResolution"

MStatus getAngleOfView(const double filmBackSize_mm,
                       const double focalLength_mm, double &angleOfView,
                       bool asDegrees) {
    angleOfView = 2.0 * atan(filmBackSize_mm * (0.5 / focalLength_mm));
    if (asDegrees) {
        angleOfView *= RADIANS_TO_DEGREES;
    }
    return MS::kSuccess;
}

MStatus getCameraPlaneScale(const double filmBackSize_mm,
                            const double focalLength_mm, double &scale) {
    double aov = 0.0;
    const bool asDegrees = true;
    getAngleOfView(filmBackSize_mm, focalLength_mm, aov, asDegrees);
    // Hard-code 'pi' so we don't have cross-platform problems
    // between Linux and Windows.
    const double pi = 3.14159265358979323846;
    scale = tan(aov * 0.5 * pi / 180.0);
    return MS::kSuccess;
}

MStatus computeFrustumCoordinates(const double focalLength_mm,  // millimetres
                                  const double filmBackWidth_inch,   // inches
                                  const double filmBackHeight_inch,  // inches
                                  const double filmOffsetX_inch,     // inches
                                  const double filmOffsetY_inch,     // inches
                                  const double nearClipPlane_cm,  // centimetres
                                  const double cameraScale, double &left,
                                  double &right, double &top, double &bottom) {
    MStatus status = MS::kSuccess;

    // Convert everything into millimetres
    double filmWidth_mm = filmBackWidth_inch * INCH_TO_MM;
    double filmHeight_mm = filmBackHeight_inch * INCH_TO_MM;
    double offsetX_mm = filmOffsetX_inch * INCH_TO_MM;
    double offsetY_mm = filmOffsetY_inch * INCH_TO_MM;

    double focal_to_near = (nearClipPlane_cm / focalLength_mm) * cameraScale;
    right = focal_to_near * (0.5 * filmWidth_mm + offsetX_mm);
    left = focal_to_near * (-0.5 * filmWidth_mm + offsetX_mm);
    top = focal_to_near * (0.5 * filmHeight_mm + offsetY_mm);
    bottom = focal_to_near * (-0.5 * filmHeight_mm + offsetY_mm);

    return status;
}

MStatus applyFilmFitLogic(
    const double frustumLeft, const double frustumRight,
    const double frustumTop, const double frustumBottom,
    const double imageAspectRatio, const double filmAspectRatio,
    const short filmFit,  // 0=fill, 1=horizontal, 2=vertical, 3=overscan
    double &filmFitScaleX, double &filmFitScaleY, double &screenSizeX,
    double &screenSizeY, double &screenRight, double &screenLeft,
    double &screenTop, double &screenBottom) {
    /*
     * 'Film Fit', from the Maya command documentation...
     *
     * This describes how the digital image (in pixels) relates to the
     * film back. Since the film back is defined in terms of real
     * numbers with some arbitrary film aspect, and the digital image
     * is defined in integer pixels with an equally arbitrary (and
     * different) resolution, relating the two can get complicated.
     * There are 4 choices:
     *
     * Horizontal
     * In this case the digital image is made to fit the film back
     * exactly in the horizontal direction. This then gives each pixel
     * a horizontal size = (film back width) / (horizontal
     * resolution). The pixel height is then = (pixel width) / (pixel
     * aspect ratio). Now that the pixel has a size, resolution gives
     * us a complete image. That image will match the film back
     * exactly in width. It will almost never match in height, either
     * being too tall or too short. By playing with the numbers you
     * can get it pretty close though.
     *
     * Vertical
     * This is the same idea as horizontal fit, only applied
     * vertically. Thus the digital image will match the film back
     * exactly in height, but miss in width.
     *
     * Fill
     * This is a convenience item. The system calculates both
     * horizontal and vertical fits and then applies the one that
     * makes the digital image larger than the film back.
     *
     * Overscan
     * Overscanning the film gate in the camera view allows us to
     * choreograph action outside of the frustum from within the
     * camera view without having to resort to a dolly or zoom. This
     * feature is also essential for animating image planes.
     *
     * Also look at scratchapixel:
     * https://www.scratchapixel.com/lessons/3d-basic-rendering/3d-viewing-pinhole-camera/implementing-virtual-pinhole-camera
     */

    filmFitScaleX = 1.0;
    filmFitScaleY = 1.0;
    screenSizeX = 0.0;
    screenSizeY = 0.0;
    screenLeft = frustumLeft;
    screenRight = frustumRight;
    screenTop = frustumTop;
    screenBottom = frustumBottom;

    switch (filmFit) {
        default:
        case 1:
            // horizontal
            filmFitScaleY = imageAspectRatio / filmAspectRatio;
            screenSizeX = frustumRight - frustumLeft;
            screenSizeY = screenSizeX / imageAspectRatio;
            break;
        case 2:
            // vertical
            filmFitScaleX = 1.0 / (imageAspectRatio / filmAspectRatio);
            screenSizeY = frustumTop - frustumBottom;
            screenSizeX = screenSizeY * imageAspectRatio;
            break;
        case 0:
            // fill
            if (filmAspectRatio > imageAspectRatio) {
                filmFitScaleX = filmAspectRatio / imageAspectRatio;
                screenSizeY = frustumTop - frustumBottom;
                screenSizeX = screenSizeY * imageAspectRatio;
            } else {
                filmFitScaleY = imageAspectRatio / filmAspectRatio;
                screenSizeX = frustumRight - frustumLeft;
                screenSizeY =
                    (screenSizeX * (filmAspectRatio / imageAspectRatio)) /
                    filmAspectRatio;
            }
            break;
        case 3:
            // overscan
            if (filmAspectRatio > imageAspectRatio) {
                filmFitScaleY = imageAspectRatio / filmAspectRatio;
                screenSizeX = frustumRight - frustumLeft;
                screenSizeY = (frustumRight - frustumLeft) / imageAspectRatio;
            } else {
                filmFitScaleX = filmAspectRatio / imageAspectRatio;
                screenSizeX = (frustumRight - frustumLeft) *
                              (imageAspectRatio / filmAspectRatio);
                screenSizeY = frustumTop - frustumBottom;
            }
            break;
    }
    screenRight *= filmFitScaleX;
    screenLeft *= filmFitScaleX;
    screenTop *= filmFitScaleY;
    screenBottom *= filmFitScaleY;

    return MS::kSuccess;
};

enum class FilmFitCorrectionDirection : short {
    kForward = 0,
    kBackward = 1,
};

void applyFilmFitCorrectionScale_horizontal(
    const FilmFitCorrectionDirection direction, const double filmBackAspect,
    const double renderAspect, double &out_x, double &out_y) {
    if (direction == FilmFitCorrectionDirection::kBackward) {
        out_y *= renderAspect / filmBackAspect;
    } else if (direction == FilmFitCorrectionDirection::kForward) {
        out_y *= 1.0 / (renderAspect / filmBackAspect);
    }
}

void applyFilmFitCorrectionScale_vertical(
    const FilmFitCorrectionDirection direction, const double filmBackAspect,
    const double renderAspect, double &out_x, double &out_y) {
    if (direction == FilmFitCorrectionDirection::kBackward) {
        out_x *= 1.0 / (renderAspect / filmBackAspect);
    } else if (direction == FilmFitCorrectionDirection::kForward) {
        out_x *= renderAspect / filmBackAspect;
    }
}

void applyFilmFitCorrectionScale_fill(
    const FilmFitCorrectionDirection direction, const double filmBackAspect,
    const double renderAspect, double &out_x, double &out_y) {
    if (direction == FilmFitCorrectionDirection::kBackward) {
        if (filmBackAspect > renderAspect) {
            out_x *= filmBackAspect / renderAspect;
        } else {
            out_y *= renderAspect / filmBackAspect;
        }
    } else if (direction == FilmFitCorrectionDirection::kForward) {
        if (filmBackAspect > renderAspect) {
            out_x *= renderAspect / filmBackAspect;
        } else {
            out_y *= filmBackAspect / renderAspect;
        }
    }
}

void applyFilmFitCorrectionScale_overscan(
    const FilmFitCorrectionDirection direction, const double filmBackAspect,
    const double renderAspect, double &out_x, double &out_y) {
    if (direction == FilmFitCorrectionDirection::kBackward) {
        if (filmBackAspect > renderAspect) {
            out_y *= renderAspect / filmBackAspect;
        } else {
            out_x *= filmBackAspect / renderAspect;
        }
    } else if (direction == FilmFitCorrectionDirection::kForward) {
        if (filmBackAspect > renderAspect) {
            out_y *= filmBackAspect / renderAspect;
        } else {
            out_x *= renderAspect / filmBackAspect;
        }
    }
}

// This function is used to reverse the scaling effects introduced
// from using a camera projection matrix - such as when a 3D point is
// reprojected into 3D space and then needs to be mapped back into the
// "marker" coordinate space (camera frustum -0.5 to +0.5, with 0.0
// being the center of the camera).
//
// Removes embedded scaling introduced from the projection matrix
// calculation (from 'getProjectionMatrix').
//
// We can apply the forward and backward directions. Applying both
// directions will cancel out and give back the exact same input.
//
// 'filmBackAspect' is the aspect ratio given by the horizontal and
// vertical film aperture.
//
// 'renderAspect' is the aspect ratio of the image width and height
// values used to create the camera projection matrix. For normal Maya
// usage this would be the 'Render Globals' width/height values, but
// for manually constructed camera projection matrices, this is the
// ratio of the image width/height values used.
void applyFilmFitCorrectionScale(const FilmFitCorrectionDirection direction,
                                 const short filmFit,
                                 const double filmBackAspect,
                                 const double renderAspect, double &out_x,
                                 double &out_y) {
    MMSOLVER_ASSERT((filmFit >= 0) && (filmFit < 4),
                    "Bounds checking filmFit value.");

    if (filmFit == 1) {
        applyFilmFitCorrectionScale_horizontal(direction, filmBackAspect,
                                               renderAspect, out_x, out_y);
    } else if (filmFit == 2) {
        applyFilmFitCorrectionScale_vertical(direction, filmBackAspect,
                                             renderAspect, out_x, out_y);
    } else if (filmFit == 0) {
        applyFilmFitCorrectionScale_fill(direction, filmBackAspect,
                                         renderAspect, out_x, out_y);
    } else if (filmFit == 3) {
        applyFilmFitCorrectionScale_overscan(direction, filmBackAspect,
                                             renderAspect, out_x, out_y);
    }
    return;
}

void applyFilmFitCorrectionScaleForward(const short filmFit,
                                        const double filmBackAspect,
                                        const double renderAspect,
                                        double &out_x, double &out_y) {
    const FilmFitCorrectionDirection direction =
        FilmFitCorrectionDirection::kForward;
    applyFilmFitCorrectionScale(direction, filmFit, filmBackAspect,
                                renderAspect, out_x, out_y);
}

void applyFilmFitCorrectionScaleBackward(const short filmFit,
                                         const double filmBackAspect,
                                         const double renderAspect,
                                         double &out_x, double &out_y) {
    const FilmFitCorrectionDirection direction =
        FilmFitCorrectionDirection::kBackward;
    applyFilmFitCorrectionScale(direction, filmFit, filmBackAspect,
                                renderAspect, out_x, out_y);
}

MStatus computeProjectionMatrix(
    const double filmFitScaleX, const double filmFitScaleY,
    const double screenSizeX, const double screenSizeY, const double screenLeft,
    const double screenRight, const double screenTop, const double screenBottom,
    const double nearClipPlane,  // centimetres
    const double farClipPlane,   // centimetres
    MMatrix &projectionMatrix) {
    projectionMatrix[0][0] = 1.0 / (screenSizeX * 0.5) * MM_TO_CM;
    projectionMatrix[0][1] = 0;
    projectionMatrix[0][2] = 0;
    projectionMatrix[0][3] = 0;

    projectionMatrix[1][0] = 0;
    projectionMatrix[1][1] = 1.0 / (screenSizeY * 0.5) * MM_TO_CM;
    projectionMatrix[1][2] = 0;
    projectionMatrix[1][3] = 0;

    projectionMatrix[2][0] =
        (screenRight + screenLeft) / (screenRight - screenLeft) * filmFitScaleX;
    projectionMatrix[2][1] =
        (screenTop + screenBottom) / (screenTop - screenBottom) * filmFitScaleY;
    projectionMatrix[2][2] =
        (farClipPlane + nearClipPlane) / (farClipPlane - nearClipPlane);
    projectionMatrix[2][3] = -1;

    projectionMatrix[3][0] = 0;
    projectionMatrix[3][1] = 0;
    projectionMatrix[3][2] =
        2.0 * farClipPlane * nearClipPlane / (farClipPlane - nearClipPlane);
    projectionMatrix[3][3] = 0;

    return MS::kSuccess;
};

MStatus getProjectionMatrix(
    const double focalLength_mm,       // millimetres
    const double filmBackWidth_inch,   // inches
    const double filmBackHeight_inch,  // inches
    const double filmOffsetX_inch,     // inches
    const double filmOffsetY_inch,     // inches
    const double imageWidth_pixels,    // pixels
    const double imageHeight_pixels,   // pixels
    const short filmFit,  // 0=fill, 1=horizontal, 2=vertical, 3=overscan
    const double nearClipPlane_cm,  // centimetres
    const double farClipPlane_cm,   // centimetres
    const double cameraScale, MMatrix &projectionMatrix) {
    MStatus status = MS::kSuccess;

    double filmAspectRatio = filmBackWidth_inch / filmBackHeight_inch;
    double imageAspectRatio = static_cast<double>(imageWidth_pixels) /
                              static_cast<double>(imageHeight_pixels);

    double left = 0.0;
    double right = 0.0;
    double top = 0.0;
    double bottom = 0.0;
    computeFrustumCoordinates(focalLength_mm, filmBackWidth_inch,
                              filmBackHeight_inch, filmOffsetX_inch,
                              filmOffsetY_inch, nearClipPlane_cm, cameraScale,
                              left, right, top, bottom);

    // Apply 'Film Fit'
    double filmFitScaleX = 1.0;
    double filmFitScaleY = 1.0;
    double screenSizeX = 0.0;
    double screenSizeY = 0.0;
    double screenRight = right;
    double screenLeft = left;
    double screenTop = top;
    double screenBottom = bottom;
    applyFilmFitLogic(left, right, top, bottom, imageAspectRatio,
                      filmAspectRatio, filmFit, filmFitScaleX, filmFitScaleY,
                      screenSizeX, screenSizeY, screenRight, screenLeft,
                      screenTop, screenBottom);

    // Projection Matrix
    computeProjectionMatrix(filmFitScaleX, filmFitScaleY, screenSizeX,
                            screenSizeY, screenLeft, screenRight, screenTop,
                            screenBottom, nearClipPlane_cm, farClipPlane_cm,
                            projectionMatrix);

    return status;
}

Camera::Camera()
    : m_transformNodeName("")
    , m_transformObject()
    , m_shapeNodeName("")
    , m_shapeObject()
    , m_isProjectionDynamic(true)
    , m_matrix()
    , m_filmbackWidth()
    , m_filmbackHeight()
    , m_filmbackOffsetX()
    , m_filmbackOffsetY()
    , m_focalLength()
    , m_cameraScaleCached(false)
    , m_nearClipPlaneCached(false)
    , m_farClipPlaneCached(false)
    , m_filmFitCached(false)
    , m_renderWidthCached(false)
    , m_renderHeightCached(false)
    , m_renderAspectCached(false)
    , m_cameraScaleValue(1.0)
    , m_nearClipPlaneValue(0.1)
    , m_farClipPlaneValue(1000.0)
    , m_filmFitValue(0)
    , m_renderWidthValue(128)
    , m_renderHeightValue(128)
    , m_renderAspectValue(1.0) {
    // Attribute names
    m_matrix.setAttrName("worldMatrix");
    m_filmbackWidth.setAttrName("horizontalFilmAperture");
    m_filmbackHeight.setAttrName("verticalFilmAperture");
    m_filmbackOffsetX.setAttrName("horizontalFilmOffset");
    m_filmbackOffsetY.setAttrName("verticalFilmOffset");
    m_focalLength.setAttrName("focalLength");
    m_cameraScale.setAttrName("cameraScale");
    m_nearClipPlane.setAttrName("nearClipPlane");
    m_farClipPlane.setAttrName("farClipPlane");
    m_filmFit.setAttrName("filmFit");
    m_rotateOrder.setAttrName("rotateOrder");

    // Default Resolution node exists in every scene.
    // These attributes are used when constructing the camera projection matrix
    m_renderWidth.setNodeName(RENDER_RES_NODE);
    m_renderHeight.setNodeName(RENDER_RES_NODE);
    m_renderAspect.setNodeName(RENDER_RES_NODE);
    m_renderWidth.setAttrName("width");
    m_renderHeight.setAttrName("height");
    m_renderAspect.setAttrName("deviceAspectRatio");
}

MString Camera::getTransformNodeName() { return m_transformNodeName; }

void Camera::setTransformNodeName(MString value) {
    if (value != m_transformNodeName) {
        m_transformObject = MObject();
        m_shapeObject = MObject();
        m_matrix.setNodeName(value);
        m_rotateOrder.setNodeName(value);
        m_transformNodeName = value;
    }
}

MObject Camera::getTransformObject() {
    if (m_transformObject.isNull()) {
        MStatus status;
        MString name = Camera::getTransformNodeName();
        status = getAsObject(name, m_transformObject);
        CHECK_MSTATUS(status);
    }
    return m_transformObject;
}

MString Camera::getShapeNodeName() { return m_shapeNodeName; }

void Camera::setShapeNodeName(MString value) {
    if (value != m_shapeNodeName) {
        m_transformObject = MObject();
        m_shapeObject = MObject();
        m_filmbackWidth.setNodeName(value);
        m_filmbackHeight.setNodeName(value);
        m_filmbackOffsetX.setNodeName(value);
        m_filmbackOffsetY.setNodeName(value);
        m_focalLength.setNodeName(value);
        m_cameraScale.setNodeName(value);
        m_nearClipPlane.setNodeName(value);
        m_farClipPlane.setNodeName(value);
        m_filmFit.setNodeName(value);
        m_shapeNodeName = value;
    }
}

MObject Camera::getShapeObject() {
    if (m_shapeObject.isNull()) {
        MStatus status;
        MString name = Camera::getShapeNodeName();
        status = getAsObject(name, m_shapeObject);
        CHECK_MSTATUS(status);
    }
    return m_shapeObject;
}

bool Camera::getProjectionDynamic() const { return m_isProjectionDynamic; }

MStatus Camera::setProjectionDynamic(bool value) {
    MStatus status = MS::kSuccess;
    m_isProjectionDynamic = value;
    return status;
}

Attr &Camera::getMatrixAttr() { return m_matrix; }

Attr &Camera::getRotateOrderAttr() { return m_rotateOrder; }

Attr &Camera::getFilmbackWidthAttr() { return m_filmbackWidth; }

Attr &Camera::getFilmbackHeightAttr() { return m_filmbackHeight; }

Attr &Camera::getFilmbackOffsetXAttr() { return m_filmbackOffsetX; }

Attr &Camera::getFilmbackOffsetYAttr() { return m_filmbackOffsetY; }

Attr &Camera::getFocalLengthAttr() { return m_focalLength; }

Attr &Camera::getCameraScaleAttr() { return m_cameraScale; }

Attr &Camera::getNearClipPlaneAttr() { return m_nearClipPlane; }

Attr &Camera::getFarClipPlaneAttr() { return m_farClipPlane; }

Attr &Camera::getFilmFitAttr() { return m_filmFit; }

Attr &Camera::getRenderWidthAttr() { return m_renderWidth; }

Attr &Camera::getRenderHeightAttr() { return m_renderHeight; }

Attr &Camera::getRenderAspectAttr() { return m_renderAspect; }

double Camera::getFilmbackWidthValue(const MTime &time,
                                     const int32_t timeEvalMode) {
    MStatus status;
    double value = 1.0;
    Attr attr = getFilmbackWidthAttr();
    status = attr.getValue(value, time, timeEvalMode);
    CHECK_MSTATUS(status);
    return value;
}

double Camera::getFilmbackHeightValue(const MTime &time,
                                      const int32_t timeEvalMode) {
    MStatus status;
    double value = 1.0;
    Attr attr = getFilmbackHeightAttr();
    status = attr.getValue(value, time, timeEvalMode);
    CHECK_MSTATUS(status);
    return value;
}

double Camera::getFilmbackOffsetXValue(const MTime &time,
                                       const int32_t timeEvalMode) {
    MStatus status;
    double value = 1.0;
    Attr attr = getFilmbackOffsetXAttr();
    status = attr.getValue(value, time, timeEvalMode);
    CHECK_MSTATUS(status);
    return value;
}

double Camera::getFilmbackOffsetYValue(const MTime &time,
                                       const int32_t timeEvalMode) {
    MStatus status;
    double value = 1.0;
    Attr attr = getFilmbackOffsetYAttr();
    status = attr.getValue(value, time, timeEvalMode);
    CHECK_MSTATUS(status);
    return value;
}

double Camera::getFocalLengthValue(const MTime &time,
                                   const int32_t timeEvalMode) {
    MStatus status;
    double value = 1.0;
    Attr attr = getFocalLengthAttr();
    status = attr.getValue(value, time, timeEvalMode);
    CHECK_MSTATUS(status);
    return value;
}

double Camera::getCameraScaleValue() {
    const int32_t timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
    double value = 1.0;
    if (m_cameraScaleCached) {
        value = m_cameraScaleValue;
    } else {
        MStatus status;
        Attr attr = getCameraScaleAttr();
        status = attr.getValue(m_cameraScaleValue, timeEvalMode);
        CHECK_MSTATUS(status);
        value = m_cameraScaleValue;
        m_cameraScaleCached = true;
    }
    return value;
}

double Camera::getNearClipPlaneValue() {
    const int32_t timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
    double value = 0.1;
    if (m_nearClipPlaneCached) {
        value = m_nearClipPlaneValue;
    } else {
        MStatus status;
        Attr attr = getNearClipPlaneAttr();
        status = attr.getValue(m_nearClipPlaneValue, timeEvalMode);
        CHECK_MSTATUS(status);
        value = m_nearClipPlaneValue;
        m_nearClipPlaneCached = true;
    }
    return value;
}

double Camera::getFarClipPlaneValue() {
    const int32_t timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
    double value = 1000.0;
    if (m_farClipPlaneCached) {
        value = m_farClipPlaneValue;
    } else {
        MStatus status;
        Attr attr = getFarClipPlaneAttr();
        status = attr.getValue(m_farClipPlaneValue, timeEvalMode);
        CHECK_MSTATUS(status);
        value = m_farClipPlaneValue;
        m_farClipPlaneCached = true;
    }
    return value;
}

short Camera::getFilmFitValue() {
    const int32_t timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
    short value = 0;
    if (m_filmFitCached) {
        value = m_filmFitValue;
    } else {
        MStatus status;
        Attr attr = getFilmFitAttr();
        status = attr.getValue(m_filmFitValue, timeEvalMode);
        CHECK_MSTATUS(status);
        value = m_filmFitValue;
        m_filmFitCached = true;
    }
    return value;
}

int32_t Camera::getRenderWidthValue() {
    const int32_t timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
    int32_t value = 128;
    if (m_renderWidthCached) {
        value = m_renderWidthValue;
    } else {
        MStatus status;
        Attr attr = getRenderWidthAttr();
        status = attr.getValue(m_renderWidthValue, timeEvalMode);
        CHECK_MSTATUS(status);
        value = m_renderWidthValue;
        m_renderWidthCached = true;
    }
    return value;
}

int32_t Camera::getRenderHeightValue() {
    const int32_t timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
    int32_t value = 128;
    if (m_renderHeightCached) {
        value = m_renderHeightValue;
    } else {
        MStatus status;
        Attr attr = getRenderHeightAttr();
        status = attr.getValue(m_renderHeightValue, timeEvalMode);
        value = m_renderHeightValue;
        m_renderHeightCached = true;
        CHECK_MSTATUS(status);
    }
    return value;
}

double Camera::getRenderAspectValue() {
    const int32_t timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
    double value = 1.0;
    if (m_renderAspectCached) {
        value = m_renderAspectValue;
    } else {
        MStatus status;
        Attr attr = getRenderAspectAttr();
        status = attr.getValue(m_renderAspectValue, timeEvalMode);
        CHECK_MSTATUS(status);
        value = m_renderAspectValue;
        m_renderAspectCached = true;
    }
    return value;
}

MStatus Camera::getFrustum(double &left, double &right, double &top,
                           double &bottom, const MTime &time,
                           const int32_t timeEvalMode) {
    MStatus status = MS::kSuccess;

    double filmWidth = 0.0;
    double filmHeight = 0.0;
    double focal = 0.0;
    double filmOffsetX = 0.0;
    double filmOffsetY = 0.0;

    // We assume these are animated
    filmWidth = getFilmbackWidthValue(time, timeEvalMode);
    filmHeight = getFilmbackHeightValue(time, timeEvalMode);
    filmOffsetX = getFilmbackOffsetXValue(time, timeEvalMode);
    filmOffsetY = getFilmbackOffsetYValue(time, timeEvalMode);
    focal = getFocalLengthValue(time, timeEvalMode);

    // We assume these are not animated
    double cameraScale = getCameraScaleValue();
    double nearClip = getNearClipPlaneValue();

    computeFrustumCoordinates(focal, filmWidth, filmHeight, filmOffsetX,
                              filmOffsetY, nearClip, cameraScale, left, right,
                              top, bottom);
    return status;
}

MStatus Camera::getProjMatrix(MMatrix &value, const MTime &time,
                              const int32_t timeEvalMode) {
    MStatus status;

    MTime::Unit unit = MTime::uiUnit();
    double timeDouble = time.as(unit);
    DoubleMatrixMapCIt found = m_projMatrixCache.find(timeDouble);

    if (found == m_projMatrixCache.end()) {
        // No entry in the cache... lets compute and add it.

        // Get the projection matrix.
#if USE_MAYA_PROJECTION_MATRIX == 1
        // Querying the projection matrix from Maya at a specific time
        // is slow, therefore using, USE_MAYA_PROJECTION = 0, reproduces Maya's
        // maths while caching various attributes.
        MFnCamera cameraFn(Camera::getShapeObject(), &status);
        MDGContext ctx(time);
        MFloatMatrix floatProjMat_maya =
            cameraFn.projectionMatrix(ctx, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MMatrix floatProjMat = MMatrix(&floatProjMat_maya.matrix[0]);
#else
        short filmFit = 1;  // 1 == Horizontal
        double imageWidth = 640.0;
        double imageHeight = 480.0;
        double filmWidth = 0.0;
        double filmHeight = 0.0;
        double focal = 0.0;
        double filmOffsetX = 0.0;
        double filmOffsetY = 0.0;
        double cameraScale = 1.0;
        double nearClip = 0.1;
        double farClip = 1000.0;

        // We assume these are animated
        filmWidth = getFilmbackWidthValue(time, timeEvalMode);
        filmHeight = getFilmbackHeightValue(time, timeEvalMode);
        filmOffsetX = getFilmbackOffsetXValue(time, timeEvalMode);
        filmOffsetY = getFilmbackOffsetYValue(time, timeEvalMode);
        focal = getFocalLengthValue(time, timeEvalMode);

        // We assume that the following attributes won't be animated, but Maya
        // allows them to be animated.
        cameraScale = getCameraScaleValue();
        // Override the near-clip value because Maya expects this value to
        // be hard-coded (for some crazy reason).
        nearClip = 0.1;  // getNearClipPlaneValue();
        farClip = getFarClipPlaneValue();
        filmFit = getFilmFitValue();

        imageWidth = static_cast<double>(getRenderWidthValue());
        imageHeight = static_cast<double>(getRenderHeightValue());

        // Compute the projection matrix
        status = getProjectionMatrix(
            focal, filmWidth, filmHeight, filmOffsetX, filmOffsetY, imageWidth,
            imageHeight, filmFit, nearClip, farClip, cameraScale, value);
        CHECK_MSTATUS(status);
#endif
        // Add into the cache.
        DoubleMatrixPair timeMatrixPair(timeDouble, value);
        m_projMatrixCache.insert(timeMatrixPair);
    } else {
        // MMSOLVER_MAYA_INFO("camera projection matrix cache hit");
        value = found->second;
    }
    return status;
}

MStatus Camera::getProjMatrix(MMatrix &value, const int32_t timeEvalMode) {
    MTime time = MAnimControl::currentTime();
    return Camera::getProjMatrix(value, time, timeEvalMode);
}

MStatus Camera::getWorldPosition(MPoint &value, const MTime &time,
                                 const int32_t timeEvalMode) {
    MStatus status;

    // Get world matrix at time
    MMatrix worldMat;
    status = m_matrix.getValue(worldMat, time, timeEvalMode);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Position
    value.x = worldMat[3][0];
    value.y = worldMat[3][1];
    value.z = worldMat[3][2];
    value.w = worldMat[3][3];
    value.cartesianize();

    return status;
}

MStatus Camera::getWorldPosition(MPoint &value, const int32_t timeEvalMode) {
    MTime time = MAnimControl::currentTime();
    return Camera::getWorldPosition(value, time, timeEvalMode);
}

MStatus Camera::getForwardDirection(MVector &value, const MTime &time,
                                    const int32_t timeEvalMode) {
    MStatus status;

    // Get world matrix at time
    MMatrix worldMat;
    status = m_matrix.getValue(worldMat, time, timeEvalMode);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    MVector temp(0.0, 0.0, -1.0);
    value = temp * worldMat;
    value.normalize();

    return status;
}

MStatus Camera::getForwardDirection(MVector &value,
                                    const int32_t timeEvalMode) {
    MTime time = MAnimControl::currentTime();
    return Camera::getForwardDirection(value, time, timeEvalMode);
}

MStatus Camera::getWorldProjMatrix(MMatrix &value, const MTime &time,
                                   const int32_t timeEvalMode) {
    MStatus status;

    MTime::Unit unit = MTime::uiUnit();
    double timeDouble = time.as(unit);
    DoubleMatrixMapCIt found = m_worldProjMatrixCache.find(timeDouble);

    if (found == m_worldProjMatrixCache.end()) {
        // No entry in the cache... lets compute and add it.

        // Get world matrix at time
        MMatrix worldMat;
        status = m_matrix.getValue(worldMat, time, timeEvalMode);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        worldMat = worldMat.inverse();

        // Get the projection matrix.
        MMatrix projMat;
        status = Camera::getProjMatrix(projMat, time, timeEvalMode);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        value = worldMat * projMat;

        // Add into the cache.
        DoubleMatrixPair timeMatrixPair(timeDouble, value);
        m_worldProjMatrixCache.insert(timeMatrixPair);
    } else {
        // MMSOLVER_MAYA_INFO("camera world proj matrix cache hit");
        value = found->second;
    }
    return status;
}

MStatus Camera::getRotateOrder(MEulerRotation::RotationOrder &value,
                               const MTime &time, const int32_t timeEvalMode) {
    MStatus status;

    short attr_value = 0;
    m_rotateOrder.getValue(attr_value, time, timeEvalMode);

    switch (attr_value) {
        break;
        case 0:
            value = MEulerRotation::kXYZ;
            break;
        case 1:
            value = MEulerRotation::kYZX;
            break;
        case 2:
            value = MEulerRotation::kZXY;
            break;
        case 3:
            value = MEulerRotation::kXZY;
            break;
        case 4:
            value = MEulerRotation::kYXZ;
            break;
        case 5:
            value = MEulerRotation::kZYX;
            break;
        default:
            value = MEulerRotation::kXYZ;
    }

    return status;
}

MStatus Camera::clearAuxilaryAttrsCache() {
    // Re-evaluation next time an attribute value is queried.
    m_cameraScaleCached = false;
    m_nearClipPlaneCached = false;
    m_farClipPlaneCached = false;
    m_filmFitCached = false;
    m_renderWidthCached = false;
    m_renderHeightCached = false;
    m_renderAspectCached = false;
    return MS::kSuccess;
}

MStatus Camera::clearProjMatrixCache() {
    m_projMatrixCache.clear();
    return MS::kSuccess;
}

MStatus Camera::getWorldProjMatrix(MMatrix &value, const int32_t timeEvalMode) {
    MTime time = MAnimControl::currentTime();
    return Camera::getWorldProjMatrix(value, time, timeEvalMode);
}

MStatus Camera::clearWorldProjMatrixCache() {
    m_worldProjMatrixCache.clear();
    return MS::kSuccess;
}

MStatus Camera::clearAttrValueCache() {
    clearProjMatrixCache();
    clearWorldProjMatrixCache();
    clearAuxilaryAttrsCache();
    return MS::kSuccess;
}
