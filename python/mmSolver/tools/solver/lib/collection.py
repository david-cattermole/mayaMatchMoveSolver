"""
Collection and solving functions.
"""

import pprint
import time
import uuid

import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver.logger
import mmSolver.api as mmapi

import mmSolver.utils.time as utils_time

import mmSolver.tools.selection.filternodes as filter_nodes
import mmSolver.tools.solver.lib.solver as solver_utils
import mmSolver.tools.solver.lib.maya_utils as maya_utils
import mmSolver.tools.solver.lib.solver_step as solver_step
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


def get_collections():
    """
    Get all Collection objects defined in the scene.

    :returns: A list of Collection objects.
    :rtype: [Collection, ..]
    """
    nodes = maya.cmds.ls(type='objectSet', long=True) or []
    node_categories = filter_nodes.get_nodes(nodes)
    cols = []
    for col_node in node_categories['collection']:
        col = mmapi.Collection(node=col_node)
        cols.append(col)
    return cols


def create_collection():
    """
    Create a new Collection in the scene.

    :returns: A new Collection object.
    :rtype: Collection
    """
    col = mmapi.Collection().create_node('collection1')
    sol = solver_utils.create_solver()
    solver_utils.add_solver_to_collection(sol, col)
    ensure_solver_steps_attr_exists(col)
    step = create_solver_step()
    add_solver_step_to_collection(col, step)
    return col


def rename_collection(col, new_name):
    """
    Rename a Collection node name.

    Note: The Collection object stores a pointer to the underlying
    node. We can change the name without affecting the Collection
    object..

    :param col: Collection object to rename.
    :type col: Collection

    :param new_name: The new name to rename the Collection to.
    :type new_name: str
    """
    if col is None:
        msg = 'rename_collection: Can not rename, collection invalid.'
        LOG.warning(msg)
        return
    node = col.get_node()
    if node is None or maya.cmds.objExists(node) is False:
        msg = 'rename_collection: Can not rename, node invalid.'
        LOG.warning(msg)
        return
    maya.cmds.rename(node, new_name)
    return


def delete_collection(col):
    """
    Delete a Collection object (and underlying Maya node).

    :param col: The Collection object to delete.
    :type col: Collection
    """
    if col is None:
        return
    node = col.get_node()
    node = str(node)
    del col
    maya.cmds.delete(node)
    return


def select_collection(col):
    """
    Select the collection node, not the members of the collection node.

    :param col: The Collection object to select.
    :type col: Collection
    """
    if col is None:
        return
    node_uid = col.get_node_uid()
    if node_uid is None:
        return
    nodes = maya.cmds.ls(node_uid)
    if nodes is None:
        return

    # Run selection when Maya is idle next, otherwise this fails to
    # select the objectSet and instead selects the contents of the
    # objectSet. Issue #23
    cmd = 'maya.cmds.select(%r, replace=True, noExpand=True)'
    cmd = cmd % str(nodes[0])
    maya.cmds.evalDeferred(cmd)
    return


def get_previous_collection_and_index(cols, current_col):
    """
    Get the previous collection to the current collection, in list of
    collections.

    :param cols: List of collections.
    :type cols: [Collection, ..]

    :param current_col: The current collection.
    :type current_col: Collection

    :returns: Collection and index in 'cols' of the previous collection.
    :rtype: Collection, int
    """
    prev_col = None
    prev_index = None
    if len(cols) < 2:
        return prev_col, prev_index
    col_names = [col.get_node() for col in cols]
    current_col_name = current_col.get_node()
    current_index = col_names.index(current_col_name)
    prev_index = current_index - 1
    prev_col = cols[prev_index]
    return prev_col, prev_index


def get_previous_collection(cols, current_col):
    """
    Get the previous collection to the current collection, in list of
    collections.

    :param cols: List of collections.
    :type cols: [Collection, ..]

    :param current_col: The current collection.
    :type current_col: Collection

    :returns: The previous Collection in cols relative to current_col.
    :rtype: Collection
    """
    prev_col, prev_index = get_previous_collection_and_index(cols, current_col)
    return prev_col


def set_solver_results_on_collection(col, solres_list):
    """
    This function is expected to manipulate the list of solver result
    """
    msg = 'TODO: Create attributes and set keyframes according to the errors'
    msg += ' returned by the solver.'
    LOG.debug(msg)


