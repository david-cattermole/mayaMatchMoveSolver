"""
Utilities built around Maya nodes and node paths.
"""
import maya.cmds
import mmSolver.logger

LOG = mmSolver.logger.get_logger()


def get_node_full_path(node):
    full_path = None
    nodes = maya.cmds.ls(node, long=True) or []
    if len(nodes) > 0:
        full_path = nodes[0]
    return full_path


def node_is_referenced(node):
    """
    Is the node given referenced (from a referenced file)?

    :param node: Node to query.

    :return: True or False, is it referenced?
    :rtype: bool
    """
    return maya.cmds.referenceQuery(node, referenceNode=True)


def set_attr(plug, value, relock=False):
    """
    Set a numeric attribute to a value.

    Optionally unlocks and re-locks the plugs.

    :param plug: Node.Attr to set.
    :param value: The ne value to set.
    :param relock: If the plug was already locked, should we set the new
                   value, then re-lock afterward?

    :return:
    """
    node = plug.partition('.')[0]
    is_referenced = node_is_referenced(node)
    locked = maya.cmds.getAttr(plug, locked=True)
    if is_referenced is True and locked is True:
        msg = 'Cannot set attr %r, it is locked and the node is referenced.'
        LOG.warning(msg, plug)
    if is_referenced is False:
        # Make sure the plug is unlocked.
        maya.cmds.setAttr(plug, lock=False)
    maya.cmds.setAttr(plug, value)
    if is_referenced is False and relock is True:
        maya.cmds.setAttr(plug, lock=locked)
    return
