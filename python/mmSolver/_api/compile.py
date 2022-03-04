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
Compile nodes into a set of actions to be performed.

Compiling is performed with Python generators, yielding values, rather
than computing a full list. Generators are used to speed up the
compilation process by being able produce validity results quickly
without waiting for the full compilation only to find an error on the
first Action.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.utils.python_compat as pycompat
import mmSolver._api.constant as const
import mmSolver._api.excep as excep
import mmSolver._api.utils as api_utils
import mmSolver._api.action as api_action
import mmSolver._api.solverbase as solverbase
import mmSolver._api.marker as marker
import mmSolver._api.attribute as attribute

LOG = mmSolver.logger.get_logger()


class DictGetOrCall(dict):

    """Wrapper around a normal 'dict', but we treat the dict as a cache,
    and if the cache is empty we will call a function to get the value.
    """

    def get_or_call(self, key, func):
        """
        Get a key from a cache, or call a function to get the value.

        :param key: Key string to look up into the dict.
        :type key: str

        :param func: Function to call, the function does not expect any
            arguments.
        :type func: callable
        """
        value = self.get(key)
        if value is None:
            assert callable(func) is True
            value = func()
        return value


def _get_bundle_node_name_from_marker(mkr):
    assert isinstance(mkr, marker.Marker)
    bnd = mkr.get_bundle()
    if bnd is None:
        LOG.warn(
            'Cannot find bundle from marker, skipping; mkr_node=%r',
            mkr.get_node())
        return None
    bnd_node = bnd.get_node()
    if bnd_node is None:
        LOG.warn(
            'Bundle node is invalid, skipping; mkr_node=%r',
            mkr.get_node())
        return None
    return bnd_node


def _get_camera_nodes_from_marker(mkr):
    cam = mkr.get_camera()
    if cam is None:
        LOG.warn(
            'Cannot find camera from marker; mkr=%r',
            mkr.get_node())
        return None
    cam_tfm_node = cam.get_transform_node()
    cam_shp_node = cam.get_shape_node()
    assert isinstance(cam_tfm_node, pycompat.TEXT_TYPE)
    assert isinstance(cam_shp_node, pycompat.TEXT_TYPE)
    return cam_tfm_node, cam_shp_node


def _get_attribute_type_from_attr(node_name, attr_name):
    return maya.cmds.attributeQuery(
        attr_name,
        node=node_name,
        attributeType=True)


def _get_maya_min_exists_from_attr(node_name, attr_name):
    return maya.cmds.attributeQuery(
        attr_name,
        node=node_name,
        minExists=True)


def _get_maya_min_value_from_attr(node_name, attr_name):
    return maya.cmds.attributeQuery(
        attr_name,
        node=node_name,
        minimum=True)


def _get_maya_max_exists_from_attr(node_name, attr_name):
    return maya.cmds.attributeQuery(
        attr_name,
        node=node_name,
        maxExists=True)


def _get_maya_max_value_from_attr(node_name, attr_name):
    return maya.cmds.attributeQuery(
        attr_name,
        node=node_name,
        maximum=True)


def get_markers_static_values(mkr_list):
    """
    Get static values from markers.

    This is intended to be used as cached values for future functions.
    The values computed in this function should not be dependent on time.

    :param mkr_list: List of Markers to compile.
    :type mkr_list: [Marker, ..]

    :returns: dictionary with marker nodes as keys, and values for
        each marker.
    :rtype: {str: {stc: any}, ..}, ..}
    """
    cache = collections.defaultdict(dict)
    for mkr in mkr_list:
        assert isinstance(mkr, marker.Marker)
        mkr_node = mkr.get_node()
        assert isinstance(mkr_node, pycompat.TEXT_TYPE)

        bnd_node = _get_bundle_node_name_from_marker(mkr)
        if bnd_node is None:
            continue
        cache[mkr_node]['bundle_node_name'] = bnd_node

        cam_nodes = _get_camera_nodes_from_marker(mkr)
        if cam_nodes is None:
            continue
        cache[mkr_node]['camera_node_names'] = cam_nodes
    return dict(cache)