def log_solve_results(log, solres_list, total_time=None, status_fn=None):
    """
    Displays / saves the Solve Results.

    :param log: Logging object to log with.
    :type log: logger

    :param solres_list: List of Solve Results to log.
    :type solres_list: list of SolveResult

    :param total_time:
    :type total_time: None or float

    :param status_fn: Function to set the status text.
    :type status_fn: callable function or None

    :returns: Nothing.
    :rtype: None
    """
    status_str = ''
    long_status_str = ''

    # Get Solver success.
    success = True
    for solres in solres_list:
        value = solres.get_success()
        if value is not True:
            success = False
            break
    if success is True:
        status_str += 'Solved: '
        long_status_str += 'Solved: '
    else:
        status_str += 'Failed: '
        long_status_str += 'Failed: '

    frame_error_list = mmapi.merge_frame_error_list(solres_list)
    frame_error_txt = pprint.pformat(dict(frame_error_list))
    log.debug('Per-Frame Errors:\n%s', frame_error_txt)

    timer_stats = mmapi.combine_timer_stats(solres_list)
    timer_stats_txt = pprint.pformat(dict(timer_stats))
    log.debug('Timer Statistics:\n%s', timer_stats_txt)

    avg_error = mmapi.get_average_frame_error_list(frame_error_list)
    status_str += 'avg err %.2fpx' % avg_error
    long_status_str += 'Average Error %.2fpx' % avg_error

    max_frame, max_error = mmapi.get_max_frame_error(frame_error_list)
    status_str += ' | max err %.2fpx at %s' % (max_error, max_frame)
    long_status_str += ' | Max Error %.2fpx at %s' % (max_error, max_frame)

    if total_time is not None:
        log.info('Total Time: %.3f seconds', total_time)
        status_str += ' | time %.3fsec' % total_time
        long_status_str += ' | Time %.3fsec' % total_time

    log.info('Max Frame Error: %.2f pixels at frame %s', max_error, max_frame)
    log.info('Average Error: %.2f pixels', avg_error)
        
    if status_fn is not None:
        status_fn(status_str)
    log.warning(long_status_str)
    return


def get_override_current_frame_from_collection(col):
    """
    Get the value of 'Override Current Frame', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: True or False.
    :rtype: bool
    """
    node = col.get_node()
    ensure_override_current_frame_attr_exists(col)
    value = mmapi.get_value_on_node_attr(node, const.OVERRIDE_CURRENT_FRAME_ATTR)
    assert isinstance(value, bool)
    return value


def set_override_current_frame_on_collection(col, value):
    """
    Set the value of 'Override Current Frame' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: bool
    """
    assert isinstance(value, bool)
    ensure_override_current_frame_attr_exists(col)
    node = col.get_node()
    mmapi.set_value_on_node_attr(node, const.OVERRIDE_CURRENT_FRAME_ATTR, value)
    return


def ensure_override_current_frame_attr_exists(col):
    """
    Forces the creation of a 'override current frame' attribute, if
    none exists already.

    :param col: The Collection to create the attribute on.
    :type col: Collection
    """
    node = col.get_node()
    default_value = False
    attr_name = const.OVERRIDE_CURRENT_FRAME_ATTR
    attrs = maya.cmds.listAttr(node)
    if attr_name in attrs:
        return
    maya.cmds.addAttr(
        node,
        defaultValue=default_value,
        longName=attr_name,
        attributeType='bool'
    )
    node_attr = node + '.' + attr_name
    maya.cmds.setAttr(node_attr, lock=True)
    return


def get_attribute_toggle_animated_from_collection(col):
    """
    Get the value of 'Attributes Toggle Animated', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: True or False.
    :rtype: bool
    """
    node = col.get_node()
    ensure_attribute_toggle_animated_attr_exists(col)
    value = mmapi.get_value_on_node_attr(node, const.ATTRIBUTE_TOGGLE_ANIMATED_ATTR)
    assert isinstance(value, bool)
    return value


def set_attribute_toggle_animated_on_collection(col, value):
    """
    Set the value of 'Attributes Toggle Animated' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: bool
    """
    assert isinstance(value, bool)
    ensure_attribute_toggle_animated_attr_exists(col)
    node = col.get_node()
    mmapi.set_value_on_node_attr(node, const.ATTRIBUTE_TOGGLE_ANIMATED_ATTR, value)
    return


