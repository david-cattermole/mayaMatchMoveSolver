/*
 * Command for running mmSolver.
 */


//
#include <MMSolverCmd.h>
#include <mmSolverUtils.h>
#include <mayaUtils.h>

// STL
#include <cmath>

// Utils
#include <utilities/debugUtils.h>

// Maya
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MFnDependencyNode.h>

// Internal Objects
#include <Marker.h>
#include <Bundle.h>
#include <Camera.h>


MMSolverCmd::~MMSolverCmd() {}

void *MMSolverCmd::creator() {
    return new MMSolverCmd();
}

/*
 * Tell Maya we have a syntax function.
 */
bool MMSolverCmd::hasSyntax() const {
    return true;
}

bool MMSolverCmd::isUndoable() const {
    return true;
}

/*
 * Add flags to the command syntax
 */
MSyntax MMSolverCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    // Flags
    syntax.addFlag(CAMERA_FLAG, CAMERA_FLAG_LONG, MSyntax::kString, MSyntax::kString);
    syntax.addFlag(MARKER_FLAG, MARKER_FLAG_LONG, MSyntax::kString, MSyntax::kString, MSyntax::kString);
    syntax.addFlag(ATTR_FLAG, ATTR_FLAG_LONG, MSyntax::kString);
    syntax.addFlag(FRAME_FLAG, FRAME_FLAG_LONG, MSyntax::kLong);
    syntax.addFlag(TAU_FLAG, TAU_FLAG_LONG, MSyntax::kDouble);
    syntax.addFlag(EPSILON1_FLAG, EPSILON1_FLAG_LONG, MSyntax::kDouble);
    syntax.addFlag(EPSILON2_FLAG, EPSILON2_FLAG_LONG, MSyntax::kDouble);
    syntax.addFlag(EPSILON3_FLAG, EPSILON3_FLAG_LONG, MSyntax::kDouble);
    syntax.addFlag(DELTA_FLAG, DELTA_FLAG_LONG, MSyntax::kDouble);
    syntax.addFlag(SOLVER_TYPE_FLAG, SOLVER_TYPE_FLAG_LONG, MSyntax::kUnsigned);
    syntax.addFlag(ITERATIONS_FLAG, ITERATIONS_FLAG_LONG, MSyntax::kUnsigned);
    syntax.addFlag(VERBOSE_FLAG, VERBOSE_FLAG_LONG, MSyntax::kBoolean);

    // We can use marker and attr flags more than once.
    syntax.makeFlagMultiUse(CAMERA_FLAG);
    syntax.makeFlagMultiUse(MARKER_FLAG);
    syntax.makeFlagMultiUse(ATTR_FLAG);
    syntax.makeFlagMultiUse(FRAME_FLAG);

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMSolverCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_cameraList.clear();
    m_markerList.clear();
    m_bundleList.clear();

    // Get 'Camera'
    MString cameraTransform = "";
    MString cameraShape = "";
    unsigned int cameraNum = argData.numberOfFlagUses(CAMERA_FLAG);
    for (unsigned int i = 0; i < cameraNum; ++i) {

        MArgList cameraArgs;
        status = argData.getFlagArgumentList(CAMERA_FLAG, i, cameraArgs);
        if (status == MStatus::kSuccess) {
            if (cameraArgs.length() != 2) {
                ERR("Camera argument list must have 2 arguments; \"cameraTransform\", \"cameraShape\".");
                continue;
            }

            cameraTransform = cameraArgs.asString(0, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            nodeExistsAndIsType(cameraTransform, MFn::Type::kTransform);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            cameraShape = cameraArgs.asString(1, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            nodeExistsAndIsType(cameraShape, MFn::Type::kCamera);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            CameraPtr camera = CameraPtr(new Camera());
            camera->setTransformNodeName(cameraTransform);
            camera->setShapeNodeName(cameraShape);
            m_cameraList.push_back(camera);

            // DBG("Camera = " << i);
            // DBG("  Transform = " << camera->getTransformNodeName());
            // DBG("  Shape = " << camera->getShapeNodeName());
        }
    }

    // Get 'Markers'
    MString markerName = "";
    MString cameraName = "";
    MString bundleName = "";
    unsigned int markerNum = argData.numberOfFlagUses(MARKER_FLAG);
    for (unsigned int i = 0; i < markerNum; ++i) {
        MArgList markerArgs;
        status = argData.getFlagArgumentList(MARKER_FLAG, i, markerArgs);
        if (status == MStatus::kSuccess) {
            if (markerArgs.length() != 3) {
                ERR("Marker argument list must have 3 arguments; \"marker\", \"cameraShape\",  \"bundle\".");
                continue;
            }

            markerName = markerArgs.asString(0, &status);
            // DBG("markerName=" << markerName);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            status = nodeExistsAndIsType(markerName, MFn::Type::kTransform);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            cameraName = markerArgs.asString(1, &status);
            // DBG("cameraName=" << cameraName);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            status = nodeExistsAndIsType(cameraName, MFn::Type::kCamera);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            bundleName = markerArgs.asString(2, &status);
            // DBG("bundleName=" << bundleName);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            status = nodeExistsAndIsType(bundleName, MFn::Type::kTransform);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            // Camera
            CameraPtr camera = CameraPtr(new Camera());
            for (unsigned int j = 0; j < m_cameraList.size(); ++j) {
                if (m_cameraList[j]->getShapeNodeName() == cameraName) {
                    camera = m_cameraList[j];
                    break;
                }
            }
            if (camera->getShapeNodeName() == "") {
                ERR("Camera shape name was not given with marker. "
                            << "marker=" << markerName << " "
                            << "camera=" << cameraName << " "
                            << "bundle=" << bundleName);
            }

            // Bundle
            BundlePtr bundle = BundlePtr(new Bundle());
            for (unsigned int j = 0; j < m_bundleList.size(); ++j) {
                if (m_bundleList[j]->getNodeName() == bundleName) {
                    bundle = m_bundleList[j];
                    break;
                }
            }
            if (bundle->getNodeName() == "") {
                bundle->setNodeName(bundleName);
            }

            // Marker
            for (unsigned int j = 0; j < m_markerList.size(); ++j) {
                if (m_markerList[j]->getNodeName() == markerName) {
                    ERR("Marker name cannot be specified more than once. markerName=" << markerName);
                }
            }
            MarkerPtr marker = MarkerPtr(new Marker());
            marker->setNodeName(markerName);
            marker->setBundle(bundle);
            marker->setCamera(camera);

            m_markerList.push_back(marker);
            m_bundleList.push_back(bundle);

            // DBG("Marker = " << i);
            // DBG("  Camera = " << cameraName << " : " << camera->getTransformNodeName() << " : "
            //                   << camera->getShapeNodeName());
            // DBG("  Marker = " << markerName << " : " << marker->getNodeName());
            // DBG("  Bundle = " << bundleName << " : " << bundle->getNodeName());
        }
    }

    // Get 'Attributes'
    m_attrList.clear();
    unsigned int attrsNum = argData.numberOfFlagUses(ATTR_FLAG);
    for (unsigned int i = 0; i < attrsNum; ++i) {
        MArgList attrArgs;
        status = argData.getFlagArgumentList(ATTR_FLAG, i, attrArgs);
        if (status == MStatus::kSuccess) {
            if (attrArgs.length() != 1) {
                ERR("Attribute argument list must have 1 argument; \"node.attribute\".");
                continue;
            }

            AttrPtr attr = AttrPtr(new Attr());
            MString nodeAttrName = attrArgs.asString(0);
            attr->setName(nodeAttrName);
            m_attrList.push_back(attr);

            MPlug attrPlug = attr->getPlug();
            // DBG("Attr = " << i << " : "
            //               << attr->getName() << " : "
            //               << attr->getNodeName() << " : "
            //               << attr->isAnimated() << " : "
            //               << attrPlug.name());
        }
    }

    // Get 'Frames'
    m_frameList.clear();
    MTime::Unit unit = MTime::uiUnit();
    unsigned int framesNum = argData.numberOfFlagUses(FRAME_FLAG);
    for (unsigned int i = 0; i < framesNum; ++i) {
        MArgList frameArgs;
        status = argData.getFlagArgumentList(FRAME_FLAG, i, frameArgs);
        if (status == MStatus::kSuccess) {
            if (frameArgs.length() != 1) {
                ERR("Attribute argument list must have 1 argument; \"frame\".");
                continue;
            }
            int value = frameArgs.asInt(0, &status);
            CHECK_MSTATUS(status);

            MTime frame = MTime((double) value, unit);
            m_frameList.append(frame);
            // DBG("Frame = " << i << " : " << frame << " : " << value);
        }
    }

    // Make sure we have a frame list.
    if (m_frameList.length() == 0) {
        status = MS::kFailure;
        status.perror("Frame List length is 0, must have a frame to solve.");
        return status;
    }

    // Get 'Iterations'
    m_iterations = ITERATIONS_DEFAULT_VALUE;
    if (argData.isFlagSet(ITERATIONS_FLAG)) {
        status = argData.getFlagArgument(ITERATIONS_FLAG, 0, m_iterations);
        CHECK_MSTATUS(status);
    }
    // DBG("m_iterations=" << m_iterations);

    // Get 'Tau'
    m_tau = TAU_DEFAULT_VALUE;
    if (argData.isFlagSet(TAU_FLAG)) {
        status = argData.getFlagArgument(TAU_FLAG, 0, m_tau);
        CHECK_MSTATUS(status);
    }
    // DBG("m_tau=" << m_tau);

    // Get 'Epsilon1'
    m_epsilon1 = EPSILON1_DEFAULT_VALUE;
    if (argData.isFlagSet(EPSILON1_FLAG)) {
        status = argData.getFlagArgument(EPSILON1_FLAG, 0, m_epsilon1);
        CHECK_MSTATUS(status);
    }
    // DBG("m_epsilon1=" << m_epsilon1);

    // Get 'Epsilon2'
    m_epsilon2 = EPSILON2_DEFAULT_VALUE;
    if (argData.isFlagSet(EPSILON2_FLAG)) {
        status = argData.getFlagArgument(EPSILON2_FLAG, 0, m_epsilon2);
        CHECK_MSTATUS(status);
    }
    // DBG("m_epsilon2=" << m_epsilon2);

    // Get 'Epsilon3'
    m_epsilon3 = EPSILON3_DEFAULT_VALUE;
    if (argData.isFlagSet(EPSILON3_FLAG)) {
        status = argData.getFlagArgument(EPSILON3_FLAG, 0, m_epsilon3);
        CHECK_MSTATUS(status);
    }
    // DBG("m_epsilon3=" << m_epsilon3);

    // Get 'Delta'
    m_delta = DELTA_DEFAULT_VALUE;
    if (argData.isFlagSet(DELTA_FLAG)) {
        status = argData.getFlagArgument(DELTA_FLAG, 0, m_delta);
        CHECK_MSTATUS(status);
    }
    // DBG("m_delta=" << m_delta);

    // Get 'Solver Type'
    m_solverType = SOLVER_TYPE_DEFAULT_VALUE;
    if (argData.isFlagSet(SOLVER_TYPE_FLAG)) {
        status = argData.getFlagArgument(SOLVER_TYPE_FLAG, 0, m_solverType);
        CHECK_MSTATUS(status);
    }
    // DBG("m_solverType=" << m_solverType);

    // Get 'Verbose'
    m_verbose = VERBOSE_DEFAULT_VALUE;
    if (argData.isFlagSet(VERBOSE_FLAG)) {
        status = argData.getFlagArgument(VERBOSE_FLAG, 0, m_verbose);
        CHECK_MSTATUS(status);
    }
    // DBG("m_verbose=" << m_verbose);

    return status;
}


MStatus MMSolverCmd::doIt(const MArgList &args) {
//
//  Description:
//    implements the MEL mmSolver command.
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
    MStatus status = MStatus::kSuccess;
    // DBG("MMSolverCmd::doIt()");

    // Mouse cursor spinning...
    MGlobal::executeCommand("waitCursor -state on;");

    // Read all the flag arguments.
    status = parseArgs(args);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    assert(m_frameList.length() > 0);

    // Don't store each individial edits, just store the combination of edits.
    m_curveChange.setInteractive(true);

    MStringArray outResult;
    bool ret = solve(
            m_iterations,
            m_tau,
            m_epsilon1,
            m_epsilon2,
            m_epsilon3,
            m_delta,
            m_solverType,
            m_cameraList,
            m_markerList,
            m_bundleList,
            m_attrList,
            m_frameList,
            m_dgmod,
            m_curveChange,
            m_computation,
            m_verbose,
            outResult
    );

    MMSolverCmd::setResult(outResult);
    if (ret == false) {
        WRN("mmSolver: Solver returned false!");
    }

    // Mouse cursor back to normal.
    MGlobal::executeCommand("waitCursor -state off;");
    return status;
}

MStatus MMSolverCmd::redoIt() {
//
//  Description:
//    Implements redo for the MEL mmSolver command.
//
//    This method is called when the user has undone a command of this type
//    and then redoes it.  No arguments are passed in as all of the necessary
//    information is cached by the doIt method.
//
//  Return Value:
//    MS::kSuccess - command succeeded
//    MS::kFailure - redoIt failed.  this is a serious problem that will
//                     likely cause the undo queue to be purged
//
    MStatus status;
    // DBG("MMSolverCmd::redoIt()");
    m_dgmod.doIt();
    m_curveChange.redoIt();
    return status;
}

MStatus MMSolverCmd::undoIt() {
//
//  Description:
//    implements undo for the MEL mmSolver command.
//
//    This method is called to undo a previous command of this type.  The
//    system should be returned to the exact state that it was it previous
//    to this command being executed.  That includes the selection state.
//
//  Return Value:
//    MS::kSuccess - command succeeded
//    MS::kFailure - redoIt failed.  this is a serious problem that will
//                     likely cause the undo queue to be purged
//
    MStatus status;
    // DBG("MMSolverCmd::undoIt()");
    m_curveChange.undoIt();
    m_dgmod.undoIt();
    return status;
}
