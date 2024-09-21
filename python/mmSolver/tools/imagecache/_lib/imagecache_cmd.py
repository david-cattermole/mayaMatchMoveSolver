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
import mmSolver.utils.python_compat as pycompat

LOG = mmSolver.logger.get_logger()


def get_gpu_cache_item_count():
    return int(maya.cmds.mmImageCache(query=True, gpuItemCount=True))


def get_cpu_cache_item_count():
    return int(maya.cmds.mmImageCache(query=True, cpuItemCount=True))


def get_gpu_cache_group_names():
    return maya.cmds.mmImageCache(query=True, gpuGroupNames=True)


def get_cpu_cache_group_names():
    return maya.cmds.mmImageCache(query=True, cpuGroupNames=True)


def get_gpu_cache_slot_count():
    # NOTE: The internal mmImageCache name for a "slot" is actually a
    # "group" - a group of images.
    return int(maya.cmds.mmImageCache(query=True, gpuGroupCount=True))


def get_cpu_cache_slot_count():
    # NOTE: The internal mmImageCache name for a "slot" is actually a
    # "group" - a group of images.
    return int(maya.cmds.mmImageCache(query=True, cpuGroupCount=True))


def get_gpu_cache_group_item_count(group_name):
    assert isinstance(group_name, pycompat.TEXT_TYPE)
    assert len(group_name) > 0
    return int(maya.cmds.mmImageCache(group_name, query=True, gpuGroupItemCount=True))


def get_cpu_cache_group_item_count(group_name):
    assert isinstance(group_name, pycompat.TEXT_TYPE)
    assert len(group_name) > 0
    return int(maya.cmds.mmImageCache(group_name, query=True, cpuGroupItemCount=True))


def get_gpu_cache_group_item_names(group_name):
    assert isinstance(group_name, pycompat.TEXT_TYPE)
    assert len(group_name) > 0
    return maya.cmds.mmImageCache(group_name, query=True, gpuGroupItemNames=True)


def get_cpu_cache_group_item_names(group_name):
    assert isinstance(group_name, pycompat.TEXT_TYPE)
    assert len(group_name) > 0
    return maya.cmds.mmImageCache(group_name, query=True, cpuGroupItemNames=True)


def get_gpu_cache_used_bytes():
    return pycompat.LONG_TYPE(maya.cmds.mmImageCache(query=True, gpuUsed=True))


def get_cpu_cache_used_bytes():
    return pycompat.LONG_TYPE(maya.cmds.mmImageCache(query=True, cpuUsed=True))


def get_gpu_cache_capacity_bytes():
    return pycompat.LONG_TYPE(maya.cmds.mmImageCache(query=True, gpuCapacity=True))


def get_cpu_cache_capacity_bytes():
    return pycompat.LONG_TYPE(maya.cmds.mmImageCache(query=True, cpuCapacity=True))


def set_gpu_cache_capacity_bytes(size_bytes):
    assert isinstance(size_bytes, pycompat.INT_TYPES)
    return maya.cmds.mmImageCache(edit=True, gpuCapacity=size_bytes)


def set_cpu_cache_capacity_bytes(size_bytes):
    assert isinstance(size_bytes, pycompat.INT_TYPES)
    return maya.cmds.mmImageCache(edit=True, cpuCapacity=size_bytes)
