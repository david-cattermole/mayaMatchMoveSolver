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
Set up callbacks for Maya events.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.ui.uiutils as uiutils
import mmSolver.utils.node as node_utils
import mmSolver.utils.event as event_utils

TYPE_NEW_SCENE = 'new_scene'
TYPE_SELECTION_CHANGED = 'selection_changed'
TYPE_ATTRIBUTE = 'attribute'
TYPE_COLLECTION = 'collection'
TYPE_MARKER = 'marker'
TYPE_LINE = 'line'
TYPE_LIST = [
    TYPE_NEW_SCENE,
    TYPE_SELECTION_CHANGED,
    TYPE_ATTRIBUTE,
    TYPE_MARKER,
    TYPE_LINE,
    TYPE_COLLECTION,
]

LOG = mmSolver.logger.get_logger()


class CallbackManager(object):
    """
    Stores Callback information used inside the Solver tool.

    The Callback Manager maintains the state of callback registration
    data structure, but does not perform any operations such as adding
    or removing Maya callbacks.

    .. note::
        The relative order of Callback Ids is not guaranteed!
    """

    def __init__(self):
        """
        Constructor does not require any arguments.
        """
        # Two nested dictionaries, with a list of callbacks.
        #
        # Level 0 key = callback_type
        # Level 1 key = node_uuid (or None if no node is used)
        # Level 2 set = Set of callback ids for the callback_type and node_uuid
        self._callbacks = collections.defaultdict(lambda: collections.defaultdict(set))

    def __del__(self):
        callback_ids = list(self.get_all_ids())
        remove_callbacks(callback_ids)

    def get_all_ids(self):
        all_callback_ids = set()
        msg = 'CallbackManager.get_all_ids: type=%r node=%r id=%r'
        for callback_type, nodes in self._callbacks.items():
            for node_uuid, callback_ids in nodes.items():
                all_callback_ids |= set(callback_ids)
                for callback_id in callback_ids:
                    LOG.warning(msg, callback_type, node_uuid, callback_id)
        return list(all_callback_ids)

    def add_node_ids(self, callback_type, node_uuid, callback_ids):
        assert callback_type in TYPE_LIST
        ids = set(self._callbacks[callback_type][node_uuid])
        self._callbacks[callback_type][node_uuid] = ids | set(callback_ids)
        return

    def get_types(self):
        return list(self._callbacks.keys())

    def get_type_nodes(self, callback_type):
        return list(self._callbacks[callback_type].keys())

    def get_type_node_ids(self, callback_type, node_uuid):
        return self._callbacks[callback_type][node_uuid]

    def remove_type_node_ids(self, callback_type, node_uuid):
        self._callbacks[callback_type][node_uuid] = set()
        return

    def type_has_node(self, callback_type, node_uuid):
        callback_ids = self.get_type_node_ids(callback_type, node_uuid)
        return len(callback_ids) > 0


def remove_callbacks(callback_ids):
    """
    Remove Maya Callbacks for 'New scene'

    :param callback_ids: List of callback ids to be removed.
    :type callback_ids: list of maya.OpenMaya.MCallbackId

    :return: Nothing.
    :rtype: None
    """
    for callback_id in callback_ids:
        OpenMaya.MMessage.removeCallback(callback_id)
    return


def add_callbacks_new_scene(obj_UI):
    """
    Create callback to be run just before a new Maya scene is created.

    :param obj_UI: The Solver Window that should be closed when a new
                   scene is created.
    :type obj_UI: mmSolver.tools.solver.ui.solver_window.SolverWindow

    :return: Maya callback ids.
    :rtype: list of maya.OpenMaya.MCallbackId
    """
    msgs = [OpenMaya.MSceneMessage.kBeforeNew, OpenMaya.MSceneMessage.kBeforeOpen]
    clientData = obj_UI
    func = new_scene_func
    callback_ids = []
    for msg in msgs:
        callback_id = OpenMaya.MSceneMessage.addCallback(msg, func, clientData)
        callback_ids.append(callback_id)
    return callback_ids


