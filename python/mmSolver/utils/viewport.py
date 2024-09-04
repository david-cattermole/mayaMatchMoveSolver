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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds
import maya.OpenMaya as OpenMaya

import mmSolver.logger
import mmSolver.utils.camera as camera_utils
import mmSolver.utils.node as node_utils
import mmSolver.utils.constant as const

LOG = mmSolver.logger.get_logger()


SUPPORTED_DISPLAY_NODE_TYPES = [
    'mesh',
    'nurbsCurve',
    'nurbsSurface',
    'subdiv',
    'locator',
    'imagePlane',
    'camera',
    'plane',
    'light',
    'joint',
    'deformer',
    'ikHandle',
    'dynamic',
    'fluid',
    'hairSystem',
    'follicle',
    'nCloth',
    'nParticle',
    'nRigid',
    'texture',
    'stroke',
    #
    # Custom mmSolver node types:
    'mmImagePlaneShape2',
    'mmMarkerShape',
    'mmBundleShape',
    'mmLineShape',
    'mmSkyDomeShape',
]


def viewport1_turn_off():
    """
    Turn off Maya UI.
    """
    is_batch = maya.cmds.about(query=True, batch=True)
    if is_batch is True:
        return
    maya.cmds.refresh(suspend=True)
    maya.mel.eval('paneLayout -e -manage false $gMainPane')
    return


def viewport1_turn_on():
    """
    Turn on Maya UI.
    """
    is_batch = maya.cmds.about(query=True, batch=True)
    if is_batch is True:
        return
    maya.mel.eval('paneLayout -e -manage true $gMainPane')
    maya.cmds.refresh(suspend=False)
    return


def viewport2_turn_off():
    """
    Turn off Viewport 2.

    ..note:: This is not supported below Maya 2017.
    """
    set_viewport2_active_state(False)
    return


def viewport2_turn_on():
    """
    Turn on Viewport 2.

    ..note:: This is not supported below Maya 2017.
    """
    set_viewport2_active_state(True)
    return


def _disable_viewport_mode():
    """
    Try to guess the best disable/enable viewport mode.
    """
    mode = const.DISABLE_VIEWPORT_MODE_VP1_VALUE
    if maya.cmds.about(apiVersion=True) >= 201700:
        # Only use viewport2 pause feature if viewport 2 is currently
        # active.
        if get_currently_using_viewport2():
            mode = const.DISABLE_VIEWPORT_MODE_VP2_VALUE
        else:
            # Viewport 2.0 is not active, we fall back to viewport 1.0
            # disabling method.
            mode = const.DISABLE_VIEWPORT_MODE_VP1_VALUE
    return mode


def viewport_turn_off(mode=None):
    """
    Turn off Viewport.

    :param mode: Set the value to force a specific disable/enable method.
    :type mode: mmSolver.utils.constant.DISABLE_VIEWPORT_MODE_*_VALUE

    .. note:: By default mode=None will automatically switch to the fastest
        implementation based on the version Maya.

    """
    if mode is None or mode == const.DISABLE_VIEWPORT_MODE_GUESS_VALUE:
        mode = _disable_viewport_mode()
    assert mode in const.DISABLE_VIEWPORT_MODE_VALUES
    if mode is const.DISABLE_VIEWPORT_MODE_VP1_VALUE:
        viewport1_turn_off()
    elif mode is const.DISABLE_VIEWPORT_MODE_VP2_VALUE:
        set_viewport2_active_state(False)
    else:
        raise NotImplementedError
    return


def viewport_turn_on(mode=None):
    """
    Turn on the Viewport.

    :param mode: Set the value to force a specific disable/enable method.
    :type mode: mmSolver.utils.constant.DISABLE_VIEWPORT_MODE_*_VALUE

    .. note:: By default mode=None will automatically switch to the fastest
        implementation based on the version Maya.
    """
    if mode is None or mode == const.DISABLE_VIEWPORT_MODE_GUESS_VALUE:
        mode = _disable_viewport_mode()
    assert mode in const.DISABLE_VIEWPORT_MODE_VALUES
    if mode is const.DISABLE_VIEWPORT_MODE_VP1_VALUE:
        viewport1_turn_on()
    elif mode is const.DISABLE_VIEWPORT_MODE_VP2_VALUE:
        set_viewport2_active_state(True)
    else:
        raise NotImplementedError
    return


