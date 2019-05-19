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
 * Camera class represents a viewable camera with a projection matrix.
 */

#ifndef MAYA_MM_SOLVER_CAMERA_H
#define MAYA_MM_SOLVER_CAMERA_H

#include <maya/MStatus.h>
#include <maya/MObject.h>
#include <maya/MMatrix.h>
#include <maya/MPoint.h>
#include <maya/MVector.h>
#include <maya/MString.h>
#include <maya/MPlug.h>

#include <cmath>
#include <vector>
#include <unordered_map>  // unordered_map
#include <memory>

#include <utilities/numberUtils.h>

#include <Attr.h>

typedef std::pair<double, MMatrix> DoubleMatrixPair;
typedef std::unordered_map<double, MMatrix> DoubleMatrixMap;
typedef DoubleMatrixMap::const_iterator DoubleMatrixMapCIt;
typedef DoubleMatrixMap::iterator DoubleMatrixMapIt;


inline
MStatus getAngleOfView(
        const double filmBackSize,
        const double focalLength,
        double &angleOfView,
        bool asDegrees = true) {
    angleOfView = 2.0 * atan(filmBackSize * (0.5 / focalLength));
    if (asDegrees) {
        angleOfView *= RADIANS_TO_DEGREES;
    }
    return MS::kSuccess;
}


inline
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


inline
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

inline
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


inline
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

inline
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


class Camera {
public:
    Camera();

    MString getTransformNodeName();

    void setTransformNodeName(MString value);

    MObject getTransformObject();

    MString getShapeNodeName();

    void setShapeNodeName(MString value);

    MObject getShapeObject();

    // TODO: Use 'Projection Dynamic' to tell the solver that
    // the projection matrix of the camera will change over time.
    // For example, we can tell if the projection matrix is dynamic
    // over time if any of the necessary input variables vary over
    // time. This flag could help speed up solving.
    bool getProjectionDynamic() const;

    MStatus setProjectionDynamic(bool value);

    Attr &getMatrixAttr();

    Attr &getFilmbackWidthAttr();

    Attr &getFilmbackHeightAttr();

    Attr &getFilmbackOffsetXAttr();

    Attr &getFilmbackOffsetYAttr();

    Attr &getFocalLengthAttr();

    Attr &getCameraScaleAttr();

    Attr &getNearClipPlaneAttr();

    Attr &getFarClipPlaneAttr();

    Attr &getFilmFitAttr();

    Attr &getRenderWidthAttr();

    Attr &getRenderHeightAttr();

    Attr &getRenderAspectAttr();

    double getFilmbackWidthValue(const MTime &time);

    double getFilmbackHeightValue(const MTime &time);

    double getFilmbackOffsetXValue(const MTime &time);

    double getFilmbackOffsetYValue(const MTime &time);

    double getFocalLengthValue(const MTime &time);

    double getCameraScaleValue();

    double getNearClipPlaneValue();

    double getFarClipPlaneValue();

    int getFilmFitValue();

    int getRenderWidthValue();

    int getRenderHeightValue();

    double getRenderAspectValue();

    MStatus getFrustum(
            double &left, double &right,
            double &top, double &bottom,
            const MTime &time);

    MStatus getProjMatrix(MMatrix &value, const MTime &time);

    MStatus getProjMatrix(MMatrix &value);

    MStatus getWorldPosition(MPoint &value, const MTime &time);

    MStatus getWorldPosition(MPoint &value);

    MStatus getForwardDirection(MVector &value, const MTime &time);

    MStatus getForwardDirection(MVector &value);

    MStatus getWorldProjMatrix(MMatrix &value, const MTime &time);

    MStatus getWorldProjMatrix(MMatrix &value);

    MStatus clearAuxilaryAttrsCache();

    MStatus clearProjMatrixCache();

    MStatus clearWorldProjMatrixCache();

    MStatus clearAttrValueCache();

private:
    MString m_transformNodeName;
    MObject m_transformObject;

    MString m_shapeNodeName;
    MObject m_shapeObject;

    // TODO: Use this variable in the solver.
    bool m_isProjectionDynamic;

    Attr m_matrix;
    Attr m_filmbackWidth;
    Attr m_filmbackHeight;
    Attr m_filmbackOffsetX;
    Attr m_filmbackOffsetY;
    Attr m_focalLength;
    Attr m_cameraScale;
    Attr m_nearClipPlane;
    Attr m_farClipPlane;
    Attr m_filmFit;
    Attr m_renderWidth;
    Attr m_renderHeight;
    Attr m_renderAspect;

    bool m_cameraScaleCached;
    bool m_nearClipPlaneCached;
    bool m_farClipPlaneCached;
    bool m_filmFitCached;
    bool m_renderWidthCached;
    bool m_renderHeightCached;
    bool m_renderAspectCached;

    double m_cameraScaleValue;
    double m_nearClipPlaneValue;
    double m_farClipPlaneValue;
    int    m_filmFitValue;
    int    m_renderWidthValue;
    int    m_renderHeightValue;
    double m_renderAspectValue;

    DoubleMatrixMap m_projMatrixCache;
    DoubleMatrixMap m_worldProjMatrixCache;
};

typedef std::vector<Camera> CameraList;
typedef CameraList::iterator CameraListIt;

typedef std::shared_ptr<Camera> CameraPtr;
typedef std::vector<std::shared_ptr<Camera> > CameraPtrList;
typedef CameraPtrList::iterator CameraPtrListIt;

#endif //MAYA_MM_SOLVER_CAMERA_H
