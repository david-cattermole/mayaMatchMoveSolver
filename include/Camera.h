/*
 * Camera class represents a viewable camera with a projection matrix.
 */

#ifndef MAYA_MM_SOLVER_CAMERA_H
#define MAYA_MM_SOLVER_CAMERA_H


#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MPlug.h>

#include <vector>
#include <memory>

#include <glm/glm.hpp>

#include <Attr.h>


class Camera {
public:
    Camera();

    MString getTransformNodeName();

    void setTransformNodeName(MString value);

    MObject getTransformObject();

    MString getShapeNodeName();

    void setShapeNodeName(MString value);

    MObject getShapeObject();

    Attr &getMatrixAttr();

    MMatrix getMatrix();

    Attr &getFilmbackWidthAttr();

    Attr &getFilmbackHeightAttr();

    Attr &getFilmbackOffsetXAttr();

    Attr &getFilmbackOffsetYAttr();

    Attr &getFocalLengthAttr();

    MMatrix getWorldProjMatrix();

private:
    MString m_transformNodeName;
    MObject m_transformObject;

    MString m_shapeNodeName;
    MObject m_shapeObject;

    Attr m_worldMatrix;
    Attr m_filmbackWidth;
    Attr m_filmbackHeight;
    Attr m_filmbackOffsetX;
    Attr m_filmbackOffsetY;
    Attr m_focalLength;
};


typedef std::vector<Camera> CameraList;
typedef CameraList::iterator CameraListIt;

typedef std::shared_ptr<Camera> CameraPtr;
typedef std::vector<std::shared_ptr<Camera> > CameraPtrList;
typedef CameraPtrList::iterator CameraPtrListIt;

#endif //MAYA_MM_SOLVER_CAMERA_H
