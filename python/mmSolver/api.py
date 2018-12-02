"""
Controls the user-facing API.

.. todo:: This API should only be importable in Maya. Importing this
    module in 3DEqualizer or any other software  should not error
    and should return only the functionallity that is supported
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
)
from mmSolver._api.constant import (
    ATTR_STATE_INVALID,
    ATTR_STATE_STATIC,
    ATTR_STATE_ANIMATED,
    ATTR_STATE_LOCKED,

    SOLVER_TYPE_LEVMAR,
)

# Utility functions that the user is allowed to use.
from mmSolver._api.utils import (
    get_long_name,
    get_object_type,
    undo_chunk,
    convert_valid_maya_name,
    get_marker_name,
    get_bundle_name,
    load_plugin,
    get_data_on_node_attr,
    set_data_on_node_attr,
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
    'ATTR_STATE_INVALID',
    'ATTR_STATE_STATIC',
    'ATTR_STATE_ANIMATED',
    'ATTR_STATE_LOCKED',
    'SOLVER_TYPE_LEVMAR',

    # Exceptions
    'MMException',
    'NotValid',
    'AlreadyLinked',
    'AlreadyUnlinked',
    'NotEnoughMarkers',

    # Functions
    'get_long_name',
    'get_object_type',
    'undo_chunk',
    'convert_valid_maya_name',
    'get_marker_name',
    'get_bundle_name',
    'load_plugin',
    'create_anim_curve_node',
    'get_data_on_node_attr',
    'set_data_on_node_attr',
    'combine_timer_stats',
    'merge_frame_error_list',
    'get_average_frame_error_list',
    'get_max_frame_error',
]
