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

#include <maya/MPlug.h>
#include <maya/MObject.h>
#include <maya/MDataHandle.h>
#include <maya/MFnMatrixData.h>
#include <maya/MMatrix.h>
#include <maya/MFloatMatrix.h>
#include <maya/MPoint.h>
#include <maya/MFnCamera.h>

#include <utilities/numberUtils.h>

#include <mayaUtils.h>
#include <Marker.h>
#include <Camera.h>

// NOTE: Turning this on will slow down the solve a lot, since
// Maya seems to switch the current time when computing the
// camera projection matrix internally, even when given
// only a DGContext.
#define USE_MAYA_PROJECTION_MATRIX 0

// The node in the Maya scene which containts the render resolution.
#define RENDER_RES_NODE "defaultResolution"


MStatus getAngleOfView(
        const double filmBackSize,
        const double focalLength,
        double &angleOfView,
        bool asDegrees) {
    angleOfView = 2.0 * atan(filmBackSize * (0.5 / focalLength));
    if (asDegrees) {
        angleOfView *= RADIANS_TO_DEGREES;
    }
    return MS::kSuccess;
}


MStatus getCameraPlaneScale(
        const double filmBackSize,
        const double focalLength,
        double &scale) {
    double aov = 0.0;
    const bool asDegrees = true;
    getAngleOfView(filmBackSize, focalLength, aov, asDegrees);
    // Hard-code 'pi' so we don't have cross-platform problems
    // between Linux and Windows.
    const double pi = 3.14159265358979323846;
    scale = tan(aov * 0.5 * pi / 180.0);
    return MS::kSuccess;
}


MStatus computeFrustumCoordinates(
        const double focalLength,     // millimetres
        const double filmBackWidth,   // inches
        const double filmBackHeight,  // inches
        const double filmOffsetX,     // inches
        const double filmOffsetY,     // inches
        const double nearClipPlane,   // centimetres
        const double cameraScale,
        double &left, double &right,
        double &top, double &bottom) {
    MStatus status = MS::kSuccess;

    // Convert everything into millimetres
    double filmWidth = filmBackWidth * INCH_TO_MM;
    double filmHeight = filmBackHeight * INCH_TO_MM;
    double offsetX = filmOffsetX * INCH_TO_MM;
    double offsetY = filmOffsetY * INCH_TO_MM;

    double focal_to_near = (nearClipPlane / focalLength) * cameraScale;
    right = focal_to_near * (0.5 * filmWidth + offsetX);
    left = focal_to_near * (-0.5 * filmWidth + offsetX);
    top = focal_to_near * (0.5 * filmHeight + offsetY);
    bottom = focal_to_near * (-0.5 * filmHeight + offsetY);

    return status;
}


