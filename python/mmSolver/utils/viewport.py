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
import maya.OpenMaya as OpenMaya

import mmSolver.logger
import mmSolver.utils.camera as camera_utils
import mmSolver.utils.node as node_utils

LOG = mmSolver.logger.get_logger()


def viewport_turn_off():
    """
    Turn off Maya UI.
    """
    maya.mel.eval('paneLayout -e -manage false $gMainPane')
    return


def viewport_turn_on():
    """
    Turn on Maya UI.
    """
    maya.mel.eval('paneLayout -e -manage true $gMainPane')
    return


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


def get_all_model_panels():
    """
    Return a list of all Maya model panels.
    """
    model_panels = []
    is_batch = maya.cmds.about(query=True, batch=True)
    if is_batch is True:
        return model_panels
    panels = maya.cmds.getPanel(allPanels=True)
    for panel in panels:
        panel_type = maya.cmds.getPanel(typeOf=panel)
        if panel_type == 'modelPanel':
            model_panels.append(panel)
    return model_panels


def get_isolated_nodes(model_panel):
    """
    Return nodes that are being isolated for 'model_panel'.
    """
    nodes = []
    state = maya.cmds.isolateSelect(
        model_panel,
        query=True,
        state=True)
    if state is False:
        return nodes

    set_node = maya.cmds.isolateSelect(
        model_panel,
        query=True,
        viewObjects=True)

    obj = node_utils.get_as_object(set_node)
    set_mfn = OpenMaya.MFnSet(obj)

    flatten = False
    full_path = True
    sel_list = OpenMaya.MSelectionList()
    try:
        set_mfn.getMembers(sel_list, flatten)
    except RuntimeError:
        return nodes

    sel_list.getSelectionStrings(nodes)
    if full_path is True:
        nodes = maya.cmds.ls(nodes, long=True) or []
    return nodes


def get_image_plane_visibility(model_panel):
    model_editor = maya.cmds.modelPanel(
        model_panel,
        query=True,
        modelEditor=True)
    value = maya.cmds.modelEditor(
        model_editor,
        query=True,
        imagePlane=True)
    return value


def set_image_plane_visibility(model_panel, value):
    model_editor = maya.cmds.modelPanel(
        model_panel,
        query=True,
        modelEditor=True)
    maya.cmds.modelEditor(
        model_editor,
        edit=True,
        imagePlane=value)
    return


def set_isolated_nodes(model_panel, nodes, enable):
    """
    Override the isolate objects on 'model_panel'.

    With an empty list, this function clears the 'model_panel's
    isolate object list.
    """
    model_editor = maya.cmds.modelPanel(
        model_panel,
        query=True,
        modelEditor=True)

    sel = maya.cmds.ls(selection=True, long=True) or []
    maya.cmds.select(nodes, replace=True)

    cmd = 'enableIsolateSelect("%s", %s);'
    cmd = cmd % (model_editor, int(enable))
    maya.mel.eval(cmd)

    cmd = 'doReload("%s");'
    cmd = cmd % model_editor
    maya.mel.eval(cmd)

    if len(sel) > 0:
        maya.cmds.select(sel, replace=True)
    else:
        maya.cmds.select(clear=True)
    return