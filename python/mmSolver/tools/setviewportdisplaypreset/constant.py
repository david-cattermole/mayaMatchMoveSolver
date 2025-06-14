# Copyright (C) 2025 David Cattermole.
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
Constants and configuration for the Set Viewport Display Preset tool.
"""

# Note: These values match the "display appearance" string, returned
# from maya.cmds.modelEditor(query=True, displayAppearance).
DISPLAY_APPEARANCE_WIREFRAME = 'wireframe'
DISPLAY_APPEARANCE_SMOOTH_SHADED = 'smoothShaded'
DISPLAY_APPEARANCE_FLAT_SHADED = 'flatShaded'
DISPLAY_APPEARANCE_BOUNDING_BOX = 'boundingBox'
DISPLAY_APPEARANCE_POINTS = 'points'
DISPLAY_APPEARANCES = [
    DISPLAY_APPEARANCE_WIREFRAME,
    DISPLAY_APPEARANCE_SMOOTH_SHADED,
    DISPLAY_APPEARANCE_FLAT_SHADED,
    DISPLAY_APPEARANCE_BOUNDING_BOX,
    DISPLAY_APPEARANCE_POINTS,
]


# The display modes that can be used in the presets.
DISPLAY_MODE_WIREFRAME = DISPLAY_APPEARANCE_WIREFRAME
DISPLAY_MODE_SMOOTH_SHADED = DISPLAY_APPEARANCE_SMOOTH_SHADED
DISPLAY_MODE_SMOOTH_SHADED_WIREFRAME = 'wireframeOnShaded'
# NOTE: These do not support all the display appearances as above.
DISPLAY_MODES = [
    DISPLAY_MODE_WIREFRAME,
    DISPLAY_MODE_SMOOTH_SHADED,
    DISPLAY_MODE_SMOOTH_SHADED_WIREFRAME,
]


# Renderer names
RENDERER_VIEWPORT_TWO = 'vp2Renderer'
RENDERER_OVERRIDE_MM_SILHOUETTE = 'mmRendererSilhouette'
RENDERER_OVERRIDE_MM_STANDARD = 'mmRendererStandard'

# List of renderers provided by mmSolver plug-in.
MMSOLVER_RENDERER_OVERRIDES = [
    RENDERER_OVERRIDE_MM_SILHOUETTE,
    RENDERER_OVERRIDE_MM_STANDARD,
]


# The default name used when a display preset is unknown.
UNKNOWN_DISPLAY_PRESET_NAME = '<Unknown>'


# Displays only the silhouette of objects.
SILHOUETTE_DISPLAY_PRESET_NAME = 'Silhouette (with Hold-Outs)'
SILHOUETTE_DISPLAY_PRESET = {
    'name': SILHOUETTE_DISPLAY_PRESET_NAME,
    'renderer': RENDERER_VIEWPORT_TWO,
    'renderer_override': RENDERER_OVERRIDE_MM_SILHOUETTE,
    'display_mode': DISPLAY_MODE_SMOOTH_SHADED,
    'hold_outs': True,
}

# Displays only the hidden-line of objects.
HIDDEN_LINE_DISPLAY_PRESET_NAME = 'Hidden-Line (with Hold-Outs)'
HIDDEN_LINE_DISPLAY_PRESET = {
    'name': HIDDEN_LINE_DISPLAY_PRESET_NAME,
    'renderer': RENDERER_VIEWPORT_TWO,
    'renderer_override': RENDERER_OVERRIDE_MM_STANDARD,
    'display_mode': DISPLAY_MODE_SMOOTH_SHADED_WIREFRAME,
    'hold_outs': True,
}

# Displays the full shaded of objects.
ALL_SHADED_DISPLAY_PRESET_NAME = 'All Shaded'
ALL_SHADED_DISPLAY_PRESET = {
    'name': ALL_SHADED_DISPLAY_PRESET_NAME,
    'renderer': RENDERER_VIEWPORT_TWO,
    'renderer_override': RENDERER_OVERRIDE_MM_STANDARD,
    'display_mode': DISPLAY_MODE_SMOOTH_SHADED,
    'hold_outs': False,
}

# Viewport cycle modes
DEFAULT_CYCLE_DISPLAY_PRESETS = [
    SILHOUETTE_DISPLAY_PRESET,
    HIDDEN_LINE_DISPLAY_PRESET,
    ALL_SHADED_DISPLAY_PRESET,
]

# Message display settings
MESSAGE_FADE_TIME = 1.5
MESSAGE_POSITION = 'topCenter'
