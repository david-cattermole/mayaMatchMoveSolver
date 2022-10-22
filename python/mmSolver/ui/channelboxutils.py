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
Functions to create Maya menus.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds
import maya.mel
import mmSolver.logger


LOG = mmSolver.logger.get_logger()


def get_ui_name():
    """
    Get the internal channel box Maya UI path.

    .. note::
        When the Maya GUI has not launched yet, this function
        returns None.

    :return: UI path str.
    :rtype: str or None
    """
    cmd = 'global string $gChannelBoxName;' 'string $temp = $gChannelBoxName;'
    return maya.mel.eval(cmd)

