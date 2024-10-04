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
Camera node constant values.
"""

# Image Plane (high-level) types.
#
# These are not node types but are high-level types of the different
# systems used. More types might be added in the future.
IMAGE_PLANE_TYPE_NAME_MM_SOLVER_VALUE = 'mmSolver_imagePlane'
IMAGE_PLANE_TYPE_NAME_MAYA_NATIVE_VALUE = 'maya_imagePlane'

IMAGE_PLANE_TYPE_NAME_MM_SOLVER_LABEL = 'mmSolver'
IMAGE_PLANE_TYPE_NAME_MAYA_NATIVE_LABEL = 'Maya'

IMAGE_PLANE_TYPE_NAME_VALUES = [
    IMAGE_PLANE_TYPE_NAME_MM_SOLVER_VALUE,
    IMAGE_PLANE_TYPE_NAME_MAYA_NATIVE_VALUE,
]

IMAGE_PLANE_TYPE_NAME_LABELS = [
    IMAGE_PLANE_TYPE_NAME_MM_SOLVER_LABEL,
    IMAGE_PLANE_TYPE_NAME_MAYA_NATIVE_LABEL,
]

MM_IMAGE_PLANE_SHAPE_NODE_TYPE = 'mmImagePlaneShape'
MM_IMAGE_PLANE_TRANSFORM_NODE_TYPE = 'mmImagePlaneTransform'
MM_IMAGE_PLANE_NODE_TYPES = [
    MM_IMAGE_PLANE_SHAPE_NODE_TYPE,
    MM_IMAGE_PLANE_TRANSFORM_NODE_TYPE,
]

SELECT_CAMERA_NODE_TOOLTIP = 'Select camera node "{name}".'
SELECT_CAMERA_NODE_CMD_LANG = 'python'
SELECT_CAMERA_NODE_CMD = (
    'import maya.cmds;' 'node = "{node}";' 'maya.cmds.select(node, replace=True);'
)


SELECT_IMAGE_PLANE_NODE_TOOLTIP = 'Select image plane node "{name}".'
SELECT_IMAGE_PLANE_NODE_CMD_LANG = 'python'
SELECT_IMAGE_PLANE_NODE_CMD = (
    'import maya.cmds;'
    'image_plane_node = "{node}";'
    'maya.cmds.select(image_plane_node, replace=True);'
)


SELECT_LENS_NODE_TOOLTIP = 'Select lens node "{name}".'
SELECT_LENS_NODE_CMD_LANG = 'python'
SELECT_LENS_NODE_CMD = (
    'import maya.cmds;'
    'lens_node = "{node}";'
    'maya.cmds.select(lens_node, replace=True);'
)


TOGGLE_CAMERA_LENS_DISTORTION_ENABLED_LABEL = 'Toggle Camera Distortion'
TOGGLE_CAMERA_LENS_DISTORTION_ENABLED_TOOLTIP = (
    'Toggles the lens distortion on the camera.'
)
TOGGLE_CAMERA_LENS_DISTORTION_ENABLED_CMD_LANG = 'python'
TOGGLE_CAMERA_LENS_DISTORTION_ENABLED_CMD = (
    'import mmSolver.tools.cameracontextmenu.lib as lib;'
    'lib.toggle_camera_lens_distortion_enabled(camera_shape_node="{camera_shape_node}");'
)


SELECT_NODE_AND_SHOW_IN_ATTR_EDITOR_TOOLTIP = (
    'Select and show node in Attribute Editor.'
)
SELECT_NODE_AND_SHOW_IN_ATTR_EDITOR_CMD_LANG = 'python'
SELECT_NODE_AND_SHOW_IN_ATTR_EDITOR_CMD = (
    'import maya.cmds;'
    'import mmSolver.tools.cameracontextmenu.lib as lib;'
    'node = "{node}";'
    'maya.cmds.select(node, replace=True);'
    'lib.open_node_in_attribute_editor(node);'
)


OPEN_NODE_IN_NODE_EDITOR_TOOLTIP = 'Show the node in the Node Editor.'
OPEN_NODE_IN_NODE_EDITOR_CMD_LANG = 'python'
OPEN_NODE_IN_NODE_EDITOR_CMD = (
    'import mmSolver.tools.cameracontextmenu.lib as lib;'
    'lib.open_node_in_node_editor(node="{node}");'
)


CREATE_CAMERA_LABEL = 'Create Camera'
CREATE_CAMERA_TOOLTIP = 'Create a camera.'
CREATE_CAMERA_CMD_LANG = 'python'
CREATE_CAMERA_CMD = (
    'import maya.cmds;'
    'import mmSolver.tools.cameracontextmenu.lib as lib;'
    'cam = lib.create_camera();'
    'cam_tfm = cam.get_transform_node();'
    'cam_shp = cam.get_shape_node();'
    'maya.cmds.select(cam_tfm, replace=True);'
    'lib.open_node_in_attribute_editor(node=cam_shp);'
)


CREATE_IMAGE_PLANE_LABEL = 'Create MM Image Plane...'
CREATE_IMAGE_PLANE_TOOLTIP = 'Create MM Image Plane on {camera_shape_name}.'
CREATE_IMAGE_PLANE_CMD_LANG = 'python'
CREATE_IMAGE_PLANE_CMD = (
    'import maya.cmds;'
    'import mmSolver.tools.cameracontextmenu.lib as lib;'
    'tfm, shp = lib.create_image_plane(camera_shape_node="{camera_shape_node}");'
    'maya.cmds.select(shp, replace=True);'
    'lib.open_node_in_attribute_editor(node=shp);'
)


CREATE_LENS_LABEL = 'Create Lens Layer'
CREATE_LENS_TOOLTIP = 'Create Lens Layer on {camera_shape_name}.'
CREATE_LENS_CMD_LANG = 'python'
CREATE_LENS_CMD = (
    'import maya.cmds\n'
    'import mmSolver.tools.cameracontextmenu.lib as lib\n'
    'lens = lib.create_lens(camera_shape_node="{camera_shape_node}")\n'
    'node = None\n'
    'if lens is not None:\n'
    '    node = lens.get_node()\n'
    'if node is not None:\n'
    '    maya.cmds.select(node, replace=True)\n'
    '    lib.open_node_in_attribute_editor(node=node)\n'
)
