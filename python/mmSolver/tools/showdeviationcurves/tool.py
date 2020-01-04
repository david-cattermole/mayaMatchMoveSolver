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
Displays deviation curves to the user, as a graph.
"""
#
# Ideas:
#
# - This tool should show the user the deviation curves for a
#   collection and markers.
#
# - Deviation is a 'state', so it's only based on the last solve
#   performed, we cannot change the deviation based on the collection
#   that was solved - that would be very complex and complicated to
#   reason with. Showing the 'last state' is intuitive and simpler to
#   store and show.
#
# - For a first version of this tool, we can simply select the
#   deviation curves of the collection and all markers in the
#   collection, then display the Maya Graph Editor.
#
# - A more complex example of this tool may create a Qt-based graph UI
#   widget. This UI widget could be embedded inside the Solver UI, or
#   displayed individually.
#
# - A separate widget may have two halves; left and right. The left
#   side would contain the marker names showing the current frame
#   Deviation and average deviation. The right side would be a
#   line-plot graph of the deviation for each marker - similar to the
#   3DEqualizer Deviation Browser.
#

import maya.cmds

import mmSolver.logger
import mmSolver.tools.solver.lib.maya_utils as solver_maya_utils

LOG = mmSolver.logger.get_logger()


def show_deviation():
    """
    Open the Maya Graph Editor, showing Deviation curves of selected markers.
    """
    # Get Selected Markers, if camera is selected, all markers
    # underneath are used.
    mkr_list = solver_maya_utils.get_markers_from_selection()
    mkr_nodes = [mkr.get_node() for mkr in mkr_list]
    if len(mkr_nodes) == 0:
        msg = 'No Markers found from selection. No deviation to display.'
        LOG.warning(msg)
        return
    maya.cmds.select(mkr_nodes, replace=True)

    # Open Maya Graph Editor, only show 'deviation' attribute.
    #
    # Note: 'graphEditor1OutlineEd' and 'graphEditor1GraphEd' are
    # constants used by Maya since v1.0. We should dynamically look
    # these up, if possible.
    cmd = (
        'GraphEditor;'
        'filterUISelectAttributesCheckbox deviation 1 graphEditor1OutlineEd;'
    )
    if maya.cmds.about(apiVersion=True) >= 201700:
        # The new Graph Editor is only in Maya 2017+
        cmd += 'GraphEditorAbsoluteView;'
    cmd += 'animCurveEditor -autoFit graphEditor1GraphEd;'
    maya.mel.eval(cmd)
    return


def hide_deviation():
    """
    Hide the deviation attribute from the Graph Editor.
    """
    # Open Maya Graph Editor, turn off display of 'deviation'
    # attribute.
    cmd = (
        'GraphEditor;'
        'filterUISelectAttributesCheckbox deviation 0 graphEditor1OutlineEd;'
    )
    maya.mel.eval(cmd)
    return


def main(show=True):
    """
    Show or hide Marker deviation.
    """
    if show is True:
        show_deviation()
    else:
        hide_deviation()
    return
