# Copyright (C) 2018, 2019 David Cattermole.
#
# This file is part of mmSolver.
#
# mmSolver is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# mmSolver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Query and set Maya scene state.

All data is stored in the Maya scene and is dependent on the Maya
scene.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.python_compat as pycompat
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
    uid = scene_data.get_scene_data(const.SCENE_DATA_ACTIVE_COLLECTION_UID)
    if uid is None:
        return None
    nodes = maya.cmds.ls(uid, long=True) or []
    col = None
    if len(nodes) > 0:
        col = mmapi.Collection(node=nodes[0])
    return col


def set_active_collection(col):
    """
    Set the Maya scene's active collection.

    There may only be 1 active collection, or no active collection in
    a Maya scene.

    :param col: The Collection to make active, or None to set no
                active collection.
    :type col: Collection or None

    :rtype: None
    """
    uid = None
    if col is None:
        scene_data.set_scene_data(const.SCENE_DATA_ACTIVE_COLLECTION_UID, uid)
        return
    uid = col.get_node_uid()
    if uid is None:
        return
    scene_data.set_scene_data(const.SCENE_DATA_ACTIVE_COLLECTION_UID, uid)
    return


def get_state_bool(name, default_value):
    """
    Get State boolean from the scene settings.

    :param name: Name of the state boolean variable.
    :type name: str

    :param default_value: Fallback value, if 'name' cannot be found.
    :type default_value: bool

    :return: The queried value, or 'default_value'.
    :rtype: bool
    """
    value = scene_data.get_scene_data(name)
    if value is None:
        value = default_value
    return value


def set_state_bool(name, value):
    """
    Get a boolean stored in the scene settings.

    :param name: Name of the state boolean variable.
    :type name: str

    :param value: Value to set.
    :type value: bool
    """
    if isinstance(value, bool) is False:
        msg = 'Value cannot be %r; %r is not bool, name=%r'
        raise TypeError(msg % (type(value), value, name))
    scene_data.set_scene_data(name, value)
    return


def get_state_str(name, default_value):
    """
    Get State string from the scene settings.

    :param name: Name of the state string variable.
    :type name: str

    :param default_value: Fallback value, if 'name' cannot be found.
    :type default_value: str

    :return: The queried value, or 'default_value'.
    :rtype: str
    """
    value = scene_data.get_scene_data(name)
    if value is None:
        value = default_value
    return value


def set_state_str(name, value):
    """
    Get a string stored in the scene settings.

    :param name: Name of the state string variable.
    :type name: str

    :param value: Value to set.
    :type value: str
    """
    if isinstance(value, pycompat.TEXT_TYPE) is False:
        msg = 'Value cannot be %r; %r is not a string, name=%r'
        raise TypeError(msg % (type(value), value, name))
    scene_data.set_scene_data(name, value)
    return


def get_pre_solve_force_eval_state():
    return get_state_bool(
        const.SCENE_DATA_PRE_SOLVE_FORCE_EVAL,
        const.SCENE_DATA_PRE_SOLVE_FORCE_EVAL_DEFAULT,
    )


def set_pre_solve_force_eval_state(value):
    return set_state_bool(const.SCENE_DATA_PRE_SOLVE_FORCE_EVAL, value)


def get_refresh_viewport_state():
    return get_state_bool(
        const.SCENE_DATA_REFRESH_VIEWPORT, const.SCENE_DATA_REFRESH_VIEWPORT_DEFAULT
    )


def set_refresh_viewport_state(value):
    return set_state_bool(const.SCENE_DATA_REFRESH_VIEWPORT, value)


def get_force_dg_update_state():
    return get_state_bool(
        const.SCENE_DATA_FORCE_DG_UPDATE, const.SCENE_DATA_FORCE_DG_UPDATE_DEFAULT
    )


def set_force_dg_update_state(value):
    return set_state_bool(const.SCENE_DATA_FORCE_DG_UPDATE, value)


def get_isolate_object_while_solving_state():
    return get_state_bool(
        const.SCENE_DATA_ISOLATE_OBJECT_WHILE_SOLVING,
        const.SCENE_DATA_ISOLATE_OBJECT_WHILE_SOLVING_DEFAULT,
    )


def set_isolate_object_while_solving_state(value):
    return set_state_bool(const.SCENE_DATA_ISOLATE_OBJECT_WHILE_SOLVING, value)


def get_display_image_plane_while_solving_state():
    return get_state_bool(
        const.SCENE_DATA_DISPLAY_IMAGE_PLANE_WHILE_SOLVING,
        const.SCENE_DATA_DISPLAY_IMAGE_PLANE_WHILE_SOLVING_DEFAULT,
    )


def set_display_image_plane_while_solving_state(value):
    return set_state_bool(const.SCENE_DATA_DISPLAY_IMAGE_PLANE_WHILE_SOLVING, value)


