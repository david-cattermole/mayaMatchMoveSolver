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
The Load Marker tool - user facing.
"""

import mmSolver.logger
import mmSolver.api as mmapi


LOG = mmSolver.logger.get_logger()


# def main(file_path, cam=None, **kwargs):
#     raise NotImplementedError


def open_window():
    mmapi.load_plugin()
    import mmSolver.tools.loadmarker.ui.loadmarker_window as loadmarker_window
    loadmarker_window.main()