def ensure_attribute_toggle_animated_attr_exists(col):
    """
    Forces the creation of a 'attribute_toggle_animated' attribute, if
    none exists already.

    :param col: The Collection to create the attribute on.
    :type col: Collection
    """
    node = col.get_node()
    default_value = const.ATTRIBUTE_TOGGLE_ANIMATED_DEFAULT_VALUE
    attr_name = const.ATTRIBUTE_TOGGLE_ANIMATED_ATTR
    attrs = maya.cmds.listAttr(node)
    if attr_name in attrs:
        return
    maya.cmds.addAttr(
        node,
        defaultValue=default_value,
        longName=attr_name,
        attributeType='bool'
    )
    node_attr = node + '.' + attr_name
    maya.cmds.setAttr(node_attr, lock=True)
    return


def get_attribute_toggle_static_from_collection(col):
    """
    Get the value of 'Attributes Toggle Static', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: True or False.
    :rtype: bool
    """
    node = col.get_node()
    ensure_attribute_toggle_static_attr_exists(col)
    value = mmapi.get_value_on_node_attr(node, const.ATTRIBUTE_TOGGLE_STATIC_ATTR)
    assert isinstance(value, bool)
    return value


def set_attribute_toggle_static_on_collection(col, value):
    """
    Set the value of 'Attributes Toggle Static' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: bool
    """
    assert isinstance(value, bool)
    ensure_attribute_toggle_static_attr_exists(col)
    node = col.get_node()
    mmapi.set_value_on_node_attr(node, const.ATTRIBUTE_TOGGLE_STATIC_ATTR, value)
    return


def ensure_attribute_toggle_static_attr_exists(col):
    """
    Forces the creation of a 'attribute_toggle_static' attribute, if
    none exists already.

    :param col: The Collection to create the attribute on.
    :type col: Collection
    """
    node = col.get_node()
    default_value = const.ATTRIBUTE_TOGGLE_STATIC_DEFAULT_VALUE
    attr_name = const.ATTRIBUTE_TOGGLE_STATIC_ATTR
    attrs = maya.cmds.listAttr(node)
    if attr_name in attrs:
        return
    maya.cmds.addAttr(
        node,
        defaultValue=default_value,
        longName=attr_name,
        attributeType='bool'
    )
    node_attr = node + '.' + attr_name
    maya.cmds.setAttr(node_attr, lock=True)
    return


def get_attribute_toggle_locked_from_collection(col):
    """
    Get the value of 'Attributes Toggle Locked', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: True or False.
    :rtype: bool
    """
    node = col.get_node()
    ensure_attribute_toggle_locked_attr_exists(col)
    value = mmapi.get_value_on_node_attr(node, const.ATTRIBUTE_TOGGLE_LOCKED_ATTR)
    assert isinstance(value, bool)
    return value


def set_attribute_toggle_locked_on_collection(col, value):
    """
    Set the value of 'Attributes Toggle Locked' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: bool
    """
    assert isinstance(value, bool)
    ensure_attribute_toggle_locked_attr_exists(col)
    node = col.get_node()
    mmapi.set_value_on_node_attr(node, const.ATTRIBUTE_TOGGLE_LOCKED_ATTR, value)
    return


def ensure_attribute_toggle_locked_attr_exists(col):
    """
    Forces the creation of a 'attribute_toggle_locked' attribute, if
    none exists already.

    :param col: The Collection to create the attribute on.
    :type col: Collection
    """
    node = col.get_node()
    default_value = const.ATTRIBUTE_TOGGLE_LOCKED_DEFAULT_VALUE
    attr_name = const.ATTRIBUTE_TOGGLE_LOCKED_ATTR
    attrs = maya.cmds.listAttr(node)
    if attr_name in attrs:
        return
    maya.cmds.addAttr(
        node,
        defaultValue=default_value,
        longName=attr_name,
        attributeType='bool'
    )
    node_attr = node + '.' + attr_name
    maya.cmds.setAttr(node_attr, lock=True)
    return


def get_object_toggle_camera_from_collection(col):
    """
    Get the value of 'Objects Toggle Camera', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: True or False.
    :rtype: bool
    """
    node = col.get_node()
    ensure_object_toggle_camera_attr_exists(col)
    value = mmapi.get_value_on_node_attr(node, const.OBJECT_TOGGLE_CAMERA_ATTR)
    assert isinstance(value, bool)
    return value


