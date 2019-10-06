# Copyright (C) 2019 David Cattermole.
#
# This file is part of mmSolver.
#
# mmSolver is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# mmSolver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Transform utilities, for querying, setting and manipulating
transform nodes and matrices.

Features:

   - Store a Maya Transform node as a Python object, irrespective of
     DAG path names.

   - A Matrix Cache object used to query a Transform Matrix across time.

   - Common functions for querying transforms using Maya Python API 2.

"""

import math

import maya.cmds
import maya.debug
import maya.api.OpenMaya as OpenMaya2

import mmSolver.logger
import mmSolver.utils.node as node_utils
import mmSolver.utils.animcurve as animcurve_utils
import mmSolver.utils.constant as const


ROTATE_ORDER_STR_TO_APITWO_CONSTANT = {
    'xyz': OpenMaya2.MTransformationMatrix.kXYZ,
    'xzy': OpenMaya2.MTransformationMatrix.kXZY,
    'yxz': OpenMaya2.MTransformationMatrix.kYXZ,
    'yzx': OpenMaya2.MTransformationMatrix.kYZX,
    'zxy': OpenMaya2.MTransformationMatrix.kZXY,
    'zyx': OpenMaya2.MTransformationMatrix.kZYX
}
LOG = mmSolver.logger.get_logger()


def create_dg_context_apitwo(t):
    """
    Create a Maya DG Context for querying values at time.
    """
    assert t is None or isinstance(t, (int, float))
    ctx = None
    if t is None:
        ctx = OpenMaya2.MDGContext()
    else:
        unit = OpenMaya2.MTime.uiUnit()
        mtime = OpenMaya2.MTime(float(t), unit)
        ctx = OpenMaya2.MDGContext(mtime)
    return ctx


def get_matrix_from_plug_apitwo(plug, ctx):
    """
    Get a matrix plug value at a given DG (time) context.

    http://chrisdevito.blogspot.com/2013/04/getting-dat-matrix-maya-python-api-20.html

    :param plug: The node.attribute to query.
    :type plug: maya.api.OpenMaya.MPlug

    :param ctx: Time DG Context to query at.
    :type ctx: maya.api.OpenMaya.MDGContext

    :returns: The 4x4 matrix value at the given DG context.
    :rtype: maya.api.OpenMaya.MMatrix
    """
    assert isinstance(plug, OpenMaya2.MPlug)
    assert isinstance(ctx, OpenMaya2.MDGContext)
    mobject = plug.asMObject(ctx)
    data = OpenMaya2.MFnMatrixData(mobject)
    matrix = data.matrix()
    return matrix


def get_double_from_plug_apitwo(plug, ctx):
    """
    Get a double plug value at a given DG (time) context.

    :param plug: The node.attribute to query.
    :type plug: maya.api.OpenMaya.MPlug

    :param ctx: Time DG Context to query at.
    :type ctx: maya.api.OpenMaya.MDGContext

    :returns: The floating point value at the given DG context.
    :rtype: float
    """
    assert isinstance(plug, OpenMaya2.MPlug)
    assert isinstance(ctx, OpenMaya2.MDGContext)
    value = plug.asDouble(ctx)
    return value


def get_parent_inverse_matrix_apitwo(node, ctx):
    """
    Get the matrix value of attribute 'parentInverseMatrix[0]' at a
    given DG Context.

    :param node: Node path to query values on.
    :type node: str

    :param ctx: The (time) context to query the attribute at.
    :type ctx: maya.api.OpenMaya.MDGContext

    :returns: The 4x4 matrix value at the given DG context.
    :rtype: maya.api.OpenMaya.MMatrix
    """
    assert isinstance(node, (str, unicode))
    assert isinstance(ctx, OpenMaya2.MDGContext)
    name = node + '.parentInverseMatrix[0]'
    plug = node_utils.get_as_plug_apitwo(name)
    return get_matrix_from_plug_apitwo(plug, ctx)


def get_world_matrix_apitwo(node, ctx):
    """
    Get the matrix value of attribute 'worldMatrix[0]' at a
    given DG Context.

    :param node: Node path to query values on.
    :type node: str

    :param ctx: The (time) context to query the attribute at.
    :type ctx: maya.api.OpenMaya.MDGContext

    :returns: The 4x4 matrix value at the given DG context.
    :rtype: maya.api.OpenMaya.MMatrix
    """
    assert isinstance(node, (str, unicode))
    assert isinstance(ctx, OpenMaya2.MDGContext)
    name = node + '.worldMatrix[0]'
    plug = node_utils.get_as_plug_apitwo(name)
    return get_matrix_from_plug_apitwo(plug, ctx)


def detect_rotate_pivot_non_zero(tfm_node):
    """
    Given a TransformNode, determine if the node has a non-zero rotate
    pivot.

    :rtype: bool
    """
    assert isinstance(tfm_node, TransformNode)
    node = tfm_node.get_node()
    plug = node + '.rotatePivot'
    rp = maya.cmds.getAttr(plug)[0]
    rp = [abs(v) for v in rp]
    return sum(rp) > 0.


class TransformNode(object):
    """
    Represents a Maya Transform node, and the data associated.

    This object store a reference to Maya node, even if the node is
    renamed or re-parented.

    >>> a = TransformNode(node='myNode')
    >>> node = a.get_node()
    >>> node_uuid = a.get_node_uuid()
    >>> tfm_node_parents = a.get_parents()
    >>> b = TransformNode()
    >>> b.set_node('myNode')

    """

    def __init__(self, node=None):
        """
        Create a Transform object initialised with 'node'.

        :param node: Maya transform node to attach this object to.
        :type node: str
        """
        if node is not None:
            assert isinstance(node, (str, unicode))
            assert maya.cmds.objExists(node)
            dag = node_utils.get_as_dag_path_apitwo(node)
            if dag is not None:
                self._mfn = OpenMaya2.MFnDagNode(dag)
        else:
            self._mfn = OpenMaya2.MFnDagNode()
        return

    def __repr__(self):
        """
        Return the TransformNode object as a string.

        :returns: A string representation of the this object; self.
        :rtype: str
        """
        result = '<{class_name}('.format(class_name=self.__class__.__name__)
        result += '{hash} node={node}'.format(
            hash=hash(self),
            node=self.get_node(),
        )
        result += ')>'
        return result

    def __eq__(self, other):
        """
        Test if two TransformNode objects DO point to the same underlying
        node.
        """
        if self is None and other is not None:
            return False
        if self is not None and other is None:
            return False
        if self is None and other is None:
            return True
        node_a = self.get_node()
        node_b = other.get_node()
        return node_a == node_b

    def __ne__(self, other):
        """
        Test if two TransformNode objects DO NOT point to the same
        underlying node.
        """
        return not self.__eq__(other)

    def get_node(self):
        """
        Get the transform node.

        :return: The transform node name or None
        :rtype: None or str or unicode
        """
        node = None
        try:
            obj = self._mfn.object()
        except RuntimeError:
            obj = None
        if obj is not None and obj.isNull() is False:
            try:
                node = self._mfn.fullPathName()
            except RuntimeError:
                pass
        if isinstance(node, (str, unicode)) and len(node) == 0:
            node = None
        return node

    def get_node_uuid(self):
        """
        The Maya node's UUID.

        :returns: The node UUID.
        :rtype: str
        """
        node = self.get_node()
        uuid = None
        if node is not None:
            uuid = maya.cmds.ls(node, uuid=True)[0]
        return uuid

    def set_node(self, node):
        """
        Set the underlying Maya node that this object will operate on.

        :param node: Node to set to.
        :type node: str
        """
        assert isinstance(node, (str, unicode))
        assert maya.cmds.objExists(node)
        dag = node_utils.get_as_dag_path_apitwo(node)
        if dag is not None:
            self._mfn = OpenMaya2.MFnDagNode(dag)
        else:
            self._mfn = OpenMaya2.MFnDagNode()
        return

    def get_parent(self):
        """
        Get the node directly above the current node.

        :returns: Transform node or None, if the node is parented to world.
        :rtype: TransformNode or None
        """
        node = self.get_node()
        parents = maya.cmds.listRelatives(
            node,
            parent=True,
            fullPath=True) or []
        parent_tfm_node = None
        if len(parents) > 0:
            parent_tfm_node = TransformNode(node=parents[0])
        return parent_tfm_node

    def get_parents(self):
        """
        Get the nodes above the current node.

        :returns: Transform nodes or empty list.
        :rtype: [TransformNode, ..]
        """
        node = self.get_node()
        parents = maya.cmds.listRelatives(
            node,
            allParents=True,
            fullPath=True) or []
        parent_tfm_nodes = []
        for parent in parents:
            n = TransformNode(node=parent)
            parent_tfm_nodes.append(n)
        return parent_tfm_nodes


class TransformMatrixCache(object):
    """
    Hold a list of matrix node/values to be queried and stored in the object.

    >>> tfm_node = TransformNode(node='myNode')
    >>> times = list(range(1001, 1101))
    >>> tfm_matrix_cache = TransformMatrixCache()
    >>> tfm_matrix_cache.add(tfm_node, times)
    >>> tfm_matrix_cache.process()
    >>> tfm_matrix_cache.get_node_attr_matrix(tfm_node, times)

    """

    def __init__(self):
        """
        Construct an empty TransformMatrixCache.
        """
        self._data = None
        self.clear()

    def clear(self):
        """
        Clear all the cached values, nodes, attributes and times.
        """
        self._data = dict()

    def add_node(self, tfm_node, times):
        """
        Add a TransformNode and set of times to evaluate.
        """
        with_pivot = detect_rotate_pivot_non_zero(tfm_node)
        attr_names = ['worldMatrix[0]']
        if with_pivot is True:
            attr_names = [
                'matrix',
                'parentInverseMatrix[0]',
                'rotatePivotX',
                'rotatePivotY',
                'rotatePivotZ'
            ]
        for attr_name in attr_names:
            self.add_node_attr(tfm_node, attr_name, times)
        return

    def add_node_attr(self, tfm_node, attr_name, times):
        """
        Add a TransformNode / attribute name and set of times to evaluate.
        """
        uuid = tfm_node
        if isinstance(tfm_node, TransformNode):
            uuid = tfm_node.get_node_uuid()
        if uuid not in self._data:
            self._data[uuid] = dict()
        if attr_name not in self._data[uuid]:
            self._data[uuid][attr_name] = dict()
        for t in times:
            self._data[uuid][attr_name][t] = None
        return

    def get_nodes(self):
        """
        Get all the nodes in the cache.

        :returns: List of node names inside the cache
        :rtype: [str, ..]
        """
        tfm_nodes = []
        for key in self._data.keys():
            nodes = maya.cmds.ls(key, long=True) or []
            for node in nodes:
                tfm_nodes.append(node)
        return tfm_nodes

    def process(self):
        """
        Evaluate all the node attributes at times.
        """
        # Get times and nodes.
        times = []
        map_uuid_to_node = dict()
        for uuid in self._data.keys():
            node = maya.cmds.ls(uuid, long=True)[0]
            map_uuid_to_node[uuid] = dict()
            for attr_name in self._data[uuid].keys():
                plug_name = node + '.' + attr_name
                plug = node_utils.get_as_plug_apitwo(plug_name)
                assert plug is not None
                map_uuid_to_node[uuid][attr_name] = plug
                data = self._data.get(uuid, dict())
                data = data.get(attr_name, dict())
                times += data
        times = list(set(times))
        times = list(sorted(times))

        # Query the matrices, looping over time sequentially.
        for t in times:
            ctx = create_dg_context_apitwo(t)
            for uuid in self._data.keys():
                d = self._data.get(uuid, dict())
                for attr_name in d.keys():
                    d2 = map_uuid_to_node.get(uuid, dict())
                    plug = d2.get(attr_name, dict())
                    if 'matrix' in attr_name.lower():
                        matrix = get_matrix_from_plug_apitwo(plug, ctx)
                        self._data[uuid][attr_name][t] = matrix
                    elif 'rotatepivot' in attr_name.lower():
                        value = get_double_from_plug_apitwo(plug, ctx)
                        self._data[uuid][attr_name][t] = value
                    else:
                        msg = 'Attribute name is not supported; attr_name=%r'
                        raise ValueError(msg % attr_name)
        return

    def get_attrs_for_node(self, tfm_node):
        """
        Get the list of attribute names for the node in the cache.

        This function allows us to detect if a node is stored with
        pivot point or not.

        :param tfm_node: The node to look into the cache with.
        :type tfm_node: TransformNode or str

        :return: List of attribute names in the cache for this node.
        :rtype: [str, ..]
        """
        node_uuid = tfm_node
        if isinstance(tfm_node, TransformNode):
            node_uuid = tfm_node.get_node_uuid()
        attr_names = self._data.get(node_uuid, dict()).keys()
        return attr_names

    def get_node_attr(self, tfm_node, attr_name, times):
        """
        Get the node attribute matrix data, at given times

        :param tfm_node: The transform node to query.
        :type tfm_node: TransformNode or str

        :param attr_name: Name of the attribute (previously added to 
                          the cache).
        :type attr_name: str

        :param times: The list of times to query from the cache.
        :type times: [int, ..]

        :returns: List of MMatrix objects for each time requested. If
                  no cached value exists, None is returned in that
                  list entry.
        :rtype: [maya.api.OpenMaya.MMatrix, ..]
        """
        node_uuid = tfm_node
        if isinstance(tfm_node, TransformNode):
            node_uuid = tfm_node.get_node_uuid()
        node_values = self._data.get(node_uuid, dict())
        attr_values = node_values.get(attr_name, dict())
        attr_values = attr_values.copy()
        values = []
        for t in times:
            v = attr_values.get(t, None)
            values.append(v)
        return values

    get_node_attr_matrix = get_node_attr


def set_transform_values(tfm_matrix_cache,
                         times,
                         src_tfm_node,
                         dst_tfm_node,
                         rotate_order=None,
                         delete_static_anim_curves=True):
    """
    Set transform node values on a destination node at times,
    using previously evaluated cached values.

    src_tfm_node is used to look-up into the cache for values.
    dst_tfm_node is the node that will be set values on. It is
    possible to have src_tfm_node and dst_tfm_node reference the same
    Maya node, or even the same object.

    .. note::
       The function assumes the given destination node has no locked
       attributes.

    :param tfm_matrix_cache: A cache holding queried matrix values.
    :type tfm_matrix_cache: TransformMatrixCache

    :param times: The times to set transforms values on.
    :type times: [int or float, ...]

    :param src_tfm_node: Source node to get cached transform values from.
    :type src_tfm_node: TransformNode

    :param dst_tfm_node: Destination node set transform values on.
    :type dst_tfm_node: TransformNode

    :param rotate_order: The rotation order to set on the dst_node,
                         or use the existing rotation on the dst_node
                         if rotate_order is None.
    :type rotate_order: str

    :param delete_static_anim_curves: If an animation curve is static,
                                      it will be deleted.
    :type delete_static_anim_curves: bool

    :rtype: None
    """
    assert isinstance(tfm_matrix_cache, TransformMatrixCache)
    assert isinstance(times, (list, tuple))
    assert isinstance(src_tfm_node, TransformNode)
    assert isinstance(dst_tfm_node, TransformNode)
    assert rotate_order is None or isinstance(rotate_order, (str, unicode))

    space = OpenMaya2.MSpace.kWorld
    attrs = [
        'translateX', 'translateY', 'translateZ',
        'rotateX', 'rotateY', 'rotateZ',
        'scaleX', 'scaleY', 'scaleZ'
    ]

    dst_node = dst_tfm_node.get_node()
    if rotate_order is None:
        rotate_order = maya.cmds.xform(
            dst_node,
            query=True,
            rotateOrder=True)
    else:
        maya.cmds.xform(
            dst_node,
            edit=True,
            rotateOrder=rotate_order)
    assert rotate_order in const.ROTATE_ORDER_STR_LIST
    rotate_order = ROTATE_ORDER_STR_TO_APITWO_CONSTANT[rotate_order]

    # Get destination node plug.
    src_node = src_tfm_node.get_node()
    src_name = src_node + '.parentInverseMatrix[0]'
    parent_inv_matrix_plug = node_utils.get_as_plug_apitwo(src_name)

    # Query the matrix node.
    src_node_uuid = src_tfm_node.get_node_uuid()
    src_node_attrs = tfm_matrix_cache.get_attrs_for_node(src_node_uuid)
    with_pivot = len(src_node_attrs) > 1
    world_mat_list = []
    if with_pivot is False:
        world_mat_list = tfm_matrix_cache.get_node_attr_matrix(
            src_node_uuid,
            'worldMatrix[0]',
            times,
        )
    else:        
        mat_list = tfm_matrix_cache.get_node_attr_matrix(
            src_node_uuid,
            'matrix',
            times,
        )
        assert len(mat_list) == len(times)
        
        par_inv_mat_list = tfm_matrix_cache.get_node_attr_matrix(
            src_node_uuid,
            'parentInverseMatrix[0]',
            times,
        )
        assert len(par_inv_mat_list) == len(times)
        
        rot_piv_x_list = tfm_matrix_cache.get_node_attr_matrix(
            src_node_uuid,
            'rotatePivotX',
            times,
        )
        assert len(rot_piv_x_list) == len(times)
        
        rot_piv_y_list = tfm_matrix_cache.get_node_attr_matrix(
            src_node_uuid,
            'rotatePivotY',
            times,
        )
        assert len(rot_piv_y_list) == len(times)
        
        rot_piv_z_list = tfm_matrix_cache.get_node_attr_matrix(
            src_node_uuid,
            'rotatePivotZ',
            times,
        )
        assert len(rot_piv_z_list) == len(times)

        # Reconstruct World-Matrix, accounting for pivot point.
        space = OpenMaya2.MSpace.kWorld
        loop_iter = zip(mat_list,
                        par_inv_mat_list,
                        rot_piv_x_list,
                        rot_piv_y_list,
                        rot_piv_z_list)
        for mat, par_inv_mat, rot_piv_x, rot_piv_y, rot_piv_z in loop_iter:
            assert mat is not None
            assert par_inv_mat is not None
            assert rot_piv_x is not None
            assert rot_piv_y is not None
            assert rot_piv_z is not None
            mat = OpenMaya2.MTransformationMatrix(mat)
            pivot = OpenMaya2.MVector(rot_piv_x, rot_piv_y, rot_piv_z)
            trans = mat.translation(space)
            mat.setTranslation(trans + pivot, space)
            mat = mat.asMatrix()
            world_mat = par_inv_mat * mat
            world_mat_list.append(world_mat)
    assert len(world_mat_list) == len(times)

    # Set transform
    dst_node = dst_tfm_node.get_node()
    prv_rot = None
    for t, world_mat in zip(times, world_mat_list):
        assert world_mat is not None
        ctx = create_dg_context_apitwo(t)
        parent_mat = get_matrix_from_plug_apitwo(
            parent_inv_matrix_plug,
            ctx
        )

        local_mat = parent_mat * world_mat
        local_mat = OpenMaya2.MTransformationMatrix(local_mat)
        local_mat.reorderRotation(rotate_order)

        # Decompose matrix into components
        trans = local_mat.translation(space)
        scl = local_mat.scale(space)
        rot = local_mat.rotation(asQuaternion=False)

        # Convert and clean rotation values
        trans = (trans[0], trans[1], trans[2])
        scl = (scl[0], scl[1], scl[2])
        rot = (
            math.degrees(rot[0]),
            math.degrees(rot[1]),
            math.degrees(rot[2])
        )
        if prv_rot is not None:
            rot = (
                animcurve_utils.euler_filter_value(prv_rot[0], rot[0]),
                animcurve_utils.euler_filter_value(prv_rot[1], rot[1]),
                animcurve_utils.euler_filter_value(prv_rot[2], rot[2])
            )
        prv_rot = rot

        # Set Keyframes
        values = trans + rot + scl
        assert len(attrs) == len(values)
        for attr, v in zip(attrs, values):
            maya.cmds.setKeyframe(dst_node, attribute=attr, time=t, value=v)

    if delete_static_anim_curves is True:
        maya.cmds.delete(dst_node, staticChannels=True)
    return
