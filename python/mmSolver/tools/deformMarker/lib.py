"""
This file contains all the lib function to help deformMarker tool
"""

import maya.cmds
import mmSolver.tools.deformMarker.constant as const
import mmSolver.logger

LOG = mmSolver.logger.get_logger()


def is_in_layer(attr, anim_layer):
    """
    Checking if given attr is in anim layer
    :param attr: Attribute
    :type attr: str
    :param anim_layer: anim layer name
    :type anim_layer: str

    :return: boolean
    :rtype: bool
    """
    attr = str(attr)

    attr_short_name = attr.split('|')[-1]
    anim_layer_attrs = maya.cmds.animLayer(anim_layer,
                                           attribute=True,
                                           query=True) or []
    if attr_short_name in anim_layer_attrs:
        return True
    else:
        return False


def get_attr_blend_plugs(attr, anim_layer):
    """
    Checking if given attr is in anim layer
    :param attr: Attribute
    :type attr: str
    :param anim_layer: anim layer name
    :type anim_layer: str

    :return: Attr inputs plugs
    :rtype: list
    """

    if not is_in_layer(attr, anim_layer):
        LOG.warning('Attribute not in anim layer ')
        return

    node_attr = attr
    anim_blend_node = const.ANIM_BLEND_NODE
    anim_blend_connection = maya.cmds.listConnections(
                            node_attr,
                            type=anim_blend_node,
                            source=True
                            )
    plugs = const.PLUGS
    inputs = []
    for plug in plugs:
        plug_source = maya.cmds.listConnections(
            '%s.%s' % (anim_blend_connection[-1], plug),
            source=True)
        inputs.append(plug_source)
    return inputs


def __get_attr_value_array(attr, first_frame, last_frame):
    """
    Returns attribute's value array for given frame range.
    :param attr: Attribute
    :type attr: str
    :param first_frame: Start frame
    :type first_frame: int
    :param last_frame: End frame
    :type last_frame: int
    :return: Value array
    :rtype: list
    """

    new_array = []
    for frame in range(int(first_frame), int(last_frame+1)):
        new_array.append(maya.cmds.getAttr('%s.output' % attr[-1],
                                           time=frame))
    return new_array


def __get_first_last_frame(attr, anim_layer):
    """
    Gets first frame and last keys frame from given animlayer
    :param attr: Attribute
    :type attr : str
    :param anim_layer: Anim Layer
    :type anim_layer: str
    :return: First and last frame
    :rtype: int, int
    """

    input_a, input_b = get_attr_blend_plugs(attr, anim_layer)

    input_a_min_max = get_min_and_max_from_plugs(input_a)

    input_b_min_max = get_min_and_max_from_plugs(input_b)

    if min(input_b_min_max) < min(input_a_min_max):
        first_frame = min(input_b_min_max)
    else:
        first_frame = min(input_a_min_max)

    if max(input_b_min_max) > max(input_a_min_max):
        last_frame = max(input_b_min_max)
    else:
        last_frame = max(input_a_min_max)
    return first_frame, last_frame


def get_min_and_max_from_plugs(plug):
    """
    Minimum and maximum keyframe for the given plug
    :param plug: anim_layer plug
    :type plug: str
    :return: minimum and maximum keyframe
    :rtype: int, int
    """
    plug_min = min(maya.cmds.keyframe(plug,
                                      query=True,
                                      timeChange=True))

    plug_max = max(maya.cmds.keyframe(plug,
                                      query=True,
                                      timeChange=True))
    return plug_min, plug_max


def set_attr_value_array(attr, new_array, first_frame, last_frame):
    """
    Sets value for a attribute for given frame range
    :param attr: Attribute
    :type attr: str
    :param new_array: array with values
    :type new_array: list
    :param first_frame: Start frame
    :type first_frame: int
    :param last_frame: End frame
    :type last_frame: int
    :return: None
    """

    for value, frame in zip(new_array, range(int(first_frame),
                                             int(last_frame+1))):
        maya.cmds.setKeyframe(attr, value=value, time=frame)
    return


def is_key_framed(attrs):
    """
    Querying if any of the given attribute is keyed
    :param attrs: Attributes
    :type attrs: list
    :return: Boolean
    :rtype: bool
    """

    for attr in attrs:
        if maya.cmds.keyframe(attr, timeChange=True,
                              query=True) is None:
            return False
    return True


def find_animlayer(anim_layer):
    """
    Finds whether given layer name is in the scene, if not then creates
    new anim layer with given name
    :param anim_layer: Anim layer name
    :type anim_layer: str
    :return: Anim Layer
    :rtype: str
    """

    if maya.cmds.animLayer(anim_layer, exists=True, query=True):
        return anim_layer
    else:
        new_anim_layer = maya.cmds.animLayer(anim_layer)
        return new_anim_layer


def get_attrs_for_offset(selection):
    """
    Getting attributes for creating offset
    :param selection: Maya selection
    :type selection: list
    :return: Offset attributes
    :rtype: list
    """

    attrs = const.ATTRS
    offset_attrs = []
    for marker in selection:
        for attr in attrs:
            offset_attrs.append('%s.%s' % (marker, attr))
    return offset_attrs
