# Copyright (C) 2023 David Cattermole.
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
Tool to add custom MM Renderer attributes to displayLayer nodes.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.logger
import mmSolver.tools.userpreferences.lib as userpref_lib
import mmSolver.tools.userpreferences.constant as userpref_const
import mmSolver.tools.mmrendererlayers.lib as lib

LOG = mmSolver.logger.get_logger()


def main():
    """
    Add MM Renderer attributes to the selected displayLayer nodes.
    """
    nodes = maya.cmds.ls(selection=True, type='displayLayer') or []
    if len(nodes) == 0:
        LOG.warn('MM Renderer: No Display Layers are selected.')
        return
    lib.add_attrs_to_layers(nodes)


def setup_all_layers():
    """
    Add MM Renderer attributes to the selected Display Layers
    """
    nodes = maya.cmds.ls(type='displayLayer') or []
    if len(nodes) == 0:
        msg = 'MM Renderer: No Display Layers in the scene to add attributes.'
        LOG.info(msg)
        return

    config = userpref_lib.get_config()
    bg_node_types_string = userpref_lib.get_value(
        config, userpref_const.MM_RENDERER_BACKGROUND_NODE_TYPES_KEY
    )
    bg_node_types = bg_node_types_string.split(' ') or []
    bg_node_types = [x.strip() for x in bg_node_types]
    bg_node_types = set([x for x in bg_node_types if len(x) > 0])

    return lib.add_attrs_to_layers(nodes, bg_node_types)
