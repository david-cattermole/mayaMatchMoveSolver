/*
 * Main Maya plugin entry point.
 */


#include <maya/MFnPlugin.h>
#include <MMSolverCmd.h>


// Register command with system
MStatus initializePlugin(MObject obj) {
    MStatus status;
    MFnPlugin plugin(obj, PLUGIN_COMPANY, COMMAND_VERSION, "Any");

    status = plugin.registerCommand(
            COMMAND_NAME,
            MMSolverCmd::creator,
            MMSolverCmd::newSyntax);
    if (!status) {
        status.perror("mmSolver: registerCommand");
        return status;
    }

    return status;
}

MStatus uninitializePlugin(MObject obj) {
    MStatus status;
    MFnPlugin plugin(obj);

    status = plugin.deregisterCommand(COMMAND_NAME);
    if (!status) {
        status.perror("mmSolver: deregisterCommand");
        return status;
    }

    return status;
}
