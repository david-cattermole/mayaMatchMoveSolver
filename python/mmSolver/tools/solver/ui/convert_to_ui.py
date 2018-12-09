"""
Convert mmSolver API objects into UI objects that can be used in Qt models.
"""

import mmSolver.logger
import mmSolver.tools.solver.lib.solver_step as solver_step
import mmSolver.tools.solver.ui.attr_nodes as attr_nodes
import mmSolver.tools.solver.ui.object_nodes as object_nodes
import mmSolver.tools.solver.ui.solver_nodes as solver_nodes


LOG = mmSolver.logger.get_logger()


def markersToUINodes(mkr_list):
    # TODO: Get related objects such as camera and marker group
    # and create ObjectNodes for each type.
    root = object_nodes.ObjectNode('root')
    for mkr in mkr_list:
        name = mkr.get_node()
        name = name.rpartition('|')[-1]
        mkr_grp = mkr.get_marker_group()
        cam = mkr.get_camera()
        LOG.debug('mkr node: %r', name)
        data = {'marker': mkr}
        object_nodes.MarkerNode(name, data=data, parent=root)
    return root


def attributesToUINodes(attr_list):
    root = attr_nodes.PlugNode('root')
    maya_nodes = dict()
    for attr in attr_list:
        n = attr.get_node()
        a = attr.get_attr()
        maya_node = maya_nodes.get(n)
        if maya_node is None:
            data = {'data': None}
            maya_node = attr_nodes.MayaNode(n, data=data, parent=root)
            maya_nodes[n] = maya_node
        data = {'data': attr}
        attr_node = attr_nodes.AttrNode(a, data=data, parent=maya_node)
    return root


def solverStepsToUINodes(step_list, col):
    node_list = []
    for step in step_list:
        assert isinstance(step, solver_step.SolverStep) is True
        name = step.get_name()
        node = solver_nodes.SolverStepNode(name, col)
        node_list.append(node)
    return node_list

