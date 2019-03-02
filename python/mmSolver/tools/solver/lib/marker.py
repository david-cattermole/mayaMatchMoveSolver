"""
Marker functions.
"""

import maya.cmds
import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.solver.maya_callbacks as maya_callbacks


LOG = mmSolver.logger.get_logger()


def add_markers_to_collection(mkr_list, col):
    if isinstance(col, mmapi.Collection) is False:
        msg = 'col argument must be a Collection: %r'
        raise TypeError(msg % col)
    col.add_marker_list(mkr_list)
    return


def remove_markers_from_collection(mkr_list, col):
    return col.remove_marker_list(mkr_list)


def get_markers_from_collection(col):
    return col.get_marker_list()


def _add_callback_to_any_node(callback_manager, callback_type, node_path, add_callbacks_func, update_func):
    msg = 'Node UUID has multiple paths: node=%r node_uuids=%r'
    node_uuids = maya.cmds.ls(node_path, uuid=True) or []
    if len(node_uuids) != 1:
        LOG.warning(msg, node_path, node_uuids)
        return
    node_uuid = node_uuids[0]
    if callback_manager.type_has_node(callback_type, node_uuid) is True:
        return
    callback_ids = add_callbacks_func(
            node_uuid,
            node_path,
            update_func,
        )
    callback_manager.add_node_ids(
        callback_type,
        node_uuid,
        callback_ids,
    )
    return


def add_callbacks_to_markers(mkr_list, update_func, callback_manager):
    callback_type = maya_callbacks.TYPE_MARKER
    for mkr_obj in mkr_list:
        # Marker
        mkr_node_path = mkr_obj.get_node()
        _add_callback_to_any_node(
            callback_manager,
            callback_type,
            mkr_node_path,
            maya_callbacks.add_callbacks_to_marker,
            update_func)

        # Bundle
        bnd_obj = mkr_obj.get_bundle()
        bnd_node_path = bnd_obj.get_node()
        _add_callback_to_any_node(
            callback_manager,
            callback_type,
            bnd_node_path,
            maya_callbacks.add_callbacks_to_bundle,
            update_func)

        # Marker Group
        mkrgrp_obj = mkr_obj.get_marker_group()
        mkrgrp_node_path = mkrgrp_obj.get_node()
        _add_callback_to_any_node(
            callback_manager,
            callback_type,
            mkrgrp_node_path,
            maya_callbacks.add_callbacks_to_marker_group,
            update_func)

        # Camera Transform
        cam_obj = mkr_obj.get_camera()
        cam_tfm_node_path = cam_obj.get_transform_node()
        _add_callback_to_any_node(
            callback_manager,
            callback_type,
            cam_tfm_node_path, maya_callbacks.add_callbacks_to_camera,
            update_func)

        # Camera Shape
        cam_shp_node_path = cam_obj.get_shape_node()
        _add_callback_to_any_node(
            callback_manager,
            callback_type,
            cam_shp_node_path,
            maya_callbacks.add_callbacks_to_camera,
            update_func)
    return


def remove_callbacks_from_markers(mkr_list, callback_manager):
    msg = 'Node UUID has multiple paths: node=%r node_uuids=%r'
    callback_type = maya_callbacks.TYPE_MARKER
    for mkr_obj in mkr_list:
        bnd_obj = mkr_obj.get_bundle()
        cam_obj = mkr_obj.get_camera()
        mkrgrp_obj = mkr_obj.get_marker_group()

        mkr_node_path = mkr_obj.get_node()
        bnd_node_path = bnd_obj.get_node()
        mkrgrp_node_path = mkrgrp_obj.get_node()
        cam_tfm_node_path = cam_obj.get_transform_node()
        cam_shp_node_path = cam_obj.get_shape_node()
        node_path_list = [
            mkr_node_path,
            bnd_node_path,
            mkrgrp_node_path,
            cam_tfm_node_path,
            cam_shp_node_path,
        ]
        for node_path in node_path_list:
            node_uuids = maya.cmds.ls(node_path, uuid=True) or []
            if len(node_uuids) != 1:
                LOG.warning(msg, node_path, node_uuids)
                continue
            node_uuid = node_uuids[0]
            have_type = callback_manager.type_has_node(callback_type, node_uuid)
            if have_type is False:
                continue
            callback_manager.remove_type_node_ids(
                callback_type,
                node_uuid,
            )
    return