def set_object_toggle_camera_on_collection(col, value):
    """
    Set the value of 'Objects Toggle Camera' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: bool
    """
    assert isinstance(value, bool)
    ensure_object_toggle_camera_attr_exists(col)
    node = col.get_node()
    mmapi.set_value_on_node_attr(node, const.OBJECT_TOGGLE_CAMERA_ATTR, value)
    return


def ensure_object_toggle_camera_attr_exists(col):
    """
    Forces the creation of a 'object_toggle_camera' attribute, if
    none exists already.

    :param col: The Collection to create the attribute on.
    :type col: Collection
    """
    node = col.get_node()
    default_value = const.OBJECT_TOGGLE_CAMERA_DEFAULT_VALUE
    attr_name = const.OBJECT_TOGGLE_CAMERA_ATTR
    attrs = maya.cmds.listAttr(node)
    if attr_name in attrs:
        return
    maya.cmds.addAttr(
        node,
        defaultValue=default_value,
        longName=attr_name,
        attributeType='bool'
    )
    node_attr = node + '.' + attr_name
    maya.cmds.setAttr(node_attr, lock=True)
    return


def get_object_toggle_marker_from_collection(col):
    """
    Get the value of 'Objects Toggle Marker', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: True or False.
    :rtype: bool
    """
    node = col.get_node()
    ensure_object_toggle_marker_attr_exists(col)
    value = mmapi.get_value_on_node_attr(node, const.OBJECT_TOGGLE_MARKER_ATTR)
    assert isinstance(value, bool)
    return value


def set_object_toggle_marker_on_collection(col, value):
    """
    Set the value of 'Objects Toggle Marker' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: bool
    """
    assert isinstance(value, bool)
    ensure_object_toggle_marker_attr_exists(col)
    node = col.get_node()
    mmapi.set_value_on_node_attr(node, const.OBJECT_TOGGLE_MARKER_ATTR, value)
    return


def ensure_object_toggle_marker_attr_exists(col):
    """
    Forces the creation of a 'object_toggle_marker' attribute, if
    none exists already.

    :param col: The Collection to create the attribute on.
    :type col: Collection
    """
    node = col.get_node()
    default_value = const.OBJECT_TOGGLE_MARKER_DEFAULT_VALUE
    attr_name = const.OBJECT_TOGGLE_MARKER_ATTR
    attrs = maya.cmds.listAttr(node)
    if attr_name in attrs:
        return
    maya.cmds.addAttr(
        node,
        defaultValue=default_value,
        longName=attr_name,
        attributeType='bool'
    )
    node_attr = node + '.' + attr_name
    maya.cmds.setAttr(node_attr, lock=True)
    return


def get_object_toggle_bundle_from_collection(col):
    """
    Get the value of 'Objects Toggle Bundle', from a Collection.

    :param col: The Collection to query.
    :type col: Collection

    :returns: True or False.
    :rtype: bool
    """
    node = col.get_node()
    ensure_object_toggle_bundle_attr_exists(col)
    value = mmapi.get_value_on_node_attr(node, const.OBJECT_TOGGLE_BUNDLE_ATTR)
    assert isinstance(value, bool)
    return value


def set_object_toggle_bundle_on_collection(col, value):
    """
    Set the value of 'Objects Toggle Bundle' on a Collection.

    :param col: The Collection to change.
    :type col: Collection

    :param value: Value to set to.
    :type value: bool
    """
    assert isinstance(value, bool)
    ensure_object_toggle_bundle_attr_exists(col)
    node = col.get_node()
    mmapi.set_value_on_node_attr(node, const.OBJECT_TOGGLE_BUNDLE_ATTR, value)
    return


def ensure_object_toggle_bundle_attr_exists(col):
    """
    Forces the creation of a 'object_toggle_bundle' attribute, if
    none exists already.

    :param col: The Collection to create the attribute on.
    :type col: Collection
    """
    node = col.get_node()
    default_value = const.OBJECT_TOGGLE_BUNDLE_DEFAULT_VALUE
    attr_name = const.OBJECT_TOGGLE_BUNDLE_ATTR
    attrs = maya.cmds.listAttr(node)
    if attr_name in attrs:
        return
    maya.cmds.addAttr(
        node,
        defaultValue=default_value,
        longName=attr_name,
        attributeType='bool'
    )
    node_attr = node + '.' + attr_name
    maya.cmds.setAttr(node_attr, lock=True)
    return


