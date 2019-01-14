"""
Set up callbacks for Maya events.
"""

import collections
import maya.OpenMaya as OpenMaya
import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.ui.uiutils as uiutils


TYPE_NEW_SCENE = 'new_scene'
TYPE_ATTRIBUTE = 'attribute'
TYPE_COLLECTION = 'collection'
TYPE_MARKER = 'marker'
TYPE_LIST = [
    TYPE_NEW_SCENE,
    TYPE_ATTRIBUTE,
    TYPE_MARKER,
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
        self._callbacks = collections.defaultdict(
            lambda: collections.defaultdict(set)
        )

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
    msgs = [
        OpenMaya.MSceneMessage.kBeforeNew,
        OpenMaya.MSceneMessage.kBeforeOpen
    ]
    clientData = obj_UI
    func = new_scene_func
    callback_ids = []
    for msg in msgs:
        callback_id = OpenMaya.MSceneMessage.addCallback(
            msg,
            func,
            clientData
        )
        callback_ids.append(callback_id)
    return callback_ids


def add_callbacks_attribute(node_uuid, node_path, update_func):
    """
    Add all callbacks for a node from a 'Attribute' class.

    Many callbacks are created for the node given.

    :param node_uuid: An 'unchanging' unique id for a node, we can
                      refer back to the node without holding a
                      reference to a smart pointer.
    :type node_uuid: str

    :param node_path: The full node path for the node.
    :type node_path: str

    :param update_func: The function pointer to be called each time
                        the a change is made.
    :type update_func: Function

    :return: List of callback ids created.
    :rtype: list of maya.OpenMaya.MCallbackId
    """
    callback_ids = []
    node_mobj = mmapi.get_as_object(node_path)

    # Attribute Changed
    clientData = (node_uuid, update_func)
    callback_id = OpenMaya.MNodeMessage.addAttributeChangedCallback(
        node_mobj,
        attribute_changed_func,
        clientData,
    )
    callback_ids.append(callback_id)

    # Node Name Change
    clientData = (node_uuid, update_func)
    callback_id = OpenMaya.MNodeMessage.addNameChangedCallback(
        node_mobj,
        node_name_changed_func,
        clientData,
    )
    callback_ids.append(callback_id)

    # Node Has Been Deleted
    clientData = (node_uuid, update_func)
    callback_id = OpenMaya.MNodeMessage.addNodeDestroyedCallback(
        node_mobj,
        node_deleted_func,
        clientData,
    )
    callback_ids.append(callback_id)
    return callback_ids


def add_callbacks_to_collection(node_uuid, node_path, update_func):
    """
    Add all callbacks for a node from a 'Collection' class.
    """
    callback_ids = []
    node_mobj = mmapi.get_as_object(node_path)

    clientData = (node_uuid, update_func)
    callback_id = OpenMaya.MObjectSetMessage.addSetMembersModifiedCallback(
        node_mobj,
        membership_change_func,
        clientData,
    )
    callback_ids.append(callback_id)
    return callback_ids


def add_callbacks_to_marker(node_uuid, node_path, update_func):
    """
    Add all callbacks for a node from a 'Marker' class.
    """
    callback_ids = []
    node_mobj = mmapi.get_as_object(node_path)

    # Node Name Change
    clientData = (node_uuid, update_func)
    callback_id = OpenMaya.MNodeMessage.addNameChangedCallback(
        node_mobj,
        node_name_changed_func,
        clientData,
    )
    callback_ids.append(callback_id)

    # Node Has Been Deleted
    clientData = (node_uuid, update_func)
    callback_id = OpenMaya.MNodeMessage.addNodeDestroyedCallback(
        node_mobj,
        node_deleted_func,
        clientData,
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

    :param clientData: Custom data given to the function. Expected to
                       be a tuple of length 2: (node_uuid, update_func)
    :type clientData: (str, function)

    :return: Nothing.
    :rtype: None
    """
    node_uuid = clientData[0]
    update_func = clientData[1]
    if (callback_msg & OpenMaya.MNodeMessage.kConnectionMade
        or callback_msg & OpenMaya.MNodeMessage.kConnectionBroken
        or callback_msg & OpenMaya.MNodeMessage.kAttributeLocked
        or callback_msg & OpenMaya.MNodeMessage.kAttributeUnlocked
        or callback_msg & OpenMaya.MNodeMessage.kAttributeKeyable
        or callback_msg & OpenMaya.MNodeMessage.kAttributeUnkeyable
        or callback_msg & OpenMaya.MNodeMessage.kAttributeRemoved
        or callback_msg & OpenMaya.MNodeMessage.kAttributeRenamed):
        update_func()
    return


def node_name_changed_func(node, prevName, clientData):
    """
    Callback triggered after a node is renamed.

    :param node: The node that has been renamed.
    :type node: OpenMaya.MObject

    :param prevName: The name of the node before the change happened.
    :type prevName: str

    :param clientData: Custom data given to the function. Expected to
                       be a tuple of length 2: (node_uuid, update_func)
    :type clientData: (str, function)

    :return: Nothing.
    :rtype: None
    """
    node_uuid = clientData[0]
    update_func = clientData[1]
    update_func()
    return


def node_deleted_func(clientData):
    """
    Callback triggered after a node is deleted.

    :param clientData: Custom data given to the function. Expected to
                       be a tuple of length 2: (node_uuid, update_func)
    :type clientData: (str, function)

    :return: Nothing.
    :rtype: None
    """
    node_uuid = clientData[0]
    update_func = clientData[1]
    update_func()
    return


def membership_change_func(node_obj, clientData):
    node_uuid = clientData[0]
    update_func = clientData[1]
    update_func()
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
