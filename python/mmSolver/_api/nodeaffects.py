"""
Query DG relationship information.
"""

import maya.cmds


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


def _get_full_path_plug(plug):
    node = plug.partition('.')[0]
    attr = plug.partition('.')[-1]
    attr = maya.cmds.attributeName(plug, long=True)
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
    bnd_node = maya.cmds.ls(bnd_node, long=True)[0]

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
                node_attr = _get_full_path_plug(node_attr)
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
                        node_attr = _get_full_path_plug(node_attr)
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


def find_marker_attr_mapping_raw(mkr_list, attr_list):
    mapping = []
    for i, mkr in enumerate(mkr_list):
        # Initialise mapping list size.
        tmp = [False] * len(attr_list)
        mapping.append(tmp)

        mkr_node = mkr[0]
        bnd_node = mkr[2]
        cam_node = maya.cmds.listRelatives(mkr[1], parent=True)[0]
        # mkr_plugs = find_attrs_affecting_transform(mkr_node, cam_tfm=cam_node)
        mkr_plugs = []
        bnd_plugs = find_attrs_affecting_transform(bnd_node)
        plugs = list(set(mkr_plugs + bnd_plugs))
        for j, attr_name in enumerate(attr_list):
            # print 'attr_name', attr_name
            # attr = maya.cmds.attributeName(attr_name, long=True)
            attr_name = _get_full_path_plug(attr_name)
            mapping[i][j] = attr_name in plugs
            # if mapping[i][j] is True:
            #     print 'attr_name in plugs:', attr_name
            # if mapping[i][j] is False:
            #     print 'attr_name not in plugs:', attr_name
    return mapping
