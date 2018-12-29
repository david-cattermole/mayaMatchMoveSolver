"""
Set up callbacks for Maya events.
"""

import maya.OpenMaya as OpenMaya
import mmSolver.logger


LOG = mmSolver.logger.get_logger()


def add_callbacks_new_scene(obj_UI):
    """
    Create callback to be run just before a new Maya scene is created.

    :param obj_UI: The Solver Window that should be closed when a new
                   scene is created.
    :type obj_UI: mmSolver.tools.solver.ui.solver_window.SolverWindow

    :return: Maya callback ids.
    :rtype: list of maya.OpenMaya.MCallbackId
    """
    msgs = [
        OpenMaya.MSceneMessage.kBeforeNew,
        OpenMaya.MSceneMessage.kBeforeOpen
    ]
    clientData = obj_UI
    func = new_scene_func_callback
    callback_ids = []
    for msg in msgs:
        callback_id = OpenMaya.MSceneMessage.addCallback(
            msg,
            func,
            clientData
        )
        callback_ids.append(callback_id)
    return callback_ids


def remove_callbacks_new_scene(callback_ids):
    """
    Remove Maya Callbacks for 'New scene'
    """
    for callback_id in callback_ids:
        OpenMaya.MMessage.removeCallback(callback_id)
    return


def new_scene_func_callback(clientData):
    """
    Create a callback called just before a new scene file is created
    or before a new file is loaded. The UI must be closed. All data
    structures stored must be removed.
    """
    # msg = 'Closing down the mmSolver Solver Window! %r'
    # LOG.warning(msg, clientData)
    clientData.close()
    return
