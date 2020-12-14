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
Contains constant data to be used by the About window.
"""

# Window Title Bar format.
WINDOW_TITLE_BAR = 'About mmSolver'


# The text to show to the user.
ABOUT_TEXT = """Maya MatchMove Solver (mmSolver) v{version}
Copyright (C) {copyrights}

Authors: {author}

Special Thanks to:
Michael Karp

Website: {page}

== License ==
This software, mmSolver, is licensed under the GNU LGPL v3 license.

mmSolver is free software: you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

mmSolver is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.

Please read the file LICENSE in the root project directory for a copy
of the GNU LGPL v3 license.

== Description ==
{description}
mmSolver is a solving engine with a bundled tool-set for MatchMove
tasks inside Autodesk Maya.  The solver core is incremental, building
on the initial values given to the solver.
"""