def set_viewport2_active_state(value):
    """
    Set Viewport 2 activation state.

    ..note:: This is not supported below Maya 2017.

    :param value: Set activation of the state.
    :type value: bool
    """
    is_batch = maya.cmds.about(query=True, batch=True)
    if is_batch is True:
        return
    is_using_vp2 = get_currently_using_viewport2()
    if is_using_vp2 is False:
        return
    if maya.cmds.about(apiVersion=True) < 201700:
        LOG.debug('Cannot turn off viewport 2, Maya version cannot do it.')
        return
    current = maya.cmds.ogs(query=True, pause=True)
    if value == current:
        maya.cmds.ogs(pause=True)
    return


def get_viewport2_active_state():
    """
    Query the Viewport 2 active state.

    ..note:: This is not supported below Maya 2017.

    :rtype: bool
    """
    is_batch = maya.cmds.about(query=True, batch=True)
    if is_batch is True:
        return False
    is_using_vp2 = get_currently_using_viewport2()
    if is_using_vp2 is False:
        return False
    if maya.cmds.about(apiVersion=True) < 201700:
        LOG.debug('Cannot turn off viewport 2, Maya version cannot do it.')
        return False
    return not maya.cmds.ogs(query=True, pause=True)


def get_active_model_panel():
    """
    Get the active model panel.

    :rtype: str or None
    """
    the_panel = maya.cmds.getPanel(withFocus=True)
    panel_type = maya.cmds.getPanel(typeOf=the_panel)

    if panel_type != 'modelPanel':
        return None
    return the_panel


def get_active_model_editor():
    """
    Get the active model editor.

    :rtype: str or None
    """
    the_panel = get_active_model_panel()
    if the_panel is None:
        return None

    model_editor = maya.cmds.modelPanel(the_panel, query=True, modelEditor=True)
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
    cam = maya.cmds.modelEditor(model_editor, query=True, camera=True)
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


def get_model_editor_renderer_device_name(model_editor):
    """
    Get the Renderer Device Name from the Model Editor.

    Query for the name of the draw API used by the Viewport 2.0
    renderer for a 3d modeling viewport. The possible return values
    are "VirtualDeviceGL" if Maya is set to use OpenGL for Viewport
    2.0 or "VirtualDeviceDx11" if Maya is set to use DirectX for
    Viewport 2.0. If the renderer for the 3d modeling viewport is not
    Viewport 2.0, an empty string will be returned.

    :rtype: str
    """
    renderer_name = maya.cmds.modelEditor(
        model_editor, query=True, rendererDeviceName=True
    )
    return renderer_name


def get_model_panel_renderer_device_name(model_panel):
    """
    Get the Renderer Device Name from the Model Panel.

    Query for the name of the draw API used by the Viewport 2.0
    renderer for a 3d modeling viewport. The possible return values
    are "VirtualDeviceGL" if Maya is set to use OpenGL for Viewport
    2.0 or "VirtualDeviceDx11" if Maya is set to use DirectX for
    Viewport 2.0. If the renderer for the 3d modeling viewport is not
    Viewport 2.0, an empty string will be returned.

    :rtype: str
    """
    model_editor = maya.cmds.modelPanel(model_panel, query=True, modelEditor=True)
    renderer_name = get_model_editor_renderer_device_name(model_editor)
    return renderer_name


def get_currently_using_viewport2():
    """
    Detect the currently used Viewport renderer devices, are we using
    Viewport 2?

    :rtype: bool
    """
    model_panels = get_all_model_panels()
    render_devices = [get_model_panel_renderer_device_name(p) for p in model_panels]
    using_viewport2 = any([x != '' for x in render_devices])
    return using_viewport2


def get_isolated_nodes(model_panel):
    """
    Return nodes that are being isolated for 'model_panel'.
    """
    nodes = []
    state = maya.cmds.isolateSelect(model_panel, query=True, state=True)
    if state is False:
        return nodes

    set_node = maya.cmds.isolateSelect(model_panel, query=True, viewObjects=True)

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


def set_isolated_nodes(model_panel, nodes, enable):
    """
    Override the isolate objects on 'model_panel'.

    With an empty list, this function clears the 'model_panel's
    isolate object list.
    """
    model_editor = maya.cmds.modelPanel(model_panel, query=True, modelEditor=True)

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


def get_selection_highlight(model_panel):
    """
    Query the display of selection highlighting.

    :param model_panel: Model panel name to set visibility.
    :type model_panel: str

    :return: True, if the selection highlighting is enable in the model
             panel/editor.
    :rtype: bool
    """
    model_editor = maya.cmds.modelPanel(model_panel, query=True, modelEditor=True)
    value = maya.cmds.modelEditor(model_editor, query=True, selectionHiliteDisplay=True)
    return value


