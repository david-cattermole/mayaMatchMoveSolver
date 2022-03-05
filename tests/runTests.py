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
Run the all tests.

This script can be run with arguments to give exact tests to run.

Run code like this from Maya's Script Editor:
.. code::

    import sys
    import os
    dev_path = 'C:/Users/user/dev/mayaMatchMoveSolver/'
    runTest_path = os.path.join(dev_path, 'tests')
    if runTest_path not in sys.path:
        sys.path.append(runTest_path)

    import runTests

    # reload the module you are testing
    import test.test_api.test_solve as mod
    reload(mod)

    path_list = []
    # # Uncomment to run tests from test_solve.py only.
    # path_list.append(os.path.join(dev_path, 'tests/test/test_api/test_solve.py'))
    runTests.main(path_list)

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys


# Ensure that '<root>/python' is on the PYTHONPATH
this_file_path = os.path.dirname(__file__)
package_path = os.path.abspath(os.path.join(this_file_path, '..', 'python'))
tests_path = os.path.abspath(os.path.join(this_file_path, '..', 'tests'))
sys.path.insert(0, package_path)
sys.path.insert(0, tests_path)


def main(path_list):
    try:
        import maya.standalone
        maya.standalone.initialize()
    except RuntimeError:
        raise
    import maya.cmds

    # Load the plug-in.
    maya.cmds.loadPlugin('mmSolver')

    import unittest
    loader = unittest.TestLoader()
    final_suite = None
    if len(path_list) == 0:
        final_suite = loader.discover(tests_path)
    else:
        suites = []
        for path_entry in path_list:
            head = path_entry
            tail = 'test*.py'
            if os.path.isfile(path_entry):
                head, tail = os.path.split(path_entry)
            s = loader.discover(head, pattern=tail, top_level_dir=tests_path)
            suites.append(s)
        final_suite = unittest.TestSuite()
        final_suite.addTests(suites)
    runner = unittest.TextTestRunner()
    results = runner.run(final_suite)

    if maya.cmds.about(batch=True):
        maya.cmds.file(new=True, force=True)
        exit_code = 0
        if results.wasSuccessful() is False:
            exit_code = 1
            print("Tests failed!", file=sys.stderr)
        print("Press CTRL+C to exit 'mayapy'.")
        if int(maya.cmds.about(apiVersion=True)) < 20220000:
            maya.standalone.uninitialize()
        sys.exit(exit_code)
    return


if __name__ == '__main__':
    main(sys.argv[1:])
