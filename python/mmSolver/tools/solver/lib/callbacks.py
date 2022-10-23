# Copyright (C) 2018, 2019, 2022 David Cattermole.
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
General callback related functions.
"""

import maya.cmds
import mmSolver.logger


LOG = mmSolver.logger.get_logger()


def add_callback_to_any_node(
    callback_manager, callback_type, node_path, add_callbacks_func
):
    msg = 'Node UUID has multiple paths: node=%r node_uuids=%r'
    node_uuids = maya.cmds.ls(node_path, uuid=True) or []
    if len(node_uuids) != 1:
        LOG.warning(msg, node_path, node_uuids)
        return
    node_uuid = node_uuids[0]
    if callback_manager.type_has_node(callback_type, node_uuid) is True:
        return
    callback_ids = add_callbacks_func(
        node_uuid,
        node_path,
    )
    callback_manager.add_node_ids(
        callback_type,
        node_uuid,
        callback_ids,
    )
    return