def set_selection_highlight(model_panel, value):
    """
    Query the display of selection highlighting.

    :param model_panel: Model panel name to set visibility.
    :type model_panel: str

    :param value: Enable or disable selection highlighting?
    :type value: bool
    """
    assert isinstance(value, bool)
    model_editor = maya.cmds.modelPanel(model_panel, query=True, modelEditor=True)
    maya.cmds.modelEditor(model_editor, edit=True, selectionHiliteDisplay=value)
    return


def _get_node_type_visibility(model_panel, node_type):
    """
    Query the node type visibility of the given model panel.

    :param model_panel: Model panel name to set visibility.
    :type model_panel: str

    :return: The visibility of the node type.
    :rtype: bool
    """
    assert isinstance(model_panel, str)
    assert isinstance(node_type, str)
    model_editor = maya.cmds.modelPanel(model_panel, query=True, modelEditor=True)
    kwargs = {
        'query': True,
        str(node_type): True,
    }
    value = maya.cmds.modelEditor(model_editor, **kwargs)
    return value


def _set_node_type_visibility(model_panel, node_type, value):
    """
    Set the visibility of any node types in the given model panel.

    :param model_panel: Model panel name to set visibility.
    :type model_panel: str

    :param value: Visibility of the node type.
    :type value: bool
    """
    assert isinstance(model_panel, str)
    assert isinstance(node_type, str)
    assert isinstance(value, bool)
    model_editor = maya.cmds.modelPanel(model_panel, query=True, modelEditor=True)
    kwargs = {
        'edit': True,
        str(node_type): value,
    }
    maya.cmds.modelEditor(model_editor, **kwargs)
    return


def _get_plugin_display_filter_visibility(model_panel, plugin_display_filter):
    """
    Query the display filter visibility of the given model panel.

    :param model_panel: Model panel name to set visibility.
    :type model_panel: str

    :return: The visibility of the display filter.
    :rtype: bool
    """
    assert isinstance(model_panel, str)
    assert isinstance(plugin_display_filter, str)
    model_editor = maya.cmds.modelPanel(model_panel, query=True, modelEditor=True)
    value = maya.cmds.modelEditor(
        model_editor, query=True, queryPluginObjects=plugin_display_filter
    )
    return value


def _set_plugin_display_filter_visibility(model_panel, plugin_display_filter, value):
    """
    Set the visibility of a plug-in display filter for the given
    model panel.

    :param model_panel: Model panel name to set visibility.
    :type model_panel: str

    :param value: Visibility of the node type.
    :type value: bool
    """
    assert isinstance(model_panel, str)
    assert isinstance(plugin_display_filter, str)
    assert isinstance(value, bool)
    model_editor = maya.cmds.modelPanel(model_panel, query=True, modelEditor=True)
    maya.cmds.modelEditor(
        model_editor, edit=True, pluginObjects=[plugin_display_filter, value]
    )
    return


def get_grid_visibility(model_panel):
    """
    Query the grids visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'grid')


def set_grid_visibility(model_panel, value):
    """
    Set the visibility of grids nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'grid', value)


def get_image_plane_visibility(model_panel):
    """
    Query the image plane visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'imagePlane')


def set_image_plane_visibility(model_panel, value):
    """
    Set the visibility of imagePlane nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'imagePlane', value)


def get_camera_visibility(model_panel):
    """
    Query the camera visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'cameras')


def set_camera_visibility(model_panel, value):
    """
    Set the visibility of camera nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'cameras', value)


def get_mesh_visibility(model_panel):
    """
    Query the mesh visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'polymeshes')


def set_mesh_visibility(model_panel, value):
    """
    Set the visibility of mesh nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'polymeshes', value)


def get_subdiv_visibility(model_panel):
    """
    Query the subdiv visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'subdivSurfaces')


def set_subdiv_visibility(model_panel, value):
    """
    Set the visibility of subdiv nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'subdivSurfaces', value)


def get_nurbs_curve_visibility(model_panel):
    """
    Query the NURBS Curve visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'nurbsCurves')


def set_nurbs_curve_visibility(model_panel, value):
    """
    Set the visibility of NURBS Curve nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'nurbsCurves', value)


def get_nurbs_surface_visibility(model_panel):
    """
    Query the NURBS surface visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'nurbsSurfaces')


def set_nurbs_surface_visibility(model_panel, value):
    """
    Set the visibility of NURBS surface nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'nurbsSurfaces', value)


def get_locator_visibility(model_panel):
    """
    Query the locators visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'locators')


def set_locator_visibility(model_panel, value):
    """
    Set the visibility of locators nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'locators', value)


