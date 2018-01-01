/*
 * Main Maya plugin entry point.
 */


#include <maya/MFnPlugin.h>

// TODO: Add entry points for mmReprojection cmd and node, mmMarkerScale cmd and node and mmTriangulate cmd.
#include <MMSolverCmd.h>
#include <MMTestCameraMatrixCmd.h>
// #include <MMReprojectionCmd.h>
// #include <MMTriangulateCmd.h>
// #include <MMMarkerScaleCmd.h>
// #include <MMMarkerScaleNode.h>


// TODO: Write #defines to register/deregister nodes.
#define REGISTER_COMMAND(plugin, name, creator, syntax, stat) \
    stat = plugin.registerCommand( name, creator, syntax);    \
    if (!stat) {                                              \
        stat.perror(MString(name) + ": registerCommand");     \
        return status;                                        \
    }

#define DEREGISTER_COMMAND(plugin, name, stat)              \
    stat = plugin.deregisterCommand(name);          \
    if (!stat) {                                            \
        stat.perror(MString(name) + ": deregisterCommand"); \
        return stat;                                        \
    }


#undef PLUGIN_COMPANY  // Maya API defines this, we override it.
#define PLUGIN_COMPANY "MM Solver"
#define PLUGIN_VERSION "1.0"


// Register with Maya
MStatus initializePlugin(MObject obj) {
    MStatus status;
    MFnPlugin plugin(obj, PLUGIN_COMPANY, PLUGIN_VERSION, "Any");

    REGISTER_COMMAND(plugin,
                     MMSolverCmd::cmdName(),
                     MMSolverCmd::creator,
                     MMSolverCmd::newSyntax,
                     status);
    REGISTER_COMMAND(plugin,
                     MMTestCameraMatrixCmd::cmdName(),
                     MMTestCameraMatrixCmd::creator,
                     MMTestCameraMatrixCmd::newSyntax,
                     status);
    // REGISTER_COMMAND(plugin,
    //                  MMReprojectionCmd::cmdName(),
    //                  MMReprojectionCmd::creator,
    //                  MMReprojectionCmd::newSyntax,
    //                  status);
    // REGISTER_COMMAND(plugin,
    //                  MMTriangulateCmd::cmdName(),
    //                  MMTriangulateCmd::creator,
    //                  MMTriangulateCmd::newSyntax,
    //                  status);
    // REGISTER_COMMAND(plugin,
    //                  MMMarkerScaleCmd::cmdName(),
    //                  MMMarkerScaleCmd::creator,
    //                  MMMarkerScaleCmd::newSyntax,
    //                  status);

//    status = plugin.registerNode(
//            kVelocityNodeName,
//            velocityNode::id,
//            velocityNode::creator,
//            velocityNode::initialize);
//    if (!status) {
//        status.perror("velocityNode: registerNode");
//        return (status);
//    }

    return status;
}


// Deregister with Maya
MStatus uninitializePlugin(MObject obj) {
    MStatus status;
    MFnPlugin plugin(obj);

    DEREGISTER_COMMAND(plugin, MMSolverCmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, MMTestCameraMatrixCmd::cmdName(), status);
    // DEREGISTER_COMMAND(plugin, MMReprojectionCmd::cmdName(), status);
    // DEREGISTER_COMMAND(plugin, MMTriangulateCmd::cmdName(), status);
    // DEREGISTER_COMMAND(plugin, MMMarkerScaleCmd::cmdName(), status);

    //    status = plugin.deregisterNode(velocityNode::id);
    //    if (!status) {
    //        status.perror("velocityNode: deregisterNode");
    //        return (status);
    //    }
    //
    //    return (status);
    //}

    return status;
}
