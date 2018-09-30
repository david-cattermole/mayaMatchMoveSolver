"""
Constant values used in the API.
"""

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


# Solver Types
SOLVER_TYPE_LEVMAR = 0


# Attribute States
ATTR_STATE_INVALID = 0
ATTR_STATE_STATIC = 1
ATTR_STATE_ANIMATED = 2
ATTR_STATE_LOCKED = 3