def get_plane_visibility(model_panel):
    """
    Query the plane visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'locators')


def set_plane_visibility(model_panel, value):
    """
    Set the visibility of plane nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'planes', value)


def get_light_visibility(model_panel):
    """
    Query the lights visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'lights')


def set_light_visibility(model_panel, value):
    """
    Set the visibility of lights nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'lights', value)


def get_joint_visibility(model_panel):
    """
    Query the joints visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'joints')


def set_joint_visibility(model_panel, value):
    """
    Set the visibility of joints nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'joints', value)


def get_deformer_visibility(model_panel):
    """
    Query the deformers visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'deformers')


def set_deformer_visibility(model_panel, value):
    """
    Set the visibility of deformers nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'deformers', value)


def get_ik_handle_visibility(model_panel):
    """
    Query the ikHandles visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'ikHandles')


def set_ik_handle_visibility(model_panel, value):
    """
    Set the visibility of ikHandles nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'ikHandles', value)


def get_dynamic_visibility(model_panel):
    """
    Query the dynamics visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'dynamics')


def set_dynamic_visibility(model_panel, value):
    """
    Set the visibility of dynamics nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'dynamics', value)


def get_fluid_visibility(model_panel):
    """
    Query the fluids visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'fluids')


def set_fluid_visibility(model_panel, value):
    """
    Set the visibility of fluids nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'fluids', value)


def get_hair_system_visibility(model_panel):
    """
    Query the hairSystems visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'hairSystems')


def set_hair_system_visibility(model_panel, value):
    """
    Set the visibility of hairSystems nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'hairSystems', value)


def get_follicle_visibility(model_panel):
    """
    Query the follicles visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'follicles')


def set_follicle_visibility(model_panel, value):
    """
    Set the visibility of follicles nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'follicles', value)


def get_ncloth_visibility(model_panel):
    """
    Query the nCloths visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'nCloths')


def set_ncloth_visibility(model_panel, value):
    """
    Set the visibility of nCloths nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'nCloths', value)


def get_nparticle_visibility(model_panel):
    """
    Query the nParticles visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'nParticles')


def set_nparticle_visibility(model_panel, value):
    """
    Set the visibility of nParticles nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'nParticles', value)


def get_nrigid_visibility(model_panel):
    """
    Query the nRigids visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'nRigids')


def set_nrigid_visibility(model_panel, value):
    """
    Set the visibility of nRigids nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'nRigids', value)


def get_texture_visibility(model_panel):
    """
    Query the textures visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'textures')


def set_texture_visibility(model_panel, value):
    """
    Set the visibility of textures nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'textures', value)


def get_stroke_visibility(model_panel):
    """
    Query the strokes visibility in given model panel.
    """
    return _get_node_type_visibility(model_panel, 'strokes')


def set_stroke_visibility(model_panel, value):
    """
    Set the visibility of strokes nodes in the given model panel.
    """
    return _set_node_type_visibility(model_panel, 'strokes', value)


def get_mm_image_plane_v2_visibility(model_panel):
    """
    Query the MM Image Plane visibility in given model panel.
    """
    return _get_plugin_display_filter_visibility(
        model_panel, 'mmImagePlane2DisplayFilter'
    )


def set_mm_image_plane_v2_visibility(model_panel, value):
    """
    Set the visibility of MM Image Plane nodes in the given model panel.
    """
    return _set_plugin_display_filter_visibility(
        model_panel, 'mmImagePlane2DisplayFilter', value
    )


def get_mm_marker_visibility(model_panel):
    """
    Query the MM Marker visibility in given model panel.
    """
    return _get_plugin_display_filter_visibility(model_panel, 'mmMarkerDisplayFilter')


def set_mm_marker_visibility(model_panel, value):
    """
    Set the visibility of MM Marker nodes in the given model panel.
    """
    return _set_plugin_display_filter_visibility(
        model_panel, 'mmMarkerDisplayFilter', value
    )


def get_mm_bundle_visibility(model_panel):
    """
    Query the MM Bundle visibility in given model panel.
    """
    return _get_plugin_display_filter_visibility(model_panel, 'mmBundleDisplayFilter')


def set_mm_bundle_visibility(model_panel, value):
    """
    Set the visibility of MM Bundle nodes in the given model panel.
    """
    return _set_plugin_display_filter_visibility(
        model_panel, 'mmBundleDisplayFilter', value
    )


def get_mm_line_visibility(model_panel):
    """
    Query the MM Line visibility in given model panel.
    """
    return _get_plugin_display_filter_visibility(model_panel, 'mmLineDisplayFilter')


