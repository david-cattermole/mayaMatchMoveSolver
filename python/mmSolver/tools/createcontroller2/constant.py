# Copyright (C) 2021, 2022 Patcha Saheb Binginapalli.

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

CONTROLLER_SPACE_WORLD = 'worldSpace'
CONTROLLER_SPACE_OBJECT = 'objectSpace'
CONTROLLER_SPACE_SCREEN = 'screenSpace'
CONTROLLER_SPACE_LIST = [
    CONTROLLER_SPACE_WORLD,
    CONTROLLER_SPACE_OBJECT,
    CONTROLLER_SPACE_SCREEN,
]

# Keys and values to save values in the Maya scene file.  The value is
# saved in the Maya scene and re-used in the same Maya scene.
CONTROLLER_TYPE_CONFIG_KEY = 'mmsolver_createcontroller_type'
CONTROLLER_TYPE_GROUP = 'group'
CONTROLLER_TYPE_LOCATOR = 'locator'


# Used in create controller 3 (beta)
SPACE_WORLD_SPACE = 'World Space'
SPACE_OBJECT_SPACE = 'Object Space'
SPACE_SCREEN_SPACE = 'Screen Space'
SPACE_LIST = [
    SPACE_WORLD_SPACE,
    SPACE_OBJECT_SPACE,
    SPACE_SCREEN_SPACE,
]


# Used in create controller 3 (beta)
PIVOT_TYPE_DYNAMIC = 'Dynamic'
PIVOT_TYPE_STATIC = 'Static'
PIVOT_TYPE_LIST = [PIVOT_TYPE_STATIC, PIVOT_TYPE_DYNAMIC]


# Used in create controller 3 (beta)
BAKE_FULL_BAKE = 'Full Bake'
BAKE_SMART_BAKE = 'Smart Bake'
BAKE_CURRENT_FRAME_BAKE = 'Current Frame'
BAKE_LIST = [
    BAKE_FULL_BAKE,
    BAKE_SMART_BAKE,
    BAKE_CURRENT_FRAME_BAKE,
]
