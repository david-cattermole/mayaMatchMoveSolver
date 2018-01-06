/*
 * Simple computation node to keep markers in screen-space when the camera filmback/focal length is modified.
 */

#ifndef MM_MARKER_SCALE_NODE_H
#define MM_MARKER_SCALE_NODE_H

#include <maya/MPxNode.h>

#include <maya/MString.h>
#include <maya/MVector.h>
#include <maya/MTime.h>

#include <maya/MFnDependencyNode.h>
#include <maya/MTypeId.h>


class MMMarkerScaleNode : public MPxNode {
public:
    MMMarkerScaleNode();

    virtual ~MMMarkerScaleNode();

    virtual MStatus compute(const MPlug &plug, MDataBlock &data);

    static void *creator();

    static MStatus initialize();

    static MString nodeName();

    static MTypeId m_id;

    // Input Attributes
    static MObject a_depth;
    static MObject a_focalLength;
    static MObject a_cameraAperture;
    static MObject a_horizontalFilmAperture;
    static MObject a_verticalFilmAperture;
    static MObject a_filmOffset;
    static MObject a_horizontalFilmOffset;
    static MObject a_verticalFilmOffset;
    
    // Output Attributes
    static MObject a_outTranslate;
    static MObject a_outTranslateX;
    static MObject a_outTranslateY;
    static MObject a_outTranslateZ;
    static MObject a_outScale;
    static MObject a_outScaleX;
    static MObject a_outScaleY;
    static MObject a_outScaleZ;
};


#endif // MM_MARKER_SCALE_NODE_H
