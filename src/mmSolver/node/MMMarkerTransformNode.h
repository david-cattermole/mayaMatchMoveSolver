/*
 * Copyright (C) 2018, 2019, 2020 David Cattermole.
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
 * A transform node that can have translate values offset with lens
 * distortion models.
 */

#ifndef MM_MARKER_TRANSFORM_NODE_H
#define MM_MARKER_TRANSFORM_NODE_H

// Maya
#include <maya/MMatrix.h>
#include <maya/MPxTransform.h>
#include <maya/MPxTransformationMatrix.h>
#include <maya/MTransformationMatrix.h>
#include <maya/MTypeId.h>

// MM Solver
#include "MMMarkerTransformMatrix.h"

namespace mmsolver {

class MMMarkerTransformNode : public MPxTransform {
public:
    MMMarkerTransformNode();
#if MAYA_API_VERSION < 20200000
    explicit MMMarkerTransformNode(MPxTransformationMatrix *);
#endif

    virtual ~MMMarkerTransformNode();

    virtual void postConstructor();

    static void *creator();

    static MStatus initialize();

    virtual void resetTransformation(MPxTransformationMatrix *);
    virtual void resetTransformation(const MMatrix &);

#if MAYA_API_VERSION < 20180000
    virtual MStatus validateAndSetValue(const MPlug &plug,
                                        const MDataHandle &handle,
                                        const MDGContext &context);
#else
    virtual MStatus validateAndSetValue(const MPlug &plug,
                                        const MDataHandle &handle);
#endif

    // Utility for getting the related matrix pointer
    MMMarkerTransformMatrix *getMarkerTransformMatrix();

    static MString nodeName();

    static MTypeId m_id;

    // Input Attributes
    static MObject a_inLens;

protected:
    typedef MPxTransform ParentClass;
};

}  // namespace mmsolver

#endif  // MM_MARKER_TRANSFORM_NODE_H
