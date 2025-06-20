/*
 * Copyright (C) 2024, 2025 David Cattermole.
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
 * Header for mmAnimCurveSimplify Maya command.
 */

#ifndef MM_SOLVER_MM_ANIM_CURVE_SIMPLIFY_CMD_H
#define MM_SOLVER_MM_ANIM_CURVE_SIMPLIFY_CMD_H

// STL
#include <cmath>
#include <limits>
#include <vector>

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDGModifier.h>
#include <maya/MEulerRotation.h>
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>
#include <maya/MSyntax.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>

// Maya helpers
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_utils.h"

// MM Scene Graph
#include "mmscenegraph/mmscenegraph.h"

namespace mmsolver {

class MMAnimCurveSimplifyCmd : public MPxCommand {
public:
    MMAnimCurveSimplifyCmd()
        : m_startFrame(std::numeric_limits<uint32_t>::max())
        , m_endFrame(std::numeric_limits<uint32_t>::max())
        , m_controlPointCount(0)
        , m_distribution(mmscenegraph::ControlPointDistribution::kUnknown)
        , m_method(mmscenegraph::InterpolationMethod::kUnknown){};
    virtual ~MMAnimCurveSimplifyCmd();

    virtual bool hasSyntax() const;
    static MSyntax newSyntax();

    virtual MStatus doIt(const MArgList &args);
    virtual bool isUndoable() const;
    virtual MStatus undoIt();
    virtual MStatus redoIt();

    static void *creator();
    static MString cmdName();

private:
    MStatus parseArgs(const MArgList &args);

    // Start/End Frames
    uint32_t m_startFrame;
    uint32_t m_endFrame;
    MTime m_startTime;
    MTime m_endTime;

    // Other settings.
    uint8_t m_controlPointCount;
    mmscenegraph::ControlPointDistribution m_distribution;
    mmscenegraph::InterpolationMethod m_method;

    // The animation curves to process.
    MSelectionList m_selection;
    MObject m_animCurveObj;
    MFnAnimCurve m_animCurveFn;

    // Undo/Redo
    MDGModifier m_dgmod;
    MAnimCurveChange m_curveChange;
};

}  // namespace mmsolver

#endif  // MM_SOLVER_MM_ANIM_CURVE_SIMPLIFY_CMD_H
