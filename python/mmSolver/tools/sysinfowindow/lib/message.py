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
Formats and displays system information.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import maya.cmds
import mmSolver.constant as mmSolver_const
import mmSolver.tools.sysinfowindow.constant as const


def get_sysinfo_text():
    text = ''

    # Python Constant values
    version = mmSolver_const.PROJECT_VERSION
    default_solver_const = mmSolver_const.DEFAULT_SOLVER
    module_name = mmSolver_const.MODULE_FULL_NAME

    # Maya Software Versions
    maya_cut_id = maya.cmds.about(cutIdentifier=True)
    maya_ver = maya.cmds.about(installedVersion=True)
    maya_api_ver = maya.cmds.about(apiVersion=True)
    qt_ver = maya.cmds.about(qtVersion=True)
    text += const.SOFTWARE_VERSION_TEXT.format(
        module_name=module_name,
        version=version,
        maya_ver=maya_ver,
        maya_cut_id=maya_cut_id,
        maya_api=maya_api_ver,
        qt_ver=qt_ver,
    )

    # System Information
    oper_sys = maya.cmds.about(operatingSystemVersion=True)
    oper_sys = oper_sys.strip()
    desktop_comp_man = maya.cmds.about(compositingManager=True)
    desktop_wind_man = maya.cmds.about(windowManager=True)
    try:
        gpu_info = ''.join(maya.cmds.ogs(deviceInformation=True))
        gpu_info = gpu_info.strip()
    except RuntimeError:
        gpu_info = '<Could not get GPU Device Information>'
    text += const.SYS_INFO_TEXT.format(
        operating_sys=oper_sys,
        desktop_comp_man=desktop_comp_man,
        desktop_wind_man=desktop_wind_man,
        gpu_info=gpu_info,
    )
    
    # mmSolver Configuration
    load_at_start = os.environ.get('MMSOLVER_LOAD_AT_STARTUP')
    create_menu = os.environ.get('MMSOLVER_CREATE_MENU')
    create_shelf = os.environ.get('MMSOLVER_CREATE_SHELF')
    help_source = os.environ.get('MMSOLVER_HELP_SOURCE')
    default_solver_env = os.environ.get('MMSOLVER_DEFAULT_SOLVER')
    debug_mode = os.environ.get('MMSOLVER_DEBUG')
    text += const.CONFIG_TEXT.format(
        load_at_start=load_at_start,
        create_menu=create_menu,
        create_shelf=create_shelf,
        help_source=help_source,
        default_solver_const=default_solver_const,
        default_solver_env=default_solver_env,
        debug_mode=debug_mode,        
    )
    return text
