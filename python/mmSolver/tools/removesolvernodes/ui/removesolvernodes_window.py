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

import Qt.QtCore as QtCore
import Qt.QtWidgets as QtWidgets

import maya.cmds

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.commonmenus as commonmenus
import mmSolver.ui.helputils as helputils
import mmSolver.utils.tools as tools_utils
import mmSolver.tools.removesolvernodes.constants as const
import mmSolver.tools.removesolvernodes.tool as tool
import mmSolver.tools.removesolvernodes.ui.removesolvernodes_layout as removesolvernodes_layout

LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


def _open_help():
    src = helputils.get_help_source()
    page = 'tools_generaltools.html#remove-solver-nodes'
    helputils.open_help_in_browser(page=page, help_source=src)
    return


def _generate_details_text(marker_nodes=None,
                           bundle_nodes=None,
                           mkr_group_nodes=None,
                           collection_nodes=None,
                           other_nodes=None):
    details = 'Nodes to delete...\n'

    details += '\nMarkers:\n'
    for node in sorted(marker_nodes):
        node = maya.cmds.ls(node)[0]
        details += '- ' + str(node) + '\n'

    details += '\nBundles:\n'
    for node in sorted(bundle_nodes):
        node = maya.cmds.ls(node)[0]
        details += '- ' + str(node) + '\n'

    details += '\nMarker Groups:\n'
    for node in sorted(mkr_group_nodes):
        node = maya.cmds.ls(node)[0]
        details += '- ' + str(node) + '\n'

    details += '\nCollections:\n'
    for node in sorted(collection_nodes):
        node = maya.cmds.ls(node)[0]
        details += '- ' + str(node) + '\n'

    details += '\nOther Nodes:\n'
    for node in sorted(other_nodes):
        node = maya.cmds.ls(node)[0]
        details += '- ' + str(node) + '\n'
    return details


def _generate_message_text(nodes_to_delete=None,
                           unknown_node_found=None,
                           marker_nodes=None,
                           bundle_nodes=None,
                           mkr_group_nodes=None,
                           collection_nodes=None,
                           other_nodes=None):
    marker_count = len(marker_nodes)
    bundle_count = len(bundle_nodes)
    mkr_group_count = len(mkr_group_nodes)
    collection_count = len(collection_nodes)
    other_count = len(other_nodes)

    msg = (
        'Found {count} nodes to delete.\n\n'
        'Nodes to delete:\n'
        '-> Markers: {marker_count}\n'
        '-> Bundles: {bundle_count}\n'
        '-> Marker Groups: {mkr_group_count}\n'
        '-> Collections: {collection_count}\n'
        '-> Other Nodes: {other_count}\n'
        '\n'
    ).format(
        count=len(nodes_to_delete),
        marker_count=marker_count,
        bundle_count=bundle_count,
        mkr_group_count=mkr_group_count,
        collection_count=collection_count,
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
    found_nodes_map, unknown_node_found = tool.filter_nodes(
        what_to_delete_dict
    )

    marker_nodes = found_nodes_map.get('markers', [])
    bundle_nodes = found_nodes_map.get('bundles', [])
    mkr_group_nodes = found_nodes_map.get('marker_groups', [])
    collection_nodes = found_nodes_map.get('collections', [])
    other_nodes = found_nodes_map.get('other_nodes', [])

    nodes_to_delete = []
    for key in found_nodes_map:
        nodes_to_delete += found_nodes_map[key]
    # Remove non-unique nodes.
    nodes_to_delete = list(sorted(set(nodes_to_delete)))

    title = const.WINDOW_TITLE
    if len(nodes_to_delete) == 0:
        msg = ('No nodes found, '
               'please choose different options in the window.\n')
        QtWidgets.QMessageBox.warning(window_parent, title, msg)
        return False

    details = _generate_details_text(
        marker_nodes=marker_nodes,
        bundle_nodes=bundle_nodes,
        mkr_group_nodes=mkr_group_nodes,
        collection_nodes=collection_nodes,
        other_nodes=other_nodes)

    msg = _generate_message_text(
        unknown_node_found=unknown_node_found,
        nodes_to_delete=nodes_to_delete,
        marker_nodes=marker_nodes,
        bundle_nodes=bundle_nodes,
        mkr_group_nodes=mkr_group_nodes,
        collection_nodes=collection_nodes,
        other_nodes=other_nodes)

    inform_text = 'Are you sure you want to delete?'
    dialog = QtWidgets.QMessageBox(window_parent, )
    dialog.setWindowTitle(title)
    dialog.setIcon(QtWidgets.QMessageBox.Question)
    dialog.setText(msg);
    dialog.setInformativeText(inform_text);
    dialog.setDetailedText(details);
    clicked_button = dialog.exec_()
    if clicked_button == QtWidgets.QMessageBox.No:
        return False

    if save_scene is True:
        maya.cmds.file(save=True)

    undo_id = 'removesolvernodes: '
    undo_id += str(datetime.datetime.isoformat(datetime.datetime.now()))
    undo_id += ' '
    undo_id += str(uuid.uuid4())
    with tools_utils.tool_context(use_undo_chunk=True,
                                  undo_chunk_name=undo_id,
                                  restore_current_frame=True):
        tool.delete_nodes(nodes_to_delete)
    return True


class RemoveSolverNodesWindow(BaseWindow):
    name = 'RemoveSolverNodesWindow'

    def __init__(self, parent=None, name=None):
        super(RemoveSolverNodesWindow, self).__init__(parent,
                                               name=name)
        self.setupUi(self)
        self.addSubForm(removesolvernodes_layout.RemoveSolverNodesLayout)

        self.setWindowTitle(const.WINDOW_TITLE)
        self.setWindowFlags(QtCore.Qt.Tool)

        # Standard Buttons
        self.baseHideStandardButtons()
        self.applyBtn.show()
        self.closeBtn.show()
        self.applyBtn.setText('Clean..')
        self.applyBtn.clicked.connect(self.clean)

        # Hide irrelevant stuff
        self.baseHideProgressBar()

        self.add_menus(self.menubar)
        self.menubar.show()

        self.reset_options()

    def add_menus(self, menubar):
        edit_menu = QtWidgets.QMenu('Edit', menubar)
        commonmenus.create_edit_menu_items(
            edit_menu,
            reset_settings_func=self.reset_options)
        menubar.addMenu(edit_menu)

        help_menu = QtWidgets.QMenu('Help', menubar)
        commonmenus.create_help_menu_items(
            help_menu,
            tool_help_func=_open_help)
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
            'collections': self.subForm.collections_checkBox.isChecked(),
            'other_nodes': self.subForm.otherNodes_checkBox.isChecked()
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
        show=show,
        auto_raise=auto_raise,
        delete=delete
    )
    return win
