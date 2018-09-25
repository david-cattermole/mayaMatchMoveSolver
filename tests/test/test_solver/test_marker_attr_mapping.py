"""
Test querying DG relationship information between Markers and Attributes.
"""

import unittest

try:
    import maya.standalone
    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds


import test.test_solver.solverutils as solverUtils
import mmSolver.api as mmapi


VALID_ATTR_TYPES = [
    'double',
    'doubleLinear',
    'doubleAngle',
    'time',
    'float',
]

CAMERA_ATTRS = [
    'nearClipPlane',
    'farClipPlane',
    'focalLength',
    'horizontalFilmAperture',
    'verticalFilmAperture',
    'cameraScale',
    'filmFitOffset',
    'horizontalFilmOffset',
    'verticalFilmOffset',
    'lensSqueezeRatio',
]


def get_full_path_plug(plug):
    node = plug.partition('.')[0]
    attr = plug.partition('.')[-1]
    node = maya.cmds.ls(node, long=True)[0]
    full_path = node + '.' + attr
    return full_path


def find_attrs_affecting_transform(bnd_node, cam_tfm=None):
    """
    Return a list of attributes that affect the world-matrix transform of
    the given node.

    :param bnd_node: The input node to query.
    :param cam_tfm: Optional, the camera that should be considered.
    :return:
    """
    # TODO: Refactor and clean up. Split into multiple functions.

    # get all the parents above this bundle
    parent_nodes = []
    parents = maya.cmds.listRelatives(bnd_node, parent=True, fullPath=True) or []
    parent_nodes += parents
    while len(parents) > 0:
        parents = maya.cmds.listRelatives(parents, parent=True, fullPath=True) or []
        parent_nodes += parents

    nodes = [bnd_node] + parent_nodes
    if cam_tfm is not None:
        cam_tfm_node = maya.cmds.ls(cam_tfm, long=True)[0]
        cam_shp_node = maya.cmds.listRelatives(cam_tfm, shapes=True, fullPath=True)[0]
        if cam_tfm_node not in nodes:
            nodes.append(cam_tfm_node)
        if cam_shp_node not in nodes:
            nodes.append(cam_shp_node)

    plugs = []
    for node in nodes:
        node_type = maya.cmds.nodeType(node)
        attrs = maya.cmds.listAttr(node, leaf=True) or []
        for attr in attrs:
            # Logic to decide if this attribute will affect the node.
            ws = maya.cmds.attributeQuery(attr, node=node, affectsWorldspace=True)
            if node_type == 'camera':
                # If the attribute affects the camera projection matrix, then
                # it's important to us.
                if attr not in CAMERA_ATTRS:
                    continue
            else:
                # All other nodes, skip if world space is not affected
                if ws is False:
                    continue

            node_attr = node + '.' + attr
            settable = maya.cmds.getAttr(node_attr, settable=True)
            if settable is True:
                typ = maya.cmds.getAttr(node_attr, type=True)
                if typ in VALID_ATTR_TYPES:
                    plugs.append(node_attr)
                continue

            # Get plugs connected to this attribute, recursively
            conn_attrs = maya.cmds.listConnections(node_attr, 
                                                   source=True, 
                                                   destination=False, 
                                                   plugs=True) or []
            while len(conn_attrs) > 0:
                node_attr = conn_attrs.pop()
                node_attr = get_full_path_plug(node_attr)
                settable = maya.cmds.getAttr(node_attr, settable=True)
                if settable is True:
                    typ = maya.cmds.getAttr(node_attr, type=True)
                    if typ in VALID_ATTR_TYPES:
                        plugs.append(node_attr)
                    continue

                # Get the plugs that affect this plug.
                tmp_list = maya.cmds.listConnections(node_attr,
                                                     source=True,
                                                     destination=False,
                                                     plugs=True) or []

                # Filter by valid plug types.
                for tmp in tmp_list:
                    node_ = tmp.partition('.')[0]
                    attr_ = tmp.partition('.')[-1]

                    affects_this_plug = maya.cmds.affects(attr_, node_)
                    for attr__ in affects_this_plug:
                        node_attr = node_ + '.' + attr__
                        node_attr = get_full_path_plug(node_attr)
                        conn_attrs += [node_attr]
                conn_attrs = list(set(conn_attrs))  # only unique

    plugs = list(set(plugs))  # only unique
    return plugs


