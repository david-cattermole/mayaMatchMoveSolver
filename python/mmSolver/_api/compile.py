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
Compile nods into a set of actions to be performed.
"""

import collections

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver._api.constant as const
import mmSolver._api.excep as excep
import mmSolver._api.utils as api_utils
import mmSolver._api.action as api_action
import mmSolver._api.solverbase as solverbase
import mmSolver._api.frame as frame
import mmSolver._api.marker as marker
import mmSolver._api.attribute as attribute

LOG = mmSolver.logger.get_logger()


def markersAndCameras_compile_flags(mkr_list):
    # Get Markers and Cameras
    added_cameras = []
    markers = []
    cameras = []
    for mkr in mkr_list:
        assert isinstance(mkr, marker.Marker)
        mkr_node = mkr.get_node()
        assert isinstance(mkr_node, basestring)
        bnd = mkr.get_bundle()
        if bnd is None:
            msg = 'Cannot find bundle from marker, skipping; mkr_node={0}'
            msg = msg.format(repr(mkr_node))
            LOG.warning(msg)
            continue
        bnd_node = bnd.get_node()
        if bnd_node is None:
            msg = 'Bundle node is invalid, skipping; mkr_node={0}'
            msg = msg.format(repr(mkr_node))
            LOG.warning(msg)
            continue
        cam = mkr.get_camera()
        if cam is None:
            msg = 'Cannot find camera from marker; mkr={0}'
            msg = msg.format(mkr.get_node())
            LOG.warning(msg)
        cam_tfm_node = cam.get_transform_node()
        cam_shp_node = cam.get_shape_node()
        assert isinstance(cam_tfm_node, basestring)
        assert isinstance(cam_shp_node, basestring)
        markers.append((mkr_node, cam_shp_node, bnd_node))
        if cam_shp_node not in added_cameras:
            cameras.append((cam_tfm_node, cam_shp_node))
            added_cameras.append(cam_shp_node)
    return markers, cameras


ATTR_SOLVER_TYPE_REGULAR = 'regular'
ATTR_SOLVER_TYPE_BUNDLE_TRANSFORM = 'bundle_transform'
ATTR_SOLVER_TYPE_CAMERA_TRANSFORM = 'camera_transform'
ATTR_SOLVER_TYPE_CAMERA_INTRINSIC = 'camera_intrinsic'
ATTR_SOLVER_TYPE_LENS_DISTORTION = 'lens_distortion'

BUNDLE_TRANSFORM_ATTR_NAME_LIST = [
    'translateX', 'translateY', 'translateZ',
]
CAMERA_INTRINSIC_ATTR_NAME_LIST = [
    'focalLength',
    'horizontalFilmAperture',
    'verticalFilmAperture',
]
CAMERA_TRANSFORM_ATTR_NAME_LIST = [
    'translateX', 'translateY', 'translateZ',
    'rotateX', 'rotateY', 'rotateZ',
    'scaleX', 'scaleY', 'scaleZ',
]


def _get_attribute_solver_type(attr):
    """
    Get the type of Attribute, one value of ATTR_SOLVER_TYPE_*.

    :param attr: The Attribute to query.
    :type attr: Attribute

    :return: One of the ATTR_SOLVER_TYPE_* values.
    :rtype: str
    """
    assert isinstance(attr, attribute.Attribute)
    attr_solve_type = ATTR_SOLVER_TYPE_REGULAR

    node = attr.get_node(full_path=True)
    name = attr.get_attr(long_name=True)
    obj_type = api_utils.get_object_type(node)

    if obj_type == const.OBJECT_TYPE_BUNDLE:
        if name in BUNDLE_TRANSFORM_ATTR_NAME_LIST:
            attr_solve_type = ATTR_SOLVER_TYPE_BUNDLE_TRANSFORM

    elif obj_type == const.OBJECT_TYPE_CAMERA:
        if name in CAMERA_INTRINSIC_ATTR_NAME_LIST:
            attr_solve_type = ATTR_SOLVER_TYPE_CAMERA_INTRINSIC
        if name in CAMERA_TRANSFORM_ATTR_NAME_LIST:
            attr_solve_type = ATTR_SOLVER_TYPE_CAMERA_TRANSFORM
    return attr_solve_type


def categorise_attributes(attr_list):
    assert isinstance(attr_list, (list, tuple))
    categories = {
        'regular': collections.defaultdict(list),
        'bundle_transform': collections.defaultdict(list),
        'camera_transform': collections.defaultdict(list),
        'camera_intrinsic': collections.defaultdict(list),
        'lens_distortion': collections.defaultdict(list),
    }
    for attr in attr_list:
        assert isinstance(attr, attribute.Attribute)
        node = attr.get_node(full_path=True)
        attr_solver_type = _get_attribute_solver_type(attr)
        if attr_solver_type == ATTR_SOLVER_TYPE_REGULAR:
            key = ATTR_SOLVER_TYPE_REGULAR
        elif attr_solver_type == ATTR_SOLVER_TYPE_BUNDLE_TRANSFORM:
            key = ATTR_SOLVER_TYPE_BUNDLE_TRANSFORM
        elif attr_solver_type == ATTR_SOLVER_TYPE_CAMERA_TRANSFORM:
            key = ATTR_SOLVER_TYPE_CAMERA_TRANSFORM
        elif attr_solver_type == ATTR_SOLVER_TYPE_CAMERA_INTRINSIC:
            key = ATTR_SOLVER_TYPE_CAMERA_INTRINSIC
        elif attr_solver_type == ATTR_SOLVER_TYPE_LENS_DISTORTION:
            key = ATTR_SOLVER_TYPE_LENS_DISTORTION
        else:
            raise excep.NotValid
        categories[key][node].append(attr)
    return categories


def attributes_compile_flags(attr_list, use_animated, use_static):
    # Get Attributes
    attrs = []
    for attr in attr_list:
        assert isinstance(attr, attribute.Attribute)
        if attr.is_locked():
            continue
        name = attr.get_name()
        node_name = attr.get_node()
        attr_name = attr.get_attr()

        # If the user does not specify a min/max value then we get it
        # from Maya directly, if Maya doesn't have one, we leave
        # min/max_value as None and pass it to the mmSolver command
        # indicating there is no bound.
        min_value = attr.get_min_value()
        max_value = attr.get_max_value()
        if min_value is None:
            min_exists = maya.cmds.attributeQuery(
                attr_name,
                node=node_name,
                minExists=True,
            )
            if min_exists:
                min_value = maya.cmds.attributeQuery(
                    attr_name,
                    node=node_name,
                    minimum=True,
                )
                if len(min_value) == 1:
                    min_value = min_value[0]
                else:
                    msg = 'Cannot handle attributes with multiple '
                    msg += 'minimum values; node={0} attr={1}'
                    msg = msg.format(node_name, attr_name)
                    raise excep.NotValid(msg)

        if max_value is None:
            max_exists = maya.cmds.attributeQuery(
                attr_name,
                node=node_name,
                maxExists=True,
            )
            if max_exists is True:
                max_value = maya.cmds.attributeQuery(
                    attr_name,
                    node=node_name,
                    maximum=True,
                )
                if len(max_value) == 1:
                    max_value = max_value[0]
                else:
                    msg = 'Cannot handle attributes with multiple '
                    msg += 'maximum values; node={0} attr={1}'
                    msg = msg.format(node_name, attr_name)
                    raise excep.NotValid(msg)

        # Scale and Offset
        scale_value = None
        offset_value = None
        attr_type = maya.cmds.attributeQuery(
            attr_name,
            node=node_name,
            attributeType=True)
        if attr_type.endswith('Angle'):
            offset_value = 360.0

        animated = attr.is_animated()
        static = attr.is_static()
        use = False
        if use_animated and animated is True:
            use = True
        if use_static and static is True:
            use = True
        if use is True:
            attrs.append(
                (name,
                 str(min_value),
                 str(max_value),
                 str(offset_value),
                 str(scale_value))
            )
    return attrs


def frames_compile_flags(frm_list, frame_use_tags):
    """
    Create a list of frame numbers using Frame objects and some rules.

    :param frm_list:
    :param frame_use_tags:
    :return:
    """
    frames = []
    for frm in frm_list:
        num = frm.get_number()
        tags = frm.get_tags()
        use = False
        if len(frame_use_tags) > 0 and len(tags) > 0:
            for tag in frame_use_tags:
                if tag in tags:
                    use = True
                    break
        else:
            use = True
        if use is True:
            frames.append(num)
    return frames


def collection_compile(col_node, sol_list, mkr_list, attr_list,
                       prog_fn=None,
                       status_fn=None):
    """
    Take the data in this class and compile it into actions to run.

    :return: list of SolverActions.
    :rtype: [SolverAction, ..]
    """
    action_list = []
    if len(sol_list) == 0:
        msg = 'Collection is not valid, no Solvers given; '
        msg += 'collection={0}'
        msg = msg.format(repr(col_node))
        raise excep.NotValid(msg)

    # Check Solvers
    sol_enabled_list = [sol for sol in sol_list
                        if sol.get_enabled() is True]
    if len(sol_enabled_list) == 0:
        msg = 'Collection is not valid, no enabled Solvers given; '
        msg += 'collection={0}'
        msg = msg.format(repr(col_node))
        raise excep.NotValid(msg)

    # Check Markers
    if len(mkr_list) == 0:
        msg = 'Collection is not valid, no Markers given; collection={0}'
        msg = msg.format(repr(col_node))
        raise excep.NotValid(msg)

    # Check Attributes
    if len(attr_list) == 0:
        msg = 'Collection is not valid, no Attributes given; collection={0}'
        msg = msg.format(repr(col_node))
        raise excep.NotValid(msg)

    # Compile all the solvers
    msg = 'Collection is not valid, failed to compile solver;'
    msg += ' collection={0}'
    msg = msg.format(repr(col_node))
    for i, sol in enumerate(sol_enabled_list):
        assert isinstance(sol, solverbase.SolverBase)
        # if sol.get_frame_list_length() == 0:
        #     msg = 'Collection is not valid, no frames to solve;'
        #     msg += ' collection={0}'
        #     msg = msg.format(repr(col_node))
        #     raise excep.NotValid(msg)

        actions = sol.compile(mkr_list, attr_list)
        assert isinstance(actions, (tuple, list))
        for action in actions:
            if not isinstance(action, api_action.Action):
                raise excep.NotValid(msg)
            assert action.func is not None
            assert action.args is not None
            assert action.kwargs is not None
            action_list.append(action)
    if len(action_list) == 0:
        raise excep.NotValid(msg)
    # LOG.warn('actions: %r', action_list)
    return action_list


