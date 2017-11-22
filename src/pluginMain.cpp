/*
 * Main Maya plugin entry point.
 */


#include <maya/MFnPlugin.h>
#include <mmSolverCmd.h>


// Register command with system
MStatus initializePlugin(MObject obj) {
    MStatus status;
    MFnPlugin plugin(obj, PLUGIN_COMPANY, "1.0", "Any");

    status = plugin.registerCommand(
            kCommandName,
            mmSolverCmd::creator,
            mmSolverCmd::newSyntax);
    if (!status) {
        status.perror("mmSolver: registerCommand");
        return status;
    }

    return status;
}

MStatus uninitializePlugin(MObject obj) {
    MStatus status;
    MFnPlugin plugin(obj);

    status = plugin.deregisterCommand(kCommandName);
    if (!status) {
        status.perror("mmSolver: deregisterCommand");
        return status;
    }

    return status;
}
