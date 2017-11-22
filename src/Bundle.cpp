/*
 *
 */

#include <maya/MPlug.h>
#include <maya/MObject.h>
#include <maya/MDataHandle.h>
#include <maya/MFnMatrixData.h>
#include <maya/MMatrix.h>
#include <maya/MPoint.h>

#include <glm/glm.hpp>

#include <mayaUtils.h>
#include <Marker.h>
#include <Bundle.h>
#include <Attr.h>


Bundle::Bundle() :
        m_nodeName(""),
        m_object(),
        m_weight(1.0),
        m_worldMatrix() {
    m_worldMatrix.setAttrName("worldMatrix");
}


MString Bundle::getNodeName() const {
    return m_nodeName;
}

void Bundle::setNodeName(MString value) {
    if (value != m_nodeName) {
        m_worldMatrix.setNodeName(value);
    }
    m_nodeName = value;
}

MObject Bundle::getObject() {
    MStatus status;
    MString name = Bundle::getNodeName();
    status = getAsObject(name, m_object);
    return m_object;
}

double Bundle::getWeight() const {
    return m_weight;
}

void Bundle::setWeight(double value) {
    m_weight = value;
}

Attr &Bundle::getWorldMatrixAttr() {
    return m_worldMatrix;
}

MMatrix Bundle::getWorldMatrix() {
    Attr &attr = Bundle::getWorldMatrixAttr();
    MPlug plug = attr.getPlug();
    MObject matrixObj = plug.asMObject();
    MFnMatrixData matrixData(matrixObj);
    MMatrix matrix = matrixData.matrix();
    return matrix;
}

void Bundle::getWorldPos(double &x, double &y, double &z) {
    MMatrix matrix = Bundle::getWorldMatrix();
    x = matrix(3, 0);
    y = matrix(3, 1);
    z = matrix(3, 2);
    return;
}

void Bundle::getPos(glm::vec3 &pos) {
    MMatrix matrix = Bundle::getWorldMatrix();
    pos.x = (float) matrix(3, 0);
    pos.y = (float) matrix(3, 1);
    pos.z = (float) matrix(3, 2);
    return;
}

void Bundle::getPos(MPoint &point) {
    MMatrix matrix = Bundle::getWorldMatrix();
    point.x = matrix(3, 0);
    point.y = matrix(3, 1);
    point.z = matrix(3, 2);
    point.w = matrix(3, 3);
    point.cartesianize();
    return;
}
