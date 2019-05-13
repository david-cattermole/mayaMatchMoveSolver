"""
Module for reading marker files.

This should be used by end-users, not the internal modules.
"""

import os

import maya.cmds

import mmSolver.api as mmapi
import mmSolver.tools.loadmarker.interface as interface
import mmSolver.tools.loadmarker.formatmanager as fmtmgr

# Used to force importing of formats; do not remove this line.
import mmSolver.tools.loadmarker.formats


def read(file_path, **kwargs):
    """
    Read a file path, find the format parser based on the file extension.
    """
    if isinstance(file_path, (str, unicode)) is False:
        msg = 'file path must be a string, got %r'
        raise TypeError(msg % type(file_path))
    if os.path.isfile(file_path) is False:
        msg = 'file path does not exist; %r'
        raise OSError(msg % file_path)

    file_format_class = None
    mgr = fmtmgr.get_format_manager()
    for fmt in mgr.get_formats():
        attr = getattr(fmt, 'file_exts', None)
        if attr is None:
            continue
        if not isinstance(fmt.file_exts, list):
            continue
        for ext in fmt.file_exts:
            if file_path.endswith(ext):
                file_format_class = fmt
                break
    if file_format_class is None:
        msg = 'No file formats found for file path: %r'
        raise RuntimeError(msg % file_path)

    file_format_obj = file_format_class()
    mkr_data_list = file_format_obj.parse(file_path, **kwargs)
    return mkr_data_list


def __create_node(mkr_data, cam, mkr_grp, with_bundles):
    """
    Create a Marker object from a MarkerData object.
    """
    if isinstance(mkr_data, interface.MarkerData) is False:
        msg = 'mkr_data must be of type: %r'
        raise TypeError(msg % interface.MarkerData.__name__)
    if isinstance(with_bundles, bool) is False:
        msg = 'with_bundles must be of type: %r'
        raise TypeError(msg % bool.__name__)

    name = mkr_data.get_name()
    mkr_name = mmapi.get_marker_name(name)
    bnd_name = mmapi.get_bundle_name(name)
    bnd = None
    mmapi.load_plugin()
    if with_bundles is True:
        bnd = mmapi.Bundle().create_node(bnd_name)
    mkr = mmapi.Marker().create_node(name=mkr_name, cam=cam, mkr_grp=mkr_grp, bnd=bnd)
    return mkr


def __set_attr_keyframes(node, attr_name, keyframes,
                         before_value=None,
                         after_value=None,
                         reduce_keys=None):
    """
    Set keyframes on a node.attribute, from a KeyframeData instance.

    :param node: Node to set data on.
    :type node: str

    :param attr_name: Attribute (on 'node') to set keyframes.
    :type attr_name: str

    :param keyframes: The keyframe information.
    :type keyframes: KeyframeData

    :param before_value: Value to set before the first keyframe.
    :type before_value: int, float or bool

    :param after_value: Value to set after the first keyframe.
    :type after_value: int, float or bool

    :param reduce_keys: Allow reducing the keyframes, potentially
                        deleting all keyframes. Values will NEVER be
                        changed, only duplicate keyframe data is
                        removed.
    :type reduce_keys: bool

    :returns: Maya API MFnAnimCurve object.
    :rtype: OpenMaya.MFnAnimCurve
    """
    if isinstance(keyframes, interface.KeyframeData) is False:
        msg = 'keyframes must be type %r'
        raise TypeError(msg % interface.KeyframeData.__name__)
    if reduce_keys is None:
        reduce_keys = False
    if isinstance(reduce_keys, bool) is False:
        msg = "reduce_keys must be type 'bool'"
        raise TypeError(msg)
    times, values = keyframes.get_times_and_values()
    assert len(times) == len(values)

    # Set an extra value before/after the first/last keyframe.
    if len(times) > 0:
        if before_value is not None:
            start_time = times[0]
            times = [start_time - 1] + times
            values = [before_value] + values
        if after_value is not None:
            end_time = times[-1]
            times = times + [end_time + 1]
            values = values + [after_value]

    # TODO: Reduce keyframes, if we can, we don't need per-frame
    # keyframes if the data is the same. Change the times/values just
    # before we set the keyframes

    node_attr = node + '.' + attr_name
    animFn = mmapi.create_anim_curve_node(times, values, node_attr)

    if reduce_keys is True:
        locked = maya.cmds.getAttr(node_attr, lock=True)
        maya.cmds.setAttr(node_attr, lock=False)
        maya.cmds.delete(node_attr, staticChannels=True)
        maya.cmds.setAttr(node_attr, lock=locked)
    return animFn


