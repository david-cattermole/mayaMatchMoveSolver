# Copyright (C) 2019 David Cattermole.
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
Position Bundle under the Marker, in screen-space.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.reprojectbundle.lib as lib


LOG = mmSolver.logger.get_logger()


def main():
    """
    Move the Bundle to the Marker, on the current-frame.

    Perform a reprojection of the selected bundle (or bundle connected
    to the selected marker), at the current frame.

    Usage:

    1) Select markers or connected bundles (or both).

    2) Run tool.

    3) Bundle is triangulated in TX, TY and TZ.

    .. note::

        If a Bundle has locked attributes, they will be unlocked and
        then relocked.

    """
    # If a bundle has locked attributes, they will be unlocked and
    # then relocked.
    relock = True
    
    # Get Markers and Bundles
    sel = maya.cmds.ls(sl=True) or []
    filter_nodes = mmapi.filter_nodes_into_categories(sel)
    mkr_nodes = filter_nodes.get('marker', [])
    bnd_nodes = filter_nodes.get('bundle', [])
    if len(mkr_nodes) == 0 and len(bnd_nodes) == 0:
        msg = 'Please select at least one marker / bundle!'
        LOG.warning(msg)
        return

    # Get Markers from Bundles
    for bnd_node in bnd_nodes:
        bnd = mmapi.Bundle(node=bnd_node)
        bnd_node_full = bnd.get_node()
        bnd_mkr_list = bnd.get_marker_list()
        mkr_count = len(bnd_mkr_list)
        if mkr_count == 0:
            msg = (
                'Cannot find Marker from Bundle, '
                'Bundle doesn\'t have any Markers connected. '
                'bnd=%r mkr_count=%r'
            )
            LOG.warning(msg, bnd_node_full, mkr_count)
            continue
        elif mkr_count > 1:
            msg = (
                'Cannot find Marker from Bundle, '
                'Bundle has more than 1 Marker. '
                'bnd=%r mkr_count=%r'
            )
            LOG.warning(msg, bnd_node_full, mkr_count)
            continue
        assert mkr_count == 1
        mkr = bnd_mkr_list[0]
        mkr_node_full = mkr.get_node()
        mkr_nodes.append(mkr_node_full)

    # Get  list of markers to operate on.
    mkr_list = []
    have_mkr_nodes = []
    attrs = ['translateX', 'translateY', 'translateZ']
    for mkr_node in mkr_nodes:
        mkr = mmapi.Marker(node=mkr_node)
        mkr_node_full = mkr.get_node()
        if mkr_node_full in have_mkr_nodes:
            msg = 'Skipping Marker, already have it; mkr=%r'
            LOG.debug(msg, mkr_node_full)
            continue

        # Get Bundle
        bnd = mkr.get_bundle()
        if bnd is None:
            msg = 'Marker does not have a connected Bundle; mkr=%r'
            LOG.warning(msg, mkr_node_full)
            continue
        bnd_node_full = bnd.get_node()

        # Check we can handle locked attributes.
        locked_num = 0
        for attr in attrs:
            plug = bnd_node_full + '.' + attr
            locked = maya.cmds.getAttr(plug, lock=True)
            locked_num += int(locked)
        if relock is False:
            if locked_num > 0:
                msg = (
                    'Bundle must have unlocked translate attributes: '
                    'bnd=%r'
                )
                LOG.warning(msg, bnd_node_full)
                continue
        elif relock is True:
            # Check the bundle isn't referenced and has locked attrs.
            referenced = maya.cmds.referenceQuery(
                bnd_node_full,
                isNodeReferenced=True
            )
            if referenced is True and locked_num > 0:
                msg = (
                    'Bundle has locked translate attributes and is referenced '
                    '(cannot be unlocked): '
                    'bnd=%r'
                )
                LOG.warning(msg, bnd_node_full)
                continue

        mkr_list.append(mkr)
        have_mkr_nodes.append(mkr_node_full)

    # Do projection
    modified_bnds = lib.reproject_bundle_current_frame(mkr_list, relock=relock)

    # Select all moved bundle nodes.
    modified_bnd_nodes = [bnd.get_node() for bnd in modified_bnds]
    if len(modified_bnd_nodes) > 0:
        maya.cmds.select(modified_bnd_nodes, replace=True)
    else:
        msg = 'No Bundle nodes modified, see Script Editor for details.'
        LOG.warning(msg)
    return
