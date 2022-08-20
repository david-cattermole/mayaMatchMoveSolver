# Copyright (C) 2019 David Cattermole.
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
Position Bundle under the Marker, using multiple frames.
"""

import warnings

import mmSolver.logger
import mmSolver.api as mmapi

LOG = mmSolver.logger.get_logger()


def triangulate_bundle(bnd, relock=None, max_distance=None, direction_tolerance=None):
    """
    Triangulate a 3D bundle position.

    Deprecated: Please use 'mmSolver.api.triangulate_bundle()'
    instead.

    :param bnd: Bundle to be triangulated.
    :type bnd: Bundle

    :param relock: If True any bundle translate attributes will be
                   unlocked, changed then relocked.
    :type relock: bool or None

    :param max_distance: Defines the maximum distance the bundle can
        be positioned away from camera until the value is clamped.
    :type max_distance: float or None

    :param direction_tolerance: Determines the tolerance used to
        consider if a triangulated point is valid or not.  It's not
        clear what the units are for this tolerance value. This value
        is used by OpenMaya.MVector.isEquivalent() and the Maya
        documentation doesn't really explain the units. The default
        value (if not given) is 1.0.
    :type direction_tolerance: float or None

    :returns: True if the bundle successfully triangulated, False if
        the bundle could not accurately be triangulated. For example
        if the bundle was computed to behind the camera this would be
        considered a failure.
    :rtype: bool
    """
    msg = 'Deprecated, please use mmSolver.api.triangulate_bundle() instead.'
    warnings.warn(msg, DeprecationWarning)

    success = mmapi.triangulate_bundle(
        bnd,
        relock=relock,
        max_distance=max_distance,
        direction_tolerance=direction_tolerance,
    )
    return success
