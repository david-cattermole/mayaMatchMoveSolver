# Copyright (C) 2019, 2020 David Cattermole.
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
# ---------------------------------------------------------------------
#

# Build features
add_subdirectory(modules)

if (BUILD_3DEQUALIZER)
  add_subdirectory(3dequalizer)
endif ()

if (BUILD_SYNTHEYES)
  add_subdirectory(syntheyes)
endif ()

if (BUILD_BLENDER)
  add_subdirectory(blender)
endif ()

if (BUILD_MM_RENDERER)
  add_subdirectory(shader)
endif ()

if (BUILD_ICONS)
  add_subdirectory(icons)
  add_subdirectory(images)
endif ()

if (BUILD_CONFIG)
  add_subdirectory(config)
endif ()

# Set variables in parent scope (directory above).
set(MODULE_OS_NAME "${MODULE_OS_NAME}" PARENT_SCOPE)
set(MODULE_NAME "${MODULE_NAME}" PARENT_SCOPE)
set(MODULE_FULL_NAME "${MODULE_FULL_NAME}" PARENT_SCOPE)
set(MODULE_BUILD_DIR "${MODULE_BUILD_DIR}" PARENT_SCOPE)
