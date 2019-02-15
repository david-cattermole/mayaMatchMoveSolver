"""
The Channel Sensitivitiy tool - user facing.
"""

import maya.cmds
import mmSolver.logger
import maya.mel


LOG = mmSolver.logger.get_logger()


def get_value():
    """
    Get the current channel sensitivity value.

    :return: Current channel sensitivity value
    :rtype: float
    """
    global_variable = __channelbox_global_variable()
    current_value = maya.cmds.channelBox(global_variable,
                                         speed=True,
                                         query=True)
    return current_value


def set_value(sensitivity=None):
    """
    Set channel sensitivity value
    :param sensitivity: A possible value to set channel sensitivity
    value
    :type: str or float or int
    :return: None
    """
    current_value = get_value()
    global_variable = __channelbox_global_variable()
    cmd = 'channelBoxSettings useManips 1;'
    maya.mel.eval(cmd)
    if sensitivity:
        maya.cmds.channelBox(global_variable,
                             speed=current_value*sensitivity,
                             edit=True)
    else:
        maya.cmds.channelBox(global_variable,
                             speed=1.0,
                             edit=True)
    return


def __channelbox_global_variable():
    """
    Get global channel box name

    :return: Global Channel box name
    :rtype: str
    """
    return maya.mel.eval("global string $gChannelBoxName;"
                         " string $temp = $gChannelBoxName;")
