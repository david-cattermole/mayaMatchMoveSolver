/*
 * Copyright (C) 2022 David Cattermole.
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
 * Define a 3DE lens. The lens can be any (supported) 3DE lens distortion model.
 */

#ifndef MM_LENS_MODEL_3DE_NODE_H
#define MM_LENS_MODEL_3DE_NODE_H

// Maya
#include <maya/MObject.h>
#include <maya/MPxNode.h>
#include <maya/MString.h>
#include <maya/MTypeId.h>

namespace mmsolver {

class MMLensModel3deNode : public MPxNode {
public:
    MMLensModel3deNode();

    virtual ~MMLensModel3deNode();

    virtual MStatus compute(const MPlug &plug, MDataBlock &data);

    static void *creator();

    static MStatus initialize();

    static MString nodeName();

    void postConstructor() override;

    static MTypeId m_id;

    // Input Attributes
    static MObject a_inLens;
    static MObject a_enable;
    static MObject a_lensModel;

    static MObject a_tdeClassic_heading;
    static MObject a_tdeClassic_distortion;
    static MObject a_tdeClassic_anamorphicSqueeze;
    static MObject a_tdeClassic_curvatureX;
    static MObject a_tdeClassic_curvatureY;
    static MObject a_tdeClassic_quarticDistortion;

    static MObject a_tdeRadialStdDeg4_heading;
    static MObject a_tdeRadialStdDeg4_degree2_distortion;
    static MObject a_tdeRadialStdDeg4_degree2_u;
    static MObject a_tdeRadialStdDeg4_degree2_v;
    static MObject a_tdeRadialStdDeg4_degree4_distortion;
    static MObject a_tdeRadialStdDeg4_degree4_u;
    static MObject a_tdeRadialStdDeg4_degree4_v;
    static MObject a_tdeRadialStdDeg4_cylindricDirection;
    static MObject a_tdeRadialStdDeg4_cylindricBending;

    static MObject a_tdeAnamorphicStdDeg4_heading;
    static MObject a_tdeAnamorphicStdDeg4_degree2_cx02;
    static MObject a_tdeAnamorphicStdDeg4_degree2_cy02;
    static MObject a_tdeAnamorphicStdDeg4_degree2_cx22;
    static MObject a_tdeAnamorphicStdDeg4_degree2_cy22;
    static MObject a_tdeAnamorphicStdDeg4_degree4_cx04;
    static MObject a_tdeAnamorphicStdDeg4_degree4_cy04;
    static MObject a_tdeAnamorphicStdDeg4_degree4_cx24;
    static MObject a_tdeAnamorphicStdDeg4_degree4_cy24;
    static MObject a_tdeAnamorphicStdDeg4_degree4_cx44;
    static MObject a_tdeAnamorphicStdDeg4_degree4_cy44;
    static MObject a_tdeAnamorphicStdDeg4_lensRotation;
    static MObject a_tdeAnamorphicStdDeg4_squeeze_x;
    static MObject a_tdeAnamorphicStdDeg4_squeeze_y;
    static MObject a_tdeAnamorphicStdDeg4_rescale;

    static MObject a_tdeAnamorphicStdDeg6_heading;
    static MObject a_tdeAnamorphicStdDeg6_degree2_cx02;
    static MObject a_tdeAnamorphicStdDeg6_degree2_cy02;
    static MObject a_tdeAnamorphicStdDeg6_degree2_cx22;
    static MObject a_tdeAnamorphicStdDeg6_degree2_cy22;
    static MObject a_tdeAnamorphicStdDeg6_degree4_cx04;
    static MObject a_tdeAnamorphicStdDeg6_degree4_cy04;
    static MObject a_tdeAnamorphicStdDeg6_degree4_cx24;
    static MObject a_tdeAnamorphicStdDeg6_degree4_cy24;
    static MObject a_tdeAnamorphicStdDeg6_degree4_cx44;
    static MObject a_tdeAnamorphicStdDeg6_degree4_cy44;
    static MObject a_tdeAnamorphicStdDeg6_degree6_cx06;
    static MObject a_tdeAnamorphicStdDeg6_degree6_cy06;
    static MObject a_tdeAnamorphicStdDeg6_degree6_cx26;
    static MObject a_tdeAnamorphicStdDeg6_degree6_cy26;
    static MObject a_tdeAnamorphicStdDeg6_degree6_cx46;
    static MObject a_tdeAnamorphicStdDeg6_degree6_cy46;
    static MObject a_tdeAnamorphicStdDeg6_degree6_cx66;
    static MObject a_tdeAnamorphicStdDeg6_degree6_cy66;
    static MObject a_tdeAnamorphicStdDeg6_lensRotation;
    static MObject a_tdeAnamorphicStdDeg6_squeeze_x;
    static MObject a_tdeAnamorphicStdDeg6_squeeze_y;
    static MObject a_tdeAnamorphicStdDeg6_rescale;

    // Output Attributes
    static MObject a_outLens;
};

}  // namespace mmsolver

#endif  // MM_LENS_MODEL_3DE_NODE_H
