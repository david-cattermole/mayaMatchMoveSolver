"""
Solve a single non-animated bundle to the screen-space location of a bundle.

This test is the same as 'test.test_solver.test1' except this test uses the
Python API. It's a basic example of how to use the API.
"""

import pprint
import math
import unittest

try:
    import maya.standalone
    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds

import mmSolver.api as api
import test.test_api.apiutils as test_api_utils
# import mmSolver.tools.loadmarker.mayareadfile as marker_read


# @unittest.skip
class TestSolve(test_api_utils.APITestCase):

    def test_init(self):
        """
        Single Frame solve.
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
        cam = api.Camera(shape=cam_shp)

        # Bundle
        bnd = api.Bundle().create_node()
        bundle_tfm = bnd.get_node()
        maya.cmds.setAttr(bundle_tfm + '.tx', 5.5)
        maya.cmds.setAttr(bundle_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundle_tfm + '.tz', -25.0)
        assert api.get_object_type(bundle_tfm) == 'bundle'

        # Marker
        mkr = api.Marker().create_node(cam=cam, bnd=bnd)
        marker_tfm = mkr.get_node()
        assert api.get_object_type(marker_tfm) == 'marker'
        maya.cmds.setAttr(marker_tfm + '.tx', 0.0)
        maya.cmds.setAttr(marker_tfm + '.ty', 0.0)

        # Attributes
        attr_tx = api.Attribute(bundle_tfm + '.tx')
        attr_ty = api.Attribute(bundle_tfm + '.ty')

        # Frames
        frm_list = [
            api.Frame(1, primary=True)
        ]

        # Solver
        sol = api.Solver()
        sol.set_max_iterations(10)
        sol.set_solver_type(api.SOLVER_TYPE_LEVMAR)
        sol.set_verbose(True)
        sol.set_frame_list(frm_list)

        # Collection
        col = api.Collection()
        col.create_node('mySolveCollection')
        col.add_solver(sol)
        col.add_marker(mkr)
        col.add_attribute(attr_tx)
        col.add_attribute(attr_ty)

        # save the output
        path = self.get_data_path('test_solve_init_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        results = col.execute()

        # Ensure the values are correct
        for res in results:
            success = res.get_success()
            err = res.get_final_error()
            self.assertTrue(success)
        # assert self.approx_equal(maya.cmds.getAttr(bundle_tfm+'.tx'), -6.0)
        # assert self.approx_equal(maya.cmds.getAttr(bundle_tfm+'.ty'), 3.6)

        # save the output
        path = self.get_data_path('test_solve_init_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

    def test_marker_enable(self):
        start = 1
        end = 5

        # Set Time Range
        maya.cmds.playbackOptions(
            animationStartTime=start,
            minTime=start,
            animationEndTime=end,
            maxTime=end
        )

        # Camera
        cam_tfm = maya.cmds.createNode('transform',
                                       name='cam_tfm')
        cam_shp = maya.cmds.createNode('camera',
                                       name='cam_shp',
                                       parent=cam_tfm)
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty',  1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)
        cam = api.Camera(shape=cam_shp)

        # Bundle
        bnd = api.Bundle().create_node()
        bundle_tfm = bnd.get_node()
        maya.cmds.setAttr(bundle_tfm + '.tx', 5.5)
        maya.cmds.setAttr(bundle_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundle_tfm + '.tz', -25.0)
        assert api.get_object_type(bundle_tfm) == 'bundle'

        # calculate angle of view (AOV)
        f = maya.cmds.getAttr(cam_shp + '.focalLength')
        fbw = maya.cmds.getAttr(cam_shp + '.horizontalFilmAperture') * 25.4
        fbh = maya.cmds.getAttr(cam_shp + '.verticalFilmAperture') * 25.4
        aov = math.degrees(2.0 * math.atan(fbw * (0.5 / f)))

        # Set Camera Anim
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=start, value=-(aov/2),
                              inTangentType='linear', outTangentType='linear')
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=end, value=(aov/2),
                              inTangentType='linear', outTangentType='linear')

        # Marker
        mkr = api.Marker().create_node(cam=cam, bnd=bnd)
        marker_tfm = mkr.get_node()
        assert api.get_object_type(marker_tfm) == 'marker'
        maya.cmds.setKeyframe(marker_tfm, attribute='translateX', time=start, value=-0.5,
                              inTangentType='linear', outTangentType='linear')
        maya.cmds.setKeyframe(marker_tfm, attribute='translateX', time=end, value=0.5,
                              inTangentType='linear', outTangentType='linear')
        maya.cmds.setAttr(marker_tfm + '.ty', 0.0)

        maya.cmds.setKeyframe(marker_tfm, attribute='enable', time=1, value=1,
                              inTangentType='linear', outTangentType='linear')
        maya.cmds.setKeyframe(marker_tfm, attribute='enable', time=2, value=1,
                              inTangentType='linear', outTangentType='linear')
        maya.cmds.setKeyframe(marker_tfm, attribute='enable', time=3, value=0,
                              inTangentType='linear', outTangentType='linear')
        maya.cmds.setKeyframe(marker_tfm, attribute='enable', time=4, value=1,
                              inTangentType='linear', outTangentType='linear')
        maya.cmds.setKeyframe(marker_tfm, attribute='enable', time=5, value=1,
                              inTangentType='linear', outTangentType='linear')

        # Create Sphere
        sph_tfm, shp_node = maya.cmds.polySphere()
        maya.cmds.setAttr(sph_tfm + '.tx', -1.0)
        maya.cmds.setAttr(sph_tfm + '.ty', 1.0)
        maya.cmds.setAttr(sph_tfm + '.tz', -25.0)

        # Attributes
        attr_tx = api.Attribute(bundle_tfm + '.tx')
        attr_ty = api.Attribute(bundle_tfm + '.ty')

        # Frames
        frm_list = [
            api.Frame(1, primary=True),
            api.Frame(2, primary=True),
            api.Frame(3, primary=True),
            api.Frame(4, primary=True),
            api.Frame(5, primary=True)
        ]

        # Solver
        sol = api.Solver()
        sol.set_max_iterations(1000)
        sol.set_solver_type(api.SOLVER_TYPE_CMINPACK_LM)
        sol.set_verbose(True)
        sol.set_frame_list(frm_list)

        # Collection
        col = api.Collection()
        col.create_node('mySolveCollection')
        col.add_solver(sol)
        col.add_marker(mkr)
        col.add_attribute(attr_tx)
        col.add_attribute(attr_ty)

        # save the output
        path = self.get_data_path('test_solve_marker_enabled_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        results = col.execute()

        # Ensure the values are correct
        for res in results:
            success = res.get_success()
            err = res.get_final_error()
            print('error stats: ' + pprint.pformat(res.get_error_stats()))
            print('timer stats: ' + pprint.pformat(res.get_timer_stats()))
            print('solver stats: ' + pprint.pformat(res.get_solver_stats()))
            print('frame error list: ' + pprint.pformat(dict(res.get_frame_error_list())))
            print('marker error list: ' + pprint.pformat(dict(res.get_marker_error_list())))

            self.assertTrue(success)
            # self.assertGreater(0.001, err)
        # assert self.approx_equal(maya.cmds.getAttr(bundle_tfm+'.tx'), -6.0)
        # assert self.approx_equal(maya.cmds.getAttr(bundle_tfm+'.ty'), 3.6)

        # save the output
        path = self.get_data_path('test_solve_marker_enabled_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

    def test_per_frame(self):
        """
        Solve animated values, per-frame.
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
        cam = api.Camera(shape=cam_shp)

        # Bundle
        bnd = api.Bundle().create_node()
        bundle_tfm = bnd.get_node()
        maya.cmds.setAttr(bundle_tfm + '.tx', 5.5)
        maya.cmds.setAttr(bundle_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundle_tfm + '.tz', -25.0)
        assert api.get_object_type(bundle_tfm) == 'bundle'
        maya.cmds.setKeyframe(bundle_tfm,
                              attribute='translateX',
                              time=1, value=5.5,
                              inTangentType='linear',
                              outTangentType='linear')
        maya.cmds.setKeyframe(bundle_tfm,
                              attribute='translateY',
                              time=1, value=6.4,
                              inTangentType='linear',
                              outTangentType='linear')
        maya.cmds.setKeyframe(bundle_tfm,
                              attribute='translateZ',
                              time=1, value=-25.0,
                              inTangentType='linear',
                              outTangentType='linear')

        # Marker
        mkr = api.Marker().create_node(cam=cam, bnd=bnd)
        marker_tfm = mkr.get_node()
        assert api.get_object_type(marker_tfm) == 'marker'
        # maya.cmds.setAttr(marker_tfm + '.tx', 0.0)
        # maya.cmds.setAttr(marker_tfm + '.ty', 0.0)
        maya.cmds.setKeyframe(marker_tfm,
                              attribute='translateX',
                              time=1, value=-0.5,
                              inTangentType='linear',
                              outTangentType='linear')
        maya.cmds.setKeyframe(marker_tfm,
                              attribute='translateX',
                              time=5, value=0.5,
                              inTangentType='linear',
                              outTangentType='linear')
        maya.cmds.setKeyframe(marker_tfm,
                              attribute='translateY',
                              time=1, value=-0.5,
                              inTangentType='linear',
                              outTangentType='linear')
        maya.cmds.setKeyframe(marker_tfm,
                              attribute='translateY',
                              time=5, value=0.5,
                              inTangentType='linear',
                              outTangentType='linear')

        # Attributes
        attr_tx = api.Attribute(bundle_tfm + '.tx')
        attr_ty = api.Attribute(bundle_tfm + '.ty')

        # Frames
        frm_list = [
            api.Frame(1),
            api.Frame(2),
            api.Frame(3),
            api.Frame(4),
            api.Frame(5),
        ]

        # Solver
        sol_list = []
        for frm in frm_list:
            sol = api.Solver()
            sol.set_max_iterations(10)
            sol.set_solver_type(api.SOLVER_TYPE_CMINPACK_LM)
            sol.set_verbose(True)
            sol.set_frame_list([frm])
            sol_list.append(sol)

        # Collection
        col = api.Collection()
        col.create_node('mySolveCollection')
        col.add_solver_list(sol_list)
        col.add_marker(mkr)
        col.add_attribute(attr_tx)
        col.add_attribute(attr_ty)

        # save the output
        path = self.get_data_path('test_solve_per_frame_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        
        # Run solver!
        results = col.execute()

        # Ensure the values are correct
        for res in results:
            success = res.get_success()
            err = res.get_final_error()
            self.assertTrue(success)

        # save the output
        path = self.get_data_path('test_solve_per_frame_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

    # def test_opera_house(self):
    #     start = 0
    #     end = 41
    #
    #     # Set Time Range
    #     maya.cmds.playbackOptions(
    #         animationStartTime=start,
    #         minTime=start,
    #         animationEndTime=end,
    #         maxTime=end
    #     )
    #
    #     # Camera
    #     cam_tfm = maya.cmds.createNode('transform',
    #                                    name='cam_tfm')
    #     cam_shp = maya.cmds.createNode('camera',
    #                                    name='cam_shp',
    #                                    parent=cam_tfm)
    #     maya.cmds.setAttr(cam_tfm + '.rotateOrder', 2)  # zxy
    #     maya.cmds.setAttr(cam_shp + '.focalLength', 14)
    #     maya.cmds.setAttr(cam_shp + '.horizontalFilmAperture', 5.4187 / 25.4)
    #     maya.cmds.setAttr(cam_shp + '.verticalFilmAperture', 4.0640 / 25.4)
    #     cam = api.Camera(shape=cam_shp)
    #
    #     # Set Camera Keyframes
    #     cam_data = {
    #         '0': (-0.19889791581420663, 0.5591321634949238, 7.258789219735233, -1.9999507874015703, -0.3999999999999992, 0.0),
    #         '22': (-4.840404384215566, 0.7543627646977502, 6.3465857678271425, -3.0709513272069815, -36.91024116734281, 0.0),
    #         '41': (-8.584368967987194, 0.6990718939718145, 5.508167213044364, -1.4738793091011815, -54.30997787050599, 0.0)
    #     }
    #     for key in sorted(cam_data.keys()):
    #         frame = int(key)
    #         for i, attr in enumerate(['tx', 'ty', 'tz', 'rx', 'ry', 'rz']):
    #             value = cam_data[key][i]
    #             maya.cmds.setKeyframe(cam_tfm, attribute=attr, time=frame, value=value)
    #     maya.cmds.setKeyframe(cam_shp, attribute='focalLength', time=start, value=14.0)
    #     maya.cmds.setKeyframe(cam_shp, attribute='focalLength', time=end, value=14.0)
    #
    #     # Create image plane
    #     imgpl = maya.cmds.imagePlane(
    #         camera=cam_shp,
    #         fileName='/data/Tutorials/Footage/operahouse/frame_proxy.00.jpg'
    #     )
    #     maya.cmds.setAttr(imgpl[1] + '.useFrameExtension', 1)
    #     maya.cmds.setAttr(imgpl[1] + '.depth', 2000)
    #     maya.cmds.setAttr(imgpl[1] + '.frameCache', 0)
    #
    #     # Create Horizon Line
    #     cir = maya.cmds.circle(name='horizon', nrx=0, nry=1, nrz=0)
    #     maya.cmds.setAttr(cir[1] + ".radius", 3000)
    #
    #     # Create Cube for Opera House
    #     cube = maya.cmds.polyCube()
    #     maya.cmds.setAttr(cube[0] + ".ty", 0.5)
    #     maya.cmds.setAttr(cube[0] + ".sx", 2.68)
    #     maya.cmds.setAttr(cube[0] + ".sy", 0.91625416)
    #     maya.cmds.setAttr(cube[0] + ".sz", 1.68658365)
    #
    #     # Marker Group
    #     mkr_grp = maya.cmds.createNode('transform',
    #                                    name='markerGroup',
    #                                    parent=cam_tfm)
    #     mkr_scl = maya.cmds.createNode('mmMarkerScale')
    #     maya.cmds.connectAttr(cam_shp + '.focalLength', mkr_scl + '.focalLength')
    #     maya.cmds.connectAttr(cam_shp + '.cameraAperture', mkr_scl + '.cameraAperture')
    #     maya.cmds.connectAttr(cam_shp + '.filmOffset', mkr_scl + '.filmOffset')
    #     maya.cmds.connectAttr(mkr_scl + '.outScale', mkr_grp + '.scale')
    #
    #     # Bundle Group
    #     bnd_grp = maya.cmds.createNode('transform', name='bundleGroup')
    #     bnd_fg_grp = maya.cmds.createNode('transform', name='bundles_fg', parent=bnd_grp)
    #     bnd_bg_grp = maya.cmds.createNode('transform', name='bundles_bg', parent=bnd_grp)
    #
    #     # Load Markers
    #     fg_points = [
    #         'Track_01',
    #         'Track_02',
    #         'Track_05',
    #         'Track_06',
    #         'Track_08',
    #         'Track_09',
    #         'Track_10',
    #         'Track_11',
    #         'Track_19',
    #         'Track_20',
    #         'Track_21',
    #         'Track_22',
    #         'Track_23',
    #         'Track_23',
    #         'Track_24',
    #         'Track_25',
    #         'Track_26',
    #         'Track_27',
    #     ]
    #     bg_points = [
    #         'Track_03',
    #         'Track_04',
    #         'Track_07',
    #         'Track_12',
    #         'Track_13',
    #         'Track_14',
    #         'Track_15',
    #         'Track_16',
    #         'Track_17',
    #         'Track_18',
    #         'Track_28',
    #         'Track_29',
    #         'Track_30',
    #         'Track_31',
    #     ]
    #     bnd_positions = {
    #         'Track_23': (-0.7669678476654883, 0.704741253611808, 0.11480582185051777),
    #         'Track_14': (-6.096859889443822, 2.0552736121532478, -64.25806442305448),
    #         'Track_12': (45.11056705173852, 2.602519222901666, -43.16772737415769),
    #         'Track_13': (-11.331222134074189, -0.9161249928992397, -63.60343691220178),
    #         'Track_28': (12.97847320083373, 0.4908757961951475, -6.558878377403925),
    #         'Track_24': (-0.9577362080844809, 0.11947272894636578, -0.29860515939718035),
    #         'Track_25': (-0.3816240705349317, 0.09511793539283707, 0.5968218516602972),
    #         'Track_05': (-0.5497538933513093, 0.9121450956455763, 0.0689419211208016),
    #         'Track_06': (0.6442115545215732, 0.09146863102772763, 0.2698159600733472),
    #         'Track_02': (-1.1928085448379213, 0.06849164070024401, 0.741609523996595),
    #         'Track_17': (4.101733117764308, 0.4416977194116366, -20.775735845844235),
    #         'Track_16': (10.499779696104385, 2.4959245952203037, -61.65315035391216),
    #         'Track_21': (0.4422885021421483, 0.15594114410956195, -0.4586671394741284),
    #         'Track_18': (13.426726902476766, 2.208127581689255, -62.440721369338476),
    #         'Track_27': (-1.203371663768503, 0.07727436882970459, -0.34432924439358475),
    #         'Track_07': (24.82344439444535, 3.8981611004590917, -62.57148439047777),
    #         'Track_26': (-1.036542158437551, 0.1301250303434169, 0.6183349238312523),
    #         'Track_11': (-1.2868698932117608, 0.07508027422294668, -0.6923287330737453),
    #         'Track_09': (-1.1210978513200678, -0.0009538700668097195, -0.7481409812887209),
    #         'Track_20': (0.5370453995103619, 0.32144750391315535, 0.10037404391850258),
    #         'Track_08': (-0.35711469535141427, 0.8134673956410489, -0.8873816770491396),
    #         'Track_19': (-1.0708190128497155, 0.5849715587489718, 0.22909459498373133),
    #         'Track_10': (-0.8256010837265352, 0.04548785302325305, -0.6865934949556973),
    #         'Track_30': (12.219883964568602, 1.6676763053004873, -63.511794156133575),
    #         'Track_22': (-0.42435005852350927, 0.6386843510112235, -1.0271747982989685),
    #         'Track_31': (14.4768210901898, 1.5761955139450978, -40.10088917167338),
    #         'Track_15': (-0.17540615158899264, 2.5048877383268424, -64.10912011449136),
    #         'Track_29': (15.264518808431728, 1.8337698745022983, -62.076762425418536),
    #         'Track_03': (311.42375656555913, 16.402469194090923, -179.38329132993437),
    #         'Track_01': (-1.0890118590423876, 0.5109764471108498, -0.707187214616633),
    #         'Track_04': (209.73939576288353, 12.878819985707446, -150.30617721944793)
    #     }
    #     mkr_fg_grp = maya.cmds.createNode('transform',
    #                                       name='fg',
    #                                       parent=mkr_grp)
    #     mkr_bg_grp = maya.cmds.createNode('transform',
    #                                       name='bg',
    #                                       parent=mkr_grp)
    #     path = self.get_data_path('match_mover', 'loadmarker.rz2')
    #     mkr_data_list = marker_read.read(path)
    #     mkr_list = marker_read.create_nodes(mkr_data_list, cam=cam)
    #     mkr_fg_list = []
    #     mkr_bg_list = []
    #     for mkr in mkr_list:
    #         mkr_node = mkr.get_node()
    #         mgrp = mkr_grp
    #         bgrp = bnd_grp
    #         pos = None
    #         for name in fg_points:
    #             if name in mkr_node:
    #                 if name in bnd_positions:
    #                     pos = bnd_positions[name]
    #                 mgrp = mkr_fg_grp
    #                 bgrp = bnd_fg_grp
    #                 mkr_fg_list.append(mkr)
    #                 break
    #         for name in bg_points:
    #             if name in mkr_node:
    #                 if name in bnd_positions:
    #                     pos = bnd_positions[name]
    #                 mgrp = mkr_bg_grp
    #                 bgrp = bnd_bg_grp
    #                 mkr_bg_list.append(mkr)
    #                 break
    #         maya.cmds.parent(mkr_node, mgrp, relative=True)
    #
    #         bnd = mkr.get_bundle()
    #         bnd_node = bnd.get_node()
    #         maya.cmds.setAttr(bnd_node + '.tx', pos[0])
    #         maya.cmds.setAttr(bnd_node + '.ty', pos[1])
    #         maya.cmds.setAttr(bnd_node + '.tz', pos[2])
    #         bnd_node = maya.cmds.parent(bnd_node, bgrp, relative=True)[0]
    #         maya.cmds.setAttr(bnd_node + '.tx', lock=True)
    #         maya.cmds.setAttr(bnd_node + '.ty', lock=True)
    #         maya.cmds.setAttr(bnd_node + '.tz', lock=True)
    #
    #     # Frames
    #     # prim = [0, 22, 41]
    #     # sec = [3, 8, 12, 27, 33, 38]
    #     # prim = [0, 3, 8, 12, 22, 27, 33, 38, 41]
    #     frm_list = []
    #     frm = api.Frame(0, tags=['primary', '1', 'single001'])
    #     frm_list.append(frm)
    #
    #     frm = api.Frame(3, tags=['primary', '1', '2', 'single002'])
    #     frm_list.append(frm)
    #
    #     frm = api.Frame(8, tags=['primary', '2', '3', 'single003'])
    #     frm_list.append(frm)
    #
    #     frm = api.Frame(12, tags=['primary', '3', '4', 'single004'])
    #     frm_list.append(frm)
    #
    #     frm = api.Frame(22, tags=['primary', '4', '5', 'single005'])
    #     frm_list.append(frm)
    #
    #     frm = api.Frame(27, tags=['primary', '5', '6', 'single006'])
    #     frm_list.append(frm)
    #
    #     frm = api.Frame(33, tags=['primary', '6', '7', 'single007'])
    #     frm_list.append(frm)
    #
    #     frm = api.Frame(38, tags=['primary', '7', '8', 'single008'])
    #     frm_list.append(frm)
    #
    #     frm = api.Frame(41, tags=['primary', '8', 'single009'])
    #     frm_list.append(frm)
    #
    #     sol_list = []
    #
    #     # solve each frame
    #     for i in range(1, 9):
    #         sol = api.Solver()
    #         sol.set_max_iterations(10)
    #         sol.set_delta_factor(-0.01)
    #         sol.set_solver_type(api.SOLVER_TYPE_LEVMAR)
    #         sol.set_attributes_use_animated(True)
    #         sol.set_attributes_use_static(True)
    #         sol.set_frames_use_tags(['single00' + str(i+1)])
    #         sol.set_verbose(True)
    #         sol.set_frame_list(frm_list)
    #         sol_list.append(sol)
    #
    #     # solve each group
    #     for i in range(1, 9):
    #         sol = api.Solver()
    #         sol.set_max_iterations(10)
    #         sol.set_delta_factor(-0.01)
    #         sol.set_solver_type(api.SOLVER_TYPE_LEVMAR)
    #         sol.set_attributes_use_animated(True)
    #         sol.set_attributes_use_static(True)
    #         sol.set_frames_use_tags([str(i)])
    #         sol.set_verbose(True)
    #         sol.set_frame_list(frm_list)
    #         sol_list.append(sol)
    #
    #     # # solve each frame
    #     # for i in range(0, 41):
    #     #     sol = api.Solver()
    #     #     sol.set_max_iterations(10)
    #     #     sol.set_delta_factor(-0.01)
    #     #     sol.set_solver_type(api.SOLVER_TYPE_LEVMAR)
    #     #     sol.set_attributes_use_animated(True)
    #     #     sol.set_attributes_use_static(True)
    #     #     sol.set_verbose(True)
    #     #     frm = api.Frame(i)
    #     #     sol.set_frame_list([frm])
    #     #     sol_list.append(sol)
    #
    #     # # All primary frames together
    #     # sol = api.Solver()
    #     # sol.set_max_iterations(10)
    #     # sol.set_delta_factor(-0.01)
    #     # sol.set_solver_type(api.SOLVER_TYPE_LEVMAR)
    #     # sol.set_attributes_use_animated(True)
    #     # sol.set_attributes_use_static(True)
    #     # sol.set_frames_use_tags(['primary'])
    #     # sol.set_verbose(False)
    #     # sol.set_frame_list(frm_list)
    #     # sol_list.append(sol)
    #
    #     # Collection
    #     col = api.Collection()
    #     col.create('mySolverCollection')
    #     col.add_solver_list(sol_list)
    #
    #     # Add markers
    #     col.add_marker_list(mkr_fg_list)
    #
    #     # Attributes
    #     attr_cam_tx = api.Attribute(cam_tfm + '.tx')
    #     attr_cam_ty = api.Attribute(cam_tfm + '.ty')
    #     attr_cam_tz = api.Attribute(cam_tfm + '.tz')
    #     # attr_cam_rx = api.Attribute(cam_tfm + '.rx')
    #     # attr_cam_ry = api.Attribute(cam_tfm + '.ry')
    #     # attr_cam_rz = api.Attribute(cam_tfm + '.rz')
    #     # attr_cam_focal = api.Attribute(cam_shp + '.focalLength')
    #     # attr_cam_focal.set_min_value(10.0)
    #     # attr_cam_focal.set_max_value(20.0)
    #     col.add_attribute(attr_cam_tx)
    #     col.add_attribute(attr_cam_ty)
    #     col.add_attribute(attr_cam_tz)
    #     # col.add_attribute(attr_cam_rx)
    #     # col.add_attribute(attr_cam_ry)
    #     # col.add_attribute(attr_cam_rz)
    #     # col.add_attribute(attr_cam_focal)
    #
    #     # for mkr in mkr_list:
    #     #     bnd = mkr.get_bundle()
    #     #     bnd_node = bnd.get_node()
    #     #     attr_tx = api.Attribute(bnd_node + '.tx')
    #     #     attr_ty = api.Attribute(bnd_node + '.ty')
    #     #     attr_tz = api.Attribute(bnd_node + '.tz')
    #     #     col.add_attribute(attr_tx)
    #     #     col.add_attribute(attr_ty)
    #     #     col.add_attribute(attr_tz)
    #
    #     # save the output
    #     path = self.get_data_path('test_solve_opera_house_before.ma')
    #     maya.cmds.file(rename=path)
    #     maya.cmds.file(save=True, type='mayaAscii', force=True)
    #
    #     # Run solver!
    #     results = col.execute()
    #
    #     # Ensure the values are correct
    #     for res in results:
    #         success = res.get_success()
    #         err = res.get_final_error()
    #         print 'success', success
    #         print 'err', err
    #
    #     # save the output
    #     path = self.get_data_path('test_solve_opera_house_after.ma')
    #     maya.cmds.file(rename=path)
    #     maya.cmds.file(save=True, type='mayaAscii', force=True)


if __name__ == '__main__':
    prog = unittest.main()
