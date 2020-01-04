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
Module of exceptions for the entire mmSolver API.
"""


class MMException(Exception):
    """
    Base class for all mmSolver exceptions.
    """
    pass


class NotValid(MMException):
    """
    Raised when an object is not valid.
    """
    pass


class AlreadyLinked(MMException):
    """
    Raised when two objects are already connected (linked).
    """
    pass


class AlreadyUnlinked(MMException):
    """
    Raised when two objects are already disconnected (unlinked).
    """
    pass


class NotEnoughMarkers(MMException):
    """
    There are too many Attribute values in the solver for the Markers given.
    """
    pass


class SolverNotAvailable(MMException):
    """
    Raised when the mmSolver cannot be used (because the plug-in isn't loaded).
    """
    pass
