# Copyright (C) 2022 David Cattermole.
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
The camera solver - allows solving static and animated attributes.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.logger

import mmSolver.utils.python_compat as pycompat
import mmSolver.utils.camera as cam_utils
import mmSolver._api.constant as const
import mmSolver._api.nodefilter as nodefilter
import mmSolver._api.frame as frame
import mmSolver._api.excep as excep
import mmSolver._api.bundle as bundle
import mmSolver._api.camera as camera
import mmSolver._api.attribute as attribute
import mmSolver._api.collection as collection
import mmSolver._api.solverbase as solverbase
import mmSolver._api.solverutils as solverutils
import mmSolver._api.action as api_action


LOG = mmSolver.logger.get_logger()


def _compile_camera_solve(
    col,
    mkr_list,
    attr_list,
    root_frames,
    start_frame,
    end_frame,
    origin_frame,
    scene_scale,
    bundle_iter_num,
    root_iter_num,
    anim_iter_num,
    adjust_every_n_poses,
    triangulate_bundles,
    solver_version,
    solver_type,
    precomputed_data,
    withtest,
    verbose,
):
    """
    Compile actions for solving a camera from scratch.

    :param withtest:
        Compile the test/validation Action, as well as the solve Action?
    :type withtest: bool

    :param verbose:
        Print out more detail to 'stderr'.
    :type verbose: bool

    :return:
        Yields two Actions at each iteration; first Action is for
        solving, second Action is to validate the inputs given.
    :rtype: (Action, Action or None)
    """
    assert isinstance(col, collection.Collection)
    assert isinstance(bundle_iter_num, int)
    assert isinstance(root_iter_num, int)
    assert isinstance(anim_iter_num, int)
    assert isinstance(scene_scale, float)
    assert isinstance(start_frame, int)
    assert isinstance(end_frame, int)
    assert isinstance(adjust_every_n_poses, int)
    assert isinstance(triangulate_bundles, bool)
    assert isinstance(solver_version, int)
    assert isinstance(solver_type, int)
    assert isinstance(withtest, bool)
    assert isinstance(verbose, bool)
    assert solver_version in const.SOLVER_VERSION_LIST
    assert solver_type in const.SOLVER_TYPE_LIST

    # Find the camera node in the attr_list.
    attr_nodes = [x.get_node() for x in attr_list]
    attr_nodes = [x for x in attr_nodes if x is not None]
    filtered_nodes = nodefilter.filter_nodes_into_categories(attr_nodes)
    cam_nodes = filtered_nodes[const.OBJECT_TYPE_CAMERA]
    lens_nodes = set(filtered_nodes[const.OBJECT_TYPE_LENS])
    assert len(cam_nodes) > 0

    cam_tfm, cam_shp = cam_utils.get_camera(cam_nodes[0])
    cam = camera.Camera(shape=cam_shp)
    assert isinstance(cam, camera.Camera)
    cam_tfm = cam.get_transform_node()
    cam_shp = cam.get_shape_node()

    # Otherwise the camera transform attributes may not be animated
    # and the solver will get very confused and fail to solve
    # correctly.
    cam_tfm_node_attrs = [
        attribute.Attribute(node=cam_tfm, attr='translateX'),
        attribute.Attribute(node=cam_tfm, attr='translateY'),
        attribute.Attribute(node=cam_tfm, attr='translateZ'),
        attribute.Attribute(node=cam_tfm, attr='rotateX'),
        attribute.Attribute(node=cam_tfm, attr='rotateY'),
        attribute.Attribute(node=cam_tfm, attr='rotateZ'),
    ]
    for attr in cam_tfm_node_attrs:
        if attr.is_animated() is False:
            attr_name = attr.get_attr()
            maya.cmds.setKeyframe(cam_tfm, attribute=attr_name, time=start_frame)
        assert attr.get_state() == const.ATTR_STATE_ANIMATED

    cam_shp_node_attrs = [x.get_name() for x in attr_list if x.get_node() == cam_shp]
    lens_node_attrs = [x.get_name() for x in attr_list if x.get_node() in lens_nodes]

    mkr_nodes = [x.get_node() for x in mkr_list]
    mkr_nodes = [x for x in mkr_nodes if x is not None]

    # Ensure all Markers have bundles connected.
    for mkr in mkr_list:
        bnd = mkr.get_bundle()
        if bnd is None:
            bnd = bundle.Bundle().create_node()
            mkr.set_bundle(bnd)

    # Locked bundle translate attributes are not supported.
    for mkr in mkr_list:
        bnd = mkr.get_bundle()
        assert isinstance(bnd, bundle.Bundle)
        bnd_node = bnd.get_node()
        assert bnd_node is not None
        x = attribute.Attribute(node=bnd_node, attr='translateX')
        y = attribute.Attribute(node=bnd_node, attr='translateY')
        z = attribute.Attribute(node=bnd_node, attr='translateZ')
        assert x.get_state() == const.ATTR_STATE_STATIC
        assert y.get_state() == const.ATTR_STATE_STATIC
        assert z.get_state() == const.ATTR_STATE_STATIC

    col_node = col.get_node()

    func = 'mmSolver._api.solvercamerautils.camera_solve'
    args = [
        col_node,
        cam_tfm,
        cam_shp,
        mkr_nodes,
        cam_shp_node_attrs,
        lens_node_attrs,
        root_frames,
        start_frame,
        end_frame,
        origin_frame,
        scene_scale,
        bundle_iter_num,
        root_iter_num,
        anim_iter_num,
        adjust_every_n_poses,
        solver_version,
        solver_type,
    ]
    kwargs = {}
    action = api_action.Action(func=func, args=args, kwargs=kwargs)
    yield action, None


