/*
 *
 */

#include <maya/MPlug.h>
#include <maya/MObject.h>
#include <maya/MDataHandle.h>
#include <maya/MFnMatrixData.h>
#include <maya/MMatrix.h>
#include <maya/MFloatMatrix.h>
#include <maya/MPoint.h>
#include <maya/MFnCamera.h>

#include <glm/glm.hpp>

#include <utilities/cgCameraUtils.h>

#include <mayaUtils.h>
#include <Marker.h>
#include <Camera.h>

Camera::Camera() :
        m_transformNodeName(""),
        m_transformObject(),
        m_shapeNodeName(""),
        m_shapeObject(),
        m_worldMatrix(),
        m_filmbackWidth(),
        m_filmbackHeight(),
        m_filmbackOffsetX(),
        m_filmbackOffsetY(),
        m_focalLength() {
    m_worldMatrix.setAttrName("worldMatrix");
    m_filmbackWidth.setAttrName("horizontalFilmAperture");
    m_filmbackHeight.setAttrName("verticalFilmAperture");
    m_filmbackOffsetX.setAttrName("horizontalFilmOffset");
    m_filmbackOffsetY.setAttrName("verticalFilmOffset");
    m_focalLength.setAttrName("focalLength");
}

MString Camera::getTransformNodeName() {
    return m_transformNodeName;
}

void Camera::setTransformNodeName(MString value) {
    if (value != m_transformNodeName) {
        m_worldMatrix.setNodeName(value);
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

Attr &Camera::getMatrixAttr() {
    return m_worldMatrix;
}

MMatrix Camera::getMatrix() {
    Attr &attr = Camera::getMatrixAttr();
    MPlug plug = attr.getPlug();
    MObject matrixObj = plug.asMObject();
    MFnMatrixData matrixData(matrixObj);
    return matrixData.matrix();
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
