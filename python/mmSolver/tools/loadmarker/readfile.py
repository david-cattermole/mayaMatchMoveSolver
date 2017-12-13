"""
Module for reading marker files.

This should be used by end-users, not the internal modules.
"""

import os

import maya.cmds

import mmSolver.api as mmapi
import mmSolver.tools.loadmarker.interface as interface
import mmSolver.tools.loadmarker.formatmanager as fmtmgr

# Used to force importing of formats, to not remove.
import mmSolver.tools.loadmarker.formats


def read(file_path):
    # assert start_frame is None or isinstance(start_frame, int)
    if not isinstance(file_path, (str, unicode)):
        return None
    if not os.path.isfile(file_path):
        return None

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
        return None

    file_format_obj = file_format_class()
    mkr_data_list = file_format_obj.parse(file_path)
    return mkr_data_list


def __create_node(mkr_data, cam, with_bundles):
    """
    Create a Marker object from a MarkerData object.
    """
    assert isinstance(mkr_data, interface.MarkerData)
    assert isinstance(with_bundles, bool)
    name = mkr_data.get_name()
    mkr_name = mmapi.get_marker_name(name)
    bnd_name = mmapi.get_bundle_name(name)
    bnd = None
    if with_bundles is True:
        bnd = mmapi.Bundle().create_node(bnd_name)
    mkr = mmapi.Marker().create_node(name=mkr_name, cam=cam, bnd=bnd)
    return mkr


def __set_attr_keyframes(node, attr_name, keyframes):
    assert isinstance(keyframes, interface.KeyframeData)
    times, values = keyframes.get_times_and_values()
    node_attr = node + '.' + attr_name
    animFn = mmapi.create_anim_curve_node(times, values, node_attr)
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

    # Get keyframe data
    mkr_x_data = mkr_data.get_x().get_raw_data()
    mkr_y_data = mkr_data.get_y().get_raw_data()
    for t, v in mkr_x_data.iteritems():
        # TODO: Work out the factor we need to put the point into camera space.
        mkr_x_data[t] = v - 0.5
    for t, v in mkr_y_data.iteritems():
        mkr_y_data[t] = v - 0.5
    mkr_x = interface.KeyframeData(data=mkr_x_data)
    mkr_y = interface.KeyframeData(data=mkr_y_data)
    mkr_enable = mkr_data.get_enable()
    mkr_weight = mkr_data.get_weight()

    # TODO: Reduce keyframes, if we can, we don't need per-frame keyframes if
    # the data is the same.

    # Set keyframes.
    __set_attr_keyframes(mkr_node, 'translateX', mkr_x)
    __set_attr_keyframes(mkr_node, 'translateY', mkr_y)
    __set_attr_keyframes(mkr_node, 'enable', mkr_enable)
    __set_attr_keyframes(mkr_node, 'weight', mkr_weight)

    return mkr


def create_nodes(mkr_data_list, cam=None, with_bundles=True):
    """
    Create Markers for all given MarkerData objects
    """
    mkr_list = []
    for mkr_data in mkr_data_list:
        # Create the nodes
        mkr = __create_node(mkr_data, cam, with_bundles)
        if mkr is not None:
            # Set attributes and add into list
            __set_node_data(mkr, mkr_data)
            mkr_list.append(mkr)
    return mkr_list


def update_nodes(mkr_list, mkr_data_list):
    """
    Update the given mkr_list with data from mkr_data_list.
    The length of both lists must match.
    """
    assert len(mkr_list) == len(mkr_data_list)
    raise NotImplementedError
    return mkr_list
