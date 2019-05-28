"""
This file holds all the helpful functions for markerbundlerename
"""

import mmSolver.logger
import maya.cmds
import mmSolver.api as mmapi


LOG = mmSolver.logger.get_logger()


def prompt_for_new_node_name(title, message, text):
    """
    Ask the user for a new node name.

    :param title: Dialog box window title.
    :type title: str

    :param message: Read-only text to show the user, for making a
                    decision.
    :type message: str

    :param text: The initial text to prompt the user as a starting
                 point.
    :type text: str

    :return: New node name, or None if user cancelled.
    :rtype: str or None
    """
    name = None
    result = maya.cmds.promptDialog(
        title=title,
        message=message,
        text=text,
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel',
    )
    if result == 'OK':
        name = maya.cmds.promptDialog(query=True, text=True)
    return name


def rename_markers_and_bundles(mkr_nodes, bnd_nodes,
                               mkr_name, bnd_name,
                               number_format,
                               mkr_suffix, bnd_suffix):
    """
    Rename the given marker and bundle nodes.

    :param mkr_nodes: Marker nodes to rename.
    :type mkr_nodes: [str, ..]

    :param bnd_nodes: Bundle nodes to rename.
    :type bnd_nodes: [str, ..]

    :param mkr_name: Rename the markers to this name.
    :type mkr_name: str

    :param bnd_name: Rename the bundle to this name.
    :type bnd_name: str

    :param number_format: The name format string for numbering.
    :type number_format: str

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
    for i, bnd_node in enumerate(bnd_nodes):
        num_str = number_format % (i + 1)
        bnd = mmapi.Bundle(node=bnd_node)

        new_bnd_name = mmapi.get_bundle_name(
            num_str,
            prefix=bnd_name,
            suffix=bnd_suffix
        )
        bnd_node = bnd.get_node()
        maya.cmds.rename(bnd_node, new_bnd_name)
        renamed_nodes.append(bnd.get_node())

        new_mkr_name = new_bnd_name.replace(bnd_name, mkr_name)
        new_mkr_name = new_mkr_name.replace(bnd_suffix, mkr_suffix)
        mkr_list = bnd.get_marker_list()
        for mkr in mkr_list:
            mkr_node = mkr.get_node()
            maya.cmds.rename(mkr_node, new_mkr_name)
            renamed_nodes.append(mkr.get_node())
    return renamed_nodes
