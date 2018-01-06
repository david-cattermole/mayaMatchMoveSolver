/*
 * A dummy transform node that acts exactly the same as Maya's normal
 * transform node, but with a different icon.
 */

#ifndef MM_MARKER_GROUP_TRANSFORM_NODE_H
#define MM_MARKER_GROUP_TRANSFORM_NODE_H

#include <maya/MMatrix.h>
#include <maya/MTransformationMatrix.h>
#include <maya/MTypeId.h>
#include <maya/MPxTransform.h>
#include <maya/MPxTransformationMatrix.h>


class MMMarkerGroupTransformNode : public MPxTransform {
public:
    MMMarkerGroupTransformNode();
    MMMarkerGroupTransformNode(MPxTransformationMatrix *);

    virtual ~MMMarkerGroupTransformNode();

    virtual void postConstructor();

    static void *creator();

    static MStatus initialize();

    static MString nodeName();

    static MTypeId m_id;
};


#endif // MM_MARKER_GROUP_TRANSFORM_NODE_H
