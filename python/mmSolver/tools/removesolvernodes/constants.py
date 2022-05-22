# Copyright (C) 2020 Kazuma Tonegawa.
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
Remove Solver Nodes constants.
"""

WINDOW_TITLE = 'Remove Solver Nodes'
CONFIG_FILE_NAME = "tools_removesolvernodes.json"

# The default values for deleting different types of nodes.
#
# All are False by default, because the intention is that users must
# consciously make a decision to delete nodes. This is a feature, not
# a bug in my (David Cattermole's) opinion (22/05/2022).
DELETE_MARKERS_DEFAULT_VALUE = False
DELETE_BUNDLES_DEFAULT_VALUE = False
DELETE_MARKER_GROUPS_DEFAULT_VALUE = False
DELETE_LENSES_DEFAULT_VALUE = False
DELETE_LINES_DEFAULT_VALUE = False
DELETE_IMAGE_PLANES_DEFAULT_VALUE = False
DELETE_COLLECTIONS_DEFAULT_VALUE = False
DELETE_DISPLAY_NODES_DEFAULT_VALUE = False
DELETE_OTHERS_DEFAULT_VALUE = False

# Save scene files by default?
SAVE_SCENE_DEFAULT_VALUE = True
