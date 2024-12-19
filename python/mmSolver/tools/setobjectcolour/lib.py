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
Getting and setting colours for objects.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.utils.node as node_utils
import mmSolver.api as mmapi

LOG = mmSolver.logger.get_logger()


def get_first_node_colour(tfm_nodes):
    rgba = [0.5, 0.5, 0.5, 1.0]
    for tfm_node in tfm_nodes:
        object_type = mmapi.get_object_type(tfm_node)
        if object_type == mmapi.OBJECT_TYPE_MARKER:
            mkr = mmapi.Marker(node=tfm_node)
            rgba = mkr.get_colour_rgba()
            return rgba
        elif object_type == mmapi.OBJECT_TYPE_BUNDLE:
            bnd = mmapi.Bundle(node=tfm_node)
            rgba = bnd.get_colour_rgba()
            return rgba
        elif object_type == mmapi.OBJECT_TYPE_LINE:
            line = mmapi.Line(node=tfm_node)
            rgba = line.get_colour_rgba()
            return rgba
        else:
            node_types = ('surfaceShape', 'locator')
            shp_nodes = (
                maya.cmds.ls(tfm_node, long=True, dag=True, type=node_types) or []
            )
            for shp_node in shp_nodes:
                rgba = node_utils.get_node_draw_override_colour_rgba(shp_node)
                if rgba:
                    return rgba
    return rgba


def reset_nodes_colour(tfm_nodes):
    for tfm_node in tfm_nodes:
        is_ref = node_utils.node_is_referenced(tfm_node)
        if is_ref is True:
            continue

        object_type = mmapi.get_object_type(tfm_node)
        if object_type == mmapi.OBJECT_TYPE_MARKER:
            mkr = mmapi.Marker(node=tfm_node)
            mkr.set_colour_rgba(None)
        elif object_type == mmapi.OBJECT_TYPE_BUNDLE:
            bnd = mmapi.Bundle(node=tfm_node)
            bnd.set_colour_rgba(None)
        elif object_type == mmapi.OBJECT_TYPE_LINE:
            line = mmapi.Line(node=tfm_node)
            line.set_colour_rgba(None)
        else:
            node_types = ('surfaceShape', 'locator', 'camera')
            shp_nodes = (
                maya.cmds.ls(tfm_node, long=True, dag=True, type=node_types) or []
            )
            for shp_node in shp_nodes:
                node_utils.set_node_draw_override_enabled(shp_node, False)
    return


def set_nodes_colour(tfm_nodes, rgba):
    assert len(rgba) >= 4
    for tfm_node in tfm_nodes:
        # TODO: Should this be here? Perhaps we should only fail.
        is_ref = node_utils.node_is_referenced(tfm_node)
        if is_ref is True:
            continue

        object_type = mmapi.get_object_type(tfm_node)
        if object_type == mmapi.OBJECT_TYPE_MARKER:
            mkr = mmapi.Marker(node=tfm_node)
            mkr.set_colour_rgba(rgba)
        elif object_type == mmapi.OBJECT_TYPE_BUNDLE:
            bnd = mmapi.Bundle(node=tfm_node)
            bnd.set_colour_rgba(rgba)
        elif object_type == mmapi.OBJECT_TYPE_LINE:
            line = mmapi.Line(node=tfm_node)
            line.set_colour_rgba(rgba)
        else:
            node_types = ('surfaceShape', 'locator', 'camera')
            shp_nodes = (
                maya.cmds.ls(tfm_node, long=True, dag=True, type=node_types) or []
            )
            for shp_node in shp_nodes:
                node_utils.set_node_draw_override_enabled(shp_node, True)
                node_utils.set_node_draw_override_colour_rgba(shp_node, rgba)
    return
