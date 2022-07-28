# Copyright (C) 2021 David Cattermole.
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
import bpy


class MmSolverPanel(bpy.types.Panel):
    bl_idname = 'MMSOLVER_PT_mmSolverPanel'

    # Nice name of the panel in the GUI.
    bl_label = 'MM Solver'

    # Specifies the space (in fact - the window), where the panel will
    # be located. It can take the following values:
    #
    # EMPTY, VIEW_3D, TIMELINE, GRAPH_EDITOR, DOPESHEET_EDITOR,
    # NLA_EDITOR, IMAGE_EDITOR, SEQUENCE_EDITOR, CLIP_EDITOR,
    # TEXT_EDITOR, NODE_EDITOR, LOGIC_EDITOR, PROPERTIES, OUTLINER,
    # USER_PREFERENCES, INFO, FILE_BROWSER, CONSOLE
    bl_space_type = 'CLIP_EDITOR'

    # Specifies the region in space to place the panel. It can take
    # the following values:
    #
    # WINDOW, HEADER, CHANNELS, TEMPORARY, UI, TOOLS, TOOL_PROPS,
    # PREVIEW, HUD, NAVIGATION_BAR, EXECUTE, FOOTER, TOOL_HEADER, XR.
    bl_region_type = 'UI'

    # Specifies the panel placement context.
    bl_context = 'object'

    # Specifies the panel placement group.
    bl_category = 'Track'

    # Possible Values:
    #
    # - DEFAULT_CLOSED - Defines if the panel has to be open or
    #   collapsed at the time of its creation.
    #
    # - HIDE_HEADER - If set to False, the panel shows a header, which
    #   contains a clickable arrow to collapse the panel and the label
    #   (see bl_label).
    #
    # - INSTANCED - Multiple panels with this type can be used as part
    #   of a list depending on data external to the UI. Used to create
    #   panels for the modifiers and other stacks.
    #
    # - HEADER_LAYOUT_EXPAND - Allow buttons in the header to stretch
    #   and shrink to fill the entire layout width.
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        self.layout.operator(
            'mmsolver.copy_selected_markers',
            icon='COPYDOWN',
            text='Copy 2D Tracks')

        self.layout.operator(
            'mmsolver.export_selected_markers',
            icon='EXPORT',
            text='Export 2D Tracks...')


def register():
    bpy.utils.register_class(MmSolverPanel)


def unregister():
    bpy.utils.unregister_class(MmSolverPanel)
