/*
 * Attribute class, represents an attribute that could be modified.
 */

#ifndef MAYA_MM_SOLVER_ATTR_H
#define MAYA_MM_SOLVER_ATTR_H

#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MPlug.h>
#include <maya/MTime.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MAnimControl.h>
#include <maya/MDGModifier.h>

#include <vector>
#include <memory>


class Attr {
public:
    Attr();

    MString getName() const;

    MStatus setName(MString value);

    MString getNodeName() const;

    MStatus setNodeName(MString value);

    MString getAttrName() const;

    MStatus setAttrName(MString value);

    MObject getObject();

    MPlug getPlug();

    MObject getAttribute();

    MString getAnimCurveName();

    bool isFreeToChange();

    bool isAnimated();

    bool isConnected();

    MStatus getValue(bool &value, const MTime &time);

    MStatus getValue(int &value, const MTime &time);

    MStatus getValue(double &value, const MTime &time);

    MStatus getValue(MMatrix &value, const MTime &time);

    MStatus getValue(bool &value);

    MStatus getValue(double &value);

    MStatus getValue(MMatrix &value);

    MStatus setValue(double value, const MTime &time,
                  MDGModifier &dgmod, MAnimCurveChange &animChange);

    MStatus setValue(double value,
                  MDGModifier &dgmod, MAnimCurveChange &animChange);

private:
    MString m_nodeName;
    MString m_attrName;
    MObject m_object;
    MPlug m_plug;
    MString m_animCurveName;
    int m_animated;
    int m_connected;
    int m_isFreeToChange;
};


typedef std::vector<Attr> AttrList;
typedef AttrList::iterator AttrListIt;

typedef std::shared_ptr<Attr> AttrPtr;
typedef std::vector<std::shared_ptr<Attr> > AttrPtrList;
typedef AttrPtrList::iterator AttrPtrListIt;

#endif //MAYA_MM_SOLVER_ATTR_H
