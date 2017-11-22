/*
 * Attribute class, represents an attribute that could be modified.
 */

#ifndef MAYA_MM_SOLVER_ATTR_H
#define MAYA_MM_SOLVER_ATTR_H

#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MPlug.h>
//#include <maya/MFnAnimCurve.h>

#include <vector>
#include <memory>

class Attr {
public:
    MString getName() const;

    void setName(MString value);

    MString getNodeName() const;

    void setNodeName(MString value);

    MString getAttrName() const;

    void setAttrName(MString value);

    MObject getObject();

    MPlug &getPlug();

    MObject getAttribute();

    bool isFreeToChange();

    bool getStatic() const;

    void setStatic(bool value);

private:
    MString m_nodeName;
    MString m_attrName;
    MObject m_object;
    bool m_static;

//    MFnAnimCurve m_curve;
    MPlug m_plug;
};

typedef std::vector<Attr> AttrList;
typedef AttrList::iterator AttrListIt;

//typedef std::vector<Attr*> AttrPtrList;
//typedef std::vector<Attr*>::iterator AttrPtrListIt;

typedef std::shared_ptr<Attr> AttrPtr;
typedef std::vector<std::shared_ptr<Attr> > AttrPtrList;
typedef AttrPtrList::iterator AttrPtrListIt;

#endif //MAYA_MM_SOLVER_ATTR_H
