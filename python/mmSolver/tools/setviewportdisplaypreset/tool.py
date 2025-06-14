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
Main tool implementation for the Set Viewport Display Preset tool.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.logger
import mmSolver.utils.viewport as viewport_utils
import mmSolver.tools.setviewportdisplaypreset.constant as const
import mmSolver.tools.setviewportdisplaypreset.lib as lib

LOG = mmSolver.logger.get_logger()


def _cycle_viewport_presets(model_panel, presets, direction):
    """
    Internal helper to cycle viewport display presets and show appropriate messages.

    :param model_panel: The model panel name.
    :type model_panel: str

    :param presets: List of preset dictionaries to cycle through.
    :type presets: list

    :param direction: 1 for forward, -1 for backward.
    :type direction: int

    :returns: True if the preset was successfully applied, False otherwise.
    :rtype: bool
    """
    success, next_preset = lib.cycle_viewport_presets(
        model_panel, presets, direction=direction
    )
    if success:
        preset_name = next_preset.get('name', const.UNKNOWN_DISPLAY_PRESET_NAME)
        lib.show_viewport_message("Viewport Display Preset: {}".format(preset_name))
        return True
    else:
        lib.show_viewport_message("Failed to set viewport display preset!", warning=True)
        return False


def cycle_active_viewport_display_preset_forward():
    """
    Cycle forward through viewport display presets.

    :returns: True if successful, False otherwise.
    :rtype: bool
    """
    model_panel = viewport_utils.get_active_model_panel()
    if not model_panel:
        lib.show_viewport_message("Viewport Display Preset: No active viewport found!", warning=True)
        return False

    direction = 1
    presets = const.DEFAULT_CYCLE_DISPLAY_PRESETS
    return _cycle_viewport_presets(model_panel, presets, direction)


def cycle_active_viewport_display_preset_backward():
    """
    Cycle backward through viewport display presets.

    :returns: True if successful, False otherwise.
    :rtype: bool
    """
    model_panel = viewport_utils.get_active_model_panel()
    if not model_panel:
        lib.show_viewport_message("Viewport Display Preset: No active viewport found!", warning=True)
        return False

    direction = -1
    presets = const.DEFAULT_CYCLE_DISPLAY_PRESETS
    return _cycle_viewport_presets(model_panel, presets, direction)


def set_active_viewport_display_preset(display_preset_name):
    """
    Set a specific viewport display preset by name.

    :param display_preset_name: The name of the preset to set.
    :type display_preset_name: str

    :returns: True if successful, False otherwise.
    :rtype: bool
    """
    model_panel = viewport_utils.get_active_model_panel()
    if not model_panel:
        lib.show_viewport_message("Viewport Display Preset: No active viewport found!", warning=True)
        return False

    presets = const.DEFAULT_CYCLE_DISPLAY_PRESETS

    # Find the preset by name
    target_preset = None
    for preset in presets:
        preset_name = preset.get('name')
        if preset_name is None:
            continue
        if preset_name.lower() == display_preset_name.lower():
            target_preset = preset
            break

    if target_preset is None:
        lib.show_viewport_message("Viewport Display Preset '{}' not found!".format(display_preset_name), warning=True)
        return False

    if lib.set_viewport_display_preset(model_panel, target_preset):
        preset_name = target_preset.get('name', const.UNKNOWN_DISPLAY_PRESET_NAME)
        lib.show_viewport_message("Viewport Display Preset: {}".format(preset_name))
        return True
    else:
        lib.show_viewport_message("Failed to set viewport display preset!", warning=True)
        return False
