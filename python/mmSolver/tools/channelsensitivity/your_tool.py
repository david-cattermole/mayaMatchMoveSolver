"""
This is a channel sensitivity tool
"""
import maya.cmds
import mmSolver.logger

LOG = mmSolver.logger.get_logger()


def channel_sensitivity(increase=None, decrease=None):
    """
    Change main channel box sensitivity
    :return:
    """
    current_value = maya.cmds.channelBox('mainChannelBox',
                                         speed=True,
                                         query=True)
    if increase:
        value = current_value*10

    elif decrease:
        value = current_value*0.1
    else:
        value = 0.1
    maya.cmds.channelBox('mainChannelBox', speed=value,
                         edit=True)
    LOG.warning('Channel Sensitivity set to %s' % value)
    return


def channel_sensitivity_ui():
    """
    Ui to control channel sensitivity
    :return:
    """

    if maya.cmds.window('ChannelSensitivity', exists=True):
        maya.cmds.deleteUI('ChannelSensitivity')

    window = maya.cmds.window('ChannelSensitivity',
                              iconName='Short Name',
                              widthHeight=(500, 200))
    maya.cmds.columnLayout(adjustableColumn=True)
    maya.cmds.button(label='Increase',
                     command='channel_sensitivity(increase=True,'
                             ' decrease=False)')
    maya.cmds.button(label='Decrease',
                     command='channel_sensitivity(increase=False,'
                             ' decrease=True)')
    maya.cmds.button(label='Default',
                     command='channel_sensitivity(increase=False,'
                             ' decrease=False)')
    maya.cmds.setParent('..')
    maya.cmds.showWindow(window)
