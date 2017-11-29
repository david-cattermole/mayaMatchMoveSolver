/*
 * Class Bundle, represents a 3D point of a 2D Marker.
 */

#ifndef MAYA_MM_SOLVER_BUNDLE_H
#define MAYA_MM_SOLVER_BUNDLE_H

#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MMatrix.h>
#include <maya/MPoint.h>
#include <maya/MPlug.h>

#include <vector>
#include <memory>

#include <glm/glm.hpp>

#include <Attr.h>

class Marker;


class Bundle {
public:
    Bundle();

    MString getNodeName() const;

    MStatus setNodeName(MString value);

    MObject getObject();

    double getWeight() const;

    MStatus setWeight(double value);

    Attr &getMatrixAttr();

    MStatus getMatrix(MMatrix &value, const MTime &time);

    MStatus getMatrix(MMatrix &value);

    MStatus getPos(double &x, double &y, double &z, const MTime &time);

    MStatus getPos(glm::vec3 &pos, const MTime &time);

    MStatus getPos(MPoint &point, const MTime &time);

    MStatus getPos(double &x, double &y, double &z);

    MStatus getPos(glm::vec3 &pos);

    MStatus getPos(MPoint &point);

private:
    MString m_nodeName;
    MObject m_object;
     double m_weight;
    Attr m_matrix;
};

typedef std::vector<Bundle> BundleList;
typedef BundleList::iterator BundleListIt;

typedef std::shared_ptr<Bundle> BundlePtr;
typedef std::vector<std::shared_ptr<Bundle> > BundlePtrList;
typedef BundlePtrList::iterator BundlePtrListIt;

#endif //MAYA_MM_SOLVER_BUNDLE_H
