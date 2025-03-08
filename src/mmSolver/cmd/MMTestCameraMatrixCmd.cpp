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
 * Command for running mmTestCameraMatrix.
 *
 * Example usage:
 * success = maya.cmds.mmTestCameraMatrix('myCameraTransform', 'myCameraShape')
 */

#include "MMTestCameraMatrixCmd.h"

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
#include <maya/MFloatMatrix.h>
#include <maya/MFnCamera.h>
#include <maya/MFnDagNode.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>
#include <maya/MMatrix.h>
#include <maya/MObject.h>
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
#include "mmSolver/adjust/adjust_defines.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

namespace mmsolver {

MMTestCameraMatrixCmd::~MMTestCameraMatrixCmd() {}

MString MMTestCameraMatrixCmd::cmdName() {
    return MString("mmTestCameraMatrix");
}

void *MMTestCameraMatrixCmd::creator() { return new MMTestCameraMatrixCmd(); }

/*
 * Tell Maya we have a syntax function.
 */
bool MMTestCameraMatrixCmd::hasSyntax() const { return true; }

bool MMTestCameraMatrixCmd::isUndoable() const { return false; }

/*
 * Add flags to the command syntax
 */
MSyntax MMTestCameraMatrixCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);
    syntax.useSelectionAsDefault(false);
    syntax.setObjectType(MSyntax::kStringObjects, 2, 2);
    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMTestCameraMatrixCmd::parseArgs(const MArgList &args) {
    // MMSOLVER_MAYA_DBG("MMTestCameraMatrixCmd::parseArgs()");
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    MStringArray objects;
    status = argData.getObjects(objects);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    if (objects.length() != 2) {
        status = MS::kFailure;
        return status;
    }

    MString cameraTransform = objects[0];
    status = nodeExistsAndIsType(cameraTransform, MFn::Type::kTransform);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    MString cameraShape = objects[1];
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status = nodeExistsAndIsType(cameraShape, MFn::Type::kCamera);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_camera = CameraPtr(new Camera());
    m_camera->setTransformNodeName(cameraTransform);
    m_camera->setShapeNodeName(cameraShape);

    // MMSOLVER_MAYA_DBG("Camera:");
    // MMSOLVER_MAYA_DBG("  Transform = " << m_camera->getTransformNodeName());
    // MMSOLVER_MAYA_DBG("  Shape = " << m_camera->getShapeNodeName());

    return status;
}

MStatus MMTestCameraMatrixCmd::doIt(const MArgList &args) {
    //
    //  Description:
    //    implements the MEL mmTestCameraMatrix command.
    //
    //  Arguments:
    //    argList - the argument list that was passes to the command from MEL
    //
    //  Return Value:
    //    MS::kSuccess - command succeeded
    //    MS::kFailure - command failed (returning this value will cause the
    //                     MEL script that is being run to terminate unless the
    //                     error is caught using a "catch" statement.
    //
    const int timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
    // MMSOLVER_MAYA_DBG("MMTestCameraMatrixCmd::doIt()");

    // Read all the arguments.
    MStatus status = parseArgs(args);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Maya Camera Function Set
    MFnCamera cameraFn(m_camera->getShapeObject(), &status);

    // Maya Projection Matrix
    MFloatMatrix floatProjMatrix_maya = cameraFn.projectionMatrix(&status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    MMatrix projMatrix_maya = MMatrix(&floatProjMatrix_maya.matrix[0]);

    // Maya World Matrix
    MMatrix worldMatrix_maya;
    Attr matrixAttr = m_camera->getMatrixAttr();
    status = matrixAttr.getValue(worldMatrix_maya, timeEvalMode);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    worldMatrix_maya = worldMatrix_maya.inverse();
    MMatrix value_maya = worldMatrix_maya * projMatrix_maya;

    // MM Solver World Projection Matrix
    MMatrix value;
    m_camera->getWorldProjMatrix(value, timeEvalMode);

    // Compare Maya verses MM Solver projection matrix
    double tolerance = 1.0e-4;  // acceptable error margin.
    bool matches = value.isEquivalent(value_maya, tolerance);
    setResult(matches);

    // Print Matches
    if (!matches) {
        for (unsigned int i = 0; i < 4; ++i) {
            for (unsigned int j = 0; j < 4; ++j) {
                MMSOLVER_MAYA_INFO(
                    "[" << i << "][" << j << "] " << value(i, j)
                        << " == " << value_maya(i, j) << " | "
                        << number::isApproxEqual<double>(
                               value(i, j), value_maya(i, j), tolerance));
            }
        }
    }

    return status;
}

}  // namespace mmsolver
