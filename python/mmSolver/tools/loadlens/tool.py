# Copyright (C) 2022 David Cattermole.
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
The Load Lens tool - user facing.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.loadlens.lib as lib


LOG = mmSolver.logger.get_logger()


def _get_start_directory():
    workspace_path = maya.cmds.workspace(query=True, fullName=True)
    if workspace_path is None:
        return os.getcwd()
    workspace_path = os.path.abspath(workspace_path)

    file_rules = maya.cmds.workspace(query=True, fileRule=True)
    if file_rules is None:
        return os.getcwd()
    file_rule_names = file_rules[0::2]
    file_rule_values = file_rules[1::2]

    file_rule = 'scene'
    file_rule_index = file_rule_names.index(file_rule)
    dir_name = file_rule_values[file_rule_index]

    path = os.path.join(workspace_path, dir_name)
    return path


def prompt_user_for_lens_file(start_dir=None):
    file_path = None
    if start_dir is None:
        start_dir = _get_start_directory()
    multiple_filters = 'Nuke Script (*.nk);;' 'All Files (*.*)'
    results = (
        maya.cmds.fileDialog2(
            caption='Select Lens File',
            okCaption='Open',
            fileMode=1,  # 1 = A single existing file.
            setProjectBtnEnabled=True,
            fileFilter=multiple_filters,
            startingDirectory=start_dir,
        )
        or []
    )
    if len(results) == 0:
        # User cancelled.
        return file_path

    file_path = results[0]
    return file_path


def main():
    mmapi.load_plugin()

    # Get selected lens(es).
    sel = maya.cmds.ls(selection=True, long=True) or []
    node_filtered = mmapi.filter_nodes_into_categories(sel)
    lens_nodes = node_filtered[mmapi.OBJECT_TYPE_LENS]
    lenses = [mmapi.Lens(node=lens_node) for lens_node in lens_nodes]

    if len(lenses) == 0:
        msg = 'Could not find lens node, select a lens node.'
        LOG.error(msg)
        return

    lens_file_path = prompt_user_for_lens_file(start_dir=None)
    if lens_file_path is None:
        msg = 'User cancelled loading lens file.'
        LOG.info(msg)
        return

    lens_object = lib.parse_file(lens_file_path)
    if lens_object is None:
        msg = 'Lens file is not valid: %r'
        LOG.error(msg, lens_file_path)
        return

    for lens in lenses:
        success = lib.apply_to_lens(lens_object, lens)
        if success is True:
            msg = 'Lens file applied to Lens: %r'
            LOG.info(msg, lens)

    lens_nodes = [lens.get_node() for lens in lenses]
    lens_nodes = [lens_node for lens_node in lens_nodes if lens_node]
    if len(lens_nodes) == 0:
        # Something weird has happened and we revert to the original
        # selection.
        maya.cmds.select(sel, replace=True)
    else:
        maya.cmds.select(lens_nodes, replace=True)
    return
