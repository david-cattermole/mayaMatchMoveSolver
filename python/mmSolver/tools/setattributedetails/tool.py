# Copyright (C) 2020 David Cattermole.
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
The Set Attribute Details UI tool.
"""

import mmSolver.logger
import mmSolver.tools.setattributedetails.lib as lib
import mmSolver.tools.setattributedetails.ui.dialog as set_attr_details_dialog


LOG = mmSolver.logger.get_logger()


def open_window(col=None, attr_list=None):
    """
    Open the Solver UI window.
    """
    if col is None:
        col = lib.get_active_collection()
    if col is None:
        title = 'No Collection.'
        text = (
            'No active collection.\n\n'
            'Please create a Collection to set Attribute detail.'
        )
        set_attr_details_dialog.warn_user(title, text)
        return

    if attr_list is None:
        attr_list = lib.get_selected_maya_attributes()
        attr_list = lib.input_attributes_filter(attr_list)
        if len(attr_list) == 0:
            attr_list = lib.get_selected_node_default_attributes()
            attr_list = lib.input_attributes_filter(attr_list)

    if attr_list is None or len(attr_list) == 0:
        title = 'No Attribute.'
        text = (
            'No selected attributes.\n\n' 'Please select attributes in the Channel Box.'
        )
        set_attr_details_dialog.warn_user(title, text)
        return

    status, dialog = set_attr_details_dialog.main(col, attr_list)
    assert isinstance(dialog, set_attr_details_dialog.Dialog)
    if status is True:
        for attr in attr_list:
            new_detail_values = dialog.get_detail_values_for_attribute(attr)
            lib.set_attribute_details(col, attr, new_detail_values)
    return
