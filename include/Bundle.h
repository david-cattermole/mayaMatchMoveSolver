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

    void setNodeName(MString value);

    MObject getObject();

    double getWeight() const;

    void setWeight(double value);

    Attr &getWorldMatrixAttr();

    MMatrix getWorldMatrix();

    void getWorldPos(double &x, double &y, double &z);

    void getPos(glm::vec3 &pos);

    void getPos(MPoint &point);

private:
    MString m_nodeName;
    MObject m_object;
    double m_weight;
    Attr m_worldMatrix;
};

typedef std::vector<Bundle> BundleList;
typedef BundleList::iterator BundleListIt;

typedef std::shared_ptr<Bundle> BundlePtr;
typedef std::vector<std::shared_ptr<Bundle> > BundlePtrList;
typedef BundlePtrList::iterator BundlePtrListIt;

#endif //MAYA_MM_SOLVER_BUNDLE_H
