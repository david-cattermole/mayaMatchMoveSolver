# Copyright (C) 2022 David Cattermole.
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

# NOTE: '{{' and '}}' is used in place of real '{' and '}' characters,
# to allow Python's 'str.format()' to work.
DISPLAY_MODE_EXPRESSION = '''
if ({image_plane_tfm}.displayMode == 0)
{{
    {baked_image_plane_shape}.lodVisibility = 0;
    {live_image_plane_shape}.lodVisibility = 1;
}} else {{
    {baked_image_plane_shape}.lodVisibility = 1;
    {live_image_plane_shape}.lodVisibility = 0;
}}
'''
