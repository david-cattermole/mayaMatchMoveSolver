"""
Query DG relationship information.

Use the Maya DG graph structure to determine the sparsity structure,
a relation of cause and effect; which attributes affect which
markers.

Answer this question: 'for each marker, determine which attributes
can affect it's bundle.'

Detect inputs and outputs for marker-bundle relationships. For each
marker, get the bundle, then find all the attributes that affect the
bundle (and it's parent nodes). If the bundle cannot be affected by
any attribute in the solver, print a warning and remove it from the
solve list.

This relationship building will be the basis for the mmSolver
residual/parameter block creation. Note we do not need to worry
about time in our relationship building, connections cannot be made
at different times (and if they did, that would be stupid). This
relationship building could mean we only need to measure a limited
number of bundles, hence improving performance.

There are special cases for detecting inputs/outputs between markers
and attributes.

- Any transform node/attribute above the marker in the DAG that
  affects the world transform.

- Cameras; transform attributes and focal length will affect all
  markers

.. todo:: Calculating node affect relationships is too slow. We need
    to find a way of caching the calculation, so that batches of
    functions that do not change connections can re-use exist
    computations, leading to greater speed ups, at the cost of memory.

"""

import maya.cmds

import mmSolver.logger


LOG = mmSolver.logger.get_logger()

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


__CACHE = dict()


def _get_full_path_plug(plug):
    """
    Get convert a 'name.attr' string into the long name equal.

    :param plug: Name and attribute as a dot-separated string.
    :type plug: str

    :returns: Long name for the given plug.
    :rtype: str
    """
    node = plug.partition('.')[0]
    attr = plug.partition('.')[-1]
    attr = maya.cmds.attributeName(plug, long=True)
    node = maya.cmds.ls(node, long=True)[0]
    full_path = node + '.' + attr
    return full_path


def _clear_query_cache():
    global __CACHE
    __CACHE = dict()
    return


def _get_from_query_cache(key):
    global __CACHE
    return __CACHE.get(key)


def _add_to_query_cache(key, value):
    global __CACHE
    __CACHE[key] = value
    return


def find_plugs_affecting_transform(tfm_node, cam_tfm):
    """
    Find plugs that affect the world-matrix transform of the node.

    :param tfm_node: The input node to query.
    :type tfm_node: str

    :param cam_tfm: The camera that should be considered (optional)
    :type cam_tfm: str or None

    :returns: Set of Maya attributes in 'node.attr' string format.
    :rtype: [str, ..]
    """
    # # Read from cache
    # #
    # # TODO: Cache invalidation is very important here. We cannot use the
    # #  cache if a new object has been added to the Maya scene or for a
    # #  different run of the solver. Each new solve must trigger a fresh
    # #  cache. We could do this by adding a new argument 'solve id'
    # #  and hashing it into the dictionary, which is generated new at
    # #  the start of each new solver.
    # plugs = _get_from_query_cache(args)
    # if plugs is not None:
    #     return plugs
    # tfm_node, cam_tfm = args

    tfm_node = maya.cmds.ls(tfm_node, long=True)[0]

    # Get all the parents above this bundle
    parent_nodes = []
    parents = maya.cmds.listRelatives(
        tfm_node,
        parent=True,
        fullPath=True) or []
    parent_nodes += parents
    while len(parents) > 0:
        parents = maya.cmds.listRelatives(
            parents,
            parent=True,
            fullPath=True) or []
        parent_nodes += parents
    nodes = [tfm_node] + parent_nodes

    # Get camera related to the given bundle.
    if cam_tfm is not None:
        assert maya.cmds.objExists(cam_tfm) is True
        cam_tfm_node = maya.cmds.ls(cam_tfm, long=True)[0]
        cam_shp_node = maya.cmds.listRelatives(
            cam_tfm,
            shapes=True,
            fullPath=True)[0]
        if cam_tfm_node not in nodes:
            nodes.append(cam_tfm_node)
        if cam_shp_node not in nodes:
            nodes.append(cam_shp_node)

    plugs = set()
    for node in nodes:
        node_type = maya.cmds.nodeType(node)
        attrs = maya.cmds.listAttr(node, leaf=True) or []
        for attr in attrs:
            # Logic to decide if this attribute will affect the node.
            ws = maya.cmds.attributeQuery(
                attr,
                node=node,
                affectsWorldspace=True)
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
                    plugs.add(node_attr)
                continue

            # Get plugs connected to this attribute, recursively
            conn_attrs = maya.cmds.listConnections(
                node_attr,
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
                        plugs.add(node_attr)
                    continue

                # Get the plugs that affect this plug.
                tmp_list = maya.cmds.listConnections(
                    node_attr,
                    source=True,
                    destination=False,
                    plugs=True) or []

                # Filter by valid plug types.
                for tmp in tmp_list:
                    node_ = tmp.partition('.')[0]
                    attr_ = tmp.partition('.')[-1]

                    affects_this_plug = maya.cmds.affects(attr_, node_) or []
                    for attr__ in affects_this_plug:
                        node_attr = node_ + '.' + attr__
                        node_attr = _get_full_path_plug(node_attr)
                        conn_attrs += [node_attr]
                # Only unique attributes.
                conn_attrs = list(set(conn_attrs))

    # Only unique plugs.
    plugs = list(set(plugs))

    # Set into cache.
    # _add_to_query_cache(args, plugs)
    return plugs


def find_marker_attr_mapping_raw(mkr_list, attr_list):
    """
    Get a mapping of markers to attributes, as a matrix.

    :param mkr_list: Tuple of marker node, bundle node and camera
                     shape node in a list; each list of nodes
                     represent a single Marker relationship and will
                     be considered in mapping.
    :type mkr_list: [(str, str, str), ..]

    :param attr_list: Maya attributes to consider in mapping, in the
                      familiar 'node.attr' string representation.
    :type attr_list: [str, ..]

    :returns: Boolean matrix of size 'markers x attrs'. Matrix index
              is 'mapping[marker_index][attr_index]', based on the
              index of the mkr_cam_node_frm_list and attr_list given.
    :rtype: [[bool, .. ]]
    """
    mapping = []
    for i, mkr in enumerate(mkr_list):
        # Initialise mapping list size.
        tmp = [False] * len(attr_list)
        mapping.append(tmp)

        mkr_node = mkr[0]
        bnd_node = mkr[2]
        cam_node = maya.cmds.listRelatives(mkr[1], parent=True)[0]
        mkr_plugs = []
        bnd_plugs = find_plugs_affecting_transform(bnd_node, None)
        plugs = list(set(mkr_plugs + bnd_plugs))
        for j, attr_name in enumerate(attr_list):
            attr_name = _get_full_path_plug(attr_name)
            mapping[i][j] = attr_name in plugs
    return mapping


def sort_into_hierarchy_groups(mkr_list, attr_list):
    """
    Create blocks of Markers and Attributes, sorted by hierarchy.

    This will allow us to solve top-level objects (ie, root level)
    first, before solving children. This will ensure we minimise the
    base before attempting to solve the children.

    TODO: Write this.

    :return:
    """
    pass
