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
 * Header for mmSolver Maya command.
 */

#ifndef MM_SOLVER_CMD_H
#define MM_SOLVER_CMD_H

// STL
#include <cmath>
#include <vector>

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MComputation.h>
#include <maya/MDGModifier.h>
#include <maya/MDagModifier.h>
#include <maya/MDagPath.h>
#include <maya/MDoubleArray.h>
#include <maya/MFnDagNode.h>
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>
#include <maya/MMatrix.h>
#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MPoint.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>
#include <maya/MVector.h>

// MM Solver
#include "mmSolver/adjust/adjust_base.h"
#include "mmSolver/adjust/adjust_defines.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"

namespace mmsolver {

class MMSolverCmd : public MPxCommand {
public:
    MMSolverCmd()
        : m_iterations(10)
        , m_tau(0.0)
        , m_epsilon1(0.0)
        , m_epsilon2(0.0)
        , m_epsilon3(0.0)
        , m_delta(0.0)
        , m_autoDiffType(AUTO_DIFF_TYPE_FORWARD)
        , m_autoParamScale(0)
        , m_robustLossType(ROBUST_LOSS_TYPE_TRIVIAL)
        , m_robustLossScale(1.0)
        , m_solverType(SOLVER_TYPE_DEFAULT_VALUE)
        , m_timeEvalMode(TIME_EVAL_MODE_DG_CONTEXT)
        , m_acceptOnlyBetter(true)
        , m_removeUnusedMarkers(false)
        , m_removeUnusedAttributes(false)
        , m_imageWidth(2048.0)
        , m_supportAutoDiffForward(false)
        , m_supportAutoDiffCentral(false)
        , m_supportParameterBounds(false)
        , m_supportRobustLoss(false){};

    virtual ~MMSolverCmd();

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

    // Solver Information.
    int m_iterations;
    double m_tau;       // Scale factor for initial transform mu
    double m_epsilon1;  // Stopping threshold for ||J^T e||_inf  (ftol)
    double m_epsilon2;  // Stopping threshold for ||Dp||_2       (xtol)
    double m_epsilon3;  // Stopping threshold for ||e||_2        (gtol)
    double m_delta;     // Step used in difference approximation to the Jacobian
    int m_autoDiffType;  // Auto Differencing type to use; 0=forward, 1=central.
    int m_autoParamScale;      // Auto Parameter Scaling; 0=OFF, 1=ON.
    int m_robustLossType;      // Robust Loss function type; 0=trivial,
                               //                            1=soft_l1,
                               //                            2=cauchy.
    double m_robustLossScale;  // Factor to scale robust loss function by.
    int m_solverType;          // Solver type to use; 0=levmar,
                               //                     1=cminpack_lmdif,
                               //                     2=cmpinpack_lmder.
    int m_timeEvalMode;        // How to evaluate values at different times?
    SceneGraphMode m_sceneGraphMode;
    bool m_acceptOnlyBetter;  // Do not accept solved parameter values if
                              // the average devation is higher than at start.
    bool m_removeUnusedMarkers;     // Remove unused Markers from solve?
    bool m_removeUnusedAttributes;  // Remove unused Attributes from solve?
    double m_imageWidth;            // Defines pixel size in camera space.
    FrameSolveMode m_frameSolveMode;

    // What type of features does the given solver type support?
    bool m_supportAutoDiffForward;
    bool m_supportAutoDiffCentral;
    bool m_supportParameterBounds;
    bool m_supportRobustLoss;

    // Solver printing.
    MStringArray m_printStatsList;
    LogLevel m_logLevel;

    // Solver Objects
    CameraPtrList m_cameraList;
    MarkerPtrList m_markerList;
    BundlePtrList m_bundleList;
    AttrPtrList m_attrList;
    MTimeArray m_frameList;
    StiffAttrsPtrList m_stiffAttrsList;
    SmoothAttrsPtrList m_smoothAttrsList;

    // Undo/Redo
    MDGModifier m_dgmod;
    MAnimCurveChange m_curveChange;
    MComputation m_computation;
};

}  // namespace mmsolver

#endif  // MM_SOLVER_CMD_H
