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

bl_info = {
    'name': 'MM Solver Blender Tools',
    'author': 'David Cattermole',
    'version': (0, 2, 1),
    'blender': (2, 80, 0),
    'location': 'Motion Clip Editor > Sidebar and File > Export > Export Selected 2D Tracks (MM Solver .uv)',
    'description': 'Tools to use mmSolver with Blender',
    'warning': '',
    'doc_url': 'https://david-cattermole.github.io/mayaMatchMoveSolver/index.html',
    'support': 'COMMUNITY',
    'category': 'Import-Export',
}


def register():
    from . import mmsolver_2d_tracks_export
    from . import mmsolver_2d_tracks_copy
    from . import mmsolver_panel
    mmsolver_2d_tracks_export.register()
    mmsolver_2d_tracks_copy.register()
    mmsolver_panel.register()


def unregister():
    from . import mmsolver_2d_tracks_export
    from . import mmsolver_2d_tracks_copy
    from . import mmsolver_panel
    mmsolver_2d_tracks_export.unregister()
    mmsolver_2d_tracks_copy.unregister()
    mmsolver_panel.unregister()


if __name__ == '__main__':
    register()
