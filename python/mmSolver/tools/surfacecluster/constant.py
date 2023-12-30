# Copyright (C) 2023 David Cattermole.
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
Surface Cluster constants.
"""

WINDOW_TITLE = 'Create Surface Cluster'

CONFIG_CREATE_MODE_KEY = 'mmSolver_surfacecluster_createMode'
CONFIG_OPEN_PAINT_WEIGHTS_KEY = 'mmSolver_surfacecluster_openPaintWeights'

CREATE_MODE_SINGLE_VALUE = 'single_surface_cluster'
CREATE_MODE_MULTIPLE_VALUE = 'multiple_surface_cluster'
CREATE_MODE_VALUES = [
    CREATE_MODE_SINGLE_VALUE,
    CREATE_MODE_MULTIPLE_VALUE,
]

CREATE_MODE_SINGLE_LABEL = 'Create Single Cluster On Components'
CREATE_MODE_MULTIPLE_LABEL = 'Create Multiple Clusters On Each Component'
CREATE_MODE_LABELS = [
    CREATE_MODE_SINGLE_LABEL,
    CREATE_MODE_MULTIPLE_LABEL,
]

DEFAULT_CREATE_MODE = CREATE_MODE_SINGLE_VALUE
DEFAULT_OPEN_PAINT_WEIGHTS = True
