"""
The Channel Sensitivity tool - user facing.
"""

import maya.cmds
import maya.mel
import mmSolver.logger


LOG = mmSolver.logger.get_logger()


def get_value():
    """
    Get the current channel sensitivity value.

    :return: Current channel sensitivity value
    :rtype: float
    """
    channel_box = __channelbox_global_variable()
    value = maya.cmds.channelBox(channel_box,
                                 query=True,
                                 speed=True)
    return value


def set_value(value):
    """
    Set channel sensitivity value.

    :param value: A possible value to set channel sensitivity
                  value
    :return: None
    """
    channel_box = __channelbox_global_variable()
    cmd = 'channelBoxSettings useManips 1;'
    maya.mel.eval(cmd)

    maya.cmds.channelBox(channel_box,
                         edit=True,
                         speed=value)
    return


def __channelbox_global_variable():
    """
    Get global channel box name

    :return: Global Channel box name
    :rtype: str
    """
    return maya.mel.eval("global string $gChannelBoxName;"
                         " string $temp = $gChannelBoxName;")