def __set_node_data(mkr, mkr_data):
    """
    Set and override the data on the given marker node.

    Note: marker may have existing data or not.
    """
    assert isinstance(mkr, mmapi.Marker)
    assert isinstance(mkr_data, interface.MarkerData)
    mkr_node = mkr.get_node()

    mkr_name = mkr_data.get_name()
    assert isinstance(mkr_name, (str, unicode))
    maya.cmds.setAttr(mkr_node + '.markerName', lock=False)
    maya.cmds.setAttr(mkr_node + '.markerName', mkr_name, type='string')
    maya.cmds.setAttr(mkr_node + '.markerName', lock=True)

    # Add marker data ID onto the marker node, to be used
    # for re-mapping point data regardless of point name.
    mkr_id = mkr_data.get_id()
    if mkr_id is not None:
        maya.cmds.setAttr(mkr_node + '.markerId', lock=False)
        maya.cmds.setAttr(mkr_node + '.markerId', mkr_id)
        maya.cmds.setAttr(mkr_node + '.markerId', lock=True)

    # Get keyframe data
    mkr_x_data = mkr_data.get_x().get_raw_data()
    mkr_y_data = mkr_data.get_y().get_raw_data()
    for t, v in mkr_x_data.iteritems():
        mkr_x_data[t] = v - 0.5
    for t, v in mkr_y_data.iteritems():
        mkr_y_data[t] = v - 0.5
    mkr_x = interface.KeyframeData(data=mkr_x_data)
    mkr_y = interface.KeyframeData(data=mkr_y_data)
    mkr_enable = mkr_data.get_enable()
    mkr_weight = mkr_data.get_weight()

    # Unlock
    maya.cmds.setAttr(mkr_node + '.translateX', lock=False)
    maya.cmds.setAttr(mkr_node + '.translateY', lock=False)
    maya.cmds.setAttr(mkr_node + '.enable', lock=False)
    maya.cmds.setAttr(mkr_node + '.weight', lock=False)

    # Set keyframes.
    __set_attr_keyframes(mkr_node, 'translateX', mkr_x)
    __set_attr_keyframes(mkr_node, 'translateY', mkr_y)
    __set_attr_keyframes(mkr_node, 'enable', mkr_enable,
                         before_value=False,
                         after_value=False,
                         reduce_keys=True)
    __set_attr_keyframes(mkr_node, 'weight', mkr_weight, reduce_keys=True)

    # Lock
    maya.cmds.setAttr(mkr_node + '.translateX', lock=True)
    maya.cmds.setAttr(mkr_node + '.translateY', lock=True)
    maya.cmds.setAttr(mkr_node + '.enable', lock=True)
    maya.cmds.setAttr(mkr_node + '.weight', lock=True)

    return mkr


def create_nodes(mkr_data_list, cam=None, mkr_grp=None, with_bundles=True):
    """
    Create Markers for all given MarkerData objects

    :param mkr_data_list: List of MarkerData with data for creating
                          markers.
    :type mkr_data_list: [MarkerData, ..]

    :param cam: Camera to create Markers under.
    :type cam: Camera

    :param mkr_grp: Marker Group, under cam, that the markers will
                    be created under.
    :type mkr_grp: MarkerGroup

    :param with_bundles: Create a bundle for each Marker.
    :type with_bundles: bool

    :returns: List of Markers.
    :rtype: [Marker, ..]
    """
    selected_nodes = maya.cmds.ls(sl=True, long=True) or []
    mkr_nodes = []
    mkr_list = []
    for mkr_data in mkr_data_list:
        # Create the nodes
        mkr = __create_node(mkr_data, cam, mkr_grp, with_bundles)
        mkr_nodes.append(mkr.get_node())
        if mkr is not None:
            # Set attributes and add into list
            __set_node_data(mkr, mkr_data)
            mkr_list.append(mkr)
    if len(mkr_nodes) > 0:
        maya.cmds.select(mkr_nodes, replace=True)
    else:
        maya.cmds.select(selected_nodes, replace=True)
    return mkr_list


def update_nodes(mkr_list, mkr_data_list):
    """
    Update the given mkr_list with data from mkr_data_list.
    The length of both lists must match.
    """
    assert len(mkr_list) == len(mkr_data_list)
    raise NotImplementedError
    return mkr_list
