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
Test functions for 'helputils' module.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest


import test.test_api.apiutils as test_api_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.ui.helputils as helputils


# @unittest.skip
class TestHelpUtils(test_api_utils.APITestCase):
    def test_get_help_source(self):
        src = helputils.get_help_source()
        msg = 'Invalid help source; src=%r'
        assert isinstance(src, pycompat.TEXT_TYPE), msg % src

    def test_get_help_base_location(self):
        src = helputils.get_help_source()
        url = helputils.get_help_base_location(help_source=src)
        msg = (
            'The help URL cannot be found! '
            'Did you build and install documentation? '
            'url=%r'
        )
        assert isinstance(url, pycompat.TEXT_TYPE), msg % url


if __name__ == '__main__':
    prog = unittest.main()
