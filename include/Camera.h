/*
 * Camera class represents a viewable camera with a projection matrix.
 */

#ifndef MAYA_MM_SOLVER_CAMERA_H
#define MAYA_MM_SOLVER_CAMERA_H


#include <maya/MStatus.h>
#include <maya/MObject.h>
#include <maya/MMatrix.h>
#include <maya/MString.h>
#include <maya/MPlug.h>

#include <vector>
#include <unordered_map>
#include <memory>

#include <Attr.h>

typedef std::pair<double, MMatrix> DoubleMatrixPair;
typedef std::unordered_map<double, MMatrix> DoubleMatrixMap;
typedef DoubleMatrixMap::const_iterator DoubleMatrixMapCIt;
typedef DoubleMatrixMap::iterator DoubleMatrixMapIt;

MStatus getFrustum(const double depth,
                   const double filmWidth, const double filmHeight,
                   const double filmOffsetX, const double filmOffsetY,
                   const double focal,
                   double &left, double &right,
                   double &top, double &bottom);

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

    Attr &getNearClippingAttr();

    Attr &getFarClippingAttr();

    Attr &getFilmFitAttr();

    Attr &getRenderWidthAttr();

    Attr &getRenderHeightAttr();

    Attr &getRenderAspectAttr();

    double getCameraScaleValue();

    double getNearClippingValue();

    double getFarClippingValue();

    int getFilmFitValue();

    int getRenderWidthValue();

    int getRenderHeightValue();

    double getRenderAspectValue();

    MStatus getFrustum(double depth,
                       double &left, double &right,
                       double &top, double &bottom,
                       const MTime &time,
                       bool withFilmFit = false);

    MStatus getFrustum(double &left, double &right,
                       double &top, double &bottom,
                       const MTime &time,
                       bool withFilmFit = false);

    MStatus getProjMatrix(MMatrix &value, const MTime &time);

    MStatus getProjMatrix(MMatrix &value);

    MStatus getWorldProjMatrix(MMatrix &value, const MTime &time);

    MStatus getWorldProjMatrix(MMatrix &value);

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