def markersAndCameras_compile_flags(mkr_list, mkr_static_values=None):
    """
    Compile mmSolver command flags for 'marker' and 'camera'.

    :param mkr_list: List of Markers to compile.
    :type mkr_list: [Marker, ..]

    :param mkr_static_values: Marker static values that can optionally
        be used to speed up compiling.

    :return:
        Tuple of both 'marker' and 'camera' flags, ready for the
        mmSolver command.
    :rtype: ([(str, str, str), ..], [(str, str)])
    """
    if mkr_static_values is None:
        mkr_static_values = dict()
    assert isinstance(mkr_static_values, dict)

    added_cameras = []
    markers = []
    cameras = []
    for mkr in mkr_list:
        assert isinstance(mkr, marker.Marker)
        mkr_node = mkr.get_node()
        assert isinstance(mkr_node, pycompat.TEXT_TYPE)
        mkr_cache = DictGetOrCall(mkr_static_values.get(mkr_node, dict()))

        bnd_node = mkr_cache.get_or_call(
            'bundle_node_name',
            lambda: _get_bundle_node_name_from_marker(mkr))
        if bnd_node is None:
            continue

        cam_nodes = mkr_cache.get_or_call(
            'camera_node_names',
            lambda: _get_camera_nodes_from_marker(mkr))
        if cam_nodes is None:
            continue
        cam_tfm_node, cam_shp_node = cam_nodes

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

    elif obj_type == const.OBJECT_TYPE_LENS:
        attr_solve_type = ATTR_SOLVER_TYPE_LENS_DISTORTION

    return attr_solve_type


def categorise_attributes(attr_list):
    """
    Sort Attributes into specific categories.

    Current categories are:

    - Regular

    - Bundle Transform

    - Camera Transform

    - Camera Intrinsic (shape node)

    - Lens Distortion

    :param attr_list: List of Attributes to be categorised.
    :type attr_list: [Attribute, ..]

    :returns: Create a mapping for Attributes based on different names.
    :rtype: {str: {str: [Attribute, ..]}}
    """
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


def get_attributes_static_values(col, attr_list):
    """
    Get static values from attributes.

    The static values can then be re-used as cached values.
    The values computed in this function should *not* be dependent on time.

    :param col: Collection to be used for min/max values.
    :type col: Collection

    :param attr_list: List of Attributes to compile
    :type attr_list: [Attribute, ..]

    :returns: A dictionary of per-attribute static values.
    :rtype: {str: {stc: any}, ..}, ..}
    """
    cache = collections.defaultdict(dict)
    for attr in attr_list:
        assert isinstance(attr, attribute.Attribute)
        name = attr.get_name()
        node_name = attr.get_node()
        attr_name = attr.get_attr()
        cache[name]['node_name'] = node_name
        cache[name]['attr_name'] = attr_name

        # Attribute State.
        cache[name]['is_locked'] = attr.is_locked()
        cache[name]['is_animated'] = attr.is_animated()
        cache[name]['is_static'] = attr.is_static()
        cache[name]['attribute_type'] = _get_attribute_type_from_attr(
            node_name, attr_name)

        # Minimum Value
        cache[name]['solver_min_enable'] = col.get_attribute_min_enable(attr)
        cache[name]['solver_min_value'] = col.get_attribute_min_value(attr)
        exists = _get_maya_min_exists_from_attr(node_name, attr_name)
        cache[name]['maya_min_exists'] = exists
        if exists:
            cache[name]['maya_min_value'] = _get_maya_min_value_from_attr(
                node_name, attr_name)

        # Maximum Value
        cache[name]['solver_max_enable'] = col.get_attribute_max_enable(attr)
        cache[name]['solver_max_value'] = col.get_attribute_max_value(attr)
        exists = _get_maya_max_exists_from_attr(node_name, attr_name)
        cache[name]['maya_max_exists'] = exists
        if exists:
            cache[name]['maya_max_value'] = _get_maya_max_value_from_attr(
                node_name, attr_name)
    return dict(cache)


