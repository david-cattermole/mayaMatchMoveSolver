"""
Animation utilities.
"""

import sys
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
    """
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
    for i in xrange(len(times)):
        time_array.append(OpenMaya.MTime(times[i], OpenMaya.MTime.uiUnit()))
        value_array.append(values[i])

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

