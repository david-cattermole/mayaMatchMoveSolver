"""
Run the all tests.

This script can be run with arguments to give exact tests to run.
"""

import os
import sys


# Ensure that '<root>/python' is on the PYTHONPATH
path = os.path.dirname(__file__)
package_path = os.path.abspath(os.path.join(path, '..', 'python'))
tests_path = os.path.abspath(os.path.join(path, '..', 'tests'))
sys.path.insert(0, package_path)
sys.path.insert(0, tests_path)


if __name__ == '__main__':
    try:
        import maya.standalone
        maya.standalone.initialize()
    except RuntimeError:
        pass
    import maya.cmds

    import unittest
    paths = sys.argv[1:]
    loader = unittest.TestLoader()
    final_suite = None
    if len(paths) == 0:
        final_suite = loader.discover(tests_path)
    else:
        suites = []
        for path in paths:
            head = path
            tail = 'test*.py'
            if os.path.isfile(path):
                head, tail = os.path.split(path)
            s = loader.discover(head, pattern=tail, top_level_dir=tests_path)
            suites.append(s)
        final_suite = unittest.TestSuite()
        final_suite.addTests(suites)
    runner = unittest.TextTestRunner()
    results = runner.run(final_suite)

    if maya.cmds.about(batch=True):
        if results.wasSuccessful() is True:
            maya.cmds.quit(force=True)
        else:
            print >> sys.stderr, "Tests failed!"
            exit(1)
