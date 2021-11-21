/*
 * Copyright (C) 2019 David Cattermole.
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
 * Command for running mmCameraSolve.
 */

// // Ensure Google Logging does not use "ERROR" macro, because Windows
// // doesn't support it.
// #define GLOG_NO_ABBREVIATED_SEVERITIES

// TODO: Test if this is needed!
#define GOOGLE_GLOG_DLL_DECL

// Internal
#include <MMCameraSolveCmd.h>
#include <mayaUtils.h>

// STL
#include <vector>
#include <cmath>
#include <cassert>

// Utils
#include <utilities/debugUtils.h>
#include <utilities/stringUtils.h>

// Google Test
#include <gtest/gtest.h>

// Google Flags
#include <gflags/gflags.h>

// Google Logging
#include <glog/logging.h>

// Ceres Solver
#pragma warning( push )
#pragma warning( disable : 4251 ) // needs to have dll-interface to be used by clients of class
#include <ceres/ceres.h>
#pragma warning( pop )


// Maya
#include <maya/MSyntax.h>
#include <maya/MArgList.h>
#include <maya/MArgDatabase.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>
#include <maya/MMatrix.h>
#include <maya/MMatrixArray.h>
#include <maya/MDagPath.h>
#include <maya/MFnDependencyNode.h>

// GFlags test.
DEFINE_bool(big_menu, true, "Include 'advanced' options in the menu listing");
DEFINE_string(languages, "english,french,german",
              "comma-separated list of languages to offer in the 'lang' menu");


MMCameraSolveCmd::~MMCameraSolveCmd() {}

void *MMCameraSolveCmd::creator() {
    return new MMCameraSolveCmd();
}

MString MMCameraSolveCmd::cmdName() {
    return MString("mmCameraSolve");
}

/*
 * Tell Maya we have a syntax function.
 */
bool MMCameraSolveCmd::hasSyntax() const {
    return true;
}

bool MMCameraSolveCmd::isUndoable() const {
    return false;
}

/*
 * Add flags to the command syntax
 */
MSyntax MMCameraSolveCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    unsigned int minNumObjects = 0;
    syntax.setObjectType(MSyntax::kSelectionList, minNumObjects);

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMCameraSolveCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    return status;
}

struct CostFunctor {
   template <typename T>
   bool operator()(const T* const x, T* residual) const {
     residual[0] = 10.0 - x[0];
     return true;
   }
};

MStatus MMCameraSolveCmd::doIt(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    // Command Outputs
    MDoubleArray outResult;

    // Test the GLOG library.
    INFO("Camera Solve Command - This is a log message!\n");

    // Ceres Solver Test
    {
        // The variable to solve for with its initial value.
        double initial_x = 5.0;
        double x = initial_x;

        // Build the problem.
        ceres::Problem problem;

        // Set up the only cost function (also known as residual). This uses
        // auto-differentiation to obtain the derivative (jacobian).
        ceres::CostFunction* cost_function =
            new ceres::AutoDiffCostFunction<CostFunctor, 1, 1>(new CostFunctor);
        problem.AddResidualBlock(cost_function, nullptr, &x);

        // Run the solver!
        ceres::Solver::Options options;
        options.linear_solver_type = ceres::DENSE_QR;
        options.minimizer_progress_to_stdout = true;
        ceres::Solver::Summary summary;
        ceres::Solve(options, &problem, &summary);

        std::cout << summary.BriefReport() << "\n";
        std::cout << "x : " << initial_x
                  << " -> " << x << "\n";
    }

    // Read all the flag arguments.
    status = parseArgs(args);
    if (status == MStatus::kFailure) {
        return status;
    }

    MMCameraSolveCmd::setResult(outResult);
    return status;
}
