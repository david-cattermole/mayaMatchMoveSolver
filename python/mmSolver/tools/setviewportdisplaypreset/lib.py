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
Library functions for tool's operations.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.logger
import mmSolver.utils.python_compat as pycompat
import mmSolver.api as mmapi
import mmSolver.tools.setviewportdisplaypreset.constant as const

LOG = mmSolver.logger.get_logger()


def _get_viewport_renderer(model_panel):
    """
    Get the current renderer for the specified model_panel.

    :param model_panel: The model panel name.
    :type model_panel: str

    :returns: The current renderer name.
    :rtype: str or None
    """
    assert isinstance(model_panel, pycompat.TEXT_TYPE)
    if not maya.cmds.modelPanel(model_panel, exists=True):
        return None

    renderer_name = maya.cmds.modelEditor(model_panel, query=True, rendererName=True)
    return renderer_name


def _set_viewport_renderer(model_panel, renderer_name):
    """
    Set the renderer for the specified model_panel.

    :param model_panel: The model panel name.
    :type model_panel: str

    :param renderer_name: The renderer to set.
    :type renderer_name: str

    :returns: True if successful, False otherwise.
    :rtype: bool
    """
    assert isinstance(model_panel, pycompat.TEXT_TYPE)
    assert isinstance(renderer_name, pycompat.TEXT_TYPE)

    if not maya.cmds.modelPanel(model_panel, exists=True):
        return False

    available_renderers = (
        maya.cmds.modelEditor(model_panel, query=True, rendererList=True) or []
    )
    if renderer_name not in available_renderers:
        LOG.warn(
            'The renderer %r is unavailable. '
            'The default Viewport 2.0 will be used instead.',
            renderer_name,
        )
        maya.cmds.modelEditor(
            model_panel, edit=True, rendererName=const.RENDERER_VIEWPORT_TWO
        )
        return False

    maya.cmds.modelEditor(model_panel, edit=True, rendererName=renderer_name)
    return True


def _get_viewport_renderer_override(model_panel):
    """
    Get the current renderer override for the specified model_panel.

    :param model_panel: The model panel name.
    :type model_panel: str

    :returns: The current renderer override name, or None if not set.
    :rtype: str or None
    """
    assert isinstance(model_panel, pycompat.TEXT_TYPE)

    if not maya.cmds.modelPanel(model_panel, exists=True):
        return None

    renderer_override_name = maya.cmds.modelEditor(
        model_panel, query=True, rendererOverrideName=True
    )
    return renderer_override_name


def _set_viewport_renderer_override(model_panel, renderer_override):
    """
    Set the renderer override for the specified model_panel.

    If the override is not available, attempts to load the mmSolver
    plugin if it's a known mmSolver renderer. Falls back to default
    Viewport 2.0 if the override cannot be set.

    :param model_panel: The model panel name.
    :type model_panel: str

    :param renderer_override: The renderer override to set.
    :type renderer_override: str

    :returns: True if successful, False otherwise.
    :rtype: bool
    """
    assert isinstance(model_panel, pycompat.TEXT_TYPE)
    assert isinstance(renderer_override, pycompat.TEXT_TYPE)

    if not maya.cmds.modelPanel(model_panel, exists=True):
        return False

    if len(renderer_override) == 0:
        # Setting an empty string will unset any currently active override.
        maya.cmds.modelEditor(model_panel, edit=True, rendererOverrideName='')
        return True

    available_overrides = (
        maya.cmds.modelEditor(model_panel, query=True, rendererOverrideList=True) or []
    )
    if renderer_override not in available_overrides:
        if renderer_override in const.MMSOLVER_RENDERER_OVERRIDES:
            # Ensure mmSolver is loaded, so we have the provided
            # renderers.
            mmapi.load_plugin()
            available_overrides = (
                maya.cmds.modelEditor(
                    model_panel, query=True, rendererOverrideList=True
                )
                or []
            )

        if renderer_override not in available_overrides:
            LOG.warn(
                'The renderer override %r is unavailable. '
                'The default Viewport 2.0 will be used instead.',
                renderer_override,
            )
            maya.cmds.modelEditor(
                model_panel, edit=True, rendererName=const.RENDERER_VIEWPORT_TWO
            )
            # Setting an empty string will unset any currently active override.
            maya.cmds.modelEditor(model_panel, edit=True, rendererOverrideName='')
            return False

    maya.cmds.modelEditor(
        model_panel, edit=True, rendererOverrideName=renderer_override
    )
    return True


