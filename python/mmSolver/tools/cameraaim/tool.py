"""
Aim the selected transform nodes at the current viewport's camera.
"""

import warnings
import maya.cmds
import mmSolver.logger
import mmSolver.utils.viewport as utils_viewport
import mmSolver.tools.cameraaim.lib as lib

LOG = mmSolver.logger.get_logger()


def main():
    """
    Aims the selected transforms at the active viewport's camera
    transform node.
    """
    sel = maya.cmds.ls(sl=True, type='transform') or []
    if len(sel) == 0:
        LOG.warning('Please select at least one object!')
        return

    # Get camera
    model_editor = utils_viewport.get_active_model_editor()
    if model_editor is None:
        msg = 'Please select an active 3D viewport.'
        LOG.warning(msg)
        return
    cam_tfm, cam_shp = utils_viewport.get_viewport_camera(model_editor)
    if cam_shp is None:
        LOG.warning('Please select an active viewport to get a camera.')
        return

    lib.aim_at_target(sel, cam_tfm, remove_after=True)
    return


def aim_at_camera():
    warnings.warn("Use 'main' function instead.")
    main()
