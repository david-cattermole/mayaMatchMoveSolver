/*
 *
 */

#include <maya/MFnDependencyNode.h>
#include <maya/MPlug.h>
#include <maya/MObject.h>
#include <maya/MFnMatrixData.h>
#include <maya/MMatrix.h>
#include <maya/MPoint.h>

#include <memory>

#include <mayaUtils.h>
#include <Camera.h>
#include <Bundle.h>
#include <Marker.h>
#include <Attr.h>

Marker::Marker() :
        m_nodeName(""),
        m_object(),
        m_camera(),
        m_bundle()
 {
    m_matrix.setAttrName("worldMatrix");
    m_px.setAttrName("translateX");
    m_py.setAttrName("translateY");
}

MString Marker::getNodeName() const {
    return MString(m_nodeName);
}

void Marker::setNodeName(MString value) {
    if (value != m_nodeName) {
        m_matrix.setNodeName(value);
        m_px.setNodeName(value);
        m_py.setNodeName(value);
    }
    m_nodeName = value;
}

MObject Marker::getObject() {
    MStatus status;
    MString name = Marker::getNodeName();
    status = getAsObject(name, m_object);
    return m_object;
}

CameraPtr Marker::getCamera() {
    return m_camera;
}

void Marker::setCamera(CameraPtr &value) {
    m_camera = value;
}

BundlePtr Marker::getBundle() {
    return m_bundle;
}

void Marker::setBundle(BundlePtr &value) {
    m_bundle = value;
}

Attr &Marker::getPosXAttr() {
    return m_px;
}

Attr &Marker::getPosYAttr() {
    return m_py;
}

Attr &Marker::getMatrixAttr() {
    return m_matrix;
}

MMatrix Marker::getMatrix() {
    Attr attr = Marker::getMatrixAttr();
    MPlug plug = attr.getPlug();
    MObject matrixObj = plug.asMObject();
    MFnMatrixData matrixData(matrixObj);
    MMatrix matrix(matrixData.matrix());
    return matrix;
}

void Marker::getPos(double &x, double &y, double &z) {
    MMatrix matrix = Marker::getMatrix();
    x = matrix(3, 0);
    y = matrix(3, 1);
    z = matrix(3, 2);
    return;
}

void Marker::getPos(glm::vec3 &pos) {
    MMatrix matrix = Marker::getMatrix();
    pos.x = matrix(3, 0);
    pos.y = matrix(3, 1);
    pos.z = matrix(3, 2);
    return;
}

void Marker::getPos(MPoint &point) {
    MMatrix matrix = Marker::getMatrix();
    point.x = matrix(3, 0);
    point.y = matrix(3, 1);
    point.z = matrix(3, 2);
    point.w = matrix(3, 3);
    point.cartesianize();
    return;
}