def _get_viewport_display_mode(model_panel):
    """
    Get the current display mode for the specified model_panel.

    Checks both wireframeOnShaded and displayAppearance settings to
    determine the effective display mode.

    :param model_panel: The model panel name.
    :type model_panel: str

    :returns: The current display mode ('wireframe', 'smoothShaded',
              'wireframeOnShaded'), or None if invalid.
    :rtype: str or None
    """
    assert isinstance(model_panel, pycompat.TEXT_TYPE)

    if not maya.cmds.modelPanel(model_panel, exists=True):
        return None

    wireframe_on_shaded = maya.cmds.modelEditor(
        model_panel, query=True, wireframeOnShaded=True
    )
    display_appearance = maya.cmds.modelEditor(
        model_panel, query=True, displayAppearance=True
    )

    shaded_appearances = [
        const.DISPLAY_APPEARANCE_SMOOTH_SHADED,
        const.DISPLAY_APPEARANCE_FLAT_SHADED,
    ]
    if wireframe_on_shaded and display_appearance in shaded_appearances:
        return const.DISPLAY_MODE_SMOOTH_SHADED_WIREFRAME

    if display_appearance not in const.DISPLAY_MODES:
        display_appearance = None
    return display_appearance


def _set_viewport_display_mode(model_panel, display_mode):
    """
    Set the display mode for the specified model_panel.

    :param model_panel: The model panel name.
    :type model_panel: str

    :param display_mode: The display mode to set.
    :type display_mode: str

    :returns: True if successful, False otherwise.
    :rtype: bool
    """
    assert isinstance(model_panel, pycompat.TEXT_TYPE)
    assert isinstance(display_mode, pycompat.TEXT_TYPE)
    assert display_mode in const.DISPLAY_MODES

    if not maya.cmds.modelPanel(model_panel, exists=True):
        return False

    wireframe = const.DISPLAY_MODE_WIREFRAME
    smooth_shaded = const.DISPLAY_MODE_SMOOTH_SHADED
    shaded_wireframe = const.DISPLAY_MODE_SMOOTH_SHADED_WIREFRAME
    if display_mode == shaded_wireframe:
        maya.cmds.modelEditor(model_panel, edit=True, displayAppearance=smooth_shaded)
        maya.cmds.modelEditor(model_panel, edit=True, wireframeOnShaded=True)
    elif display_mode in [wireframe, smooth_shaded]:
        maya.cmds.modelEditor(model_panel, edit=True, displayAppearance=display_mode)
        maya.cmds.modelEditor(model_panel, edit=True, wireframeOnShaded=False)

    return True


def _get_viewport_hold_outs(model_panel):
    """
    Get the current hold-outs state for the specified model_panel.

    :param model_panel: The model panel name.
    :type model_panel: str

    :returns: The current hold-outs state (True/False), or None if invalid.
    :rtype: bool or None
    """
    assert isinstance(model_panel, pycompat.TEXT_TYPE)

    if not maya.cmds.modelPanel(model_panel, exists=True):
        return None

    value = maya.cmds.modelEditor(model_panel, query=True, holdOuts=True)
    return value


def _set_viewport_hold_outs(model_panel, value):
    """
    Set the hold-outs state for the specified model_panel.

    :param model_panel: The model panel name.
    :type model_panel: str

    :param value: The hold-outs state to set.
    :type value: bool

    :returns: True if successful, False otherwise.
    :rtype: bool
    """
    assert isinstance(model_panel, pycompat.TEXT_TYPE)
    assert isinstance(value, bool)

    if not maya.cmds.modelPanel(model_panel, exists=True):
        return False

    maya.cmds.modelEditor(model_panel, edit=True, holdOuts=value)
    return True


