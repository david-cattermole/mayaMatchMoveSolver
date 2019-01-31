"""
Test functions for API utils module.
"""

import pprint
import unittest

import maya.cmds

import test.test_api.apiutils as test_api_utils
import mmSolver._api.solveresult as solveresult  # used indirectly.
import mmSolver.api as mmapi


def create_example_solve_scene():
    """
    Very basic single frame solver set up.

    This function does not execute the solve, execution must be done manually.

    :return: API Collection object.
    """
    # Camera
    cam_tfm = maya.cmds.createNode('transform',
                                   name='cam_tfm')
    cam_shp = maya.cmds.createNode('camera',
                                   name='cam_shp',
                                   parent=cam_tfm)
    maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
    maya.cmds.setAttr(cam_tfm + '.ty',  1.0)
    maya.cmds.setAttr(cam_tfm + '.tz', -5.0)
    cam = mmapi.Camera(shape=cam_shp)

    # Bundle
    bnd = mmapi.Bundle().create_node()
    bundle_tfm = bnd.get_node()
    maya.cmds.setAttr(bundle_tfm + '.tx', 5.5)
    maya.cmds.setAttr(bundle_tfm + '.ty', 6.4)
    maya.cmds.setAttr(bundle_tfm + '.tz', -25.0)
    assert mmapi.get_object_type(bundle_tfm) == 'bundle'

    # Marker
    mkr = mmapi.Marker().create_node(cam=cam, bnd=bnd)
    marker_tfm = mkr.get_node()
    assert mmapi.get_object_type(marker_tfm) == 'marker'
    maya.cmds.setAttr(marker_tfm + '.tx', 0.0)
    maya.cmds.setAttr(marker_tfm + '.ty', 0.0)

    # Attributes
    attr_tx = mmapi.Attribute(bundle_tfm + '.tx')
    attr_ty = mmapi.Attribute(bundle_tfm + '.ty')

    # Frames
    frm_list = [
        mmapi.Frame(1, primary=True)
    ]

    # Solver
    sol = mmapi.Solver()
    sol.set_max_iterations(10)
    sol.set_solver_type(mmapi.SOLVER_TYPE_LEVMAR)
    sol.set_verbose(True)
    sol.set_frame_list(frm_list)

    # Collection
    col = mmapi.Collection()
    col.create_node('mySolveCollection')
    col.add_solver(sol)
    col.add_marker(mkr)
    col.add_attribute(attr_tx)
    col.add_attribute(attr_ty)
    return col


# @unittest.skip
class TestSolveResult(test_api_utils.APITestCase):
    def test_init(self):
        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        print('error stats: ' + pprint.pformat(results[0].get_error_stats()))
        print('timer stats: ' + pprint.pformat(results[0].get_timer_stats()))
        print('solver stats: ' + pprint.pformat(results[0].get_solver_stats()))
        print('frame error list: ' + pprint.pformat(dict(results[0].get_frame_error_list())))
        print('marker error list: ' + pprint.pformat(dict(results[0].get_marker_error_list())))

    def test_combine_timer_stats(self):
        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        timer_stats = mmapi.combine_timer_stats(results)
        assert isinstance(timer_stats, dict)
        for k, v in timer_stats.items():
            assert v >= 0

    def test_merge_frame_error_list(self):
        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        frame_error_list = mmapi.merge_frame_error_list(results)
        assert isinstance(frame_error_list, dict)

    def test_get_average_frame_error_list(self):
        frame_error_list = {
            1: 0,
            2: 0.5,
            3: 1.0
        }
        v = mmapi.get_average_frame_error_list(frame_error_list)
        assert self.approx_equal(v, 0.5)

        frame_error_list = {1: 1.0}
        v = mmapi.get_average_frame_error_list(frame_error_list)
        assert self.approx_equal(v, 1.0)

        frame_error_list = {}
        v = mmapi.get_average_frame_error_list(frame_error_list)
        assert self.approx_equal(v, 0.0)

        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        frame_error_list = dict(results[0].get_frame_error_list())

        v = mmapi.get_average_frame_error_list(frame_error_list)
        assert isinstance(v, float)

    def test_get_max_frame_error(self):
        frame_error_list = {
            1: 0,
            2: 0.5,
            3: 1.0
        }
        frm, val = mmapi.get_max_frame_error(frame_error_list)
        assert self.approx_equal(frm, 3) and isinstance(frm, int)
        assert self.approx_equal(val, 1.0)

        frame_error_list = {1: 1.0}
        frm, val = mmapi.get_max_frame_error(frame_error_list)
        assert self.approx_equal(frm, 1) and isinstance(frm, int)
        assert self.approx_equal(val, 1.0)

        frame_error_list = {}
        frm, val = mmapi.get_max_frame_error(frame_error_list)
        assert frm is None
        assert self.approx_equal(val, -0.0)

        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        frame_error_list = dict(results[0].get_frame_error_list())
        frm, val = mmapi.get_max_frame_error(frame_error_list)
        assert frm is None or isinstance(frm, float)
        assert isinstance(val, float)


if __name__ == '__main__':
    prog = unittest.main()
