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

CONFIG_CONTROLLER_TYPE = 'mmsolver_createcontroller_type'
CONFIG_CONTROLLER_TYPE_GROUP = 'group'
CONFIG_CONTROLLER_TYPE_LOCATOR = 'locator'

CONTROLLER_TYPE_WORLD_SPACE = 'worldSpace'
CONTROLLER_TYPE_OBJECT_SPACE = 'objectSpace'
CONTROLLER_TYPE_SCREEN_SPACE = 'screenSpace'
CONTROLLER_TYPE_LIST = [
    CONTROLLER_TYPE_WORLD_SPACE,
    CONTROLLER_TYPE_OBJECT_SPACE,
    CONTROLLER_TYPE_SCREEN_SPACE,
]

COLUMN_CONTROLLER_NAME_INDEX = 0
COLUMN_MAIN_OBJECT_INDEX = 1
COLUMN_PIVOT_OBJECT_INDEX = 2
COLUMN_CAMERA_INDEX = 3
COLUMN_PIVOT_TYPE_INDEX = 4
COLUMN_BAKE_INDEX = 5
COLUMN_SPACE_INDEX = 6
COLUMN_INDICES_LIST = [
    COLUMN_CONTROLLER_NAME_INDEX,
    COLUMN_MAIN_OBJECT_INDEX,
    COLUMN_PIVOT_OBJECT_INDEX,
    COLUMN_CAMERA_INDEX,
    COLUMN_PIVOT_TYPE_INDEX,
    COLUMN_BAKE_INDEX,
    COLUMN_SPACE_INDEX
]

PIVOT_TYPE_ITEM_DYNAMIC = 'Dynamic'
PIVOT_TYPE_ITEM_STATIC = 'Static'
PIVOT_TYPE_ITEM_LIST = [
    PIVOT_TYPE_ITEM_STATIC,
    PIVOT_TYPE_ITEM_DYNAMIC
]

BAKE_ITEM_FULL_BAKE = 'Full Bake'
BAKE_ITEM_SMART_BAKE = 'Smart Bake'
BAKE_ITEM_CURRENT_FRAME_BAKE = 'Current Frame'

BAKE_ITEM_LIST = [
    BAKE_ITEM_FULL_BAKE,
    BAKE_ITEM_SMART_BAKE,
    BAKE_ITEM_CURRENT_FRAME_BAKE
]

SPACE_ITEM_WORLD_SPACE = 'World Space'
SPACE_ITEM_OBJECT_SPACE = 'Object Space'
SPACE_ITEM_SCREEN_SPACE = 'Screen Space'
SPACE_ITEM_LIST = [
    SPACE_ITEM_WORLD_SPACE,
    SPACE_ITEM_OBJECT_SPACE,
    SPACE_ITEM_SCREEN_SPACE
]

COLUMN_PIVOT_TYPE_INDEX_SIZE = 80
COLUMN_BAKE_INDEX_SIZE = 100
COLUMN_SPACE_INDEX_SIZE = 100
