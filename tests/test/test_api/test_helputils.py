"""
Test functions for 'helputils' module.
"""

import unittest

import maya.cmds
import maya.OpenMaya as OpenMaya

import test.test_api.apiutils as test_api_utils
import mmSolver.ui.helputils as helputils


# @unittest.skip
class TestHelpUtils(test_api_utils.APITestCase):
    def test_get_help_source(self):
        src = helputils.get_help_source()
        assert isinstance(src, (str, unicode))

    def test_get_help_base_location(self):
        src = helputils.get_help_source()
        url = helputils.get_help_base_location(help_source=src)
        msg = (
            'The help URL cannot be found! '
            'Did you build and install documentation?'
            'url=%r'
        )
        assert isinstance(url, (str, unicode)), msg


if __name__ == '__main__':
    prog = unittest.main()
