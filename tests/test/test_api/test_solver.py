"""
Test functions for solver module, and especially for the Solver class.
"""

import sys
import os
import unittest

import maya.cmds

import test.test_api.apiutils as test_api_utils
import mmSolver._api.solver as solver
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
        x.set_solver_type(const.SOLVER_TYPE_LEVMAR)
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
