/*
 * A dummy transform node that acts exactly the same as Maya's normal
 * transform node, but with a different icon.
 */

#include <MMMarkerGroupTransformNode.h>

#include <maya/MTypeId.h>
#include <maya/MPxTransformationMatrix.h>

#include <nodeTypeIds.h>

#include <Camera.h>


MTypeId MMMarkerGroupTransformNode::m_id(MM_MARKER_GROUP_TRANSFORM_TYPE_ID);

MString MMMarkerGroupTransformNode::nodeName() {
    return MString("mmMarkerGroupTransform");
}

MMMarkerGroupTransformNode::MMMarkerGroupTransformNode() : MPxTransform() {}

MMMarkerGroupTransformNode::MMMarkerGroupTransformNode(MPxTransformationMatrix *tm) : MPxTransform(tm) {}

void MMMarkerGroupTransformNode::postConstructor() {
    MPxTransform::postConstructor();
    if (baseTransformationMatrix == NULL) {
        baseTransformationMatrix = new MPxTransformationMatrix();
    }
}

MMMarkerGroupTransformNode::~MMMarkerGroupTransformNode() {
	// Empty function body rather than '= default', to allow compiling 
	// under Visual Studio 2012.
};


void *MMMarkerGroupTransformNode::creator() {
    return (new MMMarkerGroupTransformNode());
}


MStatus MMMarkerGroupTransformNode::initialize() {
    return MS::kSuccess;
}
