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
Copy 2D Tracks from Blender, as .uv format.
"""

import bpy

from . import uvtrack_format_blender as uv_fmt
from . import utils


class MmSolver_OT_copySelectedMarkers(bpy.types.Operator):
    """Save a temporary .uv file for 2D Tracks."""
    bl_idname = 'mmsolver.copy_selected_markers'
    bl_label = 'Copy Markers'

    def invoke(self, context, event):
        clip, cam, tracks = utils.get_selected_clip_objects(context)
        if clip is None or cam is None or tracks is None:
            msg = (
                'mmSolver: Copy 2D Tracks: '
                'Please select 2D Tracks in the Movie Clip Editor. '
                'Could not get selected 2D Tracks.'
            )
            self.report({'WARNING'}, msg)
            return {'CANCELLED'}

        start_frame = clip.frame_start
        end_frame = start_frame + clip.frame_duration
        frame_range = (start_frame, end_frame)

        data_str = uv_fmt.generate(
            context,
            clip, cam, tracks,
            frame_range,
            fmt=uv_fmt.UV_TRACK_FORMAT_VERSION_PREFERRED)
        if data_str is None or len(data_str) == 0:
            msg = 'mmSolver: Copy 2D Tracks: Could not generate file data.'
            self.report({'ERROR'}, msg)
            return {'FINISHED'}

        file_path = utils.write_text_data_to_temp_file(data_str)
        if file_path is None or len(file_path) == 0:
            msg = 'mmSolver: Copy 2D Tracks: Could not write file data.'
            self.report({'ERROR'}, msg)
            return {'FINISHED'}
        msg = 'mmSolver: Copy 2D Tracks: Successfully written file: {}'.format(file_path)
        self.report({'INFO'}, msg)

        # Encode text so it includes formatting characters like a file
        # read.
        file_path = file_path.encode('utf8')
        bpy.context.window_manager.clipboard = file_path
        return {'FINISHED'}


def register():
    bpy.utils.register_class(MmSolver_OT_copySelectedMarkers)


def unregister():
    bpy.utils.unregister_class(MmSolver_OT_copySelectedMarkers)


if __name__ == '__main__':
    register()
