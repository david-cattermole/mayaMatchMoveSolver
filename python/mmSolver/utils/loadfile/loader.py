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

import abc


class LoaderBase(object):
    """
    Base class for all format loaders.
    """
    __metaclass__ = abc.ABCMeta

    name = None
    file_exts = None

    # optional arguments and default values.
    args = None

    @abc.abstractmethod
    def parse(self, file_path, **kwargs):
        """
        Parse the given file path.

        Inherit from LoaderBase and override this method.

        :raise ParserError:
            When the parser encounters an error related to parsing.

        :raise OSError:
            When there is a problem with reading or accessing the
            given file.

        :return: Tuple of FileInfo and List of MarkerData.
        :rtype: (FileInfo, [MarkerData, ...])
        """
        return
