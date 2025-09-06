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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time

import maya.cmds
import maya.mel

import mmSolver.api as mmapi
import mmSolver.logger
import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.tools as tools_utils
import mmSolver.utils.constant as const_utils
import mmSolver.tools.attributecurvefilterpops.constant as const
import mmSolver.tools.attributecurvefilterpops.lib as lib

LOG = mmSolver.logger.get_logger()


def main():
    mmapi.load_plugin()

    nodes = maya.cmds.ls(selection=True)
    if len(nodes) == 0:
        LOG.warn("Please select at least 1 object.")
        return

    # Get configuration values
    frame_range_mode = configmaya.get_scene_option(
        const.CONFIG_FRAME_RANGE_MODE_KEY, const.DEFAULT_FRAME_RANGE_MODE
    )
    custom_start_frame = configmaya.get_scene_option(
        const.CONFIG_FRAME_START_KEY, const.DEFAULT_FRAME_START
    )
    custom_end_frame = configmaya.get_scene_option(
        const.CONFIG_FRAME_END_KEY, const.DEFAULT_FRAME_END
    )
    threshold = configmaya.get_scene_option(
        const.CONFIG_THRESHOLD_KEY, const.DEFAULT_THRESHOLD
    )
    frame_range = lib.get_frame_range(
        frame_range_mode, custom_start_frame, custom_end_frame
    )
    assert isinstance(threshold, float)

    node_attrs = lib.get_selected_node_attrs(nodes)
    LOG.debug('node_attrs: %r', node_attrs)
    if len(node_attrs) == 0:
        LOG.warn(
            "Please select at least 1 attribute in the Channel Box or Graph Editor."
        )
        return

    anim_curve_nodes = lib.get_attribute_anim_curves(
        node_attrs,
    )
    LOG.debug('anim_curve_nodes: %r', anim_curve_nodes)
    if len(anim_curve_nodes) == 0:
        LOG.warn(
            "No animation curves found on attributes, "
            "please bake attribute curves first."
        )
        return

    s = time.time()
    ctx = tools_utils.tool_context(
        use_undo_chunk=True,
        disable_viewport=True,
        disable_viewport_mode=const_utils.DISABLE_VIEWPORT_MODE_VP1_VALUE,
    )
    with ctx:
        success = False
        try:
            lib.filter_curves_pops(
                anim_curve_nodes,
                frame_range.start,
                frame_range.end,
                threshold,
            )
            success = True
        except Exception:
            LOG.exception('Filter attribute curves failed.')
        finally:
            e = time.time()
            if success is True:
                LOG.info(
                    'Filter attribute curves success. Time elapsed: %r secs', e - s
                )
            else:
                LOG.error(
                    'Filter attribute curves failed. Time elapsed: %r secs', e - s
                )
    return


def open_window():
    mmapi.load_plugin()

    import mmSolver.tools.attributecurvefilterpops.ui.attrcurvefilterpops_window as window

    window.main()
