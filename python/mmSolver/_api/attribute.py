# Copyright (C) 2018, 2019, 2020 David Cattermole.
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
Module for attributes and related functions.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

import mmSolver.utils.node as node_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver._api.utils as api_utils
import mmSolver._api.constant as const
import mmSolver.logger

LOG = mmSolver.logger.get_logger()


class Attribute(object):
    """
    The Attribute - A variable, or set of variables over time to solve.

    Example usage::

        >>> import mmSolver.api as mmapi
        >>> node = maya.cmds.createNode('transform', name='myNode')
        >>> attr = mmapi.Attribute(node=node, attr='tx')
        >>> attr.get_node()
        '|myNode'
        >>> attr.get_attr()
        'translateX'
        >>> attr.get_attr(long_name=False)
        'tx'
        >>> attr.get_name()
        '|myNode.translateX'
        >>> attr.get_state()
        1  # 1 == ATTR_STATE_STATIC

    """

    def __init__(self, name=None, node=None, attr=None):
        """
        Initialise an Attribute object.

        Attribute can use a 'name', or 'node' and 'attr'.

        A 'name' is a string of both node and attribute path; `node.attr`.

        :param name: Node and attribute path as a single string: 'node.attr'
        :type name: str

        :param node: DG Maya node path.
        :type node: str

        :param attr: Long or short attribute name.
        :type attr: str
        """
        if isinstance(name, pycompat.TEXT_TYPE):
            assert api_utils.get_object_type(name) == const.OBJECT_TYPE_ATTRIBUTE
            part = name.partition('.')
            node = part[0]
            attr = part[-1]

        self._plug = None
        if isinstance(node, pycompat.TEXT_TYPE) and isinstance(
            attr, pycompat.TEXT_TYPE
        ):
            assert maya.cmds.objExists(node)
            # Long and short names must be checked.
            attr_list_long = maya.cmds.listAttr(node, shortNames=False) or []
            attr_list_short = maya.cmds.listAttr(node, shortNames=True) or []
            alias_pairs = maya.cmds.aliasAttr(node, query=True) or []
            all_attrs = attr_list_long + attr_list_short + alias_pairs
            if attr not in all_attrs:
                msg = 'Attribute not found on node. node=%r attr=%r'
                LOG.error(msg, node, attr)
                raise RuntimeError(msg % (node, attr))

            node_attr = node + '.' + attr
            plug = node_utils.get_as_plug_apione(node_attr)
            self._plug = plug
        return

    def __repr__(self):
        result = '<{class_name}('.format(class_name=self.__class__.__name__)
        result += '{hash} name={name}'
        result += ')>'
        result = result.format(
            hash=hex(hash(self)),
            name=self.get_name(),
        )
        return result

    def get_node(self, full_path=True):
        """
        Get the node name path from this Attribute.

        :param full_path: If True, the full node name hiearachy will be
            returned, making sure the name is unique.
        :type full_path: bool

        :returns: The node name, or None if the Attribute class does
            not hold a valid node.
        :rtype: None or str
        """
        if self._plug is None:
            return None
        node = None
        node_obj = self._plug.node()
        try:
            dag_fn = OpenMaya.MFnDagNode(node_obj)
            node = dag_fn.fullPathName()
        except RuntimeError:
            depend_fn = OpenMaya.MFnDependencyNode(node_obj)
            node = depend_fn.name()
        if full_path is False:
            nodes = maya.cmds.ls(node) or []
            if len(nodes) > 0:
                node = nodes[0]
        assert node is None or isinstance(node, pycompat.TEXT_TYPE)
        return node

    def get_node_uid(self):
        """
        Get the Attribute's node unique identifier.

        .. warning::
            Although this returns a "unique" identifier, there are times
            when UUIDs are not unique. For example with the same Maya scene
            file referenced into the Maya scene more than once, the referenced
            node UUID will not change - each copy of the referenced node
            will have the same UUID value.

        :return: The Attribute UUID or None
        :rtype: None or str or unicode
        """
        node = self.get_node()
        if node is None:
            return None
        uids = maya.cmds.ls(node, uuid=True) or []
        return uids[0]

    def get_attr(self, long_name=True):
        name = None
        if self._plug is not None:
            include_node_name = False
            include_non_mandatory_indices = True
            include_instanced_indices = True
            use_alias = False
            use_full_attribute_path = False
            name = self._plug.partialName(
                include_node_name,
                include_non_mandatory_indices,
                include_instanced_indices,
                use_alias,
                use_full_attribute_path,
                long_name,  # use long name.
            )
        return name

    def get_attr_alias_name(self):
        # Alias attributes are a little tricky. Alias attributes are
        # not real attributes, they are a trick. Alias attributes do
        # not have a "Nice Name" like regular attributes.
        #
        # This method was added to allow the user of the API to get
        # the alias attribute name, but internally it's all referenced
        # relative to the "real" attribute, and we must look up the
        # alias name - if it exists.
        node = self.get_node()
        if node is None:
            return None

        alias_pairs = maya.cmds.aliasAttr(node, query=True) or []
        if len(alias_pairs) == 0:
            return None

        attr = self.get_attr()
        attr_names = alias_pairs[1::2]
        if attr not in attr_names:
            return None

        alias_names = alias_pairs[0::2]
        index = attr_names.index(attr)
        alias_name = alias_names[index]
        return alias_name

    def get_attr_nice_name(self):
        nice_name = None
        node = self.get_node()
        attr = self.get_attr()
        if node is not None and attr is not None:
            nice_name = maya.cmds.attributeQuery(attr, node=node, niceName=True)
        return nice_name

    def get_name(self, full_path=True):
        name = None
        node = self.get_node(full_path=full_path)
        attr = self.get_attr(long_name=full_path)
        if isinstance(node, pycompat.TEXT_TYPE) and isinstance(
            attr, pycompat.TEXT_TYPE
        ):
            name = node + '.' + attr
        return name

    def get_state(self):
        state = const.ATTR_STATE_INVALID

        check_parents = True
        check_children = True
        free = self._plug.isFreeToChange(check_parents, check_children)
        if free != OpenMaya.MPlug.kFreeToChange:
            state = const.ATTR_STATE_LOCKED
            return state

        check_parents = False
        animPlugs = OpenMaya.MPlugArray()
        OpenMayaAnim.MAnimUtil.findAnimatedPlugs(
            self._plug.node(), animPlugs, check_parents
        )
        for i in range(animPlugs.length()):
            plug = animPlugs[i]
            if self._plug.name() == plug.name():
                state = const.ATTR_STATE_ANIMATED
                return state

        # If the plug is connected to a Constraint, then it is
        # considered "free to change", but for the solver we consider
        # it locked and unchangeable.
        src_plug = self._plug.source()
        if src_plug.isNull() is False:
            state = const.ATTR_STATE_LOCKED
            return state

        if state == const.ATTR_STATE_INVALID:
            state = const.ATTR_STATE_STATIC

        return state

    def is_static(self):
        return self.get_state() == const.ATTR_STATE_STATIC

    def is_animated(self):
        return self.get_state() == const.ATTR_STATE_ANIMATED

    def is_locked(self):
        return self.get_state() == const.ATTR_STATE_LOCKED

    def get_attribute_type(self):
        attr_type = None
        node_name = self.get_node()
        attr_name = self.get_attr()
        if isinstance(node_name, pycompat.TEXT_TYPE) and isinstance(
            attr_name, pycompat.TEXT_TYPE
        ):
            attr_type = (
                maya.cmds.attributeQuery(attr_name, node=node_name, attributeType=True)
                or None
            )
        return attr_type

    def get_min_value(self):
        """This function is deprecated,
        please use Collection.get/set_attribute* functions."""
        raise NotImplementedError

    def set_min_value(self, value):
        """This function is deprecated,
        please use Collection.get/set_attribute* functions."""
        raise NotImplementedError

    def get_max_value(self):
        """This function is deprecated,
        please use Collection.get/set_attribute* functions."""
        raise NotImplementedError

    def set_max_value(self, value):
        """This function is deprecated,
        please use Collection.get/set_attribute* functions."""
        raise NotImplementedError
