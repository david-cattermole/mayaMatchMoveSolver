"""
Controls the user-facing API.
"""

# All the objects for the user API.
from mmSolver._api.camera import Camera
from mmSolver._api.bundle import Bundle
from mmSolver._api.marker import Marker
from mmSolver._api.markergroup import MarkerGroup
from mmSolver._api.attribute import (
    Attribute,
    ATTR_STATE_INVALID,
    ATTR_STATE_STATIC,
    ATTR_STATE_ANIMATED,
    ATTR_STATE_LOCKED
)
from mmSolver._api.collection import Collection
from mmSolver._api.frame import Frame
from mmSolver._api.solver import (
    Solver,
    SOLVER_TYPE_LEVMAR,
    SOLVER_TYPE_SPLM,
    SOLVER_TYPE_CERES
)
from mmSolver._api.solveresult import SolveResult
from mmSolver._api.excep import (
    MMException,
    NotValid,
    AlreadyLinked,
    AlreadyUnlinked,
    NotEnoughMarkers,
)

from mmSolver._api.nodeaffects import (
    find_attrs_affecting_transform,
    find_marker_attr_mapping,
)

# Utility functions that the user is allowed to use.
from mmSolver._api.utils import (
    get_long_name,
    get_object_type,
    undo_chunk,
    convert_valid_maya_name,
    get_marker_name,
    get_bundle_name
)

# Animation Utility functions that the user is allowed to use.
from mmSolver._api.animutils import (
    create_anim_curve_node
)

__all__ = [
    'Camera',
    'Bundle',
    'Marker',
    'MarkerGroup',

    'Attribute',
    'ATTR_STATE_INVALID',
    'ATTR_STATE_STATIC',
    'ATTR_STATE_ANIMATED',
    'ATTR_STATE_LOCKED',

    'Collection',
    'Frame',

    'Solver',
    'SOLVER_TYPE_LEVMAR',
    'SOLVER_TYPE_SPLM',
    'SOLVER_TYPE_CERES',

    'SolveResult',

    # functions
    'get_long_name',
    'get_object_type',
    'undo_chunk',
    'convert_valid_maya_name',
    'get_marker_name',
    'get_bundle_name',
    'create_anim_curve_node',
]
