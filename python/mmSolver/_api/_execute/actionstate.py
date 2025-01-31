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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

import mmSolver.logger
import mmSolver._api.solveresult as solveresult
import mmSolver._api.action as api_action
import mmSolver._api.constant as const

LOG = mmSolver.logger.get_logger()

ActionState = collections.namedtuple(
    'ActionState',
    [
        'status',
        'message',
        'error_number',
        'parameter_number',
        'frames_number',
        'frames',
    ],
)


def create_action_state(
    status=None,
    message=None,
    error_number=None,
    parameter_number=None,
    frames_number=None,
    frames=None,
):
    assert status is not None
    assert status in const.ACTION_STATUS_LIST
    if error_number is None:
        error_number = 0
    if parameter_number is None:
        parameter_number = 0
    if frames_number is None:
        frames_number = 0
    state = ActionState(
        status=status,
        message=message,
        error_number=error_number,
        parameter_number=parameter_number,
        frames_number=frames_number,
        frames=frames,
    )
    return state


def run_validate_action(vaction):
    """
    Call a single validate action, and see what happens.

    :param vaction: Validation action object to be run.
    :type vaction: Action

    :return:
        An ActionState object containing, if the validation succeeded,
        the user message we present for the state, metrics about the
        solve (number of parameters, number of errors, and number of
        frames to solve)
    :rtype: ActionState
    """
    if not isinstance(vaction, api_action.Action):
        state = create_action_state(
            status=const.ACTION_STATUS_SUCCESS, message='Action cannot be run.'
        )
        return state
    vfunc, vargs, vkwargs = api_action.action_to_components(vaction)
    vfunc_is_mmsolver_v1 = api_action.action_func_is_mmSolver_v1(vaction)
    vfunc_is_mmsolver_v2 = api_action.action_func_is_mmSolver_v2(vaction)
    vfunc_is_camera_solve = api_action.action_func_is_camera_solve(vaction)
    vfunc_is_mmsolver = any((vfunc_is_mmsolver_v1, vfunc_is_mmsolver_v2))

    num_param = 0
    num_err = 0
    frames = list(sorted(vkwargs.get('frame', [])))
    num_frames = len(frames)
    if num_frames == 0 and vfunc_is_mmsolver is True:
        msg = 'Failed to validate frames: frames=%r'
        message = msg % num_frames
        state = create_action_state(
            status=const.ACTION_STATUS_FAILED,
            message=message,
            error_number=num_err,
            parameter_number=num_param,
            frames_number=num_frames,
            frames=frames,
        )
        return state

    # Run validate function
    solve_data = vfunc(*vargs, **vkwargs)

    if vfunc_is_mmsolver is False:
        msg = 'Validated frames: frames=%r'
        message = msg % num_frames
        state = create_action_state(
            status=const.ACTION_STATUS_SUCCESS,
            message=message,
            error_number=num_err,
            parameter_number=num_param,
            frames_number=num_frames,
            frames=frames,
        )
        return state

    if vfunc_is_mmsolver_v2 is True:
        solve_data = vkwargs['resultsNode']
    if vfunc_is_camera_solve is True:
        # NOTE: This assumes that the camera solver is using
        # const.SOLVER_VERSION_TWO.
        #
        # Get the collection node given to the camera solve.
        solve_data = vargs[0]

    solres = solveresult.SolveResult(solve_data)

    use_valid_frame_check = False
    if use_valid_frame_check is False:
        print_stats = solres.get_print_stats()
        num_param = print_stats.get('number_of_parameters', 0)
        num_err = print_stats.get('number_of_errors', 0)
        if num_param == 0 or num_err == 0 or num_param > num_err:
            msg = (
                'Invalid parameters and errors (param=%r errors=%r frames=%r), '
                'skipping solve: %r'
            )
            message = msg % (num_param, num_err, num_frames, list(sorted(frames)))
            state = create_action_state(
                status=const.ACTION_STATUS_FAILED,
                message=message,
                error_number=num_err,
                parameter_number=num_param,
                frames_number=num_frames,
                frames=frames,
            )
            return state

        msg = 'Validated parameters, errors and frames: param=%r errors=%r frames=%r'
        message = msg % (num_param, num_err, num_frames)
        state = create_action_state(
            status=const.ACTION_STATUS_SUCCESS,
            message=message,
            error_number=num_err,
            parameter_number=num_param,
            frames_number=num_frames,
            frames=frames,
        )
        return state
    else:
        # In the future it may make sense to check for "valid frames" that
        # the solver can solve and report these to the user.

        print_stats = solres.get_print_stats()
        num_param = print_stats.get('number_of_parameters', 0)
        num_err = print_stats.get('number_of_errors', 0)
        if num_param == 0 or num_err == 0 or num_param > num_err:
            msg = (
                'Invalid parameters and errors (param=%r errors=%r frames=%r), '
                'skipping solve: %r'
            )
            message = msg % (num_param, num_err, num_frames, list(sorted(frames)))
            state = create_action_state(
                status=const.ACTION_STATUS_FAILED,
                message=message,
                error_number=num_err,
                parameter_number=num_param,
                frames_number=num_frames,
                frames=frames,
            )
            return state

        solver_valid_frames = solres.get_solver_valid_frame_list()
        if len(solver_valid_frames) == 0:
            # This error should be raised if ALL the frames in the
            # solve are invalid, and if they are invalid then the frames
            # should just be skipped and the solve should be continued.
            solver_invalid_frames = solres.get_solver_invalid_frame_list()
            assert len(solver_invalid_frames) == len(frames)
            msg = 'All frames are invalid, skipping solve: %r' % list(sorted(frames))
            state = create_action_state(
                status=const.ACTION_STATUS_FAILED,
                message=msg,
                error_number=num_err,
                parameter_number=num_param,
                frames_number=num_frames,
                frames=frames,
            )
            return state

        msg = 'Validated solver frames: %r'
        message = msg % solver_valid_frames
        state = create_action_state(
            status=const.ACTION_STATUS_SUCCESS,
            message=message,
            error_number=num_err,
            parameter_number=num_param,
            frames_number=num_frames,
            frames=frames,
        )
        return state

    # Should not get here.
    raise NotImplementedError


def run_validate_action_list(vaction_list):
    """
    Calls the validation functions attached to the Action list.

    See :py:func:`_run_validate_action` for more details.

    :param vaction_list: List of validate actions to call.
    :type vaction_list: [Action, ..]

    :return:
        A list of validations, with a single valid boolean (did the
        validation succeed?).
    :rtype: (bool, [str, ..], [(int, int, int), ..])
    """
    assert len(vaction_list) > 0
    state_list = []
    for vaction in vaction_list:
        state = run_validate_action(vaction)
        state_list.append(state)
    assert len(vaction_list) == len(state_list)
    return state_list


def convert_action_state_to_plain_old_data(state_list):
    """
    Convert ActionStates back to the previous supported data structure.

    :param state_list: [ActionState, ..]
    :return:
        A list of validations, with a single valid boolean (did the
        validation succeed?).
    :rtype: (bool, [str, ..], [(int, int, int), ..])
    """
    valid = True
    message_list = []
    metrics_list = []
    for state in state_list:
        if state.status != const.ACTION_STATUS_SUCCESS:
            valid = False
        message_list.append(state.message)
        metrics = (
            state.error_number or 0,
            state.parameter_number or 0,
            state.frames_number or 0,
        )
        metrics_list.append(metrics)
    return valid, message_list, metrics_list