MStatus applyFilmFitLogic(
        const double frustumLeft, const double frustumRight,
        const double frustumTop, const double frustumBottom,
        const double imageAspectRatio, const double filmAspectRatio,
        const int filmFit,  // 0=fill, 1=horizontal, 2=vertical, 3=overscan
        double &filmFitScaleX, double &filmFitScaleY,
        double &screenSizeX, double &screenSizeY,
        double &screenRight, double &screenLeft,
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
                screenSizeY = (screenSizeX * (filmAspectRatio / imageAspectRatio)) / filmAspectRatio;
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
                screenSizeX = (frustumRight - frustumLeft) * (imageAspectRatio / filmAspectRatio);
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


MStatus computeProjectionMatrix(
        const double filmFitScaleX,
        const double filmFitScaleY,
        const double screenSizeX,
        const double screenSizeY,
        const double screenLeft,
        const double screenRight,
        const double screenTop,
        const double screenBottom,
        const double nearClipPlane, // centimetres
        const double farClipPlane,  // centimetres
        MMatrix &projectionMatrix) {

    projectionMatrix[0][0] = 1.0 / (screenSizeX * 0.5) * MM_TO_CM;
    projectionMatrix[0][1] = 0;
    projectionMatrix[0][2] = 0;
    projectionMatrix[0][3] = 0;

    projectionMatrix[1][0] = 0;
    projectionMatrix[1][1] = 1.0 / (screenSizeY * 0.5) * MM_TO_CM;
    projectionMatrix[1][2] = 0;
    projectionMatrix[1][3] = 0;

    projectionMatrix[2][0] = (screenRight + screenLeft) / (screenRight - screenLeft) * filmFitScaleX;
    projectionMatrix[2][1] = (screenTop + screenBottom) / (screenTop - screenBottom) * filmFitScaleY;
    projectionMatrix[2][2] = (farClipPlane + nearClipPlane) / (farClipPlane - nearClipPlane);
    projectionMatrix[2][3] = -1;

    projectionMatrix[3][0] = 0;
    projectionMatrix[3][1] = 0;
    projectionMatrix[3][2] = 2.0 * farClipPlane * nearClipPlane / (farClipPlane - nearClipPlane);
    projectionMatrix[3][3] = 0;

    return MS::kSuccess;
};


MStatus getProjectionMatrix(
        const double focalLength,     // millimetres
        const double filmBackWidth,   // inches
        const double filmBackHeight,  // inches
        const double filmOffsetX,     // inches
        const double filmOffsetY,     // inches
        const double imageWidth,      // pixels
        const double imageHeight,     // pixels
        const int filmFit,  // 0=fill, 1=horizontal, 2=vertical, 3=overscan
        const double nearClipPlane,
        const double farClipPlane,
        const double cameraScale,
        MMatrix &projectionMatrix) {
    MStatus status = MS::kSuccess;

    double filmAspectRatio = filmBackWidth / filmBackHeight;
    double imageAspectRatio = (double)imageWidth / (double)imageHeight;

    double left = 0.0;
    double right = 0.0;
    double top = 0.0;
    double bottom = 0.0;
    computeFrustumCoordinates(focalLength,
                              filmBackWidth, filmBackHeight,
                              filmOffsetX, filmOffsetY,
                              nearClipPlane, cameraScale,
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
    applyFilmFitLogic(
            left, right, top, bottom,
            imageAspectRatio, filmAspectRatio,
            filmFit,
            filmFitScaleX, filmFitScaleY,
            screenSizeX, screenSizeY,
            screenRight, screenLeft, screenTop, screenBottom);

    // Projection Matrix
    computeProjectionMatrix(
            filmFitScaleX, filmFitScaleY,
            screenSizeX, screenSizeY,
            screenLeft, screenRight, screenTop, screenBottom,
            nearClipPlane, farClipPlane,
            projectionMatrix);

    return status;
}


Camera::Camera() :
        m_transformNodeName(""),
        m_transformObject(),
        m_shapeNodeName(""),
        m_shapeObject(),
        m_matrix(),
        m_filmbackWidth(),
        m_filmbackHeight(),
        m_filmbackOffsetX(),
        m_filmbackOffsetY(),
        m_focalLength(),
        m_cameraScaleCached(false),
        m_nearClipPlaneCached(false),
        m_farClipPlaneCached(false),
        m_filmFitCached(false),
        m_renderWidthCached(false),
        m_renderHeightCached(false),
        m_renderAspectCached(false),
        m_cameraScaleValue(1.0),
        m_nearClipPlaneValue(0.1),
        m_farClipPlaneValue(1000.0),
        m_filmFitValue(0),
        m_renderWidthValue(128),
        m_renderHeightValue(128),
        m_renderAspectValue(1.0) {

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

    // Default Resolution node exists in every scene.
    // These attributes are used when constructing the camera projection matrix
    m_renderWidth.setNodeName(RENDER_RES_NODE);
    m_renderHeight.setNodeName(RENDER_RES_NODE);
    m_renderAspect.setNodeName(RENDER_RES_NODE);
    m_renderWidth.setAttrName("width");
    m_renderHeight.setAttrName("height");
    m_renderAspect.setAttrName("deviceAspectRatio");
}

MString Camera::getTransformNodeName() {
    return m_transformNodeName;
}

void Camera::setTransformNodeName(MString value) {
    if (value != m_transformNodeName) {
        m_matrix.setNodeName(value);
    }
    m_transformNodeName = value;
}

MObject Camera::getTransformObject() {
    MStatus status;
    MString name = Camera::getTransformNodeName();
    status = getAsObject(name, m_transformObject);
    return m_transformObject;
}

MString Camera::getShapeNodeName() {
    return m_shapeNodeName;
}

void Camera::setShapeNodeName(MString value) {
    if (value != m_shapeNodeName) {
        m_filmbackWidth.setNodeName(value);
        m_filmbackHeight.setNodeName(value);
        m_filmbackOffsetX.setNodeName(value);
        m_filmbackOffsetY.setNodeName(value);
        m_focalLength.setNodeName(value);
        m_cameraScale.setNodeName(value);
        m_nearClipPlane.setNodeName(value);
        m_farClipPlane.setNodeName(value);
        m_filmFit.setNodeName(value);
    }
    m_shapeNodeName = value;
}

MObject Camera::getShapeObject() {
    MStatus status;
    MString name = Camera::getShapeNodeName();
    MObject object;
    status = getAsObject(name, object);
    return object;
}

bool Camera::getProjectionDynamic() const {
    return m_isProjectionDynamic;
}

MStatus Camera::setProjectionDynamic(bool value) {
    MStatus status = MS::kSuccess;
    m_isProjectionDynamic = value;
    return status;
}

Attr &Camera::getMatrixAttr() {
    return m_matrix;
}

Attr &Camera::getFilmbackWidthAttr() {
    return m_filmbackWidth;
}

Attr &Camera::getFilmbackHeightAttr() {
    return m_filmbackHeight;
}

Attr &Camera::getFilmbackOffsetXAttr() {
    return m_filmbackOffsetX;
}

Attr &Camera::getFilmbackOffsetYAttr() {
    return m_filmbackOffsetY;
}

Attr &Camera::getFocalLengthAttr() {
    return m_focalLength;
}

Attr &Camera::getCameraScaleAttr() {
    return m_cameraScale;
}

Attr &Camera::getNearClipPlaneAttr() {
    return m_nearClipPlane;
}

Attr &Camera::getFarClipPlaneAttr() {
    return m_farClipPlane;
}

Attr &Camera::getFilmFitAttr() {
    return m_filmFit;
}

Attr &Camera::getRenderWidthAttr() {
    return m_renderWidth;
}

Attr &Camera::getRenderHeightAttr() {
    return m_renderHeight;
}

Attr &Camera::getRenderAspectAttr() {
    return m_renderAspect;
}


double Camera::getFilmbackWidthValue(const MTime &time) {
    MStatus status;
    double value = 1.0;
    Attr attr = getFilmbackWidthAttr();
    status = attr.getValue(value, time);
    CHECK_MSTATUS(status);
    return value;
}

double Camera::getFilmbackHeightValue(const MTime &time) {
    MStatus status;
    double value = 1.0;
    Attr attr = getFilmbackHeightAttr();
    status = attr.getValue(value, time);
    CHECK_MSTATUS(status);
    return value;
}

double Camera::getFilmbackOffsetXValue(const MTime &time) {
    MStatus status;
    double value = 1.0;
    Attr attr = getFilmbackOffsetXAttr();
    status = attr.getValue(value, time);
    CHECK_MSTATUS(status);
    return value;
}

double Camera::getFilmbackOffsetYValue(const MTime &time) {
    MStatus status;
    double value = 1.0;
    Attr attr = getFilmbackOffsetYAttr();
    status = attr.getValue(value, time);
    CHECK_MSTATUS(status);
    return value;
}

double Camera::getFocalLengthValue(const MTime &time) {
    MStatus status;
    double value = 1.0;
    Attr attr = getFocalLengthAttr();
    status = attr.getValue(value, time);
    CHECK_MSTATUS(status);
    return value;
}

double Camera::getCameraScaleValue() {
    double value = 1.0;
    if (m_cameraScaleCached) {
        value = m_cameraScaleValue;
    } else {
        MStatus status;
        Attr attr = getCameraScaleAttr();
        status = attr.getValue(m_cameraScaleValue);
        value = m_cameraScaleValue;
        m_cameraScaleCached = true;
        CHECK_MSTATUS(status);
    }
    return value;
}

double Camera::getNearClipPlaneValue() {
    double value = 0.1;
    if (m_nearClipPlaneCached) {
        value = m_nearClipPlaneValue;
    } else {
        MStatus status;
        Attr attr = getNearClipPlaneAttr();
        status = attr.getValue(m_nearClipPlaneValue);
        value = m_nearClipPlaneValue;
        m_nearClipPlaneCached = true;
        CHECK_MSTATUS(status);
    }
    return value;
}

double Camera::getFarClipPlaneValue() {
    double value = 1000.0;
    if (m_farClipPlaneCached) {
        value = m_farClipPlaneValue;
    } else {
        MStatus status;
        Attr attr = getFarClipPlaneAttr();
        status = attr.getValue(m_farClipPlaneValue);
        value = m_farClipPlaneValue;
        m_farClipPlaneCached = true;
        CHECK_MSTATUS(status);
    }
    return value;
}

int Camera::getFilmFitValue() {
    int value = 0;
    if (m_filmFitCached) {
        value = m_filmFitValue;
    } else {
        MStatus status;
        Attr attr = getFilmFitAttr();
        status = attr.getValue(m_filmFitValue);
        value = m_filmFitValue;
        m_filmFitCached = true;
        CHECK_MSTATUS(status);
    }
    return value;
}

int Camera::getRenderWidthValue() {
    int value = 128;
    if (m_renderWidthCached) {
        value = m_renderWidthValue;
    } else {
        MStatus status;
        Attr attr = getRenderWidthAttr();
        status = attr.getValue(m_renderWidthValue);
        value = m_renderWidthValue;
        m_renderWidthCached = true;
        CHECK_MSTATUS(status);
    }
    return value;
}

int Camera::getRenderHeightValue() {
    int value = 128;
    if (m_renderHeightCached) {
        value = m_renderHeightValue;
    } else {
        MStatus status;
        Attr attr = getRenderHeightAttr();
        status = attr.getValue(m_renderHeightValue);
        value = m_renderHeightValue;
        m_renderHeightCached = true;
        CHECK_MSTATUS(status);
    }
    return value;
}

double Camera::getRenderAspectValue() {
    double value = 1.0;
    if (m_renderAspectCached) {
        value = m_renderAspectValue;
    } else {
        MStatus status;
        Attr attr = getRenderAspectAttr();
        status = attr.getValue(m_renderAspectValue);
        value = m_renderAspectValue;
        m_renderAspectCached = true;
        CHECK_MSTATUS(status);
    }
    return value;
}

MStatus Camera::getFrustum(
        double &left, double &right,
        double &top, double &bottom,
        const MTime &time) {
    MStatus status = MS::kSuccess;

    double filmWidth = 0.0;
    double filmHeight = 0.0;
    double focal = 0.0;
    double filmOffsetX = 0.0;
    double filmOffsetY = 0.0;

    // We assume these are animated
    filmWidth = getFilmbackWidthValue(time);
    filmHeight = getFilmbackHeightValue(time);
    filmOffsetX = getFilmbackOffsetXValue(time);
    filmOffsetY = getFilmbackOffsetYValue(time);
    focal = getFocalLengthValue(time);

    // We assume these are not animated
    double cameraScale = getCameraScaleValue();
    double nearClip = getNearClipPlaneValue();

    computeFrustumCoordinates(focal,
                              filmWidth, filmHeight,
                              filmOffsetX, filmOffsetY,
                              nearClip, cameraScale,
                              left, right,
                              top, bottom);
    return status;
}

MStatus Camera::getProjMatrix(MMatrix &value, const MTime &time) {
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
        MFloatMatrix floatProjMat_maya = cameraFn.projectionMatrix(ctx, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MMatrix floatProjMat = MMatrix(&floatProjMat_maya.matrix[0]);
#else
        int filmFit = 1;
        double imageWidth = 640.0;
        double imageHeight = 480.0;
        double imageAspectRatio = 1.0;
        double filmWidth = 0.0;
        double filmHeight = 0.0;
        double focal = 0.0;
        double filmOffsetX = 0.0;
        double filmOffsetY = 0.0;
        double cameraScale = 1.0;
        double nearClip = 0.1;
        double farClip = 1000.0;

        // We assume these are animated
        filmWidth = getFilmbackWidthValue(time);
        filmHeight = getFilmbackHeightValue(time);
        filmOffsetX = getFilmbackOffsetXValue(time);
        filmOffsetY = getFilmbackOffsetYValue(time);
        focal = getFocalLengthValue(time);

        // We assume that the following attributes won't be animated, but Maya
        // allows them to be animated.
        cameraScale = getCameraScaleValue();
        // override because Maya expects this value to be hard-coded,
        // for some crazy reason.
        nearClip = 0.1;  // getNearClipPlaneValue();
        farClip = getFarClipPlaneValue();
        filmFit = getFilmFitValue();

        imageWidth = static_cast<double>(getRenderWidthValue());
        imageHeight = static_cast<double>(getRenderHeightValue());

        // Compute the projection matrix
        status = getProjectionMatrix(focal,
                                     filmWidth, filmHeight,
                                     filmOffsetX, filmOffsetY,
                                     imageWidth, imageHeight,
                                     filmFit,
                                     nearClip, farClip,
                                     cameraScale,
                                     value);
        CHECK_MSTATUS(status);
#endif
        // Add into the cache.
        DoubleMatrixPair timeMatrixPair(timeDouble, value);
        m_projMatrixCache.insert(timeMatrixPair);
    } else {
        // INFO("camera projection matrix cache hit");
        value = found->second;
    }
    return status;
}

MStatus Camera::getProjMatrix(MMatrix &value) {
    MTime time = MAnimControl::currentTime();
    return Camera::getProjMatrix(value, time);
}


MStatus Camera::getWorldPosition(MPoint &value, const MTime &time) {
    MStatus status;

    MTime::Unit unit = MTime::uiUnit();
    double timeDouble = time.as(unit);

    // Get world matrix at time
    MMatrix worldMat;
    status = m_matrix.getValue(worldMat, time);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Position
    value.x = worldMat[3][0];
    value.y = worldMat[3][1];
    value.z = worldMat[3][2];
    value.w = worldMat[3][3];
    value.cartesianize();

    return status;
}

MStatus Camera::getWorldPosition(MPoint &value) {
    MTime time = MAnimControl::currentTime();
    return Camera::getWorldPosition(value, time);
}


MStatus Camera::getForwardDirection(MVector &value, const MTime &time) {
    MStatus status;

    MTime::Unit unit = MTime::uiUnit();
    double timeDouble = time.as(unit);

    // Get world matrix at time
    MMatrix worldMat;
    status = m_matrix.getValue(worldMat, time);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    MVector temp(0.0, 0.0, -1.0);
    value = temp * worldMat;
    value.normalize();

    return status;
}

MStatus Camera::getForwardDirection(MVector &value) {
    MTime time = MAnimControl::currentTime();
    return Camera::getForwardDirection(value, time);
}


MStatus Camera::getWorldProjMatrix(MMatrix &value, const MTime &time) {
    MStatus status;

    MTime::Unit unit = MTime::uiUnit();
    double timeDouble = time.as(unit);
    DoubleMatrixMapCIt found = m_worldProjMatrixCache.find(timeDouble);

    if (found == m_worldProjMatrixCache.end()) {
        // No entry in the cache... lets compute and add it.

        // Get world matrix at time
        MMatrix worldMat;
        status = m_matrix.getValue(worldMat, time);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        worldMat = worldMat.inverse();

        // Get the projection matrix.
        MMatrix projMat;
        status = Camera::getProjMatrix(projMat, time);

        value = worldMat * projMat;

        // Add into the cache.
        DoubleMatrixPair timeMatrixPair(timeDouble, value);
        m_worldProjMatrixCache.insert(timeMatrixPair);
    } else {
        // INFO("camera world proj matrix cache hit");
        value = found->second;
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

MStatus Camera::getWorldProjMatrix(MMatrix &value) {
    MTime time = MAnimControl::currentTime();
    return Camera::getWorldProjMatrix(value, time);
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

