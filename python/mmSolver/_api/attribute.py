"""
The attributes to be solved for.
"""

import maya.cmds
import maya.OpenMaya as OpenMaya
# import maya.OpenMayaAnim as OpenMayaAnim
import mmSolver._api.utils as api_utils

STATE_STATIC = 0
STATE_ANIMATED = 1
STATE_DYNAMIC = 2


class Attribute(object):
    def __init__(self, name=None, node=None, attr=None):
        if isinstance(name, (str, unicode)):
            assert api_utils.detect_object_type(name) == 'attribute'
            part = name.partition('.')
            node = part[0]
            attr = part[-1]

        self._plug = None
        self._dependFn = None
        if isinstance(node, (str, unicode)) and isinstance(attr, (str, unicode)):
            assert maya.cmds.objExists(node)
            attr_list = maya.cmds.listAttr(node)
            assert attr in attr_list

            node_attr = node + '.' + attr
            plug = api_utils.get_as_plug(node_attr)
            self._plug = plug

            node_obj = self._plug.node()
            self._dependFn = OpenMaya.MFnDependencyNode(node_obj)

        return

    def get_node(self, full_path=True):
        node = None
        if self._dependFn is not None:
            try:
                node = self._dependFn.name()
            except RuntimeError:
                pass
        if node is not None and full_path is True:
            node = api_utils.get_long_name(node)
        return node

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
                long_name  # use long name.
            )
        return name

    def get_name(self, full_path=True):
        name = None
        node = self.get_node(full_path=full_path)
        attr = self.get_attr(long_name=full_path)
        if (isinstance(node, (str, unicode)) and
                isinstance(attr, (str, unicode))):
            name = node + '.' + attr
        return name

    def get_state(self):
        pass

    def is_dynamic(self):
        pass

    def is_animated(self):
        # OpenMayaAnim.MAnimUtil
        # self._plug.
        pass

    def is_static(self):
        pass

    def is_free_to_change(self):
        pass

    def get_anim_curve_node(self):
        pass