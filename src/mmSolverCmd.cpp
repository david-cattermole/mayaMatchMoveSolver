/*
 * Command for running mmSolver.
 */


//
#include <mmSolverCmd.h>
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


mmSolverCmd::~mmSolverCmd() {}

void *mmSolverCmd::creator() {
    return new mmSolverCmd();
}


/*
 * Tell Maya we have a syntax function.
 */
bool mmSolverCmd::hasSyntax() const {
    return true;
}

bool mmSolverCmd::isUndoable() const {
    // TODO: Switch this to true once we support undo/redo.
    return false;
}


/*
 * Add flags to the command syntax
 */
MSyntax mmSolverCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    // Flags
    syntax.addFlag(kCameraFlag, kCameraFlagLong, MSyntax::kString, MSyntax::kString);
    syntax.addFlag(kMarkerFlag, kMarkerFlagLong, MSyntax::kString, MSyntax::kString, MSyntax::kString,  MSyntax::kDouble);
    syntax.addFlag(kAttrFlag, kAttrFlagLong, MSyntax::kString, MSyntax::kBoolean);
    syntax.addFlag(kStartFrameFlag, kStartFrameFlagLong, MSyntax::kLong);
    syntax.addFlag(kEndFrameFlag, kEndFrameFlagLong, MSyntax::kLong);
    syntax.addFlag(kIterationsFlag, kIterationsFlagLong, MSyntax::kUnsigned);
    syntax.addFlag(kVerboseFlag, kVerboseFlagLong, MSyntax::kBoolean);

    // We can use marker and attr flags more than once.
    syntax.makeFlagMultiUse(kCameraFlag);
    syntax.makeFlagMultiUse(kMarkerFlag);
    syntax.makeFlagMultiUse(kAttrFlag);

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus mmSolverCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Get 'Camera'
    m_cameraList.clear();
    unsigned int cameraNum = argData.numberOfFlagUses(kCameraFlag);
    for (unsigned int i=0; i<cameraNum; ++i) {
        MString cameraTransform = "";
        status = argData.getFlagArgument(kCameraFlag, 0, cameraTransform);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        MString cameraShape = "";
        status = argData.getFlagArgument(kCameraFlag, 1, cameraShape);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        // TODO: Check node names are valid before creating a Camera object.

        // Camera cam = Camera();
        CameraPtr camera = CameraPtr(new Camera());
        camera->setTransformNodeName(cameraTransform);
        camera->setShapeNodeName(cameraShape);
        m_cameraList.push_back(camera);

        INFO("Camera = " << i);
        INFO("  Transform = " << camera->getTransformNodeName());
        INFO("  Shape = " << camera->getShapeNodeName());
    }

    // Get 'Markers'
    m_markerList.clear();
    m_bundleList.clear();
    unsigned int markerNum = argData.numberOfFlagUses(kMarkerFlag);
    for (unsigned int i=0; i<markerNum; ++i) {

        MArgList markerArgs;
        status = argData.getFlagArgumentList(kMarkerFlag, i, markerArgs);
        if(status == MStatus::kSuccess) {
            if (markerArgs.length() != 4){
                ERR("Marker argument list must have 4 arguments; \"marker\", \"cameraShape\",  \"bundle\", \"weight\".");
                continue;
            }

            // TODO: Ensure we have a marker and bundle node.
            // Test the node type to be sure; they should be transforms.

            MString markerName = markerArgs.asString(0);
            MString cameraName = markerArgs.asString(1);
            MString bundleName = markerArgs.asString(2);
            double weight = markerArgs.asDouble(3);

            // Camera camera;
            CameraPtr camera = CameraPtr(new Camera());
            for (unsigned int j=0; j<m_cameraList.size(); ++j) {
                if (m_cameraList[j]->getShapeNodeName() == cameraName) {
                    camera = m_cameraList[j];
                    break;
                }
            }
            if (camera->getShapeNodeName() == "") {
                ERR("Camera shape name was not given with marker. "
                            << "marker=" << markerName << " "
                            << "camera=" << cameraName << " "
                            << "bundle=" << bundleName << " "
                            << "weight=" << weight);
            }

            BundlePtr bundle = BundlePtr(new Bundle());
            for (unsigned int j=0; j<m_bundleList.size(); ++j) {
                if (m_bundleList[j]->getNodeName() == bundleName) {
                    bundle = m_bundleList[j];
                    break;
                }
            }
            if (bundle->getNodeName() == "") {
                bundle->setNodeName(bundleName);
                bundle->setWeight(weight);
            }

            for (unsigned int j=0; j<m_markerList.size(); ++j) {
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

            INFO("Marker = " << i);
            INFO("  Camera = " << cameraName << " : " << camera->getTransformNodeName() << " : " << camera->getShapeNodeName());
            INFO("  Marker = " << markerName << " : " << marker->getNodeName());
            INFO("  Bundle = " << bundleName << " : " << bundle->getNodeName());
            INFO("  Weight = " << weight << " : " << bundle->getWeight());
        }
    }

    // Get 'Attributes'
    m_attrList.clear();
    unsigned int attrsNum = argData.numberOfFlagUses(kAttrFlag);
    for (unsigned int i=0; i<attrsNum; ++i) {
        MArgList attrArgs;
        status = argData.getFlagArgumentList(kAttrFlag, i, attrArgs);
        if(status == MStatus::kSuccess) {
            if (attrArgs.length() != 2){
                ERR("Attribute argument list must have 2 argument; \"node.attribute\", \"static\".");
                continue;
            }

            // Attr attr = Attr();
            AttrPtr attr = AttrPtr(new Attr());
            MString nodeAttrName = attrArgs.asString(0);
            bool attrStatic = attrArgs.asBool(1);
            attr->setName(nodeAttrName);
            attr->setStatic(attrStatic);
            m_attrList.push_back(attr);

            MPlug attrPlug = attr->getPlug();
            INFO("Attr = " << i << " : "
                           << attr->getName() << " : "
                           << attr->getNodeName() << " : "
                           << attr->getStatic() << " : "
                           << attrPlug.name());
        }
    }

    // Get 'Start Frame'
    m_startFrame = kStartFrameDefaultValue;
    if (argData.isFlagSet(kStartFrameFlag)) {
        status = argData.getFlagArgument(kStartFrameFlag, 0, m_startFrame);
    }
    INFO("m_startFrame=" << m_startFrame);

    // Get 'End Frame'
    m_endFrame = kEndFrameDefaultValue;
    if (argData.isFlagSet(kEndFrameFlag)) {
        status = argData.getFlagArgument(kEndFrameFlag, 0, m_endFrame);
    }
    INFO("m_endFrame=" << m_endFrame);

    // Get 'Iterations'
    m_iterations = kIterationsDefaultValue;
    if (argData.isFlagSet(kIterationsFlag)) {
        status = argData.getFlagArgument(kIterationsFlag, 0, m_iterations);
    }
    INFO("m_iterations=" << m_iterations);

    // Get 'Verbose'
    m_verbose = kVerboseDefaultValue;
    if (argData.isFlagSet(kVerboseFlag)) {
        status = argData.getFlagArgument(kVerboseFlag, 0, m_verbose);
    }
    INFO("m_verbose=" << m_verbose);

    return status;
}


MStatus mmSolverCmd::doIt(const MArgList &args) {
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
    INFO("mmSolverCmd::doIt()");

    // Read all the flag arguments.
    status = parseArgs(args);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    int iterMax = m_iterations;
    double outError = -1.0;
    bool ret = solve(
            iterMax,
            m_cameraList,
            m_markerList,
            m_bundleList,
            m_attrList,
            m_dgmod,
            outError);
    mmSolverCmd::setResult(outError);
    if (ret == false) {
        WRN("mmSolver: Solver returned false!");
    }
    return status;
}

MStatus mmSolverCmd::redoIt() {
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
    INFO("mmSolverCmd::redoIt()");
    return status;
}

MStatus mmSolverCmd::undoIt() {
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
    INFO("mmSolverCmd::undoIt()");
    return status;
}
