"""
Solver nodes for the mmSolver Window UI.
"""

import uuid

import Qt as Qt
import Qt.QtGui as QtGui
import Qt.QtCore as QtCore

import mmSolver.ui.uimodels as uimodels
import mmSolver.ui.nodes as nodes
import mmSolver.logger
import mmSolver.tools.solver.lib.collection as lib_collection
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


def _convertStringToBoolean(value):
    v = None
    if isinstance(value, bool):
        v = value
    elif isinstance(value, basestring):
        value = value.strip().lower()
        if value in const.TRUE_WORDS:
            v = True
        elif value in const.FALSE_WORDS:
            v = False
        else:
            return None
    else:
        raise TypeError
    return v


def _convertBooleanToString(value):
    return str(value)


def _convertStringToIntList(value):
    """
    value = '1001-1101'
    value = '1001,1002,1003-1005,1010-1012
    """
    if isinstance(value, basestring) is False:
        raise TypeError
    value = value.strip()
    int_list = []
    for v in value.split(','):
        v = v.strip()
        if v.isdigit() is True:
            i = int(v)
            int_list.append(i)
        if '-' not in v:
            continue

        dash_split = v.split('-')
        dash_split = filter(lambda x: x.isdigit(), dash_split)
        if len(dash_split) > 1:
            # Even if the user adds more than 1 dash character, we only take
            # the first two.
            s = int(dash_split[0])
            e = int(dash_split[1])
            if s == e:
                int_list.append(s)
                continue
            if s < e:
                int_list += list(range(s, e + 1))
    int_list = list(set(int_list))
    int_list = list(sorted(int_list))
    return int_list


def _convertIntListToString(value):
    if isinstance(value, list) is False:
        raise TypeError
    int_list = list(set(value))
    int_list = list(sorted(int_list))
    grps = []
    start = -1
    end = -1
    prev = -1
    for i, num in enumerate(int_list):
        first = i == 0
        last = (i + 1) == len(int_list)
        if first is True:
            # Start a new group.
            start = num
            end = num
        if (prev + 1) != num:
            # End old group.
            end = prev
            if end != -1:
                grps.append((start, end))
            # New group
            start = num
            end = num
        if last is True: 
            # Close off final group.
            end = num
            if end != -1:
                grps.append((start, end))
        prev = num

    string_list = []
    for grp in grps:
        s, e = grp
        if s == e:
            string_list.append(str(s))
        else:
            string_list.append('{0}-{1}'.format(s, e))
    return ','.join(string_list)


def _convertStringToStrategy(value):
    return value


def _convertStringToAttrFilter(value):
    return value


def _convertStringToInteger(value):
    return int(value)


class SolverStepNode(nodes.Node):
    def __init__(self, name, col_node,
                 parent=None,
                 data=None,
                 icon=None,
                 enabled=True,
                 editable=True,
                 selectable=True,
                 checkable=False,
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
        name = self.name()
        lib_collection.set_named_solver_step_to_collection(col, node)
        return

    def stepEnabled(self):
        n = self.stepNode()
        v = n.get_enabled()
        return _convertBooleanToString(v)

    def setStepEnabled(self, value):
        v = _convertStringToBoolean(value)
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
        string = _convertIntListToString(int_list)
        return string

    def setFrames(self, value):
        int_list = _convertStringToIntList(value)
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
            use_static = True
            use_animated = True
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

