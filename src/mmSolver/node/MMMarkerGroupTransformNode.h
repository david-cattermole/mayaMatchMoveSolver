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

#ifndef MM_MARKER_GROUP_TRANSFORM_NODE_H
#define MM_MARKER_GROUP_TRANSFORM_NODE_H

// Maya
#include <maya/MMatrix.h>
#include <maya/MPxTransform.h>
#include <maya/MPxTransformationMatrix.h>
#include <maya/MTransformationMatrix.h>
#include <maya/MTypeId.h>

namespace mmsolver {

class MMMarkerGroupTransformNode : public MPxTransform {
public:
    MMMarkerGroupTransformNode();

    // Maya 2020+ will manage the creation of MPxTransformationMatrix
    // on demand for us.
#if MAYA_API_VERSION < 20200000
    explicit MMMarkerGroupTransformNode(MPxTransformationMatrix *);
#endif

    virtual ~MMMarkerGroupTransformNode();

    virtual void postConstructor();

    static void *creator();

    static MStatus initialize();

    static MString nodeName();

    static MTypeId m_id;
};

}  // namespace mmsolver

#endif  // MM_MARKER_GROUP_TRANSFORM_NODE_H
