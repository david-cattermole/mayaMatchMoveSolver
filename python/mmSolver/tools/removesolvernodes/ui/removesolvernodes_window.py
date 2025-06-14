# Copyright (C) 2020, Kazuma Tonegawa
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
Window for the Remove Solver Nodes tool.

Usage::

   import mmSolver.tools.removesolvernodes.ui.removesolvernodes_window as removesolvernodes_window
   removesolvernodes_window.main()

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import uuid

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import maya.cmds

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.commonmenus as commonmenus
import mmSolver.ui.helputils as helputils
import mmSolver.utils.tools as tools_utils
import mmSolver.tools.removesolvernodes.constants as const
import mmSolver.tools.removesolvernodes.lib as lib
import mmSolver.tools.removesolvernodes.ui.removesolvernodes_layout as removesolvernodes_layout

LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


def _open_help():
    src = helputils.get_help_source()
    page = 'tools_generaltools.html#remove-solver-nodes'
    helputils.open_help_in_browser(page=page, help_source=src)
    return


def _generate_details_text(
    marker_nodes=None,
    bundle_nodes=None,
    mkr_group_nodes=None,
    line_nodes=None,
    lens_nodes=None,
    imageplane_nodes=None,
    collection_nodes=None,
    display_nodes=None,
    config_nodes=None,
    other_nodes=None,
):
    details = 'Nodes to delete...\n'

    def _format_node_list(nodes):
        text = ''
        for node in sorted(nodes):
            node = maya.cmds.ls(node)[0]
            text += '- ' + str(node) + '\n'
        return text

    if len(marker_nodes) > 0:
        details += '\nMarkers:\n'
        details += _format_node_list(marker_nodes)

    if len(bundle_nodes) > 0:
        details += '\nBundles:\n'
        details += _format_node_list(bundle_nodes)

    if len(mkr_group_nodes) > 0:
        details += '\nMarker Groups:\n'
        details += _format_node_list(mkr_group_nodes)

    if len(line_nodes) > 0:
        details += '\nLines:\n'
        details += _format_node_list(line_nodes)

    if len(lens_nodes) > 0:
        details += '\nLenses:\n'
        details += _format_node_list(lens_nodes)

    if len(imageplane_nodes) > 0:
        details += '\nImagePlanes:\n'
        details += _format_node_list(imageplane_nodes)

    if len(collection_nodes) > 0:
        details += '\nCollections:\n'
        details += _format_node_list(collection_nodes)

    if len(display_nodes) > 0:
        details += '\nDisplay Nodes:\n'
        details += _format_node_list(display_nodes)

    if len(config_nodes) > 0:
        details += '\nConfiguration Nodes:\n'
        details += _format_node_list(config_nodes)

    if len(other_nodes) > 0:
        details += '\nOther Nodes:\n'
        details += _format_node_list(other_nodes)
    return details


def _generate_message_text(
    nodes_to_delete=None,
    unknown_node_found=None,
    marker_nodes=None,
    bundle_nodes=None,
    mkr_group_nodes=None,
    line_nodes=None,
    lens_nodes=None,
    imageplane_nodes=None,
    collection_nodes=None,
    display_nodes=None,
    config_nodes=None,
    other_nodes=None,
):
    marker_count = len(marker_nodes)
    bundle_count = len(bundle_nodes)
    mkr_group_count = len(mkr_group_nodes)
    line_count = len(line_nodes)
    lens_count = len(lens_nodes)
    imageplane_count = len(imageplane_nodes)
    collection_count = len(collection_nodes)
    display_count = len(display_nodes)
    config_count = len(config_nodes)
    other_count = len(other_nodes)

    msg = (
        'Found {count} nodes to delete.\n\n'
        'Nodes to delete:\n'
        '-> Markers: {marker_count}\n'
        '-> Bundles: {bundle_count}\n'
        '-> Marker Groups: {mkr_group_count}\n'
        '-> Lines: {line_count}\n'
        '-> Lenses: {lens_count}\n'
        '-> Image Planes: {imageplane_count}\n'
        '-> Collections: {collection_count}\n'
        '-> Display Nodes: {display_count}\n'
        '-> Configuration Nodes: {config_count}\n'
        '-> Other Nodes: {other_count}\n'
        '\n'
    ).format(
        count=len(nodes_to_delete),
        marker_count=marker_count,
        bundle_count=bundle_count,
        mkr_group_count=mkr_group_count,
        line_count=line_count,
        lens_count=lens_count,
        imageplane_count=imageplane_count,
        collection_count=collection_count,
        display_count=display_count,
        config_count=config_count,
        other_count=other_count,
    )
    if unknown_node_found:
        msg += (
            'Note: Non-bundle nodes found parented under one or more bundle\n'
            'nodes. It is suggested that you unparent and bake nodes \n'
            'you want to keep.\n\n'
        )
    return msg


