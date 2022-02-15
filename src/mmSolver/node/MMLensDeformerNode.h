/*
 * Copyright (C) 2020 David Cattermole.
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
 * Lens Distortion Deformer.
 */

#ifndef MM_LENS_DEFORMER_NODE_H
#define MM_LENS_DEFORMER_NODE_H

// STL
#include <string.h>
#include <math.h>

// Maya
#include <maya/MIOStream.h>
#include <maya/MPxGeometryFilter.h>
#include <maya/MItGeometry.h>
#include <maya/MTypeId.h>
#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MPoint.h>
#include <maya/MMatrix.h>

namespace mmsolver {

class MMLensDeformerNode : public MPxGeometryFilter {
public:
    MMLensDeformerNode();

    virtual ~MMLensDeformerNode();

    static void* creator();

    static MStatus initialize();

    static MString nodeName();

    virtual MStatus deform(MDataBlock&    block,
                           MItGeometry&   iter,
                           const MMatrix& mat,
                           unsigned int   multiIndex);

public:
    static MObject a_inLens;
    static MObject a_focalLength;
    static MObject a_horizontalFilmAperture;
    static MObject a_verticalFilmAperture;
    static MObject a_pixelAspect;
    static MObject a_horizontalFilmOffset;
    static MObject a_verticalFilmOffset;
    static MTypeId m_id;

private:

};

} // namespace mmsolver

#endif // MM_LENS_DEFORMER_NODE_H
