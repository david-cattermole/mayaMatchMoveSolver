"""
Solver nodes for the mmSolver Window UI.
"""

import uuid

import Qt as Qt
import Qt.QtGui as QtGui
import Qt.QtCore as QtCore
import Qt.QtWidgets as QtWidgets

import mmSolver.ui.uimodels as uimodels
import mmSolver.ui.converttypes as converttypes
import mmSolver.ui.nodes as nodes
import mmSolver.logger
import mmSolver.tools.solver.lib.collection as lib_collection
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


class StrategyComboBoxDelegate(uimodels.ComboBoxDelegate):

    def __init__(self, parent=None):
        super(StrategyComboBoxDelegate, self).__init__(parent)

    def getValueList(self):
        values = list(const.STRATEGY_LABEL_LIST)
        return values


class AttributeComboBoxDelegate(uimodels.ComboBoxDelegate):

    def __init__(self, parent=None):
        super(AttributeComboBoxDelegate, self).__init__(parent)

    def getValueList(self):
        values = [
            str(const.ATTR_FILTER_STATIC_AND_ANIM_LABEL),
            str(const.ATTR_FILTER_ANIM_ONLY_LABEL),
            str(const.ATTR_FILTER_NO_ATTRS_LABEL),
        ]
        return values


class SolverStepNode(nodes.Node):
    def __init__(self, name, col_node,
                 parent=None,
                 data=None,
                 icon=None,
                 enabled=True,
                 editable=True,
                 selectable=True,
                 checkable=True,
                 neverHasChildren=False):
        if isinstance(name, basestring) is False:
            raise TypeError
        if icon is None:
            icon = ':/mmSolver_solverStep.png'
        if isinstance(data, dict) is False:
            data = {}
        data['collection_node'] = col_node
        super(SolverStepNode, self).__init__(
            name,
            data=data,
            parent=parent,
            icon=icon,
            enabled=enabled,
            selectable=selectable,
            editable=editable,
            checkable=checkable,
            neverHasChildren=neverHasChildren)
        self.typeInfo = 'solverStep'

    def collectionNode(self):
        return self.data().get('collection_node')

    def setCollectionNode(self, value):
        d = self.data()
        d['collection_node'] = value
        self.setData(d)

    def stepNode(self):
        col = self.collectionNode()
        name = self.name()
        n = lib_collection.get_named_solver_step_from_collection(col, name)
        return n

    def setStepNode(self, node):
        col = self.collectionNode()
        lib_collection.set_named_solver_step_to_collection(col, node)
        return

    def stepEnabled(self):
        n = self.stepNode()
        v = n.get_enabled()
        return converttypes.booleanToString(v)

    def setStepEnabled(self, value):
        v = converttypes.stringToBoolean(value)
        if v is None:
            return
        n = self.stepNode()
        n.set_enabled(v)
        self.setStepNode(n)
        return

    def frames(self):
        # if the option 'override current frame' is on, we ignore the actual
        # value.
        col = self.collectionNode()
        cur_frame = lib_collection.get_override_current_frame_from_collection(col)
        if cur_frame is True:
            return 'CURRENT'

        n = self.stepNode()
        int_list = n.get_frame_list()
        string = converttypes.intListToString(int_list)
        return string

    def setFrames(self, value):
        int_list = converttypes.stringToIntList(value)
        n = self.stepNode()
        n.set_frame_list(int_list)
        self.setStepNode(n)
        return

    def strategy(self):
        """
        The strategy of how to compute the frames

        A strategy order to solve the frames in.
        This strategy is only needed for static attribute computation.
        """
        n = self.stepNode()
        v = n.get_strategy()
        assert v in const.STRATEGY_LIST
        idx = const.STRATEGY_LIST.index(v)
        value = const.STRATEGY_LABEL_LIST[idx]
        return value

    def setStrategy(self, value):
        assert value in const.STRATEGY_LABEL_LIST
        idx = const.STRATEGY_LABEL_LIST.index(value)
        v = const.STRATEGY_LIST[idx]
        n = self.stepNode()
        n.set_strategy(v)
        self.setStepNode(n)
        return

    def attrs(self):
        n = self.stepNode()
        use_static = n.get_use_static_attrs()
        use_animated = n.get_use_anim_attrs()
        v = '?'
        if use_static is True and use_animated is True:
            v = const.ATTR_FILTER_STATIC_AND_ANIM_LABEL
        elif use_static is False and use_animated is True:
            v = const.ATTR_FILTER_ANIM_ONLY_LABEL
        elif use_static is True and use_animated is False:
            v = const.ATTR_FILTER_STATIC_ONLY_LABEL
        elif use_static is False and use_animated is False:
            v = const.ATTR_FILTER_NO_ATTRS_LABEL
        return v

    def setAttrs(self, value):
        use_static = None
        use_animated = None
        if value == const.ATTR_FILTER_STATIC_AND_ANIM_LABEL:
            use_static = True
            use_animated = True
        elif value == const.ATTR_FILTER_ANIM_ONLY_LABEL:
            use_static = False
            use_animated = True
        elif value == const.ATTR_FILTER_STATIC_ONLY_LABEL:
            use_static = True
            use_animated = False
        elif const.ATTR_FILTER_NO_ATTRS_LABEL:
            use_static = False
            use_animated = False
        assert use_static is not None
        assert use_animated is not None
        n = self.stepNode()
        n.set_use_anim_attrs(use_animated)
        n.set_use_static_attrs(use_static)
        self.setStepNode(n)
        return


class SolverModel(uimodels.TableModel):
    def __init__(self, node_list=None, font=None):
        super(SolverModel, self).__init__(node_list=node_list, font=font)
        self._column_names = {
            0: 'Enabled',
            1: 'Frames',
            2: 'Attributes',
            3: 'Strategy',
        }
        self._node_attr_key = {
            'Enabled': 'stepEnabled',
            'Frames': 'frames',
            'Strategy': 'strategy',
            'Attributes': 'attrs',
        }
        self._node_set_attr_key = {
            'Enabled': 'setStepEnabled',
            'Frames': 'setFrames',
            'Strategy': 'setStrategy',
            'Attributes': 'setAttrs',
        }
        self._checkable_column_mapping = {
            'Enabled': True,
            'Frames': False,
            'Strategy': False,
            'Attributes': False,
        }
