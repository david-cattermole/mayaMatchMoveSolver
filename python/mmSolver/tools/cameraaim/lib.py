"""
Aim the selected transform nodes at the current viewport's camera.
"""

import maya.cmds
import mmSolver.logger


LOG = mmSolver.logger.get_logger()
 

def aim_at_target(nodes, target, remove_after=None):
    """
    Aims the selected transforms at the target transform node.

    """
    assert maya.cmds.nodeType(target) == 'transform'
    assert isinstance(nodes, (list, tuple))
    if remove_after is None:
        remove_after = True
    constraint_list = []
    for node in nodes:
        for attr in ['rx', 'ry', 'rz']:
            # TODO: Check if the node is referenced or not.
            maya.cmds.setAttr(node + '.' + attr, lock=False)
        aim = maya.cmds.aimConstraint(
            target,
            node,
            offset=(0, 0, 0),
            weight=1.0,
            aimVector=(1, 0, 0),
            upVector=(0, 1, 0),
            worldUpType='vector',
            worldUpVector=(0, 1, 0)
        )
        constraint_list.append(aim[0])

    # Delete all constraints
    if remove_after is True:
        cons_list = [n
                     for n in constraint_list
                     if maya.cmds.objExists(n) is True]
        if len(cons_list) > 0:
            maya.cmds.delete(cons_list)
    return