class SolverCamera(solverbase.SolverBase):
    """
    The camera solver for mmSolver.

    This solver is designed to solve a camera from scratch, with only
    2D Markers as input. The solver assumes the camera is not nodal
    and has parallax. The camera translations, rotations, focal length
    and lens distortion can be calculated by this solver.

    This solver requires that the camera and bundles are fully
    unlocked - attributes will be calculated automatically.

    Parameters for solver:

    - Frame Range - with options:

      - "Single Frame"
      - "Time Slider (Inner)"
      - "Time Slider (Outer)"
      - "Custom"

    - User Frames - A list of integer frame numbers.

    - Root Frames - An semi-automatic list of integer frame numbers.

    - Choices of what to solve.

      - "Solve Everything at Once" option - On or Off
      - "Solve Root Frames Only" option - On or Off

    - Scene Scale and Orientation options.

      - Origin Frame - The frame to set the camera at the origin.
      - Scene Scale - How large will the entire camera path be?
    """

    def __init__(self, *args, **kwargs):
        super(SolverCamera, self).__init__(*args, **kwargs)
        return

    ############################################################################

    def get_solver_version(self):
        """
        Get 'Solver Version' value.

        :rtype: int
        """
        return self._data.get('solver_version', const.SOLVER_VERSION_DEFAULT)

    def set_solver_version(self, value):
        """
        Set 'Solver Version' value.

        :param value: Value to be set.
        :type value: int
        """
        assert isinstance(value, int)
        self._data['solver_version'] = value

    ############################################################################

    def get_solver_type(self):
        """
        Get 'Solver Type' value.

        :rtype: int
        """
        return self._data.get('solver_type', const.SOLVER_CAM_SOLVER_TYPE_DEFAULT_VALUE)

    def set_solver_type(self, value):
        """
        Set 'Solver Type' value.

        :param value: Value to be set.
        :type value: int
        """
        assert isinstance(value, int)
        self._data['solver_type'] = value

    ############################################################################

    def get_bundle_iteration_num(self):
        """
        :rtype: bool
        """
        return self._data.get(
            'bundle_iteration_num', const.SOLVER_CAM_BUNDLE_ITERATION_NUM_DEFAULT_VALUE
        )

    def set_bundle_iteration_num(self, value):
        """
        :param value: Value to be set.
        :type value: int
        """
        assert isinstance(value, pycompat.INT_TYPES)
        assert value > 0
        self._data['bundle_iteration_num'] = value

    def get_root_iteration_num(self):
        """
        :rtype: bool
        """
        return self._data.get(
            'root_iteration_num', const.SOLVER_STD_ROOT_ITERATION_NUM_DEFAULT_VALUE
        )

    def set_root_iteration_num(self, value):
        """
        :param value: Value to be set.
        :type value: int
        """
        assert isinstance(value, pycompat.INT_TYPES)
        assert value > 0
        self._data['root_iteration_num'] = value

    def get_anim_iteration_num(self):
        """
        :rtype: int
        """
        return self._data.get(
            'anim_iteration_num', const.SOLVER_STD_ANIM_ITERATION_NUM_DEFAULT_VALUE
        )

    def set_anim_iteration_num(self, value):
        """
        :param value: Value to be set.
        :type value: int
        """
        assert isinstance(value, pycompat.INT_TYPES)
        assert value > 0
        self._data['anim_iteration_num'] = value

    ############################################################################

    def get_frame_list(self):
        """
        Get frame objects attached to the solver.

        :return: frame objects.
        :rtype: list of frame.Frame
        """
        frame_list_data = self._data.get('frame_list')
        if frame_list_data is None:
            return []
        frm_list = []
        for f in frame_list_data:
            frm = frame.Frame(0)
            frm.set_data(f)  # Override the frame number
            frm_list.append(frm)
        return frm_list

    def get_frame_list_length(self):
        """
        Return the number of frames in the frame list.

        :rtype: int
        """
        return len(self.get_frame_list())

    def add_frame(self, frm):
        assert isinstance(frm, frame.Frame)
        key = 'frame_list'
        frm_list_data = self._data.get(key)
        if frm_list_data is None:
            frm_list_data = []

        # check we won't get a double up.
        add_frm_data = frm.get_data()
        for frm_data in frm_list_data:
            if frm_data.get('number') == add_frm_data.get('number'):
                msg = 'Frame already added to the solver, cannot add again: {0}'
                msg = msg.format(add_frm_data)
                raise excep.NotValid(msg)

        frm_list_data.append(add_frm_data)
        self._data[key] = frm_list_data
        return

    def add_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        for frm in frm_list:
            self.add_frame(frm)
        return

    def remove_frame(self, frm):
        assert isinstance(frm, frame.Frame)
        key = 'frame_list'
        frm_list_data = self._data.get(key)
        if frm_list_data is None:
            # Nothing to remove, initialise the data structure.
            self._data[key] = []
            return
        found_index = -1
        rm_frm_data = frm.get_data()
        for i, frm_data in enumerate(frm_list_data):
            if frm_data.get('number') == rm_frm_data.get('number'):
                found_index = i
                break
        if found_index != -1:
            del frm_list_data[found_index]
        self._data[key] = frm_list_data
        return

    def remove_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        for frm in frm_list:
            self.remove_frame(frm)
        return

    def set_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        self.clear_frame_list()
        self.add_frame_list(frm_list)
        return

    def clear_frame_list(self):
        key = 'frame_list'
        self._data[key] = []
        return

    ############################################################################

    def get_root_frame_list(self):
        """
        Get frame objects attached to the solver.

        :return: frame objects.
        :rtype: list of frame.Frame
        """
        frame_list_data = self._data.get('root_frame_list')
        if frame_list_data is None:
            return []
        frm_list = []
        for f in frame_list_data:
            frm = frame.Frame(0)
            frm.set_data(f)  # Override the frame number
            frm_list.append(frm)
        return frm_list

    def get_root_frame_list_length(self):
        """
        Return the number of frames in the root frame list.

        :rtype: int
        """
        return len(self.get_root_frame_list())

    def add_root_frame(self, frm):
        assert isinstance(frm, frame.Frame)
        key = 'root_frame_list'
        frm_list_data = self._data.get(key)
        if frm_list_data is None:
            frm_list_data = []

        # check we won't get a double up.
        add_frm_data = frm.get_data()
        for frm_data in frm_list_data:
            if frm_data.get('number') == add_frm_data.get('number'):
                msg = 'Frame already added to SolverCamera, cannot add again: {0}'
                msg = msg.format(add_frm_data)
                raise excep.NotValid(msg)

        frm_list_data.append(add_frm_data)
        self._data[key] = frm_list_data
        return

    def add_root_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        for frm in frm_list:
            self.add_root_frame(frm)
        return

    def remove_root_frame(self, frm):
        assert isinstance(frm, frame.Frame)
        key = 'root_frame_list'
        frm_list_data = self._data.get(key)
        if frm_list_data is None:
            # Nothing to remove, initialise the data structure.
            self._data[key] = []
            return
        found_index = -1
        rm_frm_data = frm.get_data()
        for i, frm_data in enumerate(frm_list_data):
            if frm_data.get('number') == rm_frm_data.get('number'):
                found_index = i
                break
        if found_index != -1:
            del frm_list_data[found_index]
        self._data[key] = frm_list_data
        return

    def remove_root_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        for frm in frm_list:
            self.remove_root_frame(frm)
        return

    def set_root_frame_list(self, frm_list):
        assert isinstance(frm_list, list)
        self.clear_frame_list()
        self.add_root_frame_list(frm_list)
        return

    def clear_root_frame_list(self):
        key = 'root_frame_list'
        self._data[key] = []
        return

    ############################################################################

    def get_origin_frame(self):
        """
        Get Origin Frame value.

        :rtype: Frame or None
        """
        value = self._data.get('origin_frame')
        frm = None
        if value is not None:
            frm = frame.Frame(value)
        return frm

    def set_origin_frame(self, value):
        """
        Set Origin Frame value.

        :param value: Value to be set.
        :type value: Frame or int
        """
        assert isinstance(value, (frame.Frame, int, pycompat.LONG_TYPE))
        number = value
        if isinstance(value, frame.Frame):
            number = value.get_number()
        self._data['origin_frame'] = number

    ############################################################################

    def get_triangulate_bundles(self):
        """
        :rtype: bool
        """
        return self._data.get(
            'triangulate_bundles', const.SOLVER_CAM_TRIANGULATE_BUNDLES_DEFAULT_VALUE
        )

    def set_triangulate_bundles(self, value):
        """
        :param value: Value to be set.
        :type value: bool or int
        """
        assert isinstance(value, (bool, int, pycompat.LONG_TYPE))
        self._data['triangulate_bundles'] = bool(value)

    ############################################################################

    def get_adjust_every_n_poses(self):
        """
        :rtype: bool
        """
        return self._data.get(
            'adjust_every_n_poses', const.SOLVER_CAM_ADJUST_EVERY_N_POSES_DEFAULT_VALUE
        )

    def set_adjust_every_n_poses(self, value):
        """
        :param value: Value to be set.
        :type value: bool or int
        """
        assert isinstance(value, (bool, int, pycompat.LONG_TYPE))
        self._data['adjust_every_n_poses'] = bool(value)

    ############################################################################

    def get_scene_scale(self):
        """
        :rtype: float
        """
        return self._data.get('scene_scale', const.SOLVER_CAM_SCENE_SCALE_DEFAULT_VALUE)

    def set_scene_scale(self, value):
        """
        :param value: Value to be set.
        :type value: float
        """
        assert isinstance(value, float)
        assert value > 0.0
        self._data['scene_scale'] = value

    ############################################################################

    def get_solve_focal_length(self):
        """
        :rtype: bool
        """
        return self._data.get(
            'solve_focal_length', const.SOLVER_CAM_SOLVE_FOCAL_LENGTH_DEFAULT_VALUE
        )

    def set_solve_focal_length(self, value):
        """
        :param value: Value to be set.
        :type value: bool or int
        """
        assert isinstance(value, (bool, int, pycompat.LONG_TYPE))
        self._data['solve_focal_length'] = bool(value)

    ############################################################################

    def get_solve_lens_distortion(self):
        """
        :rtype: bool
        """
        return self._data.get(
            'solve_lens_distortion',
            const.SOLVER_CAM_SOLVE_LENS_DISTORTION_DEFAULT_VALUE,
        )

    def set_solve_lens_distortion(self, value):
        """
        :param value: Value to be set.
        :type value: bool or int
        """
        assert isinstance(value, (bool, int, pycompat.LONG_TYPE))
        self._data['solve_lens_distortion'] = bool(value)

    ############################################################################

    def compile(self, col, mkr_list, attr_list, withtest=False):
        # Options to affect how the solve is constructed.
        solver_version = self.get_solver_version()
        solver_type = self.get_solver_type()
        bundle_iter_num = self.get_bundle_iteration_num()
        root_iter_num = self.get_root_iteration_num()
        anim_iter_num = self.get_anim_iteration_num()
        root_frame_list = self.get_root_frame_list()
        frame_list = self.get_frame_list()
        origin_frame = self.get_origin_frame()
        scene_scale = self.get_scene_scale()
        adjust_every_n_poses = self.get_adjust_every_n_poses()
        triangulate_bundles = self.get_triangulate_bundles()
        solve_focal_length = self.get_solve_focal_length()
        solve_lens_distortion = self.get_solve_lens_distortion()

        attr_list = solverutils.filter_attr_list(
            attr_list,
            use_camera_intrinsics=solve_focal_length,
            use_lens_distortion=solve_lens_distortion,
        )

        origin_frame = origin_frame.get_number()
        root_frames = [x.get_number() for x in root_frame_list]
        frames = [x.get_number() for x in frame_list]
        start_frame = min(frames)
        end_frame = max(frames)

        withtest = True
        verbose = True
        precomputed_data = self.get_precomputed_data()

        generator = _compile_camera_solve(
            col,
            mkr_list,
            attr_list,
            root_frames,
            start_frame,
            end_frame,
            origin_frame,
            scene_scale,
            bundle_iter_num,
            root_iter_num,
            anim_iter_num,
            adjust_every_n_poses,
            triangulate_bundles,
            solver_version,
            solver_type,
            precomputed_data,
            withtest,
            verbose,
        )
        for action, vaction in generator:
            yield action, vaction
        return
