"""
Time related utilities.
"""


import maya.cmds


def get_maya_timeline_range_inner():
    """
    Get the Maya frame range (inner bar).

    :returns: start frame and end frame as tuple.
    :rtype: int, int
    """
    s = maya.cmds.playbackOptions(query=True, minTime=True)
    e = maya.cmds.playbackOptions(query=True, maxTime=True)
    return int(s), int(e)


def get_maya_timeline_range_outer():
    """
    Get the Maya frame range (outer bar).

    :returns: start frame and end frame as tuple.
    :rtype: int, int
    """
    s = maya.cmds.playbackOptions(query=True, animationStartTime=True)
    e = maya.cmds.playbackOptions(query=True, animationEndTime=True)
    return int(s), int(e)

