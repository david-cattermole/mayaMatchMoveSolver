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
from mmSolver._api.marker import Marker
from mmSolver._api.markergroup import MarkerGroup
from mmSolver._api.attribute import Attribute
from mmSolver._api.collection import Collection
from mmSolver._api.frame import Frame
from mmSolver._api.solver import Solver
from mmSolver._api.solveresult import (
    SolveResult,
    combine_timer_stats,
    merge_frame_error_list,
    get_average_frame_error_list,
    get_max_frame_error,
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

    AUTO_DIFF_TYPE_FORWARD,
    AUTO_DIFF_TYPE_CENTRAL,
    AUTO_DIFF_TYPE_LIST,
)

# Utility functions that the user is allowed to use.
from mmSolver._api.utils import (
    get_long_name,
    get_as_selection_list,
    get_as_dag_path,
    get_as_object,
    get_as_plug,
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

# Animation Utility functions that the user is allowed to use.
from mmSolver._api.animutils import (
    create_anim_curve_node
)

__all__ = [
    # Classes
    'Camera',
    'Bundle',
    'Marker',
    'MarkerGroup',
    'Attribute',
    'Collection',
    'Frame',
    'Solver',
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

    # Functions
    'get_long_name',
    'get_as_selection_list',
    'get_as_dag_path',
    'get_as_object',
    'get_as_plug',
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
    'is_solver_running',
    'set_solver_running',
    'get_user_interrupt',
    'set_user_interrupt',
    'combine_timer_stats',
    'merge_frame_error_list',
    'get_average_frame_error_list',
    'get_max_frame_error',
]
