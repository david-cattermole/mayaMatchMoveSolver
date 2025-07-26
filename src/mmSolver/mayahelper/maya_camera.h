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

#ifndef MM_SOLVER_MAYA_HELPER_MAYA_CAMERA_H
#define MM_SOLVER_MAYA_HELPER_MAYA_CAMERA_H

// STL
#include <cmath>
#include <memory>
#include <unordered_map>  // unordered_map
#include <vector>

// Maya
#include <maya/MEulerRotation.h>
#include <maya/MMatrix.h>
#include <maya/MObject.h>
#include <maya/MPoint.h>
#include <maya/MStatus.h>
#include <maya/MString.h>
#include <maya/MVector.h>

#include "maya_attr.h"
#include "mmSolver/utilities/number_utils.h"

typedef std::pair<double, MMatrix> DoubleMatrixPair;
typedef std::unordered_map<double, MMatrix> DoubleMatrixMap;
typedef DoubleMatrixMap::const_iterator DoubleMatrixMapCIt;
typedef DoubleMatrixMap::iterator DoubleMatrixMapIt;

MStatus getAngleOfView(const double filmBackSize, const double focalLength,
                       double &angleOfView, bool asDegrees = true);

MStatus getCameraPlaneScale(const double filmBackSize, const double focalLength,
                            double &scale);

MStatus computeFrustumCoordinates(const double focalLength,     // millimetres
                                  const double filmBackWidth,   // inches
                                  const double filmBackHeight,  // inches
                                  const double filmOffsetX,     // inches
                                  const double filmOffsetY,     // inches
                                  const double nearClipPlane,   // centimetres
                                  const double cameraScale, double &left,
                                  double &right, double &top, double &bottom);

MStatus applyFilmFitLogic(
    const double frustumLeft, const double frustumRight,
    const double frustumTop, const double frustumBottom,
    const double imageAspectRatio, const double filmAspectRatio,
    const short filmFit,  // 0=fill, 1=horizontal, 2=vertical, 3=overscan
    double &filmFitScaleX, double &filmFitScaleY, double &screenSizeX,
    double &screenSizeY, double &screenRight, double &screenLeft,
    double &screenTop, double &screenBottom);

void applyFilmFitCorrectionScaleForward(
    const short filmFit,  // 0=fill, 1=horizontal, 2=vertical, 3=overscan
    const double filmBackAspect, const double renderAspect, double &out_x,
    double &out_y);

void applyFilmFitCorrectionScaleBackward(
    const short filmFit,  // 0=fill, 1=horizontal, 2=vertical, 3=overscan
    const double filmBackAspect, const double renderAspect, double &out_x,
    double &out_y);

MStatus computeProjectionMatrix(
    const double filmFitScaleX, const double filmFitScaleY,
    const double screenSizeX, const double screenSizeY, const double screenLeft,
    const double screenRight, const double screenTop, const double screenBottom,
    const double nearClipPlane,  // centimetres
    const double farClipPlane,   // centimetres
    MMatrix &projectionMatrix);

MStatus getProjectionMatrix(
    const double focalLength,     // millimetres
    const double filmBackWidth,   // inches
    const double filmBackHeight,  // inches
    const double filmOffsetX,     // inches
    const double filmOffsetY,     // inches
    const double imageWidth,      // pixels
    const double imageHeight,     // pixels
    const short filmFit,  // 0=fill, 1=horizontal, 2=vertical, 3=overscan
    const double nearClipPlane, const double farClipPlane,
    const double cameraScale, MMatrix &projectionMatrix);

class Camera {
public:
    Camera();

    MString getTransformNodeName();
    MString getShapeNodeName();

    void setTransformNodeName(MString value);
    void setShapeNodeName(MString value);

    MObject getTransformObject();
    MObject getShapeObject();

    MString getTransformLongNodeName();
    MString getShapeLongNodeName();

    // TODO: Use 'Projection Dynamic' to tell the solver that
    // the projection matrix of the camera will change over time.
    // For example, we can tell if the projection matrix is dynamic
    // over time if any of the necessary input variables vary over
    // time. This flag could help speed up solving.
    bool getProjectionDynamic() const;

    MStatus setProjectionDynamic(bool value);

    Attr &getMatrixAttr();
    Attr &getRotateOrderAttr();

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

    double getFilmbackWidthValue(const MTime &time, const int32_t timeEvalMode);
    double getFilmbackHeightValue(const MTime &time,
                                  const int32_t timeEvalMode);
    double getFilmbackOffsetXValue(const MTime &time,
                                   const int32_t timeEvalMode);
    double getFilmbackOffsetYValue(const MTime &time,
                                   const int32_t timeEvalMode);

    double getFocalLengthValue(const MTime &time, const int32_t timeEvalMode);
    double getCameraScaleValue();
    double getNearClipPlaneValue();
    double getFarClipPlaneValue();
    short getFilmFitValue();

    int32_t getRenderWidthValue();
    int32_t getRenderHeightValue();
    double getRenderAspectValue();

    MStatus getFrustum(double &left, double &right, double &top, double &bottom,
                       const MTime &time, const int32_t timeEvalMode);

    MStatus getProjMatrix(MMatrix &value, const MTime &time,
                          const int32_t timeEvalMode);

    MStatus getProjMatrix(MMatrix &value, const int32_t timeEvalMode);

    MStatus getWorldPosition(MPoint &value, const MTime &time,
                             const int32_t timeEvalMode);

    MStatus getWorldPosition(MPoint &value, const int32_t timeEvalMode);

    MStatus getForwardDirection(MVector &value, const MTime &time,
                                const int32_t timeEvalMode);

    MStatus getForwardDirection(MVector &value, const int32_t timeEvalMode);

    MStatus getWorldProjMatrix(MMatrix &value, const MTime &time,
                               const int32_t timeEvalMode);

    MStatus getWorldProjMatrix(MMatrix &value, const int32_t timeEvalMode);

    MStatus getRotateOrder(MEulerRotation::RotationOrder &value,
                           const MTime &time, const int32_t timeEvalMode);

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
    Attr m_rotateOrder;

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
    short m_filmFitValue;
    int32_t m_renderWidthValue;
    int32_t m_renderHeightValue;
    double m_renderAspectValue;

    DoubleMatrixMap m_projMatrixCache;
    DoubleMatrixMap m_worldProjMatrixCache;
};

typedef std::vector<Camera> CameraList;
typedef CameraList::iterator CameraListIt;

typedef std::shared_ptr<Camera> CameraPtr;
typedef std::vector<std::shared_ptr<Camera> > CameraPtrList;
typedef CameraPtrList::iterator CameraPtrListIt;

#endif  // MM_SOLVER_MAYA_HELPER_MAYA_CAMERA_H