def create_solver_step():
    """
    Create a SolverStep object and return it.
    """
    data = const.SOLVER_STEP_DATA_DEFAULT.copy()

    data['name'] = str(uuid.uuid4())

    start, end = utils_time.get_maya_timeline_range_inner()
    frame_list = list(xrange(start, end + 1))
    data['frame_list'] = frame_list

    step = solver_step.SolverStep(data=data)
    return step


def ensure_solver_steps_attr_exists(col):
    """
    Forces the creation of a 'solver step' attribute, if none exists
    already.

    :param col: The Collection to create the attribute on.
    :type col: Collection

    :rtype: None
    """
    assert isinstance(col, mmapi.Collection)
    node = col.get_node()
    attr_name = const.SOLVER_STEP_ATTR
    attrs = maya.cmds.listAttr(node)
    if attr_name in attrs:
        return
    maya.cmds.addAttr(
        node,
        longName=attr_name,
        dataType='string'
    )
    maya.cmds.setAttr(
        node + '.' + attr_name,
        lock=True
    )
    return


def get_solver_steps_from_collection(col):
    """
    Load all steps from collection.

    :param col: The Collection to query.
    :type col: Collection

    :rtype: list of SolverStep
    """
    assert isinstance(col, mmapi.Collection)
    if col is None:
        return []
    node = col.get_node()
    if maya.cmds.objExists(node) is False:
        return []
    ensure_solver_steps_attr_exists(col)
    data_list = mmapi.get_data_on_node_attr(node, const.SOLVER_STEP_ATTR)
    step_list = [solver_step.SolverStep(d) for d in data_list]
    return step_list


def get_named_solver_step_from_collection(col, name):
    assert isinstance(col, mmapi.Collection)
    step_list = get_solver_steps_from_collection(col)
    name_list = [s.get_name() for s in step_list]
    if name not in name_list:
        msg = 'SolverStep %r could not be found in all steps: %r'
        LOG.warning(msg, name, name_list)
        return None
    idx = name_list.index(name)
    return step_list[idx]


def set_named_solver_step_to_collection(col, step):
    assert isinstance(col, mmapi.Collection)
    name = step.get_name()
    step_list = get_solver_steps_from_collection(col)
    name_list = [s.get_name() for s in step_list]
    if name not in name_list:
        raise ValueError
    idx = list(name_list).index(name)
    step_list.pop(idx)
    step_list.insert(idx, step)
    set_solver_step_list_to_collection(col, step_list)
    return


def add_solver_step_to_collection(col, step):
    assert isinstance(col, mmapi.Collection)
    step_list = get_solver_steps_from_collection(col)
    name_list = [s.get_name() for s in step_list]
    name = step.get_name()
    if name in name_list:
        raise ValueError, 'Solver step already exists with that name.'
    step_list.insert(0, step)  # new step pushed onto the front.
    set_solver_step_list_to_collection(col, step_list)
    return


def remove_solver_step_from_collection(col, step):
    assert isinstance(col, mmapi.Collection)
    if step is None:
        msg = 'Cannot remove SolverStep, step is invalid.'
        LOG.warning(msg)
        return
    step_list = get_solver_steps_from_collection(col)
    name_list = [s.get_name() for s in step_list]
    name = step.get_name()
    if name not in name_list:
        raise ValueError
    idx = list(name_list).index(name)
    step_list.pop(idx)
    set_solver_step_list_to_collection(col, step_list)
    return


def set_solver_step_list_to_collection(col, step_list):
    node = col.get_node()
    data_list = [s.get_data() for s in step_list]
    ensure_solver_steps_attr_exists(col)
    mmapi.set_data_on_node_attr(node, const.SOLVER_STEP_ATTR, data_list)
    sol_list = compile_solvers_from_steps(col, step_list)
    col.set_solver_list(sol_list)
    return


def compile_solvers_from_steps(col, step_list, prog_fn=None):
    """
    Compile the solver steps attached to Collection into solvers.
    """
    use_cur_frame = get_override_current_frame_from_collection(col)
    sol_list = []
    for i, step in enumerate(step_list):
        sol_list += step.compile(
            col,
            override_current_frame=use_cur_frame)
        if prog_fn is not None:
            ratio = float(i) / len(step_list)
            percent = int(ratio * 100.0)
            prog_fn(percent)
    return sol_list