def add_callbacks_attribute(node_uuid, node_path):
    """
    Add all callbacks for a node from a 'Attribute' class.

    Many callbacks are created for the node given.

    :param node_uuid: An 'unchanging' unique id for a node, we can
                      refer back to the node without holding a
                      reference to a smart pointer.
    :type node_uuid: str

    :param node_path: The full node path for the node.
    :type node_path: str

    :return: List of callback ids created.
    :rtype: list of maya.OpenMaya.MCallbackId
    """
    callback_ids = []
    node_mobj = node_utils.get_as_object(node_path)

    # Attribute Changed
    clientData = node_uuid
    callback_id = OpenMaya.MNodeMessage.addAttributeChangedCallback(
        node_mobj,
        attribute_changed_func,
        clientData,
    )
    callback_ids.append(callback_id)

    # Node Name Change
    clientData = node_uuid
    callback_id = OpenMaya.MNodeMessage.addNameChangedCallback(
        node_mobj,
        node_name_changed_func,
        clientData,
    )
    callback_ids.append(callback_id)

    # Node Has Been Deleted
    clientData = node_uuid
    callback_id = OpenMaya.MNodeMessage.addNodeDestroyedCallback(
        node_mobj,
        node_deleted_func,
        clientData,
    )
    callback_ids.append(callback_id)
    return callback_ids


def add_callbacks_to_collection(node_uuid, node_path):
    """
    Add all callbacks for a node from a 'Collection' class.

    :return: List of callback ids created.
    :rtype: list of maya.OpenMaya.MCallbackId
    """
    callback_ids = []
    node_mobj = node_utils.get_as_object(node_path)

    clientData = node_uuid
    callback_id = OpenMaya.MObjectSetMessage.addSetMembersModifiedCallback(
        node_mobj,
        membership_change_func,
        clientData,
    )
    callback_ids.append(callback_id)
    return callback_ids


def add_callbacks_to_marker(node_uuid, node_path):
    """
    Add all callbacks for a node from a 'Marker' class.

    .. todo::

        - Add callback when parenting changes (marker may
          not live under camera anymore), specific to marker
          objects.

    :return: List of callback ids created.
    :rtype: list of maya.OpenMaya.MCallbackId
    """
    callback_ids = []
    node_mobj = node_utils.get_as_object(node_path)

    # Attribute Changed (if a marker/bundle relationship is changed.)
    clientData = node_uuid
    callback_id = OpenMaya.MNodeMessage.addAttributeChangedCallback(
        node_mobj,
        attribute_connection_changed_func,
        clientData,
    )
    callback_ids.append(callback_id)

    # Node Name Change
    clientData = node_uuid
    callback_id = OpenMaya.MNodeMessage.addNameChangedCallback(
        node_mobj,
        node_name_changed_func,
        clientData,
    )
    callback_ids.append(callback_id)

    # Node Has Been Deleted
    # TODO: This callback does not seem to be doing anything.
    clientData = node_uuid
    callback_id = OpenMaya.MNodeMessage.addNodeDestroyedCallback(
        node_mobj,
        node_deleted_func,
        clientData,
    )
    callback_ids.append(callback_id)
    return callback_ids


def add_callbacks_to_line(node_uuid, node_path):
    """
    Add all callbacks for a node from a 'Line' class.

    .. todo::

        - Add callback when parenting changes (line may
          not live under camera anymore), specific to marker
          objects.

    :return: List of callback ids created.
    :rtype: list of maya.OpenMaya.MCallbackId
    """
    callback_ids = []
    node_mobj = node_utils.get_as_object(node_path)

    # Attribute Changed (if a marker/bundle relationship is changed.)
    clientData = node_uuid
    callback_id = OpenMaya.MNodeMessage.addAttributeChangedCallback(
        node_mobj,
        attribute_connection_changed_func,
        clientData,
    )
    callback_ids.append(callback_id)

    # Node Name Change
    clientData = node_uuid
    callback_id = OpenMaya.MNodeMessage.addNameChangedCallback(
        node_mobj,
        node_name_changed_func,
        clientData,
    )
    callback_ids.append(callback_id)

    # Node Has Been Deleted
    # TODO: This callback does not seem to be doing anything.
    clientData = node_uuid
    callback_id = OpenMaya.MNodeMessage.addNodeDestroyedCallback(
        node_mobj,
        node_deleted_func,
        clientData,
    )
    callback_ids.append(callback_id)
    return callback_ids


