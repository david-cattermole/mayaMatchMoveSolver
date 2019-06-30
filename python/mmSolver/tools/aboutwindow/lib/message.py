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
Formats and displays 'about' information.
"""

import mmSolver.constant as mmSolver_const
import mmSolver.tools.aboutwindow.constant as const


def get_about_text():
    # Python Constant values
    version = mmSolver_const.PROJECT_VERSION
    desc = mmSolver_const.PROJECT_DESCRIPTION
    author = mmSolver_const.PROJECT_AUTHOR
    page = mmSolver_const.PROJECT_HOMEPAGE_URL
    copyrights = mmSolver_const.PROJECT_COPYRIGHT

    text = const.ABOUT_TEXT.format(
        author=author,
        description=desc,
        page=page,
        copyrights=copyrights,
        version=version
    )
    return text
