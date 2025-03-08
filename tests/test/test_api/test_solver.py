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
Test functions for solver module, and especially for the Solver class.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest


import test.test_api.apiutils as test_api_utils
import mmSolver._api.solverstep as solver
import mmSolver._api.constant as const


# @unittest.skip
class TestSolver(test_api_utils.APITestCase):
    def test_init(self):
        x = solver.Solver()
        y = solver.Solver()
        self.assertNotEqual(x.get_name(), y.get_name())

        name = 'mySolver'
        x = solver.Solver(name=name)
        self.assertEqual(x.get_name(), name)

        x = solver.Solver()
        x.set_solver_type(const.SOLVER_TYPE_DEFAULT)
        x_data = x.get_data()
        y = solver.Solver(data=x_data)
        y_data = y.get_data()
        self.assertEqual(x_data, y_data)

    # def test_get_name(self):
    #     pass

    # def test_set_name(self):
    #     pass

    # def test_get_data(self):
    #     pass

    # def test_set_data(self):
    #     pass


if __name__ == '__main__':
    prog = unittest.main()
