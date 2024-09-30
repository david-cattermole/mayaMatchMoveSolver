# Copyright (C) 2020 David Cattermole.
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
The Create Image Plane tool.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.viewport as utils_viewport
import mmSolver.utils.camera as utils_camera
import mmSolver.tools.createimageplane._lib.constant as const
import mmSolver.tools.createimageplane.lib as lib


LOG = mmSolver.logger.get_logger()


def _get_start_directory():
    fallback_path = os.getcwd()

    workspace_path = maya.cmds.workspace(query=True, fullName=True)
    if workspace_path is None:
        return fallback_path
    workspace_path = os.path.abspath(workspace_path)

    file_rules = maya.cmds.workspace(query=True, fileRule=True)
    if file_rules is None:
        return fallback_path
    file_rule_names = file_rules[0::2]
    file_rule_values = file_rules[1::2]

    file_rule = 'sourceImages'
    if file_rule not in file_rule_names:
        return fallback_path
    file_rule_index = file_rule_names.index(file_rule)
    dir_name = file_rule_values[file_rule_index]

    path = os.path.join(workspace_path, dir_name)
    return path


def prompt_user_for_image_sequence(start_dir=None):
    image_sequence_path = None
    if start_dir is None:
        start_dir = _get_start_directory()
    multiple_filters = (
        'Image Files (*.jpg *.png *.iff *.exr *.tif *.tiff *.tga *.sgi);;'
        'JPEG (*.jpg *.jpeg);;'
        'PNG (*.png);;'
        'Maya IFF (*.iff);;'
        'Silicon Graphics (*.sgi);;'
        'EXR (*.exr);;'
        'TIFF (*.tif *.tiff);;'
        'Targa (*.tga);;'
        'All Files (*.*)'
    )
    results = (
        maya.cmds.fileDialog2(
            caption='Select Image Sequence',
            okCaption='Open',
            fileMode=1,  # 1 = A single existing file.
            setProjectBtnEnabled=True,
            fileFilter=multiple_filters,
            startingDirectory=start_dir,
        )
        or []
    )
    if len(results) == 0:
        # User cancelled.
        return image_sequence_path

    image_sequence_path = results[0]
    return image_sequence_path


def _run(version):
    """
    Create a new Image Plane on the selected camera.
    """
    assert version in const.MM_IMAGE_PLANE_VERSION_LIST
    mmapi.load_plugin()

    # Get selected camera(s).
    sel = maya.cmds.ls(selection=True, long=True) or []
    node_filtered = mmapi.filter_nodes_into_categories(sel)
    cams = node_filtered[mmapi.OBJECT_TYPE_CAMERA]
    cams = [x for x in cams if utils_camera.is_not_startup_cam(x)]

    cams_to_add_lenses = []
    if len(cams) == 0:
        # Create a lens in the active viewport camera.
        model_editor = utils_viewport.get_active_model_editor()
        if model_editor is None:
            msg = 'Please select an active 3D viewport.'
            LOG.warning(msg)
            return
        cam_tfm, cam_shp = utils_viewport.get_viewport_camera(model_editor)
        node = cam_shp
        if node is None:
            msg = 'Please select an active viewport to get a camera.'
            LOG.error(msg)
            return
        if utils_camera.is_startup_cam(node) is True:
            msg = "Cannot create Lens on 'persp' camera."
            LOG.error(msg)
            return
        cam_tfm, cam_shp = utils_camera.get_camera(node)
        cam = mmapi.Camera(shape=cam_shp)
        cams_to_add_lenses.append(cam)

    elif len(cams) > 0:
        # Create a Lens under the selected cameras.
        for node in cams:
            cam_tfm, cam_shp = utils_camera.get_camera(node)
            cam = mmapi.Camera(shape=cam_shp)
            cams_to_add_lenses.append(cam)

    else:
        LOG.error('Should not get here.')
        return

    created = set()
    nodes = list()
    for cam in cams_to_add_lenses:
        cam_shp = cam.get_shape_node()
        # Don't accidentally create two image planes for a camera if the
        # user has the transform and shape nodes selected.
        if cam_shp in created:
            continue
        mm_ip_tfm, mm_ip_shp = lib.create_image_plane_on_camera(cam, version=version)

        image_seq = prompt_user_for_image_sequence()
        if image_seq:
            lib.set_image_sequence(mm_ip_tfm, image_seq, version=version)

        nodes.append(mm_ip_shp)
        created.add(cam_shp)

    if len(nodes) > 0:
        maya.cmds.select(nodes, replace=True)

        # Show the last node in the attribute editor.
        node = nodes[-1]
        maya.mel.eval('updateAE("{}");'.format(node))
    else:
        maya.cmds.select(sel, replace=True)
    return


def main():
    _run(const.MM_IMAGE_PLANE_VERSION_TWO)


def main_version_one():
    _run(const.MM_IMAGE_PLANE_VERSION_ONE)


def main_version_two():
    _run(const.MM_IMAGE_PLANE_VERSION_TWO)
