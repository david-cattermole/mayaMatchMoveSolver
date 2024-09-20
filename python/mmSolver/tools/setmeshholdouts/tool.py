# Copyright (C) 2024 Patcha Saheb Binginapalli.
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
Tools to set hold-out attributes on meshes.

These tools can enable or disable the hold-out attribute on mesh nodes.
"""

import maya.cmds

import mmSolver.logger

import mmSolver.utils.node as node_utils

LOG = mmSolver.logger.get_logger()

NO_SCENE_MESHES_WARNING_MESSAGE = "No mesh nodes found in the Maya scene."
SELECTED_MESHES_WARNING_MESSAGE = (
    "Please select mesh objects, no mesh nodes were found from the selection."
)


def _set_holdout(mesh_nodes, value):
    assert isinstance(value, bool)
    attr_name = 'holdOut'
    for mesh_node in mesh_nodes:
        if node_utils.attribute_exists(attr_name, mesh_node):
            node_attr = "{}.holdOut".format(mesh_node)
            node_utils.set_attr(node_attr, value, relock=True)
    return


def enable_all_meshes():
    all_meshes = maya.cmds.ls(dag=True, type="mesh") or []
    if len(all_meshes) == 0:
        LOG.warn(NO_SCENE_MESHES_WARNING_MESSAGE)
        return
    _set_holdout(all_meshes, True)


def disable_all_meshes():
    all_meshes = maya.cmds.ls(dag=True, type="mesh") or []
    if len(all_meshes) == 0:
        LOG.warn(NO_SCENE_MESHES_WARNING_MESSAGE)
        return
    _set_holdout(all_meshes, False)


def enable_selected_meshes():
    selected_meshes = maya.cmds.ls(selection=True, dag=True, type="mesh") or []
    if len(selected_meshes) == 0:
        LOG.warn(SELECTED_MESHES_WARNING_MESSAGE)
        return
    _set_holdout(selected_meshes, True)


def disable_selected_meshes():
    selected_meshes = maya.cmds.ls(selection=True, dag=True, type="mesh") or []
    if len(selected_meshes) == 0:
        LOG.warn(SELECTED_MESHES_WARNING_MESSAGE)
        return
    _set_holdout(selected_meshes, False)
