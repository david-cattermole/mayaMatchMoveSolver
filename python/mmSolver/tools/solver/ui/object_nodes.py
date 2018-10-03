"""
Object nodes for the mmSolver Window UI.
"""

import mmSolver.ui.uimodels as uimodels
import mmSolver.ui.nodes as nodes


class ObjectNode(nodes.Node):
    def __init__(self, name,
                 parent=None,
                 data=None,
                 icon=None,
                 enabled=True,
                 editable=False,
                 selectable=True,
                 checkable=False,
                 neverHasChildren=False):
        if icon is None:
            icon = ':/object.png'
        super(ObjectNode, self).__init__(
            name,
            data=data,
            parent=parent,
            icon=icon,
            enabled=enabled,
            selectable=selectable,
            editable=editable,
            checkable=checkable,
            neverHasChildren=neverHasChildren)
        self.typeInfo = 'object'


class MarkerNode(ObjectNode):
    def __init__(self, name, user, desc,
                 data=None,
                 parent=None):
        icon = ':/marker.png'
        super(MarkerNode, self).__init__(
            name,
            data=data,
            parent=parent,
            icon=icon,
            selectable=True,
            editable=False)
        self._user = user
        self._desc = desc
        self.typeInfo = 'marker'

    def user(self):
        return self._user

    def description(self):
        return self._desc


class ObjectModel(uimodels.ItemModel):
    def __init__(self, root, font=None):
        super(ObjectModel, self).__init__(root, font=font)
        self._column_names = {
            0: 'Object',
            1: 'User',
            2: 'Description',
        }
        self._node_attr_key = {
            'Object': 'name',
            'User': 'user',
            'Description': 'description',
        }

