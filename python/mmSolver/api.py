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
Controls the user-facing API.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# All the objects for the user API.
from mmSolver._api.camera import Camera
from mmSolver._api.bundle import Bundle
from mmSolver._api.marker import Marker, update_deviation_on_markers
from mmSolver._api.markergroup import MarkerGroup
from mmSolver._api.attribute import Attribute
from mmSolver._api.collection import Collection, update_deviation_on_collection
from mmSolver._api.line import Line
from mmSolver._api.lens import Lens
from mmSolver._api.execute import (
    create_execute_options,
    ExecuteOptions,
    ActionState,
    validate,
    execute,
)
from mmSolver._api.frame import Frame
from mmSolver._api.rootframe import (
    get_root_frames_from_markers,
    root_frames_subdivide,
    root_frames_list_combine,
)
from mmSolver._api.action import (
    Action,
    action_func_is_mmSolver,
    action_func_is_mmSolver_v1,
    action_func_is_mmSolver_v2,
    action_func_is_mmSolverAffects,
    func_str_to_callable,
    action_to_components,
)
from mmSolver._api.solverbase import (
    SolverBase,
)
from mmSolver._api.solverstep import (
    Solver,
    SolverStep,
)
from mmSolver._api.solverstandard import (
    SolverStandard,
)
from mmSolver._api.solverbasic import (
    SolverBasic,
)
from mmSolver._api.solvercamera import (
    SolverCamera,
)
from mmSolver._api.collectionutils import (
    run_progress_func,
    run_status_func,
    is_single_frame,
    disconnect_animcurves,
    reconnect_animcurves,
    clear_attr_keyframes,
    generate_isolate_nodes,
)
from mmSolver._api.markerutils import (
    calculate_marker_deviation,
    get_markers_start_end_frames,
    find_marker_attr_mapping,
    calculate_average_deviation,
    calculate_maximum_deviation,
)
from mmSolver._api.naming import (
    find_valid_maya_node_name,
    get_new_marker_name,
    get_new_bundle_name,
    get_new_line_name,
)
from mmSolver._api.state import (
    is_solver_running,
    set_solver_running,
    get_user_interrupt,
    set_user_interrupt,
)
from mmSolver._api.nodeconversion import (
    get_bundle_nodes_from_marker_nodes,
    get_marker_nodes_from_bundle_nodes,
    get_camera_nodes_from_marker_nodes,
)
from mmSolver._api.nodefilter import (
    filter_nodes_into_categories,
    filter_marker_nodes,
    filter_line_nodes,
    filter_lens_nodes,
    filter_image_plane_nodes,
    filter_marker_group_nodes,
    filter_bundle_nodes,
    filter_camera_nodes,
    filter_collection_nodes,
)
from mmSolver._api.solveresult import (
    SolveResult,
    combine_timer_stats,
    merge_frame_list,
    merge_frame_error_list,
    get_average_frame_error_list,
    get_max_frame_error,
    merge_marker_error_list,
    merge_marker_node_list,
    format_timestamp,
)
from mmSolver._api.triangulatebundle import (
    triangulate_bundle,
)
from mmSolver._api.excep import (
    MMException,
    NotValid,
    AlreadyLinked,
    AlreadyUnlinked,
    NotEnoughMarkers,
    SolverNotAvailable,
)
from mmSolver._api.constant import (
    OBJECT_TYPE_UNKNOWN,
    OBJECT_TYPE_ATTRIBUTE,
    OBJECT_TYPE_MARKER,
    OBJECT_TYPE_CAMERA,
    OBJECT_TYPE_MARKER_GROUP,
    OBJECT_TYPE_BUNDLE,
    OBJECT_TYPE_LINE,
    OBJECT_TYPE_LENS,
    OBJECT_TYPE_COLLECTION,
    OBJECT_TYPE_IMAGE_PLANE,
    OBJECT_TYPE_LIST,
    ATTR_STATE_INVALID,
    ATTR_STATE_STATIC,
    ATTR_STATE_ANIMATED,
    ATTR_STATE_LOCKED,
    SOLVER_TYPE_LEVMAR,
    SOLVER_TYPE_CMINPACK_LM,
    SOLVER_TYPE_CMINPACK_LMDIF,
    SOLVER_TYPE_CMINPACK_LMDER,
    SOLVER_TYPE_CERES_LMDIF,
    SOLVER_TYPE_CERES_LMDER,
    SOLVER_TYPE_DEFAULT,
    SOLVER_TYPE_LIST,
    SCENE_GRAPH_MODE_AUTO,
    SCENE_GRAPH_MODE_MAYA_DAG,
    SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
    SCENE_GRAPH_MODE_DEFAULT,
    SCENE_GRAPH_MODE_LIST,
    SCENE_GRAPH_MODE_AUTO_NAME,
    SCENE_GRAPH_MODE_MAYA_DAG_NAME,
    SCENE_GRAPH_MODE_MM_SCENE_GRAPH_NAME,
    SCENE_GRAPH_MODE_NAME_LIST,
    SCENE_GRAPH_MODE_AUTO_LABEL,
    SCENE_GRAPH_MODE_MAYA_DAG_LABEL,
    SCENE_GRAPH_MODE_MM_SCENE_GRAPH_LABEL,
    SCENE_GRAPH_MODE_LABEL_LIST,
    TIME_EVAL_MODE_DG_CONTEXT,
    TIME_EVAL_MODE_SET_TIME,
    TIME_EVAL_MODE_DEFAULT,
    TIME_EVAL_MODE_LIST,
    FRAME_SOLVE_MODE_ALL_FRAMES_AT_ONCE,
    FRAME_SOLVE_MODE_PER_FRAME,
    FRAME_SOLVE_MODE_DEFAULT,
    FRAME_SOLVE_MODE_LIST,
    AUTO_DIFF_TYPE_FORWARD,
    AUTO_DIFF_TYPE_CENTRAL,
    AUTO_DIFF_TYPE_LIST,
    ROOT_FRAME_STRATEGY_GLOBAL_VALUE,
    ROOT_FRAME_STRATEGY_FWD_PAIR_VALUE,
    ROOT_FRAME_STRATEGY_FWD_PAIR_AND_GLOBAL_VALUE,
    ROOT_FRAME_STRATEGY_FWD_INCREMENT_VALUE,
    ROOT_FRAME_STRATEGY_VALUE_LIST,
    ROOT_FRAME_STRATEGY_DEFAULT_VALUE,
    ROBUST_LOSS_TYPE_TRIVIAL_VALUE,
    ROBUST_LOSS_TYPE_SOFT_L_ONE_VALUE,
    ROBUST_LOSS_TYPE_CAUCHY_VALUE,
    ROBUST_LOSS_TYPE_VALUE_LIST,
    ROBUST_LOSS_TYPE_DEFAULT_VALUE,
    VALIDATE_MODE_PRE_VALIDATE_VALUE,
    VALIDATE_MODE_AT_RUNTIME_VALUE,
    VALIDATE_MODE_NONE_VALUE,
    VALIDATE_MODE_VALUE_LIST,
    EVENT_NAME_MARKER_CREATED,
    EVENT_NAME_BUNDLE_CREATED,
    EVENT_NAME_LINE_CREATED,
    EVENT_NAME_COLLECTION_CREATED,
    EVENT_NAME_COLLECTION_MARKERS_CHANGED,
    EVENT_NAME_COLLECTION_LINES_CHANGED,
    EVENT_NAME_COLLECTION_ATTRS_CHANGED,
    EVENT_NAME_ATTRIBUTE_STATE_CHANGED,
    EVENT_NAME_ATTRIBUTE_CONNECTION_CHANGED,
    EVENT_NAME_NODE_NAME_CHANGED,
    EVENT_NAME_NODE_DELETED,
    EVENT_NAME_MEMBERSHIP_CHANGED,
    EVENT_NAME_MAYA_SCENE_CLOSING,
    EVENT_NAME_LIST,
    ATTRIBUTE_USED_HINT_DEFAULT_VALUE,
    ATTRIBUTE_USED_HINT_USED_VALUE,
    ATTRIBUTE_USED_HINT_NOT_USED_VALUE,
    ATTRIBUTE_USED_HINT_LIST,
    MARKER_USED_HINT_DEFAULT_VALUE,
    MARKER_USED_HINT_USED_VALUE,
    MARKER_USED_HINT_NOT_USED_VALUE,
    MARKER_USED_HINT_LIST,
    ACTION_STATUS_SUCCESS,
    ACTION_STATUS_FAILED,
    ACTION_STATUS_LIST,
    LOG_LEVEL_ERROR,
    LOG_LEVEL_WARNING,
    LOG_LEVEL_INFO,
    LOG_LEVEL_VERBOSE,
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_LIST,
    LOG_LEVEL_ERROR_VALUE,
    LOG_LEVEL_WARNING_VALUE,
    LOG_LEVEL_INFO_VALUE,
    LOG_LEVEL_VERBOSE_VALUE,
    LOG_LEVEL_DEBUG_VALUE,
    LOG_LEVEL_NAME_TO_VALUE_MAP,
    LOG_LEVEL_DEFAULT,
    LOG_LEVEL_DEFAULT_VALUE,
)

