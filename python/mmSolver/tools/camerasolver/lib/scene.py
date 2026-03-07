# Copyright (C) 2026 David Cattermole.
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
Maya scene query utilities shared by the Camera Solver tool and UI.

All functions that inspect or navigate the Maya scene graph live here
so that both the non-UI tool (tool.py) and the UI layout can call them
without the layout importing from tool.py's private namespace.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import tempfile

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.camera as camera_utils
import mmSolver.utils.viewport as viewport_utils

import mmSolver.tools.camerasolver.constant as const

LOG = mmSolver.logger.get_logger()


def get_camera_from_selection():
    """Get a camera from the current selection, falling back to the active viewport.

    :returns: A Camera object, or None if no camera can be determined.
    :rtype: mmapi.Camera or None
    """
    # type: () -> mmapi.Camera | None
    nodes = maya.cmds.ls(long=True, selection=True) or []
    node_categories = mmapi.filter_nodes_into_categories(nodes)
    camera_nodes = node_categories.get(mmapi.OBJECT_TYPE_CAMERA, [])
    if camera_nodes:
        _, camera_shape_node = camera_utils.get_camera(camera_nodes[0])
        if camera_shape_node is not None:
            return mmapi.Camera(shape=camera_shape_node)

    # Fall back to the camera shown in the active viewport.
    model_editor = viewport_utils.get_active_model_editor()
    if model_editor is None:
        return None
    _, camera_shape_node = viewport_utils.get_viewport_camera(model_editor)
    if camera_shape_node is None:
        return None
    return mmapi.Camera(shape=camera_shape_node)


def get_markers_under_camera(camera):
    """Return all Marker objects parented under the given camera.

    :param camera: Camera to search under.
    :type camera: mmapi.Camera

    :rtype: list[mmapi.Marker]
    """
    # type: (...) -> list
    assert isinstance(camera, mmapi.Camera)
    camera_transform_node = camera.get_transform_node()
    if camera_transform_node is None:
        return []
    below_nodes = maya.cmds.ls(camera_transform_node, dag=True, long=True) or []
    marker_nodes = mmapi.filter_marker_nodes(below_nodes)
    marker_nodes = list(set(marker_nodes))
    return [mmapi.Marker(node=x) for x in marker_nodes]


def get_lens_from_camera(camera):
    """Return the lens distortion node connected to the camera, or None.

    :param camera: Camera to inspect.
    :type camera: mmapi.Camera

    :rtype: mmapi.Lens or None
    """
    # type: (...) -> mmapi.Lens | None
    assert isinstance(camera, mmapi.Camera)
    camera_shape_node = camera.get_shape_node()
    if camera_shape_node is None:
        return None
    lens_nodes = (
        maya.cmds.listConnections(
            camera_shape_node + '.inLens',
            source=True,
            destination=False,
            type='mmLensModel3de',
        )
        or []
    )
    if not lens_nodes:
        return None
    return mmapi.Lens(node=lens_nodes[0])


def get_camera_focal_length(camera):
    """Return the current focal length in mm for the camera, or 35.0 as default.

    :param camera: Camera to query. May be None.
    :type camera: mmapi.Camera or None

    :rtype: float
    """
    # type: (...) -> float
    assert camera is None or isinstance(camera, mmapi.Camera)
    if camera is None:
        return 35.0
    camera_shape_node = camera.get_shape_node()
    if camera_shape_node is None:
        return 35.0
    return float(maya.cmds.getAttr(camera_shape_node + '.focalLength'))


def get_output_directory():
    """Return the output directory, preferring a writable Maya workspace location.

    Falls back to the OS temporary directory when the workspace is not
    writable or not set.

    :rtype: str
    """
    # type: () -> str
    workspace_path = maya.cmds.workspace(query=True, fullName=True)
    if workspace_path is not None:
        workspace_path = os.path.abspath(workspace_path)
        output_directory = os.path.join(
            workspace_path,
            const.WORKSPACE_OUTPUT_SUBDIR,
            const.OUTPUT_DIRECTORY_NAME,
        )
        try:
            if not os.path.isdir(output_directory):
                os.makedirs(output_directory)
            # Verify the directory is writable before committing to it.
            test_file = os.path.join(output_directory, '.write_test')
            with open(test_file, 'w') as f:
                f.write('')
            os.remove(test_file)
            return output_directory
        except (OSError, IOError):
            LOG.warning(
                'Workspace output directory is not writable, falling back to temp: %r',
                output_directory,
            )

    output_directory = os.path.join(tempfile.gettempdir(), const.OUTPUT_DIRECTORY_NAME)
    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)
    return output_directory


def get_prefix_name(camera):
    """Return a solver output file prefix derived from the camera name.

    :param camera: Camera whose name is used for the prefix.
    :type camera: mmapi.Camera

    :rtype: str
    """
    # type: (...) -> str
    assert isinstance(camera, mmapi.Camera)
    camera_transform_node = camera.get_transform_node() or ''
    camera_name = camera_transform_node.split('|')[-1]
    return 'camerasolver_' + camera_name
