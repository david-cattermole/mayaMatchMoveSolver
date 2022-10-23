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
"""
Export 2D Markers from Blender.
"""

import os

import bpy
from bpy.props import StringProperty, IntProperty
from bpy_extras.io_utils import ExportHelper

from . import utils
from . import uvtrack_format_blender as uv_fmt


class MmSolver_OT_exportSelectedMarkers(bpy.types.Operator, ExportHelper):
    """Save a .uv file for 2D Tracks."""
    bl_idname = 'mmsolver.export_selected_markers'
    bl_label = 'Export Selected 2D Tracks'

    filename_ext = '.uv'
    filter_glob: StringProperty(
        default='*.uv',
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    frame_start: IntProperty(name='Start Frame',
            description='Start frame for export',
            default=1, min=1, max=300000)
    frame_end: IntProperty(name='End Frame',
            description='End frame for export',
            default=250, min=1, max=300000)

    def execute(self, context):
        file_path = self.filepath
        if file_path is None or len(file_path) == 0:
            msg = 'mmSolver: Export 2D Tracks: Could not write file data.'
            self.report({'ERROR'}, msg)
            return {'FINISHED'}

        clip, cam, tracks = utils.get_selected_clip_objects(context)
        if clip is None or cam is None or tracks is None:
            msg = (
                'mmSolver: Export 2D Tracks: '
                'Please select 2D Tracks in the Movie Clip Editor. '
                'Could not get selected 2D Tracks.'
            )
            self.report({'WARNING'}, msg)
            return {'CANCELLED'}

        start_frame = clip.frame_start
        end_frame = start_frame + clip.frame_duration
        frame_range = (max(self.frame_start, start_frame),
                       min(self.frame_end, end_frame))

        data_str = uv_fmt.generate(
            context,
            clip, cam, tracks,
            frame_range,
            fmt=uv_fmt.UV_TRACK_FORMAT_VERSION_PREFERRED)
        if data_str is None or len(data_str) == 0:
            msg = 'mmSolver: Export 2D Tracks: Could not generate file data.'
            self.report({'ERROR'}, msg)
            return {'FINISHED'}

        file_path = utils.write_text_data_to_file(data_str, file_path)
        msg = 'mmSolver: Export 2D Tracks: Successfully written file: {}'
        self.report({'INFO'}, msg.format(file_path))
        return {'FINISHED'}

    def invoke(self, context, event):
        self.frame_start = context.scene.frame_start
        self.frame_end = context.scene.frame_end

        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


def menu_export(self, context):
    default_path = os.path.splitext(bpy.data.filepath)[0] + '.uv'
    op = self.layout.operator(
        MmSolver_OT_exportSelectedMarkers.bl_idname,
        text='Export Selected 2D Tracks (MM Solver .uv)')
    op.filepath = default_path


def register():
    bpy.utils.register_class(MmSolver_OT_exportSelectedMarkers)
    bpy.types.TOPBAR_MT_file_export.append(menu_export)


def unregister():
    bpy.utils.unregister_class(MmSolver_OT_exportSelectedMarkers)
    bpy.types.TOPBAR_MT_file_export.remove(menu_export)


if __name__ == '__main__':
    register()
