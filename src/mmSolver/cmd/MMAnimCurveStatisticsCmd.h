/*
 * Copyright (C) 2025 David Cattermole.
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
 * Header for 'mmAnimCurveStatistics' Maya command.
 */

#ifndef MM_SOLVER_MM_ANIM_CURVE_STATISTICS_CMD_H
#define MM_SOLVER_MM_ANIM_CURVE_STATISTICS_CMD_H

// STL
#include <limits>

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDoubleArray.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MObject.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>
#include <maya/MSyntax.h>

// MM Solver
#include "mmSolver/core/frame.h"

namespace mmsolver {

class MMAnimCurveStatisticsCmd : public MPxCommand {
public:
    MMAnimCurveStatisticsCmd()
        : m_startFrame(std::numeric_limits<FrameNumber>::max())
        , m_endFrame(std::numeric_limits<FrameNumber>::max())
        , m_calculateMean(false)
        , m_calculateMedian(false)
        , m_calculateVariance(false)
        , m_calculateStdDev(false)
        , m_calculateSNR(false){};
    virtual ~MMAnimCurveStatisticsCmd();

    virtual bool hasSyntax() const;
    static MSyntax newSyntax();

    virtual MStatus doIt(const MArgList &args);
    virtual bool isUndoable() const;

    static void *creator();
    static MString cmdName();

private:
    MStatus parseArgs(const MArgList &args);

    // Start/End frames.
    FrameNumber m_startFrame;
    FrameNumber m_endFrame;

    // Statistics flags
    bool m_calculateMean;
    bool m_calculateMedian;
    bool m_calculateVariance;
    bool m_calculateStdDev;
    bool m_calculateSNR;

    // The animation curves to process.
    MSelectionList m_selection;
    MObject m_animCurveObj;
    MFnAnimCurve m_animCurveFn;
};

}  // namespace mmsolver

#endif  // MM_SOLVER_MM_ANIM_CURVE_STATISTICS_CMD_H
