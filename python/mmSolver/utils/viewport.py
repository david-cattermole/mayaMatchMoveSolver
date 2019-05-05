# Copyright (C) 2019 David Cattermole.
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
Utilities for setting and querying viewport related information.
"""
import maya.cmds
import mmSolver.logger
import mmSolver.utils.camera as camera_utils

LOG = mmSolver.logger.get_logger()


def get_active_model_editor():
    """
    Get the active model editor.

    :rtype: str or None
    """
    the_panel = maya.cmds.getPanel(withFocus=True)
    panel_type = maya.cmds.getPanel(typeOf=the_panel)

    if panel_type != 'modelPanel':
        return None

    model_editor = maya.cmds.modelPanel(
        the_panel,
        query=True,
        modelEditor=True)
    return model_editor


def get_viewport_camera(model_editor):
    """
    Get the camera from the model editor.

    :param model_editor: The viewport model editor to get the camera from.
    :type model_editor: str

    :returns: Camera transform and camera shape nodes.
    :rtype: (str, str) or (None, None)
    """
    if model_editor is None:
        msg = 'Cannot get camera, Model Editor is invalid! model_editor=%r'
        LOG.warning(msg, model_editor)
    cam = maya.cmds.modelEditor(
        model_editor,
        query=True,
        camera=True
    )
    cam_tfm, cam_shp = camera_utils.get_camera(cam)
    return cam_tfm, cam_shp
