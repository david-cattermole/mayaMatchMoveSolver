"""
Animation utilities.
"""

import maya.cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

import mmSolver._api.utils as utils


def create_anim_curve_node(times, values,
                           node_attr=None,
                           tangent_in_type=OpenMayaAnim.MFnAnimCurve.kTangentGlobal,
                           tangent_out_type=OpenMayaAnim.MFnAnimCurve.kTangentGlobal,
                           anim_type=OpenMayaAnim.MFnAnimCurve.kAnimCurveTL,
                           undo_cache=None):
    """
    Create an animCurve using the Maya API


    :param times: Time values for the animCurve
    :type times: list

    :param values: Values for the animCurve.
    :type values: list

    :param node_attr: The 'plug' to connect the animCurve to.
    :type node_attr: str

    :param tangent_in_type: The "in" tangent type for keyframes.
    :param tangent_out_type: The "out" tangent type for keyframes.
    :param anim_type: The type of animation curve node.
    :param undo_cache: The Maya AnimCurve Undo Cache data structure.
    :return:
    """
    if not isinstance(times, list):
        raise ValueError('times must be a list or sequence type.')
    if not isinstance(values, list):
        raise ValueError('times must be a list or sequence type.')
    if len(times) == 0:
        raise ValueError('times must have 1 or more values.')
    if len(values) == 0:
        raise ValueError('values must have 1 or more values.')
    if len(times) != len(values):
        raise ValueError('Number of times and values does not match.')

    # create anim curve
    animfn = OpenMayaAnim.MFnAnimCurve()
    if node_attr is None:
        animCurve = animfn.create(anim_type)
    else:
        # Get the plug to be animated.
        dst_plug = utils.get_as_plug(node_attr)

        objs = OpenMaya.MObjectArray()
        find = OpenMayaAnim.MAnimUtil.findAnimation(dst_plug, objs)
        if find is True and objs.length() > 0:
            animfn = OpenMayaAnim.MFnAnimCurve(objs[0])
        else:
            animfn = OpenMayaAnim.MFnAnimCurve()
            animfn.create(dst_plug)

    # Copy the times into an MTimeArray and the values into an MDoubleArray.
    time_array = OpenMaya.MTimeArray()
    value_array = OpenMaya.MDoubleArray()
    for time, value in zip(times, values):
        time_array.append(OpenMaya.MTime(time, OpenMaya.MTime.uiUnit()))
        value_array.append(value)

    # force a default undo cache
    if not undo_cache:
        undo_cache = OpenMayaAnim.MAnimCurveChange()

    # Add the keys to the animCurve.
    animfn.addKeys(
        time_array,
        value_array,
        tangent_in_type,
        tangent_out_type,
        False,  # overwrite any keys that get in our way
        undo_cache
    )
    return animfn