def attributes_compile_flags(col, attr_list,
                             use_animated, use_static,
                             attr_static_values=None):
    """
    Compile Attributes into flags for mmSolver.

    :param col: Collection to be used for min/max values,
    :type col: Collection

    :param attr_list: List of Attributes to compile
    :type attr_list: [Attribute, ..]

    :param use_animated: Should we compile Attributes that are animated?
    :type use_animated: bool

    :param use_static: Should we compile Attributes that are static?
    :type use_static: bool

    :param attr_static_values: Attribute static values that can optionally
        be used to speed up compiling.

    :returns:
        List of tuples. Attributes in a form to be given to the
        mmSolver command.
    :rtype: [(str, str, str, str, str), ..]
    """
    assert isinstance(use_animated, bool)
    assert isinstance(use_static, bool)
    if attr_static_values is None:
        attr_static_values = dict()
    assert isinstance(attr_static_values, dict)

    attrs = []
    for attr in attr_list:
        assert isinstance(attr, attribute.Attribute)
        name = attr.get_name()
        attr_cache = DictGetOrCall(attr_static_values.get(name, dict()))

        locked = attr_cache.get_or_call('is_locked', attr.is_locked)
        if locked is True:
            continue

        node_name = attr_cache.get_or_call('node_name', attr.get_node)
        attr_name = attr_cache.get_or_call('attr_name', attr.get_attr)

        # If the user does not specify a min/max value then we get it
        # from Maya directly, if Maya doesn't have one, we leave
        # min/max_value as None and pass it to the mmSolver command
        # indicating there is no bound.

        # Minimum Value
        min_value = None
        min_enable = attr_cache.get_or_call(
            'solver_min_enable',
            lambda: col.get_attribute_min_enable(attr))
        if min_enable is True:
            min_value = attr_cache.get_or_call(
                'solver_min_value',
                lambda: col.get_attribute_min_value(attr))
        maya_min_exists = attr_cache.get_or_call(
            'maya_min_exists',
            lambda: _get_maya_min_exists_from_attr(node_name, attr_name))
        if maya_min_exists is True:
            maya_min_value = attr_cache.get_or_call(
                'maya_min_value',
                lambda: _get_maya_min_value_from_attr(node_name, attr_name))
            if len(maya_min_value) == 1:
                maya_min_value = maya_min_value[0]
            else:
                msg = 'Cannot handle attributes with multiple '
                msg += 'minimum values; node={0} attr={1}'
                msg = msg.format(repr(node_name), repr(attr_name))
                raise excep.NotValid(msg)
            if min_value is None:
                min_value = maya_min_value
            else:
                min_value = max(min_value, maya_min_value)

        # Maximum Value
        max_value = None
        max_enable = attr_cache.get_or_call(
            'solver_max_enable',
            lambda: col.get_attribute_max_enable(attr))
        if max_enable is True:
            max_value = attr_cache.get_or_call(
                'solver_max_value',
                lambda: col.get_attribute_max_value(attr))
        maya_max_exists = attr_cache.get_or_call(
            'maya_max_exists',
            lambda: _get_maya_max_exists_from_attr(node_name, attr_name))
        if maya_max_exists is True:
            maya_max_value = attr_cache.get_or_call(
                'maya_max_value',
                lambda: _get_maya_max_value_from_attr(node_name, attr_name))
            if len(maya_max_value) == 1:
                maya_max_value = maya_max_value[0]
            else:
                msg = 'Cannot handle attributes with multiple '
                msg += 'maximum values; node={0} attr={1}'
                msg = msg.format(repr(node_name), repr(attr_name))
                raise excep.NotValid(msg)
            if max_value is None:
                max_value = maya_max_value
            else:
                max_value = min(max_value, maya_max_value)

        # Scale and Offset
        scale_value = None
        offset_value = None
        attr_type = attr_cache.get_or_call(
            'attribute_type',
            lambda: _get_attribute_type_from_attr(node_name, attr_name))
        if attr_type.endswith('Angle'):
            offset_value = 360.0

        animated = attr_cache.get_or_call('is_animated', attr.is_animated)
        static = attr_cache.get_or_call('is_static', attr.is_static)
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
                 str(scale_value)))
    return attrs