def add_callbacks_to_marker_group(node_uuid, node_path):
    """
    Add all callbacks for a node from a 'MarkerGroup' class.

    :return: List of callback ids created.
    :rtype: list of maya.OpenMaya.MCallbackId
    """
    callback_ids = []
    node_mobj = node_utils.get_as_object(node_path)

    # Node Has Been Deleted
    # TODO: This callback does not seem to be doing anything.
    clientData = node_uuid
    callback_id = OpenMaya.MNodeMessage.addNodeDestroyedCallback(
        node_mobj,
        node_deleted_func,
        clientData,
    )
    callback_ids.append(callback_id)
    return callback_ids


def add_callbacks_to_bundle(node_uuid, node_path):
    """
    Add all callbacks for a node from a 'Bundle' class.

    :return: List of callback ids created.
    :rtype: list of maya.OpenMaya.MCallbackId
    """
    callback_ids = []
    node_mobj = node_utils.get_as_object(node_path)

    # Attribute Changed (if a marker/bundle relationship is changed.)
    clientData = node_uuid
    callback_id = OpenMaya.MNodeMessage.addAttributeChangedCallback(
        node_mobj,
        attribute_connection_changed_func,
        clientData,
    )
    callback_ids.append(callback_id)

    # Node Name Change
    clientData = node_uuid
    callback_id = OpenMaya.MNodeMessage.addNameChangedCallback(
        node_mobj,
        node_name_changed_func,
        clientData,
    )
    callback_ids.append(callback_id)

    # Node Has Been Deleted
    clientData = node_uuid
    callback_id = OpenMaya.MNodeMessage.addNodeDestroyedCallback(
        node_mobj,
        node_deleted_func,
        clientData,
    )
    callback_ids.append(callback_id)
    return callback_ids


def add_callbacks_to_camera(node_uuid, node_path):
    """
    Add all callbacks for a node from a 'Camera' class.

    :return: List of callback ids created.
    :rtype: list of maya.OpenMaya.MCallbackId
    """
    callback_ids = []
    node_mobj = node_utils.get_as_object(node_path)

    # Node Name Change
    clientData = node_uuid
    callback_id = OpenMaya.MNodeMessage.addNameChangedCallback(
        node_mobj,
        node_name_changed_func,
        clientData,
    )
    callback_ids.append(callback_id)

    # Node Has Been Deleted
    clientData = node_uuid
    callback_id = OpenMaya.MNodeMessage.addNodeDestroyedCallback(
        node_mobj,
        node_deleted_func,
        clientData,
    )
    callback_ids.append(callback_id)
    return callback_ids


def add_selection_changed_callback(obj_UI):
    """
    Add a selection event callback to Maya.

    Note we can get all Event Message and Condition names::

    >>> import maya.OpenMaya as OpenMaya
    >>> array = []
    >>> OpenMaya.MEventMessage.getEventNames(array)
    >>> for x in sorted(array): print(x)
    >>> OpenMaya.MConditionMessage.getConditionNames(array)
    >>> for x in sorted(array): print(x)
    >>>

    :param obj_UI: Expected to be an instance of the Solver UI
                   window class (Qt).
    :type obj_UI: SolverWindow

    :return: List of callback ids created.
    :rtype: list of maya.OpenMaya.MCallbackId
    """
    callback_ids = []

    clientData = obj_UI
    func = selection_changed_func
    callback_id = OpenMaya.MEventMessage.addEventCallback(
        "SelectionChanged", func, clientData
    )

    callback_ids.append(callback_id)
    return callback_ids


def attribute_changed_func(callback_msg, plugA, plugB, clientData):
    """
    Callback triggered when an event happens to an attribute on a node.

    One callback handles many attributes and event types for one node.
    The callback is linked to the node, not the attribute.

    :param callback_msg: The type of callback message.
    :type callback_msg: OpenMaya.MNodeMessage.AttributeMessage

    :param plugA: First plug related to callback.
    :type plugA: OpenMaya.MPlug

    :param plugB: Second plug related to callback, may not be used if
                  not relevant to callback type.
    :type plugB: OpenMaya.MPlug

    :param clientData: node_uuid given to the function.
    :type clientData: str

    :return: Nothing.
    :rtype: None
    """
    if (
        callback_msg & OpenMaya.MNodeMessage.kConnectionMade
        or callback_msg & OpenMaya.MNodeMessage.kConnectionBroken
        or callback_msg & OpenMaya.MNodeMessage.kAttributeLocked
        or callback_msg & OpenMaya.MNodeMessage.kAttributeUnlocked
        or callback_msg & OpenMaya.MNodeMessage.kAttributeKeyable
        or callback_msg & OpenMaya.MNodeMessage.kAttributeUnkeyable
        or callback_msg & OpenMaya.MNodeMessage.kAttributeRemoved
        or callback_msg & OpenMaya.MNodeMessage.kAttributeRenamed
    ):
        if mmapi.is_solver_running() is True:
            return
        node_uuid = clientData
        event_utils.trigger_event(
            mmapi.EVENT_NAME_ATTRIBUTE_STATE_CHANGED, node=node_uuid, plug=plugA
        )
    return


