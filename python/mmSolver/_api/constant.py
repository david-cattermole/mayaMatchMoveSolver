"""
Constant values used in the API.
"""


# Plug-in names
PLUGIN_NAMES = [
    'mmSolver'
]


# Maya node suffixes
MARKER_NAME_SUFFIX = '_MKR'
BUNDLE_NAME_SUFFIX = '_BND'


# list of characters that are not supported in maya for node names.
# Note, only ':' and '_' are not in the list.
BAD_MAYA_CHARS = [
    ' ', '#', '-', '@', '!', '$', '%', '^', '&', '*',
    '+', '=', '/', '\\', '~', '`', '.', ',', '?', ';', '|'
    '(', ')', '[', ']', '{', '}', '<', '>'
    '\'', '\"'
]


# Solver objects.
SOLVER_DATA_DEFAULT = {
    'enabled': True,
}


# Solver Types
SOLVER_TYPE_LEVMAR = 0


# Attribute States
ATTR_STATE_INVALID = 0
ATTR_STATE_STATIC = 1
ATTR_STATE_ANIMATED = 2
ATTR_STATE_LOCKED = 3


# Auto Differencing Types
AUTO_DIFF_TYPE_FORWARD = 0
AUTO_DIFF_TYPE_CENTRAL = 1
AUTO_DIFF_TYPE_LIST = [
    AUTO_DIFF_TYPE_FORWARD,
    AUTO_DIFF_TYPE_CENTRAL,
]