def set_viewport_display_preset(model_panel, preset):
    """
    Apply a specific viewport preset to the model_panel.

    Sets the renderer, renderer override, display mode, and hold-outs state.
    If any setting fails, reverts all changes to maintain consistency.

    :param model_panel: The model panel name.
    :type model_panel: str

    :param preset: Preset dictionary containing 'name', 'renderer',
                   'display_mode', and 'hold_outs' keys, and optionally
                   the 'renderer_override' key.
    :type preset: dict

    :returns: True if all settings were successfully applied, False otherwise.
    :rtype: bool
    """
    assert isinstance(model_panel, pycompat.TEXT_TYPE)
    if len(model_panel) == 0 or len(preset) == 0:
        return False

    preset_name = preset.get('name')
    renderer = preset.get('renderer')
    override = preset.get('renderer_override')
    display_mode = preset.get('display_mode')
    hold_outs = preset.get('hold_outs')

    if preset_name is None:
        LOG.warn(
            'Could not set viewport, preset name is invalid; preset_name=%r',
            preset_name,
        )
        return False
    if renderer is None:
        LOG.warn(
            'Could not set viewport to %r preset, renderer is invalid; renderer=%r',
            preset_name,
            renderer,
        )
        return False
    if display_mode is None:
        LOG.warn(
            'Could not set viewport to %r preset, display mode is invalid; display_mode=%r',
            preset_name,
            display_mode,
        )
        return False
    if display_mode not in const.DISPLAY_MODES:
        LOG.warn(
            'Could not set viewport to %r preset, display mode is invalid; display_mode=%r',
            preset_name,
            display_mode,
        )
        return False
    if hold_outs is None:
        LOG.warn(
            'Could not set viewport to %r preset, hold-outs state is invalid; hold_outs=%r',
            preset_name,
            hold_outs,
        )
        return False

    previous_renderer = _get_viewport_renderer(model_panel)
    previous_override = _get_viewport_renderer_override(model_panel)
    previous_display_mode = _get_viewport_display_mode(model_panel)
    previous_hold_outs = _get_viewport_hold_outs(model_panel)

    success = True
    try:
        renderer_success = _set_viewport_renderer(model_panel, renderer)
        override_success = True
        if override is not None:
            override_success = _set_viewport_renderer_override(model_panel, override)
        display_success = _set_viewport_display_mode(model_panel, display_mode)
        hold_outs_success = _set_viewport_hold_outs(model_panel, hold_outs)
        success = (
            renderer_success
            and override_success
            and display_success
            and hold_outs_success
        )
    except RuntimeError:
        LOG.exception('Failed to set the preset; %r', preset)
        success = False

    if success is False:
        _set_viewport_renderer(model_panel, previous_renderer)
        if previous_override is not None:
            _set_viewport_renderer_override(model_panel, previous_override)
        if previous_display_mode in const.DISPLAY_MODES:
            _set_viewport_display_mode(model_panel, previous_display_mode)
        if previous_hold_outs is not None:
            _set_viewport_hold_outs(model_panel, previous_hold_outs)

    return success


def _get_current_preset_index(model_panel, presets):
    """
    Determine which preset in the cycle is currently active.

    :param model_panel: The model panel name.
    :type model_panel: str

    :param presets: List of preset dictionaries.
    :type presets: list

    :returns: Index of the current preset, or 0 if not found.
    :rtype: int
    """
    result_preset_index = 0
    if model_panel is None or len(presets) == 0:
        return result_preset_index

    current_renderer = _get_viewport_renderer(model_panel)
    current_override = _get_viewport_renderer_override(model_panel)
    current_display_mode = _get_viewport_display_mode(model_panel)
    current_hold_outs = _get_viewport_hold_outs(model_panel)
    if current_renderer is None or current_display_mode is None:
        return result_preset_index

    for i, preset in enumerate(presets):
        preset_renderer = preset.get('renderer')
        preset_override = preset.get('renderer_override')
        preset_display = preset.get('display_mode')
        preset_hold_outs = preset.get('hold_outs')
        if (
            current_renderer == preset_renderer
            and current_override == preset_override
            and current_display_mode == preset_display
            and current_hold_outs == preset_hold_outs
        ):
            result_preset_index = i
            break

    return result_preset_index


def cycle_viewport_presets(model_panel, presets, direction=1):
    """
    Cycle viewport presets in the specified direction.

    :param model_panel: The model panel name.
    :type model_panel: str

    :param presets: List of preset dictionaries to cycle through.
    :type presets: list

    :param direction: 1 for forward, -1 for backward.
    :type direction: int

    :returns: Tuple of (success, next_preset) where success indicates
              if the preset was applied successfully, and next_preset
              is the preset dictionary that was attempted.
    :rtype: tuple of (bool, dict)
    """
    assert isinstance(model_panel, pycompat.TEXT_TYPE)
    assert len(presets) > 0

    current_index = _get_current_preset_index(model_panel, presets)
    next_index = (current_index + direction) % len(presets)
    next_preset = presets[next_index]

    success = set_viewport_display_preset(model_panel, next_preset)
    return success, next_preset


def show_viewport_message(message, fade_time=None, position=None, warning=None):
    """
    Show a message in the viewport.

    :param message: The message to display.
    :type message: str

    :param fade_time: How long to show the message.
    :type fade_time: float

    :param position: Where to position the message.
    :type position: str
    """
    if fade_time is None:
        fade_time = const.MESSAGE_FADE_TIME
    if position is None:
        position = const.MESSAGE_POSITION
    assert isinstance(fade_time, float)
    assert fade_time > 0.0
    assert isinstance(position, pycompat.TEXT_TYPE)
    assert warning is None or isinstance(warning, bool)

    display_message = message
    if warning:
        pre_text = '<p style="color:#DCCE88";>'
        post_text = '</p>'
        display_message = pre_text + message + post_text

    try:
        maya.cmds.inViewMessage(
            assistMessage=display_message,
            position=position,
            fade=True,
            fadeOutTime=fade_time,
        )
    except RuntimeError:
        LOG.exception()

        # Fallback and print to the console.
        if not warning:
            LOG.info(message)
        else:
            LOG.warn(message)
