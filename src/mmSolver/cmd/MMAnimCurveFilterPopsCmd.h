/*
 * Copyright (C) 2024 David Cattermole.
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
 * Header for 'mmBestFitPlane' Maya command.
 */

#ifndef MM_SOLVER_MM_ANIM_CURVE_FILTER_POPS_CMD_H
#define MM_SOLVER_MM_ANIM_CURVE_FILTER_POPS_CMD_H

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDGModifier.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MObject.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>
#include <maya/MSyntax.h>
#include <maya/MTime.h>

namespace mmsolver {

class MMAnimCurveFilterPopsCmd : public MPxCommand {
public:
    MMAnimCurveFilterPopsCmd()
        : m_startFrame(1.0), m_endFrame(101.0), m_threshold(1.0){};
    virtual ~MMAnimCurveFilterPopsCmd();

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

    // Command Options
    double m_startFrame;
    double m_endFrame;
    double m_threshold;

    // The animation curves to process.
    MSelectionList m_selection;
    MObject m_animCurveObj;
    MFnAnimCurve m_animCurveFn;

    // Undo/Redo
    MDGModifier m_dgmod;
    MAnimCurveChange m_curveChange;
};

}  // namespace mmsolver

#endif  // MM_SOLVER_MM_ANIM_CURVE_FILTER_POPS_CMD_H
