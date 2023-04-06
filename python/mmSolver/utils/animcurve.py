# Copyright (C) 2018, 2019 David Cattermole.
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
Animation curve (animCurve) utilities.

.. note:: Any function names ending with *_apione* or *_apitwo* depicts
   the Python Maya API version used in that function, and the returned
   types. Be careful not to mix API function values, otherwise it will
   all end in tears.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import warnings

import maya.cmds
import maya.OpenMaya as OpenMaya1
import maya.OpenMayaAnim as OpenMayaAnim1

import mmSolver.utils.node as node_utils


def create_anim_curve_node_apione(
    times,
    values,
    node_attr=None,
    tangent_in_type=OpenMayaAnim1.MFnAnimCurve.kTangentGlobal,
    tangent_out_type=OpenMayaAnim1.MFnAnimCurve.kTangentGlobal,
    anim_type=OpenMayaAnim1.MFnAnimCurve.kAnimCurveTL,
    undo_cache=None,
):
    """
    Create an animCurve using Maya API (one).

    :param times: Time values for the animCurve
    :type times: list

    :param values: Values for the animCurve.
    :type values: list

    :param node_attr: The 'plug' to connect the animCurve to.
    :type node_attr: str

    :param tangent_in_type: The "in" tangent type for keyframes.
    :type tangent_in_type: maya.OpenMayaAnim.MFnAnimCurve.kTangent*

    :param tangent_out_type: The "out" tangent type for keyframes.
    :type tangent_out_type: maya.OpenMayaAnim.MFnAnimCurve.kTangent*

    :param anim_type: The type of animation curve node.
    :type anim_type: maya.OpenMayaAnim.MFnAnimCurve.kAnimCurve*

    :param undo_cache: The Maya AnimCurve Undo Cache data structure or
                       None if no undo is required.
    :type undo_cache: maya.OpenMayaAnim.MAnimCurveChange

    :return: MFnAnimCurve object attached to a newly created animation curve.
    :rtype: maya.OpenMaya.MFnAnimCurve
    """
    if not isinstance(times, list):
        raise ValueError('times must be a list or sequence type; %r' % times)
    if not isinstance(values, list):
        raise ValueError('values must be a list or sequence type; %r' % values)
    if len(times) == 0:
        raise ValueError('times must have 1 or more values; %r' % times)
    if len(values) == 0:
        raise ValueError('values must have 1 or more values; %r' % values)
    if len(times) != len(values):
        raise ValueError(
            'Number of times and values does not match; times=%r values=%r'
            % (len(times), len(values))
        )

    # create anim curve
    animfn = OpenMayaAnim1.MFnAnimCurve()
    if node_attr is None:
        animCurve = animfn.create(anim_type)
    else:
        # Get the plug to be animated.
        dst_plug = node_utils.get_as_plug(node_attr)

        objs = OpenMaya1.MObjectArray()
        find = OpenMayaAnim1.MAnimUtil.findAnimation(dst_plug, objs)
        if find is True and objs.length() > 0:
            animfn = OpenMayaAnim1.MFnAnimCurve(objs[0])
        else:
            animfn = OpenMayaAnim1.MFnAnimCurve()
            animfn.create(dst_plug)

    # Copy the times into an MTimeArray and the values into an MDoubleArray.
    time_array = OpenMaya1.MTimeArray()
    value_array = OpenMaya1.MDoubleArray()
    for time, value in zip(times, values):
        time_array.append(OpenMaya1.MTime(time, OpenMaya1.MTime.uiUnit()))
        value_array.append(float(value or 0))

    # force a default undo cache
    if not undo_cache:
        undo_cache = OpenMayaAnim1.MAnimCurveChange()

    # Add the keys to the animCurve.
    animfn.addKeys(
        time_array,
        value_array,
        tangent_in_type,
        tangent_out_type,
        False,  # overwrite any keys that get in our way
        undo_cache,
    )
    return animfn


def create_anim_curve_node(*args, **kwargs):
    msg = 'Use mmSolver.utils.animcurve.create_anim_curve_node_apione instead.'
    warnings.warn(msg, DeprecationWarning)
    return create_anim_curve_node_apione(*args, **kwargs)


def get_anim_curves_from_nodes(nodes_or_plugs, attrs=None):
    """
    Get all animCurve nodes connected to the given nodes.

    :param nodes_or_plugs: List of nodes (or plugs) to query animation curves.
    :type nodes_or_plugs: [str, ..]

    :returns: List of animation nodes. List may be empty if no
              animCurves were found.
    :rtype: [str, ..]
    """
    assert isinstance(nodes_or_plugs, (list, tuple))
    anim_curve_nodes = maya.cmds.listConnections(nodes_or_plugs, type='animCurve') or []
    return anim_curve_nodes


def euler_filter_plug(node_name, attr_name):
    """
    Perform Euler filter for the given node attribute.
    """
    plug_name = '{0}.{1}'.format(node_name, attr_name)
    num_keys = maya.cmds.keyframe(plug_name, query=True, keyframeCount=True) or 0
    if num_keys <= 0:
        return

    # Perform Euler filter for the entire animation curve.
    prev_value = 0.0
    for key_index in range(num_keys):
        values = (
            maya.cmds.keyframe(
                node_name,
                query=True,
                attribute=attr_name,
                index=(key_index,),
                valueChange=True,
            )
            or None
        )
        assert values is not None
        # Modulo the keyframe value to ensure the starting value is
        # not too high to begin with, causing Maximum Recursion
        # exceptions if the value is too large.
        value = values[0] % 360.0
        new_value = euler_filter_value(prev_value, value)
        maya.cmds.keyframe(
            node_name,
            query=True,
            attribute=attr_name,
            index=(key_index,),
            valueChange=new_value,
        )
    return


def euler_filter_value(prev_value, value):
    """
    Perform a 'Euler Filter' on the given rotation values.

    The filter will ensure that each sequential rotation value will be
    with-in +/-360 degrees of the previous value.

    Each axis (X, Y and Z) must be filtered individuality.

    .. note::
        This function is called recursively when a rotation is
        more/less than 360 degrees.

    :param prev_value: The rotation value on the previous frame.
    :type prev_value: float

    :param value: The current rotation value.
    :type value: float

    :returns: A new filter rotation value.
    :rtype: float
    """
    value_diff = value - prev_value
    if value_diff > 180.0:
        value = euler_filter_value(prev_value, value - 360.0)
    elif value_diff < -180.0:
        value = euler_filter_value(prev_value, value + 360.0)
    return value