def set_mm_line_visibility(model_panel, value):
    """
    Set the visibility of MM Line nodes in the given model panel.
    """
    return _set_plugin_display_filter_visibility(
        model_panel, 'mmLineDisplayFilter', value
    )


def get_mm_sky_dome_visibility(model_panel):
    """
    Query the MM Sky Dome visibility in given model panel.
    """
    return _get_plugin_display_filter_visibility(model_panel, 'mmSkyDomeDisplayFilter')


def set_mm_sky_dome_visibility(model_panel, value):
    """
    Set the visibility of MM Sky Dome nodes in the given model panel.
    """
    return _set_plugin_display_filter_visibility(
        model_panel, 'mmSkyDomeDisplayFilter', value
    )


NODE_TYPE_TO_GET_VIS_FUNC = {
    'mesh': get_mesh_visibility,
    'imagePlane': get_image_plane_visibility,
    'nurbsCurve': get_nurbs_curve_visibility,
    'nurbsSurface': get_nurbs_surface_visibility,
    'subdiv': get_subdiv_visibility,
    'locator': get_locator_visibility,
    'plane': get_plane_visibility,
    'light': get_light_visibility,
    'joint': get_joint_visibility,
    'deformer': get_deformer_visibility,
    'ikHandle': get_ik_handle_visibility,
    'dynamic': get_dynamic_visibility,
    'fluid': get_fluid_visibility,
    'hairSystem': get_hair_system_visibility,
    'follicle': get_follicle_visibility,
    'nCloth': get_ncloth_visibility,
    'nParticle': get_nparticle_visibility,
    'nRigid': get_nrigid_visibility,
    'texture': get_texture_visibility,
    'stroke': get_stroke_visibility,
    #
    # Custom MM Solver node types.
    'mmImagePlaneShape2': get_mm_image_plane_v2_visibility,
    'mmMarkerShape': get_mm_marker_visibility,
    'mmBundleShape': get_mm_bundle_visibility,
    'mmLineShape': get_mm_line_visibility,
    'mmSkyDomeShape': get_mm_sky_dome_visibility,
}


NODE_TYPE_TO_SET_VIS_FUNC = {
    'mesh': set_mesh_visibility,
    'imagePlane': set_image_plane_visibility,
    'nurbsCurve': set_nurbs_curve_visibility,
    'nurbsSurface': set_nurbs_surface_visibility,
    'subdiv': set_subdiv_visibility,
    'locator': set_locator_visibility,
    'plane': set_plane_visibility,
    'light': set_light_visibility,
    'joint': set_joint_visibility,
    'deformer': set_deformer_visibility,
    'ikHandle': set_ik_handle_visibility,
    'dynamic': set_dynamic_visibility,
    'fluid': set_fluid_visibility,
    'hairSystem': set_hair_system_visibility,
    'follicle': set_follicle_visibility,
    'nCloth': set_ncloth_visibility,
    'nParticle': set_nparticle_visibility,
    'nRigid': set_nrigid_visibility,
    'texture': set_texture_visibility,
    'stroke': set_stroke_visibility,
    #
    # Custom MM Solver node types.
    'mmImagePlaneShape2': set_mm_image_plane_v2_visibility,
    'mmMarkerShape': set_mm_marker_visibility,
    'mmBundleShape': set_mm_bundle_visibility,
    'mmLineShape': set_mm_line_visibility,
    'mmSkyDomeShape': set_mm_sky_dome_visibility,
}


def get_node_type_visibility(model_panel, node_type):
    """
    Query the visibility of 'node_type' in the given model panel.

    :param model_panel: Model panel name to set visibility.
    :type model_panel: str

    :param node_type: Node type to get visibility for.
    :type node_type: str

    :return: The visibility of the given node type.
    :rtype: bool
    """
    func = NODE_TYPE_TO_GET_VIS_FUNC.get(node_type)
    if func is None:
        msg = 'The requested node type is not valid: %r'
        LOG.warn(msg, node_type)
        return None
    value = func(model_panel)
    return value


def set_node_type_visibility(model_panel, node_type, value):
    """
    Set the visibility of 'node_type' nodes in the given model panel.

    :param model_panel: Model panel name to set visibility.
    :type model_panel: str

    :param node_type: Node type to set visibility for.
    :type node_type: str

    :param value: Visibility of node type.
    :type value: bool
    """
    func = NODE_TYPE_TO_SET_VIS_FUNC.get(node_type)
    if func is None:
        msg = 'The requested node type is not valid: %r'
        LOG.warn(msg, node_type)
        return None
    func(model_panel, value)
    return value