def _run_tool(window_parent, save_scene, what_to_delete_dict):
    assert isinstance(save_scene, bool)
    assert isinstance(what_to_delete_dict, dict)
    found_nodes_map, unknown_node_found = lib.filter_nodes(what_to_delete_dict)

    marker_nodes = found_nodes_map.get('markers', [])
    bundle_nodes = found_nodes_map.get('bundles', [])
    mkr_group_nodes = found_nodes_map.get('marker_groups', [])
    lens_nodes = found_nodes_map.get('lenses', [])
    line_nodes = found_nodes_map.get('lines', [])
    imageplane_nodes = found_nodes_map.get('imageplanes', [])
    collection_nodes = found_nodes_map.get('collections', [])
    display_nodes = found_nodes_map.get('display_nodes', [])
    config_nodes = found_nodes_map.get('configuration_nodes', [])
    other_nodes = found_nodes_map.get('other_nodes', [])

    nodes_to_delete = []
    for key in found_nodes_map:
        nodes_to_delete += found_nodes_map[key]
    # Remove non-unique nodes.
    nodes_to_delete = list(sorted(set(nodes_to_delete)))

    title = const.WINDOW_TITLE
    if len(nodes_to_delete) == 0:
        msg = 'No nodes found, ' 'please choose different options in the window.\n'
        QtWidgets.QMessageBox.warning(window_parent, title, msg)
        return False

    details = _generate_details_text(
        marker_nodes=marker_nodes,
        bundle_nodes=bundle_nodes,
        mkr_group_nodes=mkr_group_nodes,
        line_nodes=line_nodes,
        lens_nodes=lens_nodes,
        imageplane_nodes=imageplane_nodes,
        collection_nodes=collection_nodes,
        display_nodes=display_nodes,
        config_nodes=config_nodes,
        other_nodes=other_nodes,
    )

    msg = _generate_message_text(
        unknown_node_found=unknown_node_found,
        nodes_to_delete=nodes_to_delete,
        marker_nodes=marker_nodes,
        bundle_nodes=bundle_nodes,
        mkr_group_nodes=mkr_group_nodes,
        line_nodes=line_nodes,
        lens_nodes=lens_nodes,
        imageplane_nodes=imageplane_nodes,
        collection_nodes=collection_nodes,
        display_nodes=display_nodes,
        config_nodes=config_nodes,
        other_nodes=other_nodes,
    )

    inform_text = 'Are you sure you want to delete?'
    dialog = QtWidgets.QMessageBox(
        window_parent,
    )
    dialog.setWindowTitle(title)
    dialog.setIcon(QtWidgets.QMessageBox.Question)
    dialog.setText(msg)
    dialog.setInformativeText(inform_text)
    dialog.setDetailedText(details)
    dialog.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    # No is default button because we don't want users to accidentally
    # delete nodes - users must make a choice.
    dialog.setDefaultButton(QtWidgets.QMessageBox.No)

    clicked_button = dialog.exec_()
    if clicked_button != QtWidgets.QMessageBox.Yes:
        # The user may close the UI without clicking a yes/no button.
        return False

    if save_scene is True:
        maya.cmds.file(save=True)

    undo_id = 'removesolvernodes: '
    undo_id += str(datetime.datetime.isoformat(datetime.datetime.now()))
    undo_id += ' '
    undo_id += str(uuid.uuid4())
    with tools_utils.tool_context(
        use_undo_chunk=True, undo_chunk_name=undo_id, restore_current_frame=True
    ):
        lib.delete_nodes(nodes_to_delete)
    return True


class RemoveSolverNodesWindow(BaseWindow):
    name = 'RemoveSolverNodesWindow'

    def __init__(self, parent=None, name=None):
        super(RemoveSolverNodesWindow, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(removesolvernodes_layout.RemoveSolverNodesLayout)

        self.setWindowTitle(const.WINDOW_TITLE)
        self.setWindowType(qtpyutils.WINDOW_TYPE_DIALOG)

        # Standard Buttons
        self.baseHideStandardButtons()
        self.applyBtn.show()
        self.closeBtn.show()
        self.applyBtn.setText('Clean...')
        self.applyBtn.clicked.connect(self.clean)

        # Hide irrelevant stuff
        self.baseHideProgressBar()

        self.add_menus(self.menubar)
        self.menubar.show()

        self.reset_options()

    def add_menus(self, menubar):
        edit_menu = QtWidgets.QMenu('Edit', menubar)
        commonmenus.create_edit_menu_items(
            edit_menu, reset_settings_func=self.reset_options
        )
        menubar.addMenu(edit_menu)

        help_menu = QtWidgets.QMenu('Help', menubar)
        commonmenus.create_help_menu_items(help_menu, tool_help_func=_open_help)
        menubar.addMenu(help_menu)

    def reset_options(self):
        form = self.getSubForm()
        form.reset_options()
        return

    def clean(self):
        save_scene = self.subForm.saveSceneBefore_checkBox.isChecked()
        what_to_delete_dict = {
            'markers': self.subForm.markers_checkBox.isChecked(),
            'bundles': self.subForm.bundles_checkBox.isChecked(),
            'marker_groups': self.subForm.markerGroup_checkBox.isChecked(),
            'lenses': self.subForm.lenses_checkBox.isChecked(),
            'lines': self.subForm.lines_checkBox.isChecked(),
            'imageplanes': self.subForm.imagePlanes_checkBox.isChecked(),
            'collections': self.subForm.collections_checkBox.isChecked(),
            'display_nodes': self.subForm.displayNodes_checkBox.isChecked(),
            'configuration_nodes': self.subForm.configuration_checkBox.isChecked(),
            'other_nodes': self.subForm.otherNodes_checkBox.isChecked(),
        }
        ok = _run_tool(self, save_scene, what_to_delete_dict)
        if ok is True:
            # If the run was successful, we save the preferences.
            form = self.getSubForm()
            form.save_options()
        return


def main(show=True, auto_raise=True, delete=False):
    """
    Open the Remove Solver Nodes UI.

    :param show: Show the UI.
    :type show: bool

    :param auto_raise: If the UI is open, raise it to the front?
    :type auto_raise: bool

    :param delete: Delete the existing UI and rebuild it? Helpful when
                   developing the UI in Maya script editor.
    :type delete: bool

    :returns: A new solver window, or None if the window cannot be
              opened.
    :rtype: RemoveSolverNodesWindow or None.
    """
    win = RemoveSolverNodesWindow.open_window(
        show=show, auto_raise=auto_raise, delete=delete
    )
    return win
