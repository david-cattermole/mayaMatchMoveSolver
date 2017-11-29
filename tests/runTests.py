"""
Run the all tests.
"""

import os
import sys


# Ensure that '<root>/python' is on the PYTHONPATH
path = os.path.dirname(__file__)
package_path = os.path.abspath(os.path.join(path, '..', 'python'))
tests_path = os.path.abspath(os.path.join(path, '..', 'tests'))
sys.path.insert(0, package_path)
sys.path.insert(0, tests_path)


def runNose():
    import nose
    nose.run()


def runNose2():
    import nose2
    nose2.discover(exit=False)


def runUnittest():
    import unittest
    suite = unittest.TestLoader().discover(tests_path)
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    if 'coverage' in dir():
        import coverage
        cov = coverage.Coverage()
        cov.start()

    try:
        import maya.standalone
        maya.standalone.initialize()
    except RuntimeError:
        pass
    import maya.cmds

    # Put all test module imports here.
    import test.test_api.test_sethelper

    func = None
    msg = ''
    try:
        import nose2
        print("Using 'nose2' package for testing.")
        func = runNose2
    except ImportError:
        try:
            import nose
            print("Using 'nose' package for testing.")
            func = runNose
        except ImportError:
            # The backwards compatible way, using the in-build unittest module.
            import unittest
            print("Using 'unittest' package for testing.")
            func = runUnittest
    func()

    if 'coverage' in dir():
        cov.stop()
        cov.save()
        print('')
        cov.report()
        cov.html_report()

    if maya.cmds.about(batch=True):
        maya.cmds.quit(force=True)

