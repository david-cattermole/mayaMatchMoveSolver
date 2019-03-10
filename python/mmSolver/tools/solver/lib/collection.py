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

    # BUG: Using Maya 'select' command does not work, it always
    # selects with 'noExpand=False', regardless of option,
    # # maya.cmds.select(nodes[0], replace=True, noExpand=True)

    # HACK around above Maya bug:
    # Get API selection object, and then force the Maya selection to
    # this node.
    sel_list = OpenMaya.MSelectionList()
    for node in nodes:
        try:
            sel_list.add(node)
        except RuntimeError:
            pass
    OpenMaya.MGlobal.setActiveSelectionList(sel_list)
    return


def set_solver_results_on_collection(col, solres_list):
    """
    This function is expected to manipulate the list of solver result
    """
    msg = 'TODO: Create attributes and set keyframes according to the errors'
    msg += ' returned by the solver.'
    LOG.debug(msg)


def log_solve_results(log, solres_list, total_time=None):
    """
    Displays / saves the Solve Results.

    :param log: Logging object to log with.
    :type log: logger

    :param solres_list: List of Solve Results to log.
    :type solres_list: list of SolveResult

    :param total_time:
    :type total_time: None or float

    :returns: Nothing.
    :rtype: None
    """
    frame_error_list = mmapi.merge_frame_error_list(solres_list)
    frame_error_txt = pprint.pformat(dict(frame_error_list))
    log.debug('Per-Frame Errors:\n%s', frame_error_txt)

    timer_stats = mmapi.combine_timer_stats(solres_list)
    timer_stats_txt = pprint.pformat(dict(timer_stats))
    log.debug('Timer Statistics:\n%s', timer_stats_txt)

    avg_error = mmapi.get_average_frame_error_list(frame_error_list)
    log.info('Average Error: %.2f pixels', avg_error)

    max_frame_error = mmapi.get_max_frame_error(frame_error_list)
    log.info(
        'Max Frame Error: %.2f pixels at frame %s',
        max_frame_error[1],
        max_frame_error[0]
    )

    if total_time is not None:
        log.info('Total Time: %.3f seconds', total_time)
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
    node = col.get_node()
    ensure_solver_steps_attr_exists(col)
    data_list = mmapi.get_data_on_node_attr(node, const.SOLVER_STEP_ATTR)
    step_list = map(lambda x: solver_step.SolverStep(x), data_list)
    return step_list


def get_named_solver_step_from_collection(col, name):
    step_list = get_solver_steps_from_collection(col)
    name_list = map(lambda x: x.get_name(), step_list)
    if name not in name_list:
        msg = 'SolverStep %r could not be found in all steps: %r'
        LOG.warning(msg, name, name_list)
        return None
    idx = name_list.index(name)
    return step_list[idx]


def set_named_solver_step_to_collection(col, step):
    name = step.get_name()
    step_list = get_solver_steps_from_collection(col)
    name_list = map(lambda x: x.get_name(), step_list)
    if name not in name_list:
        raise ValueError
    idx = list(name_list).index(name)
    step_list.pop(idx)
    step_list.insert(idx, step)
    set_solver_step_list_to_collection(col, step_list)
    return


def add_solver_step_to_collection(col, step):
    step_list = get_solver_steps_from_collection(col)
    name_list = map(lambda x: x.get_name(), step_list)
    name = step.get_name()
    if name in name_list:
        raise ValueError
    step_list.insert(0, step)  # new step pushed onto the front.
    set_solver_step_list_to_collection(col, step_list)
    return


def remove_solver_step_from_collection(col, step):
    if step is None:
        msg = 'Cannot remove SolverStep, step is invalid.'
        LOG.warning(msg)
        return
    step_list = get_solver_steps_from_collection(col)
    name_list = map(lambda x: x.get_name(), step_list)
    name = step.get_name()
    if name not in name_list:
        raise ValueError
    idx = list(name_list).index(name)
    step_list.pop(idx)
    set_solver_step_list_to_collection(col, step_list)
    return


def set_solver_step_list_to_collection(col, step_list):
    node = col.get_node()
    data_list = map(lambda x: x.get_data(), step_list)
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
        tmp_list = step.compile(col, override_current_frame=use_cur_frame)
        sol_list += tmp_list
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
    msg += 'col=%r log_level=%r refresh=%r prog_fn=%r status_fn=%r'
    LOG.debug(msg, col, log_level, refresh, prog_fn, status_fn)

    assert isinstance(refresh, bool)
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
        prog_fn=prog_fn,
        status_fn=status_fn,
    )
    e = time.time()

    # Display Solver results
    set_solver_results_on_collection(col, solres_list)
    log_solve_results(log, solres_list, total_time=e-s)
    return


def run_solve_ui(col, refresh_state, log_level, window):
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
        ok = compile_collection(col)
        if ok is not True:
            msg = 'Cannot execute solver, collection is not valid.'
            msg += 'collection=%r'
            if window is not None:
                window.setStatusLine('Warning: ' + msg)
            LOG.warning(msg, col)
        else:
            prog_fn = LOG.warning
            status_fn = LOG.warning
            if window is not None:
                prog_fn = window.progressBar.setValue
                status_fn = window.setStatusLine
            
            execute_collection(
                col,
                log_level=log_level,
                refresh=refresh_state,
                prog_fn=prog_fn,
                status_fn=status_fn,
            )
    finally:
        if window is not None:
            window.progressBar.setValue(100)
            window.progressBar.hide()
            window.setStatusLine(const.STATUS_FINISHED)
    return
