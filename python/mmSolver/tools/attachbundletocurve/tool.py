"""
Attach Bundle to Curve tool. Attaches a bundle node to a NURBs curve.
"""

import maya.cmds
import mmSolver.logger
import mmSolver.tools.selection.filternodes as filternodes
import mmSolver.tools.attachbundletocurve.constant as const
import mmSolver.tools.attachbundletocurve.lib as lib

LOG = mmSolver.logger.get_logger()


def main():
    """
    Renames selected markers and bundles (and the connected nodes).
    """
    selection = maya.cmds.ls(selection=True, long=True) or []
    bnd_nodes = filternodes.get_bundle_nodes(selection)
    crv_shp_nodes = lib.get_nurbs_curve_nodes(selection)
    if len(bnd_nodes) == 0 and len(crv_shp_nodes) != 1:
        msg = 'Please select at least one Bundle and only one NURBS curve.'
        LOG.warning(msg)
        return
    if len(bnd_nodes) > 0 and len(crv_shp_nodes) != 1:
        msg = 'Please select one NURBS curve.'
        LOG.warning(msg)
        return
    if len(bnd_nodes) == 0 and len(crv_shp_nodes) == 1:
        msg = 'Please select at least one Bundle.'
        LOG.warning(msg)
        return

    attr_name = const.ATTR_NAME
    crv_shp_node = crv_shp_nodes[0]
    for bnd_node in bnd_nodes:
        lib.attach_bundle_to_curve(bnd_node, crv_shp_node, attr_name)
    maya.cmds.select(bnd_nodes)
    return
