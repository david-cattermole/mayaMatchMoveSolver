/*
 * Copyright (C) 2018, 2019 David Cattermole.
 *
 * This file is part of mmSolver.
 *
 * mmSolver is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * mmSolver is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
 * ====================================================================
 *
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
