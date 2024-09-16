# Copyright (C) 2024 Patcha Saheb Binginapalli.
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

WINDOW_TITLE = 'Mesh From Locators'

# We must have at least 3 points to make a mesh.
MINIMUM_NUMBER_OF_POINTS = 3

# The different types of meshes that can be created.
MESH_TYPE_FULL_MESH_VALUE = 'full_mesh'
MESH_TYPE_BORDER_MESH_VALUE = 'border_mesh'
MESH_TYPE_BORDER_EDGE_STRIP_MESH_VALUE = 'border_edge_strip_mesh'
MESH_TYPE_VALUES = [
    MESH_TYPE_FULL_MESH_VALUE,
    MESH_TYPE_BORDER_MESH_VALUE,
    MESH_TYPE_BORDER_EDGE_STRIP_MESH_VALUE,
]

# Default values.
DEFAULT_MESH_NAME = 'meshFromLocators'
DEFAULT_STRIP_WIDTH = 1.0

# Config value keys.
CONFIG_STRIP_WIDTH_KEY = 'mmSolver_meshfromlocators_stripWidth'