def find_marker_attr_mapping(mkr_list, attr_list):
    mapping = []
    for i, mkr in enumerate(mkr_list):
        # Initialise mapping list size.
        tmp = [False] * len(attr_list)
        mapping.append(tmp)

        bnd = mkr.get_bundle()
        cam = mkr.get_camera()
        mkr_node = mkr.get_node()
        bnd_node = bnd.get_node()
        cam_node = cam.get_transform_node()
        mkr_plugs = find_attrs_affecting_transform(mkr_node, cam_tfm=cam_node)
        bnd_plugs = find_attrs_affecting_transform(bnd_node)
        plugs = list(set(mkr_plugs + bnd_plugs))
        for j, attr in enumerate(attr_list):
            attr_name = attr.get_name()
            mapping[i][j] = attr_name in plugs
    return mapping


# @unittest.skip
class TestMarkerAttrMapping(solverUtils.SolverTestCase):

    def test_find_marker_attr_mapping(self):
        # top level transform
        root = maya.cmds.createNode('transform', name='top1')

        # Camera A, don't parent under the root.
        cam_tfm_a = maya.cmds.createNode('transform',
                                         name='camA_tfm')
        cam_shp_a = maya.cmds.createNode('camera',
                                         name='camA_shp',
                                         parent=cam_tfm_a)
        maya.cmds.setAttr(cam_tfm_a + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm_a + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm_a + '.tz', -5.0)
        cam_a = mmapi.Camera(shape=cam_shp_a)

        # Camera B, parent under the root
        cam_tfm_b = maya.cmds.createNode('transform',
                                         name='camB_tfm',
                                         parent=root)
        cam_shp_b = maya.cmds.createNode('camera',
                                         name='camB_shp',
                                         parent=cam_tfm_b)
        maya.cmds.setAttr(cam_tfm_b + '.tx', 1.0)
        maya.cmds.setAttr(cam_tfm_b + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm_b + '.tz', -5.0)
        cam_b = mmapi.Camera(shape=cam_shp_b)

        # Hierarchy structure
        dummy = maya.cmds.createNode('transform', name='dummy')
        dummy = maya.cmds.ls(dummy, long=True)[0]
        nothing = maya.cmds.createNode('transform', name='nothing')
        nothing = maya.cmds.ls(nothing, long=True)[0]
        top = maya.cmds.createNode('transform', name='top2')
        top = maya.cmds.ls(top, long=True)[0]
        multDivide = maya.cmds.createNode('multiplyDivide', name='multDiv')
        multDivide2 = maya.cmds.createNode('multiplyDivide', name='multDivNotValid')
        child1 = maya.cmds.createNode('transform', name='child1', parent=top)
        child2 = maya.cmds.createNode('transform', name='child2',
                                      parent=child1)
        child1 = maya.cmds.ls(child1, long=True)[0]
        child2 = maya.cmds.ls(child2, long=True)[0]

        # Set up animation and connections
        maya.cmds.setKeyframe(dummy, at='tx', t=1, v=1)
        maya.cmds.setKeyframe(dummy, at='tx', t=10, v=10)
        maya.cmds.connectAttr(dummy + '.tx', child2 + '.ty')
        maya.cmds.connectAttr(dummy + '.tx', child1 + '.tz')
        maya.cmds.connectAttr(dummy + '.ty', top + '.tx')
        maya.cmds.connectAttr(dummy + '.ry', child2 + '.ry')

        maya.cmds.connectAttr(multDivide + '.outputX', dummy + '.ty')
        maya.cmds.connectAttr(multDivide2 + '.outputX', dummy + '.tz')

        maya.cmds.setKeyframe(child2, at='tz', t=1, v=1)
        maya.cmds.setKeyframe(child2, at='tz', t=10, v=10)

        maya.cmds.setKeyframe(top, at='ty', t=1, v=1)
        maya.cmds.setKeyframe(top, at='ty', t=10, v=10)

        maya.cmds.setKeyframe(top, at='tz', t=1, v=1)
        maya.cmds.setKeyframe(top, at='tz', t=10, v=10)

        maya.cmds.setKeyframe(top, at='ry', t=1, v=-90)
        maya.cmds.setKeyframe(top, at='ry', t=10, v=45)

        # Bundle
        bnd = mmapi.Bundle().create_node()
        bundle_tfm = bnd.get_node()
        maya.cmds.setKeyframe(bundle_tfm, at='tx', t=1, v=-1)
        maya.cmds.setKeyframe(bundle_tfm, at='tx', t=10, v=1)
        maya.cmds.parent(bundle_tfm, child2)
        bundle_tfm = bnd.get_node()
        maya.cmds.setAttr(bundle_tfm + '.tx', 5.5)
        maya.cmds.setAttr(bundle_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundle_tfm + '.tz', -25.0)

        # Marker A
        mkr_a = mmapi.Marker().create_node(cam=cam_a, bnd=bnd)
        marker_tfm = mkr_a.get_node()
        maya.cmds.setAttr(marker_tfm + '.tx', 0.0)

        maya.cmds.setAttr(marker_tfm + '.ty', 0.0)

        # Marker B
        mkr_b = mmapi.Marker().create_node(cam=cam_b, bnd=bnd)
        marker_tfm = mkr_b.get_node()
        maya.cmds.setAttr(marker_tfm + '.tx', 0.0)
        maya.cmds.setAttr(marker_tfm + '.ty', 0.0)

        mkr_list = [mkr_a, mkr_b]

        # Attributes
        attr_tx = mmapi.Attribute(bundle_tfm + '.tx')
        attr_ty = mmapi.Attribute(bundle_tfm + '.ty')
        attr_top_tz = mmapi.Attribute(top + '.tz')

        attr_top_rx = mmapi.Attribute(top + '.rx')
        attr_child1_ty = mmapi.Attribute(child1 + '.ty')
        attr_child1_rx = mmapi.Attribute(child1 + '.rx')

        attr_root_ty = mmapi.Attribute(root + '.ty')
        attr_cam_a_ty = mmapi.Attribute(cam_tfm_a + '.ty')
        attr_cam_a_focal = mmapi.Attribute(cam_shp_a + '.focalLength')

        attr_nothing_tx = mmapi.Attribute(nothing + '.tx')

        attr_list = [
            attr_tx,
            attr_ty,
            attr_top_tz,

            attr_top_rx,
            attr_child1_ty,
            attr_child1_rx,

            attr_root_ty,
            attr_cam_a_ty,
            attr_cam_a_focal,

            attr_nothing_tx,
        ]

        # Test getting affected plugs from a base transform node.
        bnd_node = bnd.get_node()
        ret = find_attrs_affecting_transform(bnd_node)
        assert (multDivide + '.input1X') in ret
        assert (dummy + '.translateX') in ret
        assert (dummy + '.rotateY') in ret
        assert (dummy + '.translateY') not in ret
        for r in ret:
            assert multDivide2 not in r
        assert len(ret) == 106

        # Test again, with the refactored API function.
        ret = mmapi.find_attrs_affecting_transform(bnd_node)
        assert (multDivide + '.input1X') in ret
        assert (dummy + '.translateX') in ret
        assert (dummy + '.rotateY') in ret
        assert (dummy + '.translateY') not in ret
        for r in ret:
            assert multDivide2 not in r
        assert len(ret) == 106

        # Test getting the affect mapping between markers and attrs.
        ret = find_marker_attr_mapping(mkr_list, attr_list)
        expected = [
            [True, True, True, True, True, True, False, True, True, False],
            [True, True, True, True, True, True, True, False, False, False]
        ]
        assert ret == expected

        # Test again, with the refactored API function.
        ret = mmapi.find_marker_attr_mapping(mkr_list, attr_list)
        expected = [
            [True, True, True, True, True, True, False, True, True, False],
            [True, True, True, True, True, True, True, False, False, False]
        ]
        assert ret == expected

        # Save the output
        path = self.get_data_path('find_marker_attr_mapping_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        return


if __name__ == '__main__':
    prog = unittest.main()
