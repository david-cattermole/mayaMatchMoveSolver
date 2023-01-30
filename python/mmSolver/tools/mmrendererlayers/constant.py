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
Values used for MM Renderer Layers
"""

LAYER_ATTR_LAYER_MODE = 'mmLayerMode'
LAYER_ATTR_LAYER_MIX = 'mmLayerMix'
LAYER_ATTR_LAYER_DRAW_DEBUG = 'mmLayerDrawDebug'

LAYER_ATTR_OBJECT_DISPLAY_STYLE = 'mmObjectDisplayStyle'
LAYER_ATTR_OBJECT_ALPHA = 'mmObjectAlpha'

LAYER_ATTR_EDGE_ENABLE = 'mmEdgeEnable'
LAYER_ATTR_EDGE_COLOR = 'mmEdgeColor'
LAYER_ATTR_EDGE_COLOR_R = 'mmEdgeColorR'
LAYER_ATTR_EDGE_COLOR_G = 'mmEdgeColorG'
LAYER_ATTR_EDGE_COLOR_B = 'mmEdgeColorB'
LAYER_ATTR_EDGE_ALPHA = 'mmEdgeAlpha'
LAYER_ATTR_EDGE_DETECT_MODE = 'mmEdgeDetectMode'
LAYER_ATTR_EDGE_THICKNESS = 'mmEdgeThickness'
LAYER_ATTR_EDGE_THRESHOLD = 'mmEdgeThreshold'
LAYER_ATTR_EDGE_THRESHOLD_COLOR = 'mmEdgeThresholdColor'
LAYER_ATTR_EDGE_THRESHOLD_ALPHA = 'mmEdgeThresholdAlpha'
LAYER_ATTR_EDGE_THRESHOLD_DEPTH = 'mmEdgeThresholdDepth'

LAYER_ATTR_LIST_ALL = [
    LAYER_ATTR_LAYER_MODE,
    LAYER_ATTR_LAYER_MIX,
    LAYER_ATTR_LAYER_DRAW_DEBUG,
    LAYER_ATTR_OBJECT_DISPLAY_STYLE,
    LAYER_ATTR_OBJECT_ALPHA,
    LAYER_ATTR_EDGE_ENABLE,
    LAYER_ATTR_EDGE_COLOR,
    LAYER_ATTR_EDGE_COLOR_R,
    LAYER_ATTR_EDGE_COLOR_G,
    LAYER_ATTR_EDGE_COLOR_B,
    LAYER_ATTR_EDGE_ALPHA,
    LAYER_ATTR_EDGE_DETECT_MODE,
    LAYER_ATTR_EDGE_THICKNESS,
    LAYER_ATTR_EDGE_THRESHOLD,
    LAYER_ATTR_EDGE_THRESHOLD_COLOR,
    LAYER_ATTR_EDGE_THRESHOLD_ALPHA,
    LAYER_ATTR_EDGE_THRESHOLD_DEPTH,
]

LAYER_NICE_LAYER_MODE = 'Layer Mode'
LAYER_NICE_LAYER_MIX = 'Layer Mix'
LAYER_NICE_LAYER_DRAW_DEBUG = 'Layer Draw Debug'

LAYER_NICE_OBJECT_DISPLAY_STYLE = 'Object Display Style'
LAYER_NICE_OBJECT_ALPHA = 'Object Alpha'

LAYER_NICE_EDGE_ENABLE = 'Edge Enable'
LAYER_NICE_EDGE_COLOR = 'Edge Color'
LAYER_NICE_EDGE_COLOR_R = 'Edge Color R'
LAYER_NICE_EDGE_COLOR_G = 'Edge Color G'
LAYER_NICE_EDGE_COLOR_B = 'Edge Color B'
LAYER_NICE_EDGE_ALPHA = 'Edge Alpha'
LAYER_NICE_EDGE_DETECT_MODE = 'Edge Detect Mode'
LAYER_NICE_EDGE_THICKNESS = 'Edge Thickness'
LAYER_NICE_EDGE_THRESHOLD = 'Edge Threshold'
LAYER_NICE_EDGE_THRESHOLD_COLOR = 'Edge Threshold Color'
LAYER_NICE_EDGE_THRESHOLD_ALPHA = 'Edge Threshold Alpha'
LAYER_NICE_EDGE_THRESHOLD_DEPTH = 'Edge Threshold Depth'

LAYER_MODE_ZDEPTH = 'ZDepth'
LAYER_MODE_OVER = 'Over'
LAYER_MODE_PLUS = 'Plus'
LAYER_MODE_DEFAULT_VALUE = LAYER_MODE_ZDEPTH
LAYER_MODE_ENUM_VALUES = {LAYER_MODE_ZDEPTH: 0, LAYER_MODE_OVER: 1, LAYER_MODE_PLUS: 2}

OBJECT_DISPLAY_STYLE_NO_OVERRIDE = 'NoOverride'
OBJECT_DISPLAY_STYLE_HOLD_OUT = 'HoldOut'
OBJECT_DISPLAY_STYLE_WIREFRAME = 'Wireframe'
OBJECT_DISPLAY_STYLE_HIDDEN_LINE = 'HiddenLine'
OBJECT_DISPLAY_STYLE_WIREFRAME_SHADED = 'WireframeOnShaded'
OBJECT_DISPLAY_STYLE_SHADED = 'Shaded'
OBJECT_DISPLAY_STYLE_DEFAULT_VALUE = OBJECT_DISPLAY_STYLE_NO_OVERRIDE
OBJECT_DISPLAY_STYLE_ENUM_VALUES = {
    OBJECT_DISPLAY_STYLE_NO_OVERRIDE: 0,
    OBJECT_DISPLAY_STYLE_HOLD_OUT: 1,
    OBJECT_DISPLAY_STYLE_WIREFRAME: 2,
    OBJECT_DISPLAY_STYLE_HIDDEN_LINE: 3,
    OBJECT_DISPLAY_STYLE_WIREFRAME_SHADED: 4,
    OBJECT_DISPLAY_STYLE_SHADED: 5,
}

EDGE_DETECT_MODE_SOBEL = 'Sobel'
EDGE_DETECT_MODE_FREI_CHEN = 'FreiChen'
EDGE_DETECT_MODE_DEFAULT_VALUE = EDGE_DETECT_MODE_FREI_CHEN
EDGE_DETECT_MODE_ENUM_VALUES = {
    EDGE_DETECT_MODE_SOBEL: 0,
    EDGE_DETECT_MODE_FREI_CHEN: 1,
}