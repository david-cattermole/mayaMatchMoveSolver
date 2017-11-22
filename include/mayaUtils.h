/*
 * Miscellaneous Maya utilities, related to objects and selection, etc.
 */


#ifndef MAYA_UTILS_H
#define MAYA_UTILS_H

// Utils
#include <utilities/debugUtils.h>

// Maya
#include <maya/MPoint.h>
#include <maya/MVector.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MSelectionList.h>
#include <maya/MFnDependencyNode.h>


static inline
MStatus getAsSelectionList(MStringArray nodeNames, MSelectionList &selList) {
    MStatus status;
    for (unsigned int i = 0; i < nodeNames.length(); ++i) {
        status = selList.add(nodeNames[i]);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    if (selList.length() != nodeNames.length()) {
        status = MStatus::kFailure;
        status.perror("getAsSelectionList failed.");
    }
    return status;
}


static inline
MStatus getAsSelectionList(MString nodeName, MSelectionList &selList) {
    MStringArray nodeNames;
    nodeNames.append(nodeName);
    return getAsSelectionList(nodeNames, selList);
}


static inline
MStatus getAsObject(MString nodeName, MObject &object) {
    MStatus status;
    MSelectionList selList;
    status = getAsSelectionList(nodeName, selList);
    if (selList.length() == 1) {
        selList.getDependNode(0, object);
    }
    return status;
}


#endif // MAYA_UTILS_H
