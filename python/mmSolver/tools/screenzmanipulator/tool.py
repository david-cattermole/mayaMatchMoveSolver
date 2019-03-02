"""
This tool aims the move manipulator tool at the active viewport camera.
After aiming the move tool at the camera, the screen-space Z axis is
highlighted, ready to be middle-click dragged.
"""
import maya.cmds
import mmSolver.logger
import mmSolver.tools.screenzmanipulator.lib as lib
LOG = mmSolver.logger.get_logger()


def screen_space_z(camera):
    """
    Modifies moveManipContext to custom and points one of the axis to
    focus camera.

    :param camera: Camera to point to
    :type camera: str
    :return: None
    """

    if not camera:
        LOG.warning('Please select a viewport')
        return
        
    cam_position = maya.cmds.xform(camera,
                                   worldSpace=True,
                                   query=True,
                                   translation=True)
    maya.cmds.manipMoveContext('Move',
                               edit=True,
                               mode=6,
                               activeHandle=0,
                               orientTowards=cam_position)
    return


def main():
    """
    Main function toggles between screen-space Z and object
    :return: None
    """
    selection = maya.cmds.ls(sl=True)
    if not selection:
        LOG.warning('Please select a object.')
        return

    camera = lib.__get_camera()

    if not camera:
        LOG.warning('Please select a viewport')
        return

    move_manip_mode = maya.cmds.manipMoveContext('Move',
                                                 query=True,
                                                 mode=True)
    maya.cmds.setToolTo('moveSuperContext')

    if move_manip_mode == 0 or move_manip_mode == 2:
        maya.cmds.manipMoveContext('Move', edit=True, mode=6)
        screen_space_z(camera)
        LOG.warning('manipMoveContext to ScreenZ')
    elif move_manip_mode == 6:
        maya.cmds.manipMoveContext('Move', edit=True, mode=0)
        LOG.warning('manipMoveContext to Object')
    return