def attribute_connection_changed_func(callback_msg, plugA, plugB, clientData):
    """
    Callback triggered when an event happens to an attribute on a node.

    One callback handles many attributes and event types for one node.
    The callback is linked to the node, not the attribute.

    :param callback_msg: The type of callback message.
    :type callback_msg: OpenMaya.MNodeMessage.AttributeMessage

    :param plugA: First plug related to callback.
    :type plugA: OpenMaya.MPlug

    :param plugB: Second plug related to callback, may not be used if
                  not relevant to callback type.
    :type plugB: OpenMaya.MPlug

    :param clientData: node_uuid given to the function.
    :type clientData: str

    :return: Nothing.
    :rtype: None
    """
    node_uuid = clientData
    if (
        callback_msg & OpenMaya.MNodeMessage.kConnectionMade
        or callback_msg & OpenMaya.MNodeMessage.kConnectionBroken
        or callback_msg & OpenMaya.MNodeMessage.kAttributeRemoved
    ):
        event_utils.trigger_event(
            mmapi.EVENT_NAME_ATTRIBUTE_CONNECTION_CHANGED, node=node_uuid, plug=plugA
        )
    return


def node_name_changed_func(node, prevName, clientData):
    """
    Callback triggered after a node is renamed.

    :param node: The node that has been renamed.
    :type node: OpenMaya.MObject

    :param prevName: The name of the node before the change happened.
    :type prevName: str

    :param clientData: node_uuid given to the function.
    :type clientData: str

    :return: Nothing.
    :rtype: None
    """
    node_uuid = clientData
    LOG.debug('node_name_changed: %r', node_uuid)
    event_utils.trigger_event(
        mmapi.EVENT_NAME_NODE_NAME_CHANGED, node=node_uuid, previous_name=prevName
    )
    return


def node_deleted_func(clientData):
    """
    Callback triggered *after* a node is deleted.

    :param clientData: node_uuid given to the function.
    :type clientData: str

    :return: Nothing.
    :rtype: None
    """
    node_uuid = clientData
    LOG.debug('node_deleted: %r', node_uuid)
    event_utils.trigger_event(mmapi.EVENT_NAME_NODE_DELETED, node=node_uuid)
    return


def membership_change_func(node_obj, clientData):
    node_uuid = clientData
    LOG.debug('membership_changed: %r', node_uuid)
    event_utils.trigger_event(mmapi.EVENT_NAME_MEMBERSHIP_CHANGED, node=node_uuid)
    return


def new_scene_func(clientData):
    """
    Create a callback called just before a new scene file is created
    or before a new file is loaded. The UI must be closed. All data
    structures stored must be removed.

    :param clientData: The Qt window object class.
    :type clientData: SolverWindow

    :return: Nothing.
    :rtype: None
    """
    try:
        valid = uiutils.isValidQtObject(clientData)
        if clientData is not None and valid is True:
            clientData.close()
    except RuntimeError:
        msg = 'New Maya Scene callback failed to close UI: ui=%r'
        LOG.warning(msg, clientData)
    return


def selection_changed_func(clientData):
    """The Maya selection has changed, we must synchronize the Maya
    selection with the Solver UI.

    :param clientData: The Qt window object class.
    :type clientData: SolverWindow

    :return: Nothing.
    :rtype: None
    """
    if mmapi.is_solver_running() is True:
        return
    sel_uuids = maya.cmds.ls(selection=True, uuid=True) or []
    valid = uiutils.isValidQtObject(clientData)
    if clientData is not None and valid is True:
        clientData.setNodeSelection(sel_uuids)
    return
