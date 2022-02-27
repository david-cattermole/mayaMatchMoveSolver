# Copyright (C) 2020 David Cattermole.
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
Toggle NURBS curves, locators and cameras in the active 3D viewport.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.logger
import mmSolver.utils.viewport as viewport_utils
import mmSolver.tools.toggleviewportctrls.lib as lib


LOG = mmSolver.logger.get_logger()


def main():
    """
    Toggle the active viewport with Rig Controls on/off.

    Usage:

    1) Activate viewport.

    2) Run tool; the visibility of rig controls in the viewport is toggled
       on/off.

    """
    model_panel = viewport_utils.get_active_model_panel()
    if model_panel is None:
        LOG.error('Please select an active viewport; model_panel=%r',
                  model_panel)
        return
    lib.toggle_ctrls_visibility(model_panel)
    return
