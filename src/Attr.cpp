/*
 *
 */

#include <mayaUtils.h>
#include <Attr.h>


MString Attr::getName() const {
    return m_nodeName + "." + m_attrName;
}

void Attr::setName(MString value) {
    MStringArray values;
    MStatus status;
    status = value.split('.', values);
    if (status != MStatus::kSuccess) {
        ERR("Attr::setName: Error splitting name. " << value);
        return;
    }
    if (values.length() == 2) {
        Attr::setNodeName(values[0]);
        Attr::setAttrName(values[1]);
    } else {
        ERR("Attr::setName: Value given has more than one dot character. " << value);
    }
}

MString Attr::getNodeName() const {
    return m_nodeName;
}

void Attr::setNodeName(MString value) {
    if (value != m_nodeName) {
        m_object = MObject();
        m_plug = MPlug();
    }
    m_nodeName = value;
}

MString Attr::getAttrName() const {
    return m_attrName;
}

void Attr::setAttrName(MString value) {
    if (value != m_attrName) {
        m_object = MObject();
        m_plug = MPlug();
    }
    m_attrName = value;
}

MObject Attr::getObject() {
    MString name = Attr::getNodeName();
    getAsObject(name, m_object);
    return m_object;
}

MPlug &Attr::getPlug() {
    MStatus status;
    m_plug.isNull();
    MObject nodeObj = Attr::getObject();
    MString attrName = Attr::getAttrName();
    MFnDependencyNode dependsNode(nodeObj, &status);
    MPlug plug = dependsNode.findPlug(attrName, true, &status);

    // For attributes like 'worldMatrix', where we need the first element of the array, not the attribute itself.
    int num = plug.numElements();
    if (num > 0) {
        plug = plug.elementByPhysicalIndex(0, &status);
        if (status != MStatus::kSuccess) {
            ERR("Could not get first plug element.");
        }
    }

    MString name = Attr::getName();
    if (status != MStatus::kSuccess) {
        ERR("Attribute cannot be found; " << name);
    }
    if (plug.isFreeToChange() == MPlug::kFreeToChange) {
        m_plug = plug;
    } else {
        ERR("Attribute cannot be modified; " << name);
        m_plug = MPlug();
    }
    return m_plug;
}

MObject Attr::getAttribute() {
    MPlug plug = Attr::getPlug();
    MObject attrObj;
    if (!plug.isNull()) {
        attrObj = plug.attribute();
    }
    return attrObj;
}

bool Attr::isFreeToChange() {
    MPlug plug = Attr::getPlug();
    return plug.isFreeToChange() == MPlug::kFreeToChange;
}


bool Attr::getStatic() const {
    return m_static;
}

void Attr::setStatic(bool value) {
    m_static = value;
}