def compile_collection(col, prog_fn=None):
    """
    Compiles, checks and validates the collection, ready for a solve.

    :param col: Collection to execute.
    :type col: Collection

    :param prog_fn: Progress function that is called each time progress
                    is made. The function should take a single 'int'
                    argument, and the integer is expected to be a
                    percentage value, between 0 and 100.
    :type prog_fn: None or function
    """
    step_list = get_solver_steps_from_collection(col)
    sol_list = compile_solvers_from_steps(col, step_list, prog_fn=prog_fn)
    col.set_solver_list(sol_list)
    return col.is_valid(prog_fn=prog_fn)


def execute_collection(col,
                       log_level=None,
                       refresh=False,
                       force_update=False,
                       prog_fn=None,
                       status_fn=None):
    """
    Execute the entire collection; Solvers, Markers, Bundles, etc.

    :param col: Collection to execute.
    :type col: Collection

    :param log_level: Logging level to print out.
    :type log_level: None or str

    :param refresh: Should we refresh the viewport?
    :type refresh: bool

    :param force_update: Should we force-update the Maya DG?
    :type force_update: bool

    :param prog_fn: A function called with an 'int' argument, to
                    display progress information to the user. The
                    integer is expected to be between 0 and 100 (and
                    is read as a percentage).
    :type prog_fn: None or function

    :param status_fn: A function called with an 'str' argument, to display
                      status information to the user.
    :type status_fn: None or function
    """
    msg = 'execute_collection: '
    msg += 'col=%r log_level=%r refresh=%r force_update=%r '
    msg += 'prog_fn=%r status_fn=%r'
    LOG.debug(msg, col, log_level, refresh, prog_fn, status_fn)

    assert isinstance(refresh, bool)
    assert isinstance(force_update, bool)
    assert log_level is None or isinstance(log_level, (str, unicode))
    assert prog_fn is None or hasattr(prog_fn, '__call__')
    assert status_fn is None or hasattr(status_fn, '__call__')

    log = LOG
    verbose = False
    if log_level in const.LOG_LEVEL_LIST:
        if log_level == const.LOG_LEVEL_VERBOSE:
            log_level = const.LOG_LEVEL_INFO
            verbose = True
        log_level = log_level.upper()
        mmSolver.logger.get_logger(log_level)
    else:
        msg = 'log_level value is invalid; value=%r'
        raise ValueError(msg % log_level)

    # Execute the solve.
    s = time.time()
    solres_list = col.execute(
        verbose=verbose,
        refresh=refresh,
        force_update=force_update,
        prog_fn=prog_fn,
        status_fn=status_fn,
    )
    e = time.time()

    # Display Solver results
    set_solver_results_on_collection(col, solres_list)
    log_solve_results(log, solres_list, total_time=e-s, status_fn=status_fn)
    return


def run_solve_ui(col, refresh_state, force_update_state, log_level, window):
    """
    Run the active "solve" (UI state information), and update the UI.

    This is a UI focused function. Calling this function with the
    'window' argument set will update the UI and show progress to the
    user.

    If the UI window is not given, the solve still runs, but does not
    update the UI.

    :param col: The active collection to solve.
    :type col: Collection

    :param refresh_state: Should we update the viewport while solving?
    :type refresh_state: bool

    :param force_update_state: Should we forcibly update the DG while solving?
    :type force_update_state: bool

    :param log_level: How much information should we print out;a
                      'error', 'warning', 'info', 'verbose' or 'debug'.
    :type log_level: str

    :param window: The SolverWindow object for the UI.
    :type window: SolverWindow or None
    """
    if window is not None:
        window.setStatusLine(const.STATUS_EXECUTING)

    try:
        if window is not None:
            window.progressBar.setValue(0)
            window.progressBar.show()

        if col is None:
            msg = 'No active collection.'
            if window is not None:
                window.setStatusLine('ERROR: ' + msg)
            LOG.error(msg)
            return
        ok = compile_collection(col)
        if ok is not True:
            msg = 'Cannot execute solver, collection is not valid.'
            msg += 'collection=%r'
            col_node = col.get_node()
            if window is not None:
                status = 'Warning: ' + msg
                window.setStatusLine(status % col_node)
            LOG.warning(msg, col_node)
        else:
            prog_fn = LOG.warning
            status_fn = LOG.warning
            if window is not None:
                prog_fn = window.setProgressValue
                status_fn = window.setStatusLine

            execute_collection(
                col,
                log_level=log_level,
                refresh=refresh_state,
                force_update=force_update_state,
                prog_fn=prog_fn,
                status_fn=status_fn,
            )
    finally:
        if window is not None:
            window.progressBar.setValue(100)
            window.progressBar.hide()
    return
