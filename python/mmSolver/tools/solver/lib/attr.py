"""
Attribute functions
"""

import maya.cmds
import mmSolver.logger
import mmSolver.tools.solver.maya_callbacks as maya_callbacks

LOG = mmSolver.logger.get_logger()


def get_attributes_from_collection(col):
    return col.get_attribute_list()


def add_attributes_to_collection(attr_list, col):
    return col.add_attribute_list(attr_list)


def remove_attr_from_collection(attr_list, col):
    return col.remove_attribute_list(attr_list)


def add_callbacks_to_attributes(attr_list, update_func, callback_manager):
    msg = 'Node UUID has multiple paths: node=%r node_uuids=%r'
    callback_type = maya_callbacks.TYPE_ATTRIBUTE
    for attr_obj in attr_list:
        node_path = attr_obj.get_node(full_path=True)
        node_uuids = maya.cmds.ls(node_path, uuid=True) or []
        if len(node_uuids) != 1:
            LOG.warning(msg, node_path, node_uuids)
            continue
        node_uuid = node_uuids[0]
        if callback_manager.type_has_node(callback_type, node_uuid) is True:
            continue
        callback_ids = maya_callbacks.add_callbacks_attribute(
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


def remove_callbacks_from_attributes(attr_list, callback_manager):
    msg = 'Node UUID has multiple paths: node=%r node_uuids=%r'
    callback_type = maya_callbacks.TYPE_ATTRIBUTE
    for attr_obj in attr_list:
        node_path = attr_obj.get_node(full_path=True)
        node_uuids = maya.cmds.ls(node_path, uuid=True) or []
        if len(node_uuids) != 1:
            LOG.warning(msg, node_path, node_uuids)
            continue
        node_uuid = node_uuids[0]
        if callback_manager.type_has_node(callback_type, node_uuid) is False:
            msg = 'Node does not have callback type assigned: '
            msg += 'callback_type=%r node_path=%r'
            LOG.warning(msg, callback_type, node_path)
            continue
        callback_manager.remove_type_node_ids(
            callback_type,
            node_uuid,
        )
    return
