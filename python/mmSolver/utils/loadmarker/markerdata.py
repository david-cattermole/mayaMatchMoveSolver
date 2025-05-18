# Copyright (C) 2018 David Cattermole.
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
Provides a base interface for marker import plug-ins.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import mmSolver.utils.loadfile.keyframedata as keyframedata


class MarkerData(object):
    def __init__(self):
        self._name = None  # None or str or unicode
        self._group_name = None  # None or str or unicode
        self._id = None  # None or int
        self._color = None  # the colour of the point
        self._x = keyframedata.KeyframeData()  # 0.0 is left, 1.0 is right.
        self._y = keyframedata.KeyframeData()  # 0.0 is bottom, 1.0 is top.
        self._enable = keyframedata.KeyframeData()
        self._weight = keyframedata.KeyframeData()
        self._bnd_x = None
        self._bnd_y = None
        self._bnd_z = None
        self._bnd_lock_x = None
        self._bnd_lock_y = None
        self._bnd_lock_z = None
        self._bnd_world_x = keyframedata.KeyframeData()
        self._bnd_world_y = keyframedata.KeyframeData()
        self._bnd_world_z = keyframedata.KeyframeData()

    def get_name(self):
        return self._name

    def set_name(self, value):
        self._name = value

    def get_id(self):
        return self._id

    def set_id(self, value):
        self._id = value

    def get_group_name(self):
        return self._group_name

    def set_group_name(self, value):
        self._group_name = value

    def get_color(self):
        return self._color

    def set_color(self, value):
        self._color = value

    def get_x(self):
        return self._x

    def set_x(self, value):
        self._x = value

    def get_y(self):
        return self._y

    def set_y(self, value):
        self._y = value

    def get_enable(self):
        return self._enable

    def set_enable(self, value):
        self._enable = value

    def get_weight(self):
        return self._weight

    def set_weight(self, value):
        self._weight = value

    def get_bundle_x(self):
        return self._bnd_x

    def set_bundle_x(self, value):
        self._bnd_x = value

    def get_bundle_y(self):
        return self._bnd_y

    def set_bundle_y(self, value):
        self._bnd_y = value

    def get_bundle_z(self):
        return self._bnd_z

    def set_bundle_z(self, value):
        self._bnd_z = value

    def get_bundle_lock_x(self):
        return self._bnd_lock_x

    def set_bundle_lock_x(self, value):
        self._bnd_lock_x = value

    def get_bundle_lock_y(self):
        return self._bnd_lock_y

    def set_bundle_lock_y(self, value):
        self._bnd_lock_y = value

    def get_bundle_lock_z(self):
        return self._bnd_lock_z

    def set_bundle_lock_z(self, value):
        self._bnd_lock_z = value

    def get_bundle_world_x(self):
        return self._bnd_world_x

    def set_bundle_world_x(self, value):
        self._bnd_world_x = value

    def get_bundle_world_y(self):
        return self._bnd_world_y

    def set_bundle_world_y(self, value):
        self._bnd_world_y = value

    def get_bundle_world_z(self):
        return self._bnd_world_z

    def set_bundle_world_z(self, value):
        self._bnd_world_z = value

    name = property(get_name, set_name)
    id = property(get_id, set_id)
    x = property(get_x, set_x)
    y = property(get_y, set_y)
    enable = property(get_enable, set_enable)
    weight = property(get_weight, set_weight)
    group_name = property(get_group_name, set_group_name)
    color = property(get_color, set_color)
    bundle_x = property(get_bundle_x, set_bundle_x)
    bundle_y = property(get_bundle_y, set_bundle_y)
    bundle_z = property(get_bundle_z, set_bundle_z)
    bundle_lock_x = property(get_bundle_lock_x, set_bundle_lock_x)
    bundle_lock_y = property(get_bundle_lock_y, set_bundle_lock_y)
    bundle_lock_z = property(get_bundle_lock_z, set_bundle_lock_z)
    bundle_world_x = property(get_bundle_world_x, set_bundle_world_x)
    bundle_world_y = property(get_bundle_world_y, set_bundle_world_y)
    bundle_world_z = property(get_bundle_world_z, set_bundle_world_z)
