# Copyright (C) 2022 David Cattermole.
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
Contains constant values for the Save Lens File tool.

The Save Lens File tool can write mmSolver Lens nodes as .nk files,
readable by The Foundry Nuke.
"""

EXT = '.nk'

DATA_TYPE_NUKE_NODE = 'nuke_node'
DATA_TYPE_LIST = [DATA_TYPE_NUKE_NODE]


NUKE_FILE_HEADER_COMMENT = (
    '# Created by Maya MatchMove Solver with the Save Lens File tool.\n'
    '#\n'
    '# Version: {module_version_name}\n'
    '# Website: {project_homepage_url}\n'
)

# fmt: off
NUKE_FORMAT_SPEC_NODE = (
    '{node_type} {left_brace}\n'
    '{knobs}\n'
    '{right_brace}\n'
)
# fmt: on
NUKE_FORMAT_SPEC_KNOB = '  {name} {value}\n'


DEFAULT_ATTRIBUTE_DATA = {
    # Attribute name.
    'name': None,
    # If 'frames' is empty, the 'values' is assumed to be static and
    # therefore have only a single value in the list. Otherwise the
    # length of the 'frames' and 'values' is expected to be the same.
    'frames': [],
    # 'values' may be a single float value in the list: [0.0]
    #
    # ... or lists of values; [42.0, 42.1]
    'values': [],
}


DEFAULT_LENS_NODE_DATA = {
    'node_type': None,
    'lens_model_type': None,
    'node_name': None,
    'attributes': [],
}


# The Nuke curve format is specified as "{{curve xtime value }}",
# where 'time' and 'value' are integer and floating point numbers, for
# example "{{curve x0 1.34 }}". There can be many time and value
# entries in the curve.
NUKE_FILE_SPEC_CURVE_START = '{{curve '
NUKE_FILE_SPEC_CURVE_END = '}}'
