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
Aim the selected transform nodes at the current viewport's camera.
"""

import maya.cmds
import mmSolver.logger


LOG = mmSolver.logger.get_logger()


def aim_at_target(nodes, target, remove_after=None):
    """
    Aims the selected transforms at the target transform node.
    """
    assert maya.cmds.nodeType(target) == 'transform'
    assert isinstance(nodes, (list, tuple))
    if remove_after is None:
        remove_after = True
    constraint_list = []
    for node in nodes:
        msg = 'Node has locked rotation attributes, skipping.'
        for attr in ['rx', 'ry', 'rz']:
            plug = node + '.' + attr
            locked = maya.cmds.getAttr(plug, lock=True)
            if locked is True:
                LOG.warning(msg, node)
                continue
        aim = maya.cmds.aimConstraint(
            target,
            node,
            offset=(0, 0, 0),
            weight=1.0,
            aimVector=(1, 0, 0),
            upVector=(0, 1, 0),
            worldUpType='vector',
            worldUpVector=(0, 1, 0),
        )
        constraint_list.append(aim[0])

    # Delete all constraints
    if remove_after is True:
        cons_list = [n for n in constraint_list if maya.cmds.objExists(n) is True]
        if len(cons_list) > 0:
            maya.cmds.delete(cons_list)
    return
