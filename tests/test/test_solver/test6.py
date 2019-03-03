"""
Testing a single point nodal camera solve across time.

This script calls the solver multiple times in different ways, the aim
is to reduce the slowness while maintaining static value solving.
"""

import time
import unittest

try:
    import maya.standalone
    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds


import test.test_solver.solverutils as solverUtils


# @unittest.skip
class TestSolver6(solverUtils.SolverTestCase):

    def do_solve(self, solver_name, solver_index):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            self.assertTrue(False, msg)

        start = 1
        end = 100
        mid = start + ((end - start) / 2)

        cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
        cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty',  1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateX', time=start, value=-2.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateX', time=end, value=2.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=start, value=-2.5)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=end, value=2.5)

        bundle_tfm = maya.cmds.createNode('transform', name='bundle_tfm')
        bundle_shp = maya.cmds.createNode('locator', name='bundle_shp', parent=bundle_tfm)
        maya.cmds.setAttr(bundle_tfm + '.tx', -2.5)
        maya.cmds.setAttr(bundle_tfm + '.ty', 2.4)
        maya.cmds.setAttr(bundle_tfm + '.tz', -15.0)

        marker_tfm = maya.cmds.createNode('transform', name='marker_tfm', parent=cam_tfm)
        marker_shp = maya.cmds.createNode('locator', name='marker_shp', parent=marker_tfm)
        maya.cmds.addAttr(marker_tfm, longName='enable', at='byte',
                          minValue=0, maxValue=1, defaultValue=True)
        maya.cmds.addAttr(marker_tfm, longName='weight', at='double',
                      minValue=0.0, defaultValue=1.0)
        maya.cmds.setAttr(marker_tfm + '.tz', -10)
        maya.cmds.setKeyframe(marker_tfm, attribute='translateX', time=start, value=-2.5)
        maya.cmds.setKeyframe(marker_tfm, attribute='translateX', time=end, value=3.0)
        maya.cmds.setKeyframe(marker_tfm, attribute='translateY', time=start, value=1.5)
        maya.cmds.setKeyframe(marker_tfm, attribute='translateY', time=end, value=1.3)

        # save the output
        path = self.get_data_path('solver_test6_%s_before.ma' % solver_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        cameras = (
            (cam_tfm, cam_shp),
        )
        markers = (
            (marker_tfm, cam_shp, bundle_tfm),
        )
        # NOTE: All dynamic attributes must have a keyframe before starting to solve.
        node_attrs = [
            (cam_tfm + '.rx', 'None', 'None'),
            (cam_tfm + '.ry', 'None', 'None'),
        ]

        framesList = [
            [(start), (mid), (end)],
            [(start), (25), (mid), (75), (end)],
            [(start), (12), (25), (37), (mid), (62), (75), (87), (end)],
        ]
        print 'framesList:', framesList
        allFrames = []
        for f in range(start, end+1):
            allFrames.append(f)
        print 'allFrames:', allFrames

        # Run solver!
        results = []
        s = time.time()

        # Solve primary frames (first, middle and last), and sub-divide.
        for frames in framesList:
            result = maya.cmds.mmSolver(
                camera=cameras,
                marker=markers,
                attr=node_attrs,
                iterations=10,
                solverType=solver_index,
                frame=frames,
                verbose=True,
            )
            results.append(result)

        # # Solve between primary frames
        # for frames in framesList:
        #     for i in range(len(frames)-1):
        #         betweenFrames = []
        #         for j in range(frames[i]+1, frames[i+1]):
        #             result = maya.cmds.mmSolver(
        #                 camera=cameras,
        #                 marker=markers,
        #                 attr=node_attrs,
        #                 iterations=10,
        #                 solverType=solver_index,
        #                 frame=[j],
        #                 verbose=True,
        #             )
        #             results.append(result)
        #         # betweenFrames = []
        #         # for j in range(frames[i]+1, frames[i+1]):
        #         #     betweenFrames.append(j)
        #         # result = maya.cmds.mmSolver(
        #         #     camera=cameras,
        #         #     marker=markers,
        #         #     attr=node_attrs,
        #         #     iterations=10,
        #         #     solverType=solver_index,
        #         #     frame=betweenFrames,
        #         #     verbose=True,
        #         # )
        #         # results.append(result)

        # # Global Solve
        # result = maya.cmds.mmSolver(
        #     camera=cameras,
        #     marker=markers,
        #     attr=node_attrs,
        #     iterations=10,
        #     solverType=solver_index,
        #     frame=allFrames,
        #     verbose=True,
        # )
        # results.append(result)

        e = time.time()
        print 'total time:', e - s

        # save the output
        path = self.get_data_path('solver_test6_%s_after.ma' % solver_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        
        # Ensure the values are correct
        for i, result in enumerate(results):
            print 'i', i, result[0]
        for result in results:
            print result[0]
            self.assertEqual(result[0], 'success=1')
        return

    def test_init_levmar(self):
        self.do_solve('levmar', 0)

    def test_init_cminpack_lm(self):
        self.do_solve('cminpack_lm', 1)


if __name__ == '__main__':
    prog = unittest.main()
