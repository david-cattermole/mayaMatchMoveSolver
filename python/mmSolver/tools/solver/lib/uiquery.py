# Copyright (C) 2018, 2019 David Cattermole.
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
Query the Qt UI in some way.
"""


import mmSolver.logger

LOG = mmSolver.logger.get_logger()


def get_ui_node_from_index(idx, filter_model):
    if idx.isValid() is False:
        return None
    idx_map = filter_model.mapToSource(idx)
    ui_node = idx_map.internalPointer()
    return ui_node


def get_selected_ui_nodes(tree_view, filter_model):
    node_list = []
    sel_model = tree_view.selectionModel()
    index_list = sel_model.selectedRows()
    for idx in index_list:
        ui_node = get_ui_node_from_index(idx, filter_model)
        if ui_node is None:
            continue
        node_list.append(ui_node)
    return node_list


def get_selected_ui_table_row(tree_view, model, filter_model):
    node_list = []
    sel_model = tree_view.selectionModel()
    selection = sel_model.selection()
    index_list = selection.indexes()
    all_node_list = model.nodeList()
    for idx in index_list:
        if idx.isValid() is False:
            continue
        idx_map = filter_model.mapToSource(idx)
        row = idx.row()
        ui_node = all_node_list[row]
        if ui_node is None:
            continue
        node_list.append(ui_node)
    return node_list


def convert_ui_nodes_to_nodes(ui_nodes, key):
    """
    Get the list of data from the UI objects.

    :param ui_nodes:
        Nodes from the UI classes. `ui_nodes` is expected to be a list
        of classes derived from
        :py:class:`mmSolver.tools.solver.ui.attr_nodes.PlugNode` or
        :py:class:`mmSolver.tools.solver.ui.object_nodes.ObjectNode`.
    :type ui_nodes: [PlugNode, ..] or [ObjectNode, ..]

    :param key: Key to look up on the node, to get the data.
    :type key: str

    :return: List of the data contents in the UI nodes given.
    :rtype: [object, ..]
    """
    nodes = []
    for ui_node in ui_nodes:
        node_data = ui_node.data()
        if node_data is None:
            continue
        data_content = node_data.get(key)
        if data_content is None:
            continue
        nodes.append(data_content)
    return nodes
