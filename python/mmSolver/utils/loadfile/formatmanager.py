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
A manager class for registering new marker file formats.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


class FormatManager(object):
    def __init__(self):
        self.__formats = {}

    def register_format(self, class_obj):
        if str(class_obj) not in self.__formats:
            self.__formats[str(class_obj)] = class_obj
        return True

    def get_formats(self):
        format_list = []
        for key in self.__formats:
            fmt = self.__formats[key]
            format_list.append(fmt)
        return format_list
