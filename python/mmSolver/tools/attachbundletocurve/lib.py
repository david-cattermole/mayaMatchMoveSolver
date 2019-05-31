"""
Attach Bundle to Curve tool. Attaches a bundle node to a NURBs curve.
"""

import maya.cmds
import mmSolver.logger
import mmSolver.api as mmapi

LOG = mmSolver.logger.get_logger()


def _lerp(a, b, f):
    return a + f * (b - a)


def get_nurbs_curve_nodes(sel):
    """
    """
    crv_shp_nodes = []
    for node in sel:
        node_type = maya.cmds.nodeType(node)
        if node_type == 'transform':
            shps = maya.cmds.listRelatives(
                node,
                shapes=True,
                type='nurbsCurve') or []
            crv_shp_nodes += shps
        elif node_type == 'nurbsCurve':
            crv_shp_nodes.append(node)
    crv_shp_nodes = list(set(crv_shp_nodes))
    return crv_shp_nodes


def get_closest_point_on_nurbs_curve(pos, crv_shp_node):
    """
    """
    assert isinstance(pos, (tuple, list))
    assert len(pos) == 3
    assert maya.cmds.objExists(crv_shp_node)

    node = maya.cmds.createNode('nearestPointOnCurve')
    try:
        crv_min = maya.cmds.getAttr(crv_shp_node + '.minValue')
        crv_max = maya.cmds.getAttr(crv_shp_node + '.maxValue')
        
        src = crv_shp_node + '.worldSpace[0]'
        dst = node + '.inputCurve'
        maya.cmds.connectAttr(src, dst)

        maya.cmds.setAttr(node + '.inPosition', pos)
        closest_pos = maya.cmds.getAttr(node + '.position')
        closest_param = maya.cmds.getAttr(node + '.parameter')
        closest_param = _lerp(crv_min, crv_max, closest_param)
    finally:
        maya.cmds.delete(node)
    return closest_pos, closest_param


def connect_transform_to_nurbs_curve(tfm_node, crv_shp_node, attr_name):
    """
    Connect a transform node to a NURBS curve.
    """
    assert maya.cmds.objExists(tfm_node)
    assert maya.cmds.objExists(crv_shp_node)

    maya.cmds.addAttr(
        tfm_node,
        longName=attr_name,
        attributeType='double',
        minValue=0.0,
        maxValue=100.0,
        defaultValue=50.0,
        keyable=True)

    info_node = maya.cmds.createNode('pointOnCurveInfo')
    src = crv_shp_node + '.worldSpace[0]'
    dst = info_node + '.inputCurve'
    maya.cmds.connectAttr(src, dst)
    
    mult_node = maya.cmds.createNode('multiplyDivide')
    maya.cmds.setAttr(mult_node + '.input2X', 0.01)
    src = mult_node + '.outputX'
    dst = info_node + '.parameter'
    maya.cmds.connectAttr(src, dst)

    src = tfm_node + '.' + attr_name
    dst = mult_node + '.input1X'
    maya.cmds.connectAttr(src, dst)
    return info_node


def attach_bundle_to_curve(bnd_node, crv_shp_node, attr_name):
    pos = maya.cmds.xform(
        bnd_node,
        query=True,
        worldSpace=True,
        translation=True)
    crv_pos, crv_param = get_closest_point_on_nurbs_curve(
        pos,
        crv_shp_node)
    connect_transform_to_nurbs_curve(
        bnd_node,
        crv_shp_node,
        attr_name)
    value = crv_param * 100.0
    plug = bnd_node + '.' + attr_name
    maya.cmds.setAttr(plug, value)
    return

