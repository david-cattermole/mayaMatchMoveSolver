"""
Query and set Maya scene state.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.solver.constant as const
import mmSolver.tools.solver.lib.scene_data as scene_data


LOG = mmSolver.logger.get_logger()


def get_active_collection():
    """
    Get the active collection object in the current scene file.

    :returns: The active Collection object, or None if no Collection
              is active.
    :rtype: Collection or None
    """
    uid = scene_data.get_scene_data(
        const.SCENE_DATA_ACTIVE_COLLECTION_UID
    )
    if uid is None:
        return None
    nodes = maya.cmds.ls(uid, long=True) or []
    col = None
    if len(nodes) > 0:
        col = mmapi.Collection(name=nodes[0])
    return col


def set_active_collection(col):
    """
    Set the Maya scene's active collection.

    There may only be 1 active collection in a Maya scene.

    :param col: The Collection to make active, or None to set no
                active collection.
    :type col: Collection or None

    :rtype: None
    """
    uid = None
    if col is not None:
        uid = col.get_node_uid()
    if uid is None:
        return
    scene_data.set_scene_data(
        const.SCENE_DATA_ACTIVE_COLLECTION_UID,
        uid
    )
    return


def get_refresh_viewport_state():
    value = scene_data.get_scene_data(
        const.SCENE_DATA_REFRESH_VIEWPORT
    )
    if value is None:
        value = const.SCENE_DATA_REFRESH_VIEWPORT_DEFAULT
    return value


def set_refresh_viewport_state(value):
    if isinstance(value, bool) is False:
        msg = 'value cannot be %r; %r is not bool'
        raise TypeError(msg % (type(value), value))
    scene_data.set_scene_data(
        const.SCENE_DATA_REFRESH_VIEWPORT,
        value
    )
    return


def get_log_level():
    value = scene_data.get_scene_data(
        const.SCENE_DATA_LOG_LEVEL
    )
    if value is None:
        value = const.SCENE_DATA_LOG_LEVEL_DEFAULT
    return value


def set_log_level(value):
    if isinstance(value, basestring) is False:
        msg = 'value cannot be %r; %r is not a string'
        raise TypeError(msg % (type(value), value))
    scene_data.set_scene_data(
        const.SCENE_DATA_LOG_LEVEL,
        value
    )
    return