def get_attr_stiffness_static_values(col, attr_list):
    """
    Compile Attributes into flags for mmSolver.

    :param col: Collection to be used for stiffness.
    :type col: Collection

    :param attr_list: List of Attributes to compile.
    :type attr_list: [Attribute, ..]

    :returns: dictionary with attribute plugs as keys, and values for
        each attribute.
    :rtype: {str: {stc: any}, ..}, ..}
    """
    cache = collections.defaultdict(dict)
    for attr in attr_list:
        assert isinstance(attr, attribute.Attribute)
        name = attr.get_name()
        enable = col.get_attribute_stiffness_enable(attr)
        weight = col.get_attribute_stiffness_weight(attr)

        weight_plug_name = col.get_attribute_stiffness_weight_plug_name(attr)
        prev_plug_name = col.get_attribute_previous_value_plug_name(attr)
        variance_plug_name = col.get_attribute_stiffness_variance_plug_name(attr)

        cache[name]['enable'] = enable
        cache[name]['weight'] = weight
        cache[name]['weight_plug'] = weight_plug_name
        cache[name]['previous_plug'] = prev_plug_name
        cache[name]['variance_plug'] = variance_plug_name
    return dict(cache)


def attr_stiffness_compile_flags(col, attr_list,
                                 attr_static_values=None,
                                 attr_stiff_static_values=None):
    """
    Compile Attributes into flags for mmSolver.

    :param col: Collection to be used for stiffness.
    :type col: Collection

    :param attr_list: List of Attributes to compile.
    :type attr_list: [Attribute, ..]

    :param attr_static_values: Attribute static values that can optionally
        be used to speed up compiling.

    :param attr_stiff_static_values: Attribute stiffness static values that
        can optionally be used to speed up compiling.

    :returns:
        List of tuples. Attributes in a form to be given to the
        mmSolver command.
    :rtype: [(str, str, str, str, str), ..]
    """
    if attr_static_values is None:
        attr_static_values = dict()
    if attr_stiff_static_values is None:
        attr_stiff_static_values = dict()
    assert isinstance(attr_static_values, dict)
    assert isinstance(attr_stiff_static_values, dict)

    stiffness_flags = []
    for attr in attr_list:
        assert isinstance(attr, attribute.Attribute)
        name = attr.get_name()
        attr_cache = DictGetOrCall(attr_static_values.get(name, dict()))
        stiff_cache = DictGetOrCall(attr_stiff_static_values.get(name, dict()))

        animated = attr_cache.get_or_call('is_animated', attr.is_animated)
        if not animated:
            continue

        enable = stiff_cache.get_or_call(
            'enable', lambda: col.get_attribute_stiffness_enable(attr))
        if enable is not True:
            continue

        weight = stiff_cache.get_or_call(
            'weight', lambda: col.get_attribute_stiffness_weight(attr))
        if weight <= 0.0:
            continue

        weight_plug_name = stiff_cache.get_or_call(
            'weight_plug',
            lambda: col.get_attribute_stiffness_weight_plug_name(attr))
        prev_plug_name = stiff_cache.get_or_call(
            'previous_plug',
            lambda: col.get_attribute_previous_value_plug_name(attr))
        variance_plug_name = stiff_cache.get_or_call(
            'variance_plug',
            lambda: col.get_attribute_stiffness_variance_plug_name(attr))

        stiffness_flags.append((
            name,
            weight_plug_name,
            variance_plug_name,
            prev_plug_name)
        )
    return stiffness_flags


def get_attr_smoothness_static_values(col, attr_list):
    """
    Compile Attributes into flags for mmSolver.

    :param col: Collection to be used for smoothness.
    :type col: Collection

    :param attr_list: List of Attributes to compile.
    :type attr_list: [Attribute, ..]

    :returns: dictionary with attribute plugs as keys, and values for
        each attribute.
    :rtype: {str: {stc: any}, ..}, ..}
    """
    cache = collections.defaultdict(dict)
    for attr in attr_list:
        assert isinstance(attr, attribute.Attribute)
        name = attr.get_name()
        enable = col.get_attribute_smoothness_enable(attr)
        weight = col.get_attribute_smoothness_weight(attr)

        weight_plug_name = col.get_attribute_smoothness_weight_plug_name(attr)
        mean_plug_name = col.get_attribute_mean_value_plug_name(attr)
        variance_plug_name = col.get_attribute_smoothness_variance_plug_name(attr)

        cache[name]['enable'] = enable
        cache[name]['weight'] = weight
        cache[name]['weight_plug'] = weight_plug_name
        cache[name]['mean_plug'] = mean_plug_name
        cache[name]['variance_plug'] = variance_plug_name
    return dict(cache)


