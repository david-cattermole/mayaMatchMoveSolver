# Copyright (C) 2019 Anil Reddy, David Cattermole
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
This file holds all the helpful functions for 'marker bundle rename with metadata'.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.node as node_utils


LOG = mmSolver.logger.get_logger()


def _get_marker_internal_name(mkr):
    """
    Get the Marker object's internal ID (the 'Persistent ID' given
    from 3DE).

    :rtype: str or None
    """
    assert isinstance(mkr, mmapi.Marker)
    node = mkr.get_node()
    value = None
    attr_name = 'markerName'
    if node_utils.attribute_exists(attr_name, node):
        plug = '{0}.{1}'.format(node, attr_name)
        value = maya.cmds.getAttr(plug)
    return value


def rename_markers_and_bundles_with_metadata(mkr_nodes, bnd_nodes,
                                             mkr_prefix, bnd_prefix,
                                             mkr_suffix, bnd_suffix):
    """
    Rename the given marker and bundle nodes.

    :param mkr_nodes: Marker nodes to rename.
    :type mkr_nodes: [str, ..]

    :param bnd_nodes: Bundle nodes to rename.
    :type bnd_nodes: [str, ..]

    :param mkr_prefix: Rename the markers to this name.
    :type mkr_prefix: str

    :param bnd_prefix: Rename the bundle to this name.
    :type bnd_prefix: str

    :param mkr_suffix: Set the marker suffix name.
    :type mkr_suffix: str

    :param bnd_suffix: Set the bundle suffix name.
    :type bnd_suffix: str

    :returns: Nodes that have been renamed.
    :rtype: [str, ..]
    """
    # Convert markers to bundles.
    mkr_nodes = list(mkr_nodes)
    bnd_nodes = list(bnd_nodes)
    for node in mkr_nodes:
        mkr = mmapi.Marker(node=node)
        bnd = mkr.get_bundle()
        if bnd is None:
            continue
        bnd_node = bnd.get_node()
        if not bnd_node:
            continue
        if bnd_node not in bnd_nodes:
            bnd_nodes.append(bnd_node)

    # Rename the bundles.
    renamed_nodes = []
    for bnd_node in bnd_nodes:
        bnd = mmapi.Bundle(node=bnd_node)

        base_name = None
        mkr_list = bnd.get_marker_list()
        for mkr in mkr_list:
            mkr_name = _get_marker_internal_name(mkr)
            if mkr_name is None or len(mkr_name) == 0:
                continue
            base_name = mkr_name
        if base_name is None:
            LOG.warn('Cannot rename Marker/Bundle with metadata: '
                     'bnd=%r mkr_list=%r', bnd, mkr_list)
            continue

        new_bnd_name = '{prefix}_{base}{suffix}'
        new_bnd_name = new_bnd_name.format(prefix=bnd_prefix,
                                           base=base_name,
                                           suffix=bnd_suffix)
        bnd_node = bnd.get_node()
        maya.cmds.rename(bnd_node, new_bnd_name)
        renamed_nodes.append(bnd.get_node())

        new_mkr_name = new_bnd_name.replace(bnd_prefix, mkr_prefix)
        new_mkr_name = new_mkr_name.replace(bnd_suffix, mkr_suffix)
        mkr_list = bnd.get_marker_list()
        for mkr in mkr_list:
            mkr_node = mkr.get_node()
            maya.cmds.rename(mkr_node, new_mkr_name)
            renamed_nodes.append(mkr.get_node())
    return renamed_nodes
