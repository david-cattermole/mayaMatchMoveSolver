/*
 * Class for 2D Marker objects, aka 'track points' or '2d points'.
 */

#ifndef MAYA_MM_SOLVER_MARKER_H
#define MAYA_MM_SOLVER_MARKER_H

#include <vector>
#include <memory>

#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MPlug.h>

#include <Attr.h>

class Camera;

class Bundle;


class Marker {
public:
    Marker();

    MString getNodeName() const;

    MStatus setNodeName(MString value);

    MObject getObject();

    std::shared_ptr<Camera> getCamera();

    MStatus setCamera(std::shared_ptr<Camera> &value);

    std::shared_ptr<Bundle> getBundle();

    MStatus setBundle(std::shared_ptr<Bundle> &value);

    Attr &getMatrixAttr();

    Attr &getPosXAttr();

    Attr &getPosYAttr();

    Attr &getEnableAttr();

    Attr &getWeightAttr();

    MStatus getMatrix(MMatrix &value, const MTime &time);

    MStatus getMatrix(MMatrix &value);

    MStatus getPos(double &x, double &y, double &z, const MTime &time);

    MStatus getPos(MPoint &point, const MTime &time);

    MStatus getPos(double &x, double &y, double &z);

    MStatus getPos(MPoint &point);

    MStatus getEnable(bool &value, const MTime &time);

    MStatus getWeight(double &value, const MTime &time);

private:
    MString m_nodeName;
    MObject m_object;

    std::shared_ptr<Camera> m_camera;
    std::shared_ptr<Bundle> m_bundle;

    Attr m_matrix;
    Attr m_px;
    Attr m_py;
    Attr m_enable;
    Attr m_weight;
};


typedef std::vector<Marker> MarkerList;
typedef MarkerList::iterator MarkerListIt;

typedef std::shared_ptr<Marker> MarkerPtr;
typedef std::vector<std::shared_ptr<Marker> > MarkerPtrList;
typedef MarkerPtrList::iterator MarkerPtrListIt;

#endif // MAYA_MM_SOLVER_MARKER_H
