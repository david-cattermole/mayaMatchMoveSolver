/*
 * Class for 2D Marker objects, aka 'track points' or '2d points'.
 */

#ifndef MAYA_MM_SOLVER_MARKER_H
#define MAYA_MM_SOLVER_MARKER_H

#include <vector>
#include <memory>

#include <glm/glm.hpp>

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
    void setNodeName(MString value);
    MObject getObject();

    std::shared_ptr<Camera> getCamera();
    void setCamera(std::shared_ptr<Camera> &value);

    std::shared_ptr<Bundle> getBundle();
    void setBundle(std::shared_ptr<Bundle> &value);

    Attr &getPosXAttr();

    Attr &getPosYAttr();

    Attr& getMatrixAttr();
    MMatrix getMatrix();
    void getPos(double &x, double &y, double &z);
    void getPos(glm::vec3 &pos);
    void getPos(MPoint &point);

private:
    MString m_nodeName;
    MObject m_object;
    std::shared_ptr<Camera> m_camera;
    std::shared_ptr<Bundle> m_bundle;
    Attr m_matrix;
    Attr m_px;
    Attr m_py;
};


typedef std::vector<Marker> MarkerList;
typedef MarkerList::iterator MarkerListIt;

typedef std::shared_ptr<Marker> MarkerPtr;
typedef std::vector< std::shared_ptr<Marker> > MarkerPtrList;
typedef MarkerPtrList::iterator MarkerPtrListIt;

#endif // MAYA_MM_SOLVER_MARKER_H
