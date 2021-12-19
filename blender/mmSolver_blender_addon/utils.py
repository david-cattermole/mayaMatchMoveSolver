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

import tempfile
import time

import bpy

from . import uvtrack_format_blender as uv_fmt


def get_selected_clip_objects(context):
    # The context must be a clip editor only, otherwise we cannot get
    # the movieclip.
    print('context.area.type', context.area.type)
    if context.area.type == 'CLIP_EDITOR':
        clip = context.edit_movieclip
    else:
        clip = bpy.context.scene.active_clip
    cam = clip.tracking.camera

    # Only selected tracks
    tracks = [x for x in clip.tracking.tracks
              if (x.select
                  or x.select_anchor
                  or x.select_pattern
                  or x.select_search)]
    return clip, cam, tracks


def write_text_data_to_file(data_str, file_path):
    assert isinstance(data_str, str)
    with open(file_path, 'w') as f:
        f.write(data_str)
    return file_path


def write_text_data_to_temp_file(data_str):
    assert isinstance(data_str, str)
    # Prefix with the current time 'YYYY-MM-DD_HH_MM', for example
    # '2020-12-04_14_26'.
    now_str = time.strftime('%Y-%m-%d_%H_%M')
    prefix = 'tmp_{0}_'.format(now_str)
    f = tempfile.NamedTemporaryFile(
        mode='w',
        prefix=prefix,
        suffix=uv_fmt.FILE_EXT,
        delete=False
    )
    if f.closed:
        msg = "Error: Couldn't open file.\n{}"
        print(msg.format(repr(f.name)))
        return None
    f.write(data_str)
    f.close()
    return f.name