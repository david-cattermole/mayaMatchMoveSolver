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
Formats and displays 'about' information.
"""

import os
import maya.cmds
import mmSolver.constant as mmSolver_const
import mmSolver.tools.aboutwindow.constant as const


def get_about_text():
    # Python Constant values
    version = mmSolver_const.PROJECT_VERSION
    desc = mmSolver_const.PROJECT_DESCRIPTION
    author = mmSolver_const.PROJECT_AUTHOR
    page = mmSolver_const.PROJECT_HOMEPAGE_URL
    copyrights = mmSolver_const.PROJECT_COPYRIGHT
    default_solver_const = mmSolver_const.DEFAULT_SOLVER
    module_name = mmSolver_const.MODULE_FULL_NAME

    # System Information
    oper_sys = maya.cmds.about(operatingSystemVersion=True)
    oper_sys = oper_sys.strip()
    maya_cut_id = maya.cmds.about(cutIdentifier=True)
    maya_ver = maya.cmds.about(installedVersion=True)
    maya_api_ver = maya.cmds.about(apiVersion=True)
    qt_ver = maya.cmds.about(qtVersion=True)
    desktop_comp_man = maya.cmds.about(compositingManager=True)
    desktop_wind_man = maya.cmds.about(windowManager=True)
    try:
        gpu_info = ''.join(maya.cmds.ogs(deviceInformation=True))
        gpu_info = gpu_info.strip()
    except RuntimeError:
        gpu_info = '<Could not get GPU Device Information>'

    # mmSolver Configuration
    load_at_start = os.environ.get('MMSOLVER_LOAD_AT_STARTUP')
    create_menu = os.environ.get('MMSOLVER_CREATE_MENU')
    create_shelf = os.environ.get('MMSOLVER_CREATE_SHELF')
    help_source = os.environ.get('MMSOLVER_HELP_SOURCE')
    default_solver_env = os.environ.get('MMSOLVER_DEFAULT_SOLVER')
    debug_mode = os.environ.get('MMSOLVER_DEBUG')

    text = const.ABOUT_TEXT.format(
        author=author,
        description=desc,
        page=page,
        copyrights=copyrights,
        module_name=module_name,
        default_solver_const=default_solver_const,

        version=version,
        maya_ver=maya_ver,
        maya_cut_id=maya_cut_id,
        maya_api=maya_api_ver,
        qt_ver=qt_ver,
        
        operating_sys=oper_sys,
        desktop_comp_man=desktop_comp_man,
        desktop_wind_man=desktop_wind_man,
        gpu_info=gpu_info,

        load_at_start=load_at_start,
        create_menu=create_menu,
        create_shelf=create_shelf,
        help_source=help_source,
        default_solver_env=default_solver_env,
        debug_mode=debug_mode,        
    )
    return text