def get_display_meshes_while_solving_state():
    return get_state_bool(
        const.SCENE_DATA_DISPLAY_MESHES_WHILE_SOLVING,
        const.SCENE_DATA_DISPLAY_MESHES_WHILE_SOLVING_DEFAULT,
    )


def set_display_meshes_while_solving_state(value):
    return set_state_bool(const.SCENE_DATA_DISPLAY_MESHES_WHILE_SOLVING, value)


def get_display_object_frame_deviation_state():
    return get_state_bool(
        const.SCENE_DATA_DISPLAY_OBJECT_FRAME_DEVIATION,
        const.SCENE_DATA_DISPLAY_OBJECT_FRAME_DEVIATION_DEFAULT,
    )


def set_display_object_frame_deviation_state(value):
    return set_state_bool(const.SCENE_DATA_DISPLAY_OBJECT_FRAME_DEVIATION, value)


def get_display_object_average_deviation_state():
    return get_state_bool(
        const.SCENE_DATA_DISPLAY_OBJECT_AVERAGE_DEVIATION,
        const.SCENE_DATA_DISPLAY_OBJECT_AVERAGE_DEVIATION_DEFAULT,
    )


def set_display_object_average_deviation_state(value):
    return set_state_bool(const.SCENE_DATA_DISPLAY_OBJECT_AVERAGE_DEVIATION, value)


def get_display_object_maximum_deviation_state():
    return get_state_bool(
        const.SCENE_DATA_DISPLAY_OBJECT_MAXIMUM_DEVIATION,
        const.SCENE_DATA_DISPLAY_OBJECT_MAXIMUM_DEVIATION_DEFAULT,
    )


def set_display_object_maximum_deviation_state(value):
    return set_state_bool(const.SCENE_DATA_DISPLAY_OBJECT_MAXIMUM_DEVIATION, value)


def get_display_object_weight_state():
    return get_state_bool(
        const.SCENE_DATA_DISPLAY_OBJECT_WEIGHT,
        const.SCENE_DATA_DISPLAY_OBJECT_WEIGHT_DEFAULT,
    )


def set_display_object_weight_state(value):
    return set_state_bool(const.SCENE_DATA_DISPLAY_OBJECT_WEIGHT, value)


def get_display_attribute_state_state():
    return get_state_bool(
        const.SCENE_DATA_DISPLAY_ATTRIBUTE_STATE,
        const.SCENE_DATA_DISPLAY_ATTRIBUTE_STATE_DEFAULT,
    )


def set_display_attribute_state_state(value):
    return set_state_bool(const.SCENE_DATA_DISPLAY_ATTRIBUTE_STATE, value)


def get_display_attribute_min_max_state():
    return get_state_bool(
        const.SCENE_DATA_DISPLAY_ATTRIBUTE_MIN_MAX,
        const.SCENE_DATA_DISPLAY_ATTRIBUTE_MIN_MAX_DEFAULT,
    )


def set_display_attribute_min_max_state(value):
    return set_state_bool(const.SCENE_DATA_DISPLAY_ATTRIBUTE_MIN_MAX, value)


def get_display_attribute_stiffness_state():
    return get_state_bool(
        const.SCENE_DATA_DISPLAY_ATTRIBUTE_STIFFNESS,
        const.SCENE_DATA_DISPLAY_ATTRIBUTE_STIFFNESS_DEFAULT,
    )


def set_display_attribute_stiffness_state(value):
    return set_state_bool(const.SCENE_DATA_DISPLAY_ATTRIBUTE_STIFFNESS, value)


def get_display_attribute_smoothness_state():
    return get_state_bool(
        const.SCENE_DATA_DISPLAY_ATTRIBUTE_SMOOTHNESS,
        const.SCENE_DATA_DISPLAY_ATTRIBUTE_SMOOTHNESS_DEFAULT,
    )


def set_display_attribute_smoothness_state(value):
    return set_state_bool(const.SCENE_DATA_DISPLAY_ATTRIBUTE_SMOOTHNESS, value)


def get_log_level():
    return get_state_str(const.SCENE_DATA_LOG_LEVEL, const.SCENE_DATA_LOG_LEVEL_DEFAULT)


def set_log_level(value):
    return set_state_str(const.SCENE_DATA_LOG_LEVEL, value)


def get_solver_is_running_state():
    value = mmapi.is_solver_running()
    return value


def set_solver_is_running_state(value):
    if isinstance(value, bool) is False:
        msg = 'value cannot be %r; %r is not bool'
        raise TypeError(msg % (type(value), value))
    mmapi.set_solver_running(value)
    return


def get_solver_user_interrupt_state():
    value = mmapi.get_user_interrupt()
    return value


def set_solver_user_interrupt_state(value):
    if isinstance(value, bool) is False:
        msg = 'value cannot be %r; %r is not bool'
        raise TypeError(msg % (type(value), value))
    mmapi.set_user_interrupt(value)
    return