def attr_smoothness_compile_flags(col, attr_list,
                                  attr_static_values=None,
                                  attr_smooth_static_values=None):
    """
    Compile Attributes into flags for mmSolver.

    :param col: Collection to be used for smoothness.
    :type col: Collection

    :param attr_list: List of Attributes to compile.
    :type attr_list: [Attribute, ..]

    :param attr_static_values: Attribute static values that can optionally
        be used to speed up compiling.

    :param attr_smooth_static_values: Attribute smoothness static values that
        can optionally be used to speed up compiling.

    :returns:
        List of tuples. Attributes in a form to be given to the
        mmSolver command.
    :rtype: [(str, str, str, str, str), ..]
    """
    if attr_static_values is None:
        attr_static_values = dict()
    if attr_smooth_static_values is None:
        attr_smooth_static_values = dict()
    assert isinstance(attr_static_values, dict)
    assert isinstance(attr_smooth_static_values, dict)

    smoothness_flags = []
    for attr in attr_list:
        assert isinstance(attr, attribute.Attribute)
        name = attr.get_name()
        attr_cache = DictGetOrCall(attr_static_values.get(name, dict()))
        smooth_cache = DictGetOrCall(attr_smooth_static_values.get(name, dict()))

        animated = attr_cache.get_or_call('is_animated', attr.is_animated)
        if not animated:
            continue

        enable = smooth_cache.get_or_call(
            'enable', lambda: col.get_attribute_smoothness_enable(attr))
        if enable is not True:
            continue

        weight = smooth_cache.get_or_call(
            'weight', lambda: col.get_attribute_smoothness_weight(attr))
        if weight <= 0.0:
            continue

        weight_plug_name = smooth_cache.get_or_call(
            'weight_plug',
            lambda: col.get_attribute_smoothness_weight_plug_name(attr))
        mean_plug_name = smooth_cache.get_or_call(
            'mean_plug',
            lambda: col.get_attribute_mean_value_plug_name(attr))
        variance_plug_name = smooth_cache.get_or_call(
            'variance_plug',
            lambda: col.get_attribute_smoothness_variance_plug_name(attr))

        smoothness_flags.append((
            name,
            weight_plug_name,
            variance_plug_name,
            mean_plug_name)
        )
    return smoothness_flags


