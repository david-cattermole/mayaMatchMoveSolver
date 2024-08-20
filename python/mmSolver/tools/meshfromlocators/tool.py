# Copyright (C) 2024 Patcha Saheb Binginapalli.
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
Mesh From Locators main.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.logger

LOG = mmSolver.logger.get_logger()


def main():
    """
    Open the 'Mesh From Locators' window.
    """
    import mmSolver.tools.meshfromlocators.ui.meshfromlocators_window as window

    window.main()