# Utility functions that the user is allowed to use.
from mmSolver._api.utils import (
    load_plugin,
    get_object_type,
    get_data_on_node_attr,
    set_data_on_node_attr,
    get_value_on_node_attr,
    set_value_on_node_attr,
    get_marker_group_above_node,
    get_line_above_node,
)
from mmSolver.utils.undo import (
    undo_chunk_context,
)

undo_chunk = undo_chunk_context
from mmSolver.utils.animcurve import (
    create_anim_curve_node,
)
from mmSolver.utils.node import (
    get_long_name,
    get_as_selection_list,
    get_as_dag_path,
    get_as_object,
    get_as_plug,
)

__all__ = [
    # Classes
    'Camera',
    'Bundle',
    'Marker',
    'Line',
    'MarkerGroup',
    'Attribute',
    'ExecuteOptions',
    'Collection',
    'Lens',
    'Frame',
    'Solver',  # Backwards compatibility
    'Action',
    'ActionState',
    'SolverBase',
    'SolverStandard',
    'SolverBasic',
    'SolverCamera',
    'SolverStep',
    'SolveResult',
    # Constants
    'OBJECT_TYPE_UNKNOWN',
    'OBJECT_TYPE_ATTRIBUTE',
    'OBJECT_TYPE_MARKER',
    'OBJECT_TYPE_CAMERA',
    'OBJECT_TYPE_LINE',
    'OBJECT_TYPE_LENS',
    'OBJECT_TYPE_MARKER_GROUP',
    'OBJECT_TYPE_BUNDLE',
    'OBJECT_TYPE_COLLECTION',
    'OBJECT_TYPE_IMAGE_PLANE',
    'OBJECT_TYPE_LIST',
    'ATTR_STATE_INVALID',
    'ATTR_STATE_STATIC',
    'ATTR_STATE_ANIMATED',
    'ATTR_STATE_LOCKED',
    'SOLVER_TYPE_LEVMAR',
    'SOLVER_TYPE_CMINPACK_LM',
    'SOLVER_TYPE_CMINPACK_LMDIF',
    'SOLVER_TYPE_CMINPACK_LMDER',
    'SOLVER_TYPE_CERES_LMDIF',
    'SOLVER_TYPE_CERES_LMDER',
    'SOLVER_TYPE_DEFAULT',
    'SOLVER_TYPE_LIST',
    'SCENE_GRAPH_MODE_AUTO',
    'SCENE_GRAPH_MODE_MAYA_DAG',
    'SCENE_GRAPH_MODE_MM_SCENE_GRAPH',
    'SCENE_GRAPH_MODE_DEFAULT',
    'SCENE_GRAPH_MODE_LIST',
    'SCENE_GRAPH_MODE_AUTO_NAME',
    'SCENE_GRAPH_MODE_MAYA_DAG_NAME',
    'SCENE_GRAPH_MODE_MM_SCENE_GRAPH_NAME',
    'SCENE_GRAPH_MODE_NAME_LIST',
    'SCENE_GRAPH_MODE_AUTO_LABEL',
    'SCENE_GRAPH_MODE_MAYA_DAG_LABEL',
    'SCENE_GRAPH_MODE_MM_SCENE_GRAPH_LABEL',
    'SCENE_GRAPH_MODE_LABEL_LIST',
    'TIME_EVAL_MODE_DG_CONTEXT',
    'TIME_EVAL_MODE_SET_TIME',
    'TIME_EVAL_MODE_DEFAULT',
    'TIME_EVAL_MODE_LIST',
    'FRAME_SOLVE_MODE_ALL_FRAMES_AT_ONCE',
    'FRAME_SOLVE_MODE_PER_FRAME',
    'FRAME_SOLVE_MODE_DEFAULT',
    'FRAME_SOLVE_MODE_LIST',
    'AUTO_DIFF_TYPE_FORWARD',
    'AUTO_DIFF_TYPE_CENTRAL',
    'AUTO_DIFF_TYPE_LIST',
    'ROOT_FRAME_STRATEGY_GLOBAL_VALUE',
    'ROOT_FRAME_STRATEGY_FWD_PAIR_VALUE',
    'ROOT_FRAME_STRATEGY_FWD_PAIR_AND_GLOBAL_VALUE',
    'ROOT_FRAME_STRATEGY_FWD_INCREMENT_VALUE',
    'ROOT_FRAME_STRATEGY_VALUE_LIST',
    'ROOT_FRAME_STRATEGY_DEFAULT_VALUE',
    'ROBUST_LOSS_TYPE_TRIVIAL_VALUE',
    'ROBUST_LOSS_TYPE_SOFT_L_ONE_VALUE',
    'ROBUST_LOSS_TYPE_CAUCHY_VALUE',
    'ROBUST_LOSS_TYPE_VALUE_LIST',
    'ROBUST_LOSS_TYPE_DEFAULT_VALUE',
    'VALIDATE_MODE_PRE_VALIDATE_VALUE',
    'VALIDATE_MODE_AT_RUNTIME_VALUE',
    'VALIDATE_MODE_NONE_VALUE',
    'VALIDATE_MODE_VALUE_LIST',
    'EVENT_NAME_MARKER_CREATED',
    'EVENT_NAME_LINE_CREATED',
    'EVENT_NAME_BUNDLE_CREATED',
    'EVENT_NAME_COLLECTION_CREATED',
    'EVENT_NAME_COLLECTION_MARKERS_CHANGED',
    'EVENT_NAME_COLLECTION_LINES_CHANGED',
    'EVENT_NAME_COLLECTION_ATTRS_CHANGED',
    'EVENT_NAME_ATTRIBUTE_STATE_CHANGED',
    'EVENT_NAME_ATTRIBUTE_CONNECTION_CHANGED',
    'EVENT_NAME_NODE_NAME_CHANGED',
    'EVENT_NAME_NODE_DELETED',
    'EVENT_NAME_MEMBERSHIP_CHANGED',
    'EVENT_NAME_MAYA_SCENE_CLOSING',
    'EVENT_NAME_LIST',
    'ATTRIBUTE_USED_HINT_DEFAULT_VALUE',
    'ATTRIBUTE_USED_HINT_USED_VALUE',
    'ATTRIBUTE_USED_HINT_NOT_USED_VALUE',
    'ATTRIBUTE_USED_HINT_LIST',
    'MARKER_USED_HINT_DEFAULT_VALUE',
    'MARKER_USED_HINT_USED_VALUE',
    'MARKER_USED_HINT_NOT_USED_VALUE',
    'MARKER_USED_HINT_LIST',
    'ACTION_STATUS_SUCCESS',
    'ACTION_STATUS_FAILED',
    'ACTION_STATUS_LIST',
    'LOG_LEVEL_ERROR',
    'LOG_LEVEL_WARNING',
    'LOG_LEVEL_INFO',
    'LOG_LEVEL_VERBOSE',
    'LOG_LEVEL_DEBUG',
    'LOG_LEVEL_LIST',
    'LOG_LEVEL_ERROR_VALUE',
    'LOG_LEVEL_WARNING_VALUE',
    'LOG_LEVEL_INFO_VALUE',
    'LOG_LEVEL_VERBOSE_VALUE',
    'LOG_LEVEL_DEBUG_VALUE',
    'LOG_LEVEL_NAME_TO_VALUE_MAP',
    'LOG_LEVEL_DEFAULT',
    'LOG_LEVEL_DEFAULT_VALUE',
    # Exceptions
    'MMException',
    'NotValid',
    'AlreadyLinked',
    'AlreadyUnlinked',
    'NotEnoughMarkers',
    'SolverNotAvailable',
    # Marker
    'update_deviation_on_markers',
    # Collection
    'update_deviation_on_collection',
    # Collection Utils
    'run_progress_func',
    'run_status_func',
    'is_single_frame',
    'disconnect_animcurves',
    'reconnect_animcurves',
    'clear_attr_keyframes',
    'generate_isolate_nodes',
    # Action
    'action_func_is_mmSolver',
    'action_func_is_mmSolver_v1',
    'action_func_is_mmSolver_v2',
    'action_func_is_mmSolverAffects',
    'func_str_to_callable',
    'action_to_components',
    # Execute
    'create_execute_options',
    'execute',
    'validate',
    # Marker Utils
    'calculate_marker_deviation',
    'get_markers_start_end_frames',
    'find_marker_attr_mapping',
    'calculate_average_deviation',
    'calculate_maximum_deviation',
    # Naming
    'find_valid_maya_node_name',
    'get_new_marker_name',
    'get_new_bundle_name',
    'get_new_line_name',
    # State
    'is_solver_running',
    'set_solver_running',
    'get_user_interrupt',
    'set_user_interrupt',
    # Root Frame
    'get_root_frames_from_markers',
    'root_frames_subdivide',
    'root_frames_list_combine',
    # Node Conversion
    'get_bundle_nodes_from_marker_nodes',
    'get_marker_nodes_from_bundle_nodes',
    'get_camera_nodes_from_marker_nodes',
    # Node Filter
    'filter_nodes_into_categories',
    'filter_marker_nodes',
    'filter_line_nodes',
    'filter_lens_nodes',
    'filter_image_plane_nodes',
    'filter_marker_group_nodes',
    'filter_bundle_nodes',
    'filter_camera_nodes',
    'filter_collection_nodes',
    # Utilities Functions
    'load_plugin',
    'get_object_type',
    'undo_chunk',
    'undo_chunk_context',
    'create_anim_curve_node',
    'get_data_on_node_attr',
    'set_data_on_node_attr',
    'get_value_on_node_attr',
    'set_value_on_node_attr',
    'get_marker_group_above_node',
    'get_line_above_node',
    # Nodes
    'get_long_name',
    'get_as_selection_list',
    'get_as_dag_path',
    'get_as_object',
    'get_as_plug',
    # Solver Result.
    'combine_timer_stats',
    'merge_frame_list',
    'merge_frame_error_list',
    'get_average_frame_error_list',
    'get_max_frame_error',
    'merge_marker_error_list',
    'merge_marker_node_list',
    'format_timestamp',
    # Triangulate Bundle
    'triangulate_bundle',
]