def frames_compile_flags(frm_list, frame_use_tags):
    """
    Create a list of frame numbers using Frame objects and some rules.

    :param frm_list: List of Frame objects.
    :type frm_list: Frame

    :param frame_use_tags: List of tag names that Frame objects must
                           contain to be compiled.
    :type frame_use_tags: [str, ..]

    :return: A list of frame numbers.
    :rtype: [int, ..]
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


def collection_compile(col, sol_list, mkr_list, attr_list,
                       withtest=False,
                       prog_fn=None,
                       status_fn=None):
    """
    Take the data in this class and compile it into actions to run.

    :return: list of SolverActions.
    :rtype: [SolverAction, ..]
    """
    col_node = col.get_node()
    action_list = []
    vaction_list = []
    if len(sol_list) == 0:
        msg = 'Collection is not valid, no Solvers given; '
        msg += 'collection={0}'
        msg = msg.format(repr(col_node))
        raise excep.NotValid(msg)

    sol_enabled_list = [sol for sol in sol_list
                        if sol.get_enabled() is True]
    if len(sol_enabled_list) == 0:
        msg = 'Collection is not valid, no enabled Solvers given; '
        msg += 'collection={0}'
        msg = msg.format(repr(col_node))
        raise excep.NotValid(msg)

    if len(mkr_list) == 0:
        msg = 'Collection is not valid, no Markers given; collection={0}'
        msg = msg.format(repr(col_node))
        raise excep.NotValid(msg)

    if len(attr_list) == 0:
        msg = 'Collection is not valid, no Attributes given; collection={0}'
        msg = msg.format(repr(col_node))
        raise excep.NotValid(msg)

    # Query and cache static values from Maya, so we don't need to
    # re-compute the values inside Solvers.
    attr_static_values = get_attributes_static_values(col, attr_list)
    attr_stiff_static_values = get_attr_stiffness_static_values(col, attr_list)
    attr_smooth_static_values = get_attr_smoothness_static_values(col, attr_list)
    mkr_static_values = get_markers_static_values(mkr_list)
    precomputed_data = {
        solverbase.MARKER_STATIC_VALUES_KEY: mkr_static_values,
        solverbase.ATTR_STATIC_VALUES_KEY: attr_static_values,
        solverbase.ATTR_STIFFNESS_STATIC_VALUES_KEY: attr_stiff_static_values,
        solverbase.ATTR_SMOOTHNESS_STATIC_VALUES_KEY: attr_smooth_static_values,
    }

    # Compile all the solvers
    msg = 'Collection is not valid, failed to compile solver;'
    msg += ' collection={0}'
    msg = msg.format(repr(col_node))
    for sol in sol_enabled_list:
        assert isinstance(sol, solverbase.SolverBase)
        sol.set_precomputed_data(precomputed_data)
        for action, vaction in sol.compile(col, mkr_list, attr_list,
                                           withtest=withtest):
            if not isinstance(action, api_action.Action):
                raise excep.NotValid(msg)
            assert action.func is not None
            assert action.args is not None
            assert action.kwargs is not None
            action_list.append(action)
            vaction_list.append(vaction)
    assert len(action_list) == len(vaction_list)
    return action_list, vaction_list


def create_compile_solver_cache():
    """
    Create the cache for use with the 'compile_solver_with_cache' function.
    """
    cache = collections.defaultdict(list)
    return cache


def compile_solver_with_cache(sol, col, mkr_list, attr_list, withtest, cache):
    """
    Compile a single solver, storing the internals in the given cache,
    and using the cache to speed up future compilations.

    The given cache is expected to be used *only* for one solver and the
    compiled solver should only vary in frame numbers. This function assumes
    only the given Markers vary over time, and the Attributes given to the
    solver will not change in each different solve. If None is given as the
    Cache, we do not use any caching.

    The cache is expected to be created like so:
    >>> import mmSolver._api.compile
    >>> cache = mmSolver._api.compile.create_compile_solver_cache()
    >>> compile_solver_with_cache(sol, col, mkr_list, attr_list, withtest, cache)

    Compile unique list of frames to test the solver when it changes,
    for example when a marker turns off, then only sample the unique
    sets of markers. This will reduce the compile/testing time
    considerably, and because we know there are no changes in the
    structure or number of errors, we can copy the same mmSolver
    kwargs multiple times (with the frames argument set differently).

    :param col: The Collection to compile.
    :type col: Collection

    :param sol: The solver to compile.
    :type sol: Solver

    :param mkr_list: The list of Markers to use for compiling.
    :type mkr_list: [Marker, ..]

    :param attr_list: The list of Attribute to use for compiling.
    :type attr_list: [Attribute, ..]

    :returns: A generator function yielding a tuple of two Action
              objects. The first object is used for solving, the
              second Action is for validation of the solve.
    :rtype: (Action, Action or None)
    """
    if cache is None or withtest is False:
        for action, vaction in sol.compile(col, mkr_list, attr_list,
                                           withtest=withtest):
            yield action, vaction
    else:
        frame_list = sol.get_frame_list()

        # Get frame with lowest number of active markers.
        #
        # If we have a list of frames in the current solver, and on
        # one of the frames there are zero markers, most frames will
        # solve, except for that one. We must detect this and skip the entire
        # solve to avoid any invalid solve frames.
        min_num_of_active_mkr_nodes = 999999999
        min_list_of_active_mkr_nodes = []
        for frm in frame_list:
            frm_num = frm.get_number()
            active_mkr_nodes = [m.get_node()
                                for m in mkr_list
                                if m.get_enable(frm_num)]
            if len(active_mkr_nodes) < min_num_of_active_mkr_nodes:
                min_list_of_active_mkr_nodes = active_mkr_nodes

        hash_string = str(len(min_list_of_active_mkr_nodes))
        hash_string += '#'.join(min_list_of_active_mkr_nodes)
        vaction_list = cache.get(hash_string, None)

        # Compile if our testing action is not in the cache.
        if vaction_list is None:
            # Add to the cache
            for action, vaction in sol.compile(col, mkr_list, attr_list,
                                               withtest=True):
                cache[hash_string].append(vaction)
                yield action, vaction
        else:
            # Re-use the cache
            generator = zip(
                sol.compile(col, mkr_list, attr_list, withtest=False),
                vaction_list
            )
            for (action, _), vaction in generator:
                yield action, vaction
    return
