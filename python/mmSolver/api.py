# Copyright (C) 2018, 2019 David Cattermole.
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

.. todo:: This API should not only be importable in Maya. Importing this
    module in 3DEqualizer or any other software  should not error
    and should return only the functionality that is supported
    in that software package.

"""

# All the objects for the user API.
from mmSolver._api.camera import Camera
from mmSolver._api.bundle import Bundle
from mmSolver._api.marker import (
    Marker,
    update_deviation_on_markers
)
from mmSolver._api.markergroup import MarkerGroup
from mmSolver._api.attribute import Attribute
from mmSolver._api.collection import (
    Collection,
    update_deviation_on_collection
)
from mmSolver._api.execute import (
    createExecuteOptions,
    ExecuteOptions,
    execute,
)
from mmSolver._api.frame import Frame
from mmSolver._api.action import (
    Action,
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
from mmSolver._api.collectionutils import (
    is_single_frame,
    disconnect_animcurves,
    reconnect_animcurves,
    clear_attr_keyframes,
    generate_isolate_nodes,
)
from mmSolver._api.markerutils import (
    calculate_marker_deviation,
    get_markers_start_end_frames,
)
from mmSolver._api.naming import (
    find_valid_maya_node_name,
    get_new_marker_name,
    get_new_bundle_name,
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
    SOLVER_TYPE_DEFAULT,

    AUTO_DIFF_TYPE_FORWARD,
    AUTO_DIFF_TYPE_CENTRAL,
    AUTO_DIFF_TYPE_LIST,
)

# Utility functions that the user is allowed to use.
from mmSolver._api.utils import (
    load_plugin,
    get_object_type,
    undo_chunk,
    convert_valid_maya_name,
    get_marker_name,
    get_bundle_name,
    load_plugin,
    get_data_on_node_attr,
    set_data_on_node_attr,
    get_value_on_node_attr,
    set_value_on_node_attr,
    is_solver_running,
    set_solver_running,
    get_user_interrupt,
    set_user_interrupt,
)
from mmSolver.utils.node import get_long_name, get_as_selection_list, \
    get_as_dag_path, get_as_object, get_as_plug

__all__ = [
    # Classes
    'Camera',
    'Bundle',
    'Marker',
    'MarkerGroup',
    'Attribute',
    'ExecuteOptions',
    'Collection',
    'Frame',
    'Solver',  # Backwards compatibility
    'Action',
    'SolverBase',
    'SolverStandard',
    'SolverStep',
    'SolveResult',

    # Constants
    'OBJECT_TYPE_UNKNOWN',
    'OBJECT_TYPE_ATTRIBUTE',
    'OBJECT_TYPE_MARKER',
    'OBJECT_TYPE_CAMERA',
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
    'SOLVER_TYPE_DEFAULT',
    'AUTO_DIFF_TYPE_FORWARD',
    'AUTO_DIFF_TYPE_CENTRAL',
    'AUTO_DIFF_TYPE_LIST',

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

    # Execute
    'createExecuteOptions',
    'execute',

    # Marker Utils
    'calculate_marker_deviation',
    'get_markers_start_end_frames',

    # Naming
    'find_valid_maya_node_name',
    'get_new_marker_name',
    'get_new_bundle_name',

    # State
    'is_solver_running',
    'set_solver_running',
    'get_user_interrupt',
    'set_user_interrupt',

    # Node Conversion
    'get_bundle_nodes_from_marker_nodes',
    'get_marker_nodes_from_bundle_nodes',
    'get_camera_nodes_from_marker_nodes',

    # Node Filter
    'filter_nodes_into_categories',
    'filter_marker_nodes',
    'filter_marker_group_nodes',
    'filter_bundle_nodes',
    'filter_camera_nodes',
    'filter_collection_nodes',

    # Utilities Functions
    'load_plugin',
    'get_object_type',
    'undo_chunk',
    'convert_valid_maya_name',
    'get_marker_name',
    'get_bundle_name',
    'load_plugin',
    'create_anim_curve_node',
    'get_data_on_node_attr',
    'set_data_on_node_attr',
    'get_value_on_node_attr',
    'set_value_on_node_attr',

    # Solver Result.
    'combine_timer_stats',
    'merge_frame_list',
    'merge_frame_error_list',
    'get_average_frame_error_list',
    'get_max_frame_error',
    'merge_marker_error_list',
    'merge_marker_node_list',
    'format_timestamp',
]
