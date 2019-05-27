"""
Convert mmSolver API objects into UI objects that can be used in Qt models.
"""

import mmSolver.logger
import mmSolver.tools.solver.lib.solver_step as solver_step
import mmSolver.tools.solver.ui.attr_nodes as attr_nodes
import mmSolver.tools.solver.ui.object_nodes as object_nodes
import mmSolver.tools.solver.ui.solver_nodes as solver_nodes


LOG = mmSolver.logger.get_logger()


def markersToUINodes(mkr_list, show_cam, show_mkr, show_bnd):
    """
    Convert a list of markers into a hierarchy to show the user.
    """
    assert isinstance(show_cam, bool)
    assert isinstance(show_mkr, bool)
    assert isinstance(show_bnd, bool)
    root = object_nodes.ObjectNode('root')
    cam_nodes_store = {}
    for mkr in mkr_list:
        mkr_name = mkr.get_node()
        mkr_name = mkr_name.rpartition('|')[-1]
        cam = mkr.get_camera()
        bnd = mkr.get_bundle()

        # Get camera
        if show_cam is False:
            cam_node = root
        else:
            cam_shp_node = cam.get_shape_node()
            cam_name = cam.get_shape_node()
            cam_name = cam_name.rpartition('|')[-1]
            cam_node = None
            if cam_shp_node not in cam_nodes_store:
                data = {
                    'marker': mkr,
                    'camera': cam,
                }
                cam_node = object_nodes.CameraNode(cam_name, data=data, parent=root)
                cam_nodes_store[cam_shp_node] = cam_node
            else:
                cam_node = cam_nodes_store[cam_shp_node]
        assert cam_node is not None

        # The marker.
        mkr_node = cam_node
        if show_mkr is True:
            data = {
                'marker': mkr,
                'camera': cam,
            }
            mkr_node = object_nodes.MarkerNode(mkr_name, data=data, parent=cam_node)

        # Get Bundle under marker.
        if bnd is None:
            continue
        if show_bnd is False:
            continue
        bnd_name = bnd.get_node()
        bnd_name = bnd_name.rpartition('|')[-1]
        data = {
            'marker': mkr,
            'bundle': bnd,
            'camera': cam,
        }
        assert mkr_node is not None
        bnd_node = object_nodes.BundleNode(bnd_name, data=data, parent=mkr_node)
    return root


def attributesToUINodes(attr_list, show_anm, show_stc, show_lck):
    """
    Convert a list of mmSolver API Attributes into classes to be used
    in the Solver UI.

    :param attr_list: List of Attributes to convert.
    :type attr_list: [Attribute, ..]

    :param show_anm: Should the animated attributes be visible?
    :type show_anm: bool

    :param show_stc: Should the static attributes be visible?
    :type show_stc: bool

    :param show_lck: Should the locked attributes be visible?
    :type show_lck: bool

    :returns: A hierarchy of UI nodes to be viewed in a 'tree view'.
    :rtype: PlugNode
    """
    root = attr_nodes.PlugNode('root')
    maya_nodes = dict()
    for attr in attr_list:
        n = attr.get_node()
        if attr.is_animated() is True and show_anm is False:
            continue
        elif attr.is_static() is True and show_stc is False:
            continue
        elif attr.is_locked() is True and show_lck is False:
            continue
        maya_node = maya_nodes.get(n)
        data = {'data': attr}
        if maya_node is None:
            maya_node = attr_nodes.MayaNode(n, data=data, parent=root)
            maya_nodes[n] = maya_node
        a = attr.get_attr()
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
