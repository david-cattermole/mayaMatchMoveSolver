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
Test functions for 'frame' module.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import unittest

import maya.cmds
import maya.OpenMaya as OpenMaya

import test.test_api.apiutils as test_api_utils
import mmSolver._api.frame as frame


# @unittest.skip
class TestFrame(test_api_utils.APITestCase):
    def test_init(self):
        f1 = frame.Frame(10)
        self.assertIs(f1.get_number(), 10)

        f2 = frame.Frame(10.0)
        self.assertIs(f2.get_number(), 10.0)

        self.assertRaises(AssertionError, frame.Frame, 'string')
        self.assertRaises(AssertionError, frame.Frame, None)

        f3 = frame.Frame(10.0)
        self.assertEqual(f3.get_tags(), ['normal'])

        f4 = frame.Frame(10.0, primary=True)
        self.assertEqual(f4.get_tags(), ['primary'])

        f5 = frame.Frame(10.0, secondary=True)
        self.assertEqual(f5.get_tags(), ['secondary'])

    def test_get_data(self):
        f1 = frame.Frame(10)
        self.assertEqual(f1.get_data(), {'number': 10, 'tags': ['normal']})

        f2 = frame.Frame(10.0, tags=['myTag'])
        self.assertEqual(f2.get_data(), {'number': 10, 'tags': ['myTag']})

    def test_set_data(self):
        f1 = frame.Frame(10)
        f1_data = f1.get_data()

        f2 = frame.Frame(3147)
        f2.set_data(f1_data)
        f2_data = f2.get_data()
        self.assertEqual(f1_data, f2_data)

    def test_get_number(self):
        f1 = frame.Frame(10)
        self.assertIs(f1.get_number(), 10)

        f2 = frame.Frame(10.0)
        self.assertIs(f2.get_number(), 10.0)

    def test_set_number(self):
        f1 = frame.Frame(10)
        f1.set_number(3147)
        self.assertEqual(f1.get_number(), 3147)

        f1.set_number(24)
        self.assertEqual(f1.get_number(), 24)

    def test_get_tags(self):
        f = frame.Frame(10, primary=False)
        self.assertEqual(f.get_tags(), ['normal'])

        f = frame.Frame(10, primary=True)
        self.assertEqual(f.get_tags(), ['primary'])

    def test_set_tags(self):
        f = frame.Frame(10)
        f.set_tags(['tag'])
        self.assertEqual(f.get_tags(), ['tag'])

        f.set_tags([])
        self.assertEqual(f.get_tags(), [])

    def test_add_tag(self):
        f = frame.Frame(10)
        f.add_tag('primary')
        self.assertEqual(f.get_tags(), ['normal', 'primary'])

        f.set_tags([])
        f.add_tag('tag')
        self.assertEqual(f.get_tags(), ['tag'])


if __name__ == '__main__':
    prog = unittest.main()
