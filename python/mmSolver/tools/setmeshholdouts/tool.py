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

import maya.cmds as cmds

import mmSolver.logger

LOG = mmSolver.logger.get_logger()


def set_holdout(mesh_list, enable=True):
    for mesh in mesh_list:
        cmds.setAttr(mesh + ".holdOut", enable)


def enable_all_meshes():
    all_meshes = cmds.ls(dag=True, type="mesh") or []
    if not all_meshes:
        LOG.warn("Mesh not found.")
        return
    set_holdout(all_meshes, True)


def disable_all_meshes():
    all_meshes = cmds.ls(dag=True, type="mesh") or []
    if not all_meshes:
        LOG.warn("Mesh not found.")
        return
    set_holdout(all_meshes, False)


def enable_selected_meshes():
    selected_meshes = cmds.ls(selection=True, dag=True, type="mesh") or []
    if not selected_meshes:
        LOG.warn("Mesh selection not found.")
        return
    set_holdout(selected_meshes, True)


def disable_selected_meshes():
    selected_meshes = cmds.ls(selection=True, dag=True, type="mesh") or []
    if not selected_meshes:
        LOG.warn("Mesh selection not found.")
        return
    set_holdout(selected_meshes, False)
