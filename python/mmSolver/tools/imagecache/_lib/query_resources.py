# Copyright (C) 2024 David Cattermole.
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
Functions to control the image cache.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.logger

LOG = mmSolver.logger.get_logger()


def get_gpu_memory_total_bytes():
    total_bytes = maya.cmds.mmMemoryGPU(query=True, total=True)
    if total_bytes is None:
        return 0
    return int(total_bytes)


def get_gpu_memory_used_bytes():
    used_bytes = maya.cmds.mmMemoryGPU(query=True, used=True)
    if used_bytes is None:
        return 0
    return int(used_bytes)


def get_cpu_memory_total_bytes():
    # The value returned from the command is a 'str', because the
    # value may be more than what a 32-bit integer can support, which
    # is the largest integer size returned by the Maya API. Therefore
    # we simply convert the string to a integer in Python (which
    # supports more than 32-bit integers in the 'int' type).
    value = maya.cmds.mmMemorySystem(
        query=True,
        systemPhysicalMemoryTotal=True,
    )
    return int(value)


def get_cpu_memory_used_bytes():
    # The value returned from the command is a 'str', because the
    # value may be more than what a 32-bit integer can support, which
    # is the largest integer size returned by the Maya API. Therefore
    # we simply convert the string to a integer in Python (which
    # supports more than 32-bit integers in the 'int' type).
    value = maya.cmds.mmMemorySystem(
        query=True,
        systemPhysicalMemoryUsed=True,
    )
    return int(value)
