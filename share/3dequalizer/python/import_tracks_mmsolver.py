# -*- mode: python-mode; python-indent-offset: 4 -*-
#
# Copyright (C) 2018, 2021, 2022 David Cattermole.
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
# ----------------------------------------------------------------------
#
# 3DE4.script.name:    Import 2D Tracks (MM Solver)...
#
# 3DE4.script.version: v1.2
#
# 3DE4.script.gui:     Main Window::3DE4::File::Import
# 3DE4.script.gui:     Object Browser::Context Menu Point
# 3DE4.script.gui:     Object Browser::Context Menu Points
# 3DE4.script.gui:     Object Browser::Context Menu PGroup
#
# 3DE4.script.comment: Imports 2D tracking points from a file.
# 3DE4.script.comment:
# 3DE4.script.comment: The supported file formats are:
# 3DE4.script.comment: - MM Solver (.uv)
# 3DE4.script.comment: - 3DEqualizer (.txt)
# 3DE4.script.comment: - MatchMover (.rz2)
# 3DE4.script.comment: - PFTrack/PFMatchIt (.2dt / .txt)
#

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import abc
import collections
import json
import logging
import math
import sys
import os
import os.path
import re

import tde4

import mmSolver.utils.python_compat as pycompat
import mmSolver.utils.loadfile.excep as excep
import mmSolver.utils.loadfile.loader as loader
import mmSolver.utils.loadfile.floatutils as floatutils
import mmSolver.utils.loadfile.keyframedata as keyframedata
import mmSolver.utils.loadfile.formatmanager as fmtmgr
import mmSolver.utils.loadmarker.fileinfo as fileinfo
import mmSolver.utils.loadmarker.formatmanager as formatmanager
import mmSolver.utils.loadmarker.formatmanager as fmtmgr
import mmSolver.utils.loadmarker.markerdata as markerdata
import mmSolver.tools.loadmarker.constant as const
import mmSolver.logger

LOG = logging.getLogger()

WINDOW_TITLE = 'Import 2D Tracks (MM Solver)...'
SUPPORT_POINT_SURVEY_XYZ_ENABLED = 'setPointSurveyXYZEnabledFlags' in dir(tde4)
HELP_TEXT = """Import 2D Tracks from:
- MM Solver (.uv files)
- 3DEqualizer (.txt files) *
- MatchMover (.rz2 files)
- PFTrack/PFMatchIt (.2dt / .txt files) *

* Note: Some file formats embed the image resolution.
The resolution must match in order to align to the image correctly."""

# INCLUDE_FILE ./../../../python/mmSolver/utils/python_compat.py

# INCLUDE_FILE ./../../../python/mmSolver/tools/loadmarker/constant.py

# INCLUDE_FILE ./../../../python/mmSolver/utils/loadfile/excep.py

# INCLUDE_FILE ./../../../python/mmSolver/utils/loadfile/floatutils.py

# INCLUDE_FILE ./../../../python/mmSolver/utils/loadfile/formatmanager.py

# INCLUDE_FILE ./../../../python/mmSolver/utils/loadfile/keyframedata.py

# INCLUDE_FILE ./../../../python/mmSolver/utils/loadfile/loader.py

# INCLUDE_FILE ./../../../python/mmSolver/utils/loadmarker/fileinfo.py

# INCLUDE_FILE ./../../../python/mmSolver/utils/loadmarker/fileutils.py

# INCLUDE_FILE ./../../../python/mmSolver/utils/loadmarker/formatmanager.py

# INCLUDE_FILE ./../../../python/mmSolver/utils/loadmarker/markerdata.py

# INCLUDE_FILE ./../../../python/mmSolver/utils/loadmarker/formats/pftrack2dt.py

# INCLUDE_FILE ./../../../python/mmSolver/utils/loadmarker/formats/rz2.py

# INCLUDE_FILE ./../../../python/mmSolver/utils/loadmarker/formats/tdetxt.py

# INCLUDE_FILE ./../../../python/mmSolver/utils/loadmarker/formats/uvtrack.py


def read(file_path, **kwargs):
    """
    Read a file path, find the format parser based on the file extension.
    """
    if isinstance(file_path, pycompat.TEXT_TYPE) is False:
        msg = 'file path must be a string, got %r'
        raise TypeError(msg % type(file_path))
    if os.path.isfile(file_path) is False:
        msg = 'file path does not exist; %r'
        raise OSError(msg % file_path)

    file_format_classes = []
    mgr = formatmanager.get_format_manager()
    for fmt in mgr.get_formats():
        attr = getattr(fmt, 'file_exts', None)
        if attr is None:
            continue
        if not isinstance(fmt.file_exts, list):
            continue
        for ext in fmt.file_exts:
            if file_path.endswith(ext):
                file_format_classes.append(fmt)
    if len(file_format_classes) == 0:
        msg = 'No file formats found for file path: %r'
        raise RuntimeError(msg % file_path)

    file_info = None
    mkr_data_list = []
    for file_format_class in file_format_classes:
        file_format_obj = file_format_class()
        try:
            contents = file_format_obj.parse(file_path, **kwargs)
        except (excep.ParserError, OSError):
            contents = (None, [])

        file_info, mkr_data_list = contents
        if file_info and (isinstance(mkr_data_list, list) and len(mkr_data_list) > 0):
            break

    return file_info, mkr_data_list


def _set_3d_point(pg, p, mkr_data):
    bundle_pos = [mkr_data.bundle_x, mkr_data.bundle_y, mkr_data.bundle_z]
    bundle_pos_are_float = [isinstance(x, float) for x in bundle_pos]
    if all(bundle_pos_are_float) is False:
        return False

    tde4.setPointCalculated3D(pg, p, 1)
    tde4.setPointSurveyPosition3D(pg, p, bundle_pos)
    tde4.setPointSurveyMode(pg, p, 'SURVEY_EXACT')

    if SUPPORT_POINT_SURVEY_XYZ_ENABLED is False:
        return True

    bundle_lock = [
        int(mkr_data.bundle_lock_x or 0),
        int(mkr_data.bundle_lock_y or 0),
        int(mkr_data.bundle_lock_z or 0)
    ]
    if any(bundle_lock) is True:
        tde4.setPointSurveyXYZEnabledFlags(
            pg,
            p,
            bundle_lock[0],
            bundle_lock[1],
            bundle_lock[2],
        )
    return True


def create_markers(c, pg, start_frame, file_info, mkr_data_list):
    frames = tde4.getCameraNoFrames(c)
    if frames == 0:
        return []

    point_list = []
    for mkr_data in mkr_data_list:
        curve = [[-1.0, -1.0]] * (frames + 1)
        for frame in range(frames):
            pos_x = -1.0
            pos_y = -1.0
            real_frame = start_frame + frame
            enable = mkr_data.enable.get_value(real_frame)
            if enable:
                pos_x = mkr_data.x.get_value(real_frame)
                pos_y = mkr_data.y.get_value(real_frame)
            curve[frame] = [pos_x, pos_y]

        weight = mkr_data.weight.get_value(1)

        p = tde4.createPoint(pg)
        tde4.setPointName(pg, p, mkr_data.name)
        tde4.setPointWeight(pg, p, weight)
        tde_start_frame = 1  # 3DE internally always starts at frame 1.
        tde4.setPointPosition2DBlock(pg, p, c, tde_start_frame, curve)
        point_list.append(p)

        _set_3d_point(pg, p, mkr_data)

    return point_list


# GUI
c = tde4.getCurrentCamera()
pg = tde4.getCurrentPGroup()
if c is not None and pg is not None:
    req = tde4.createCustomRequester()
    tde4.addTextAreaWidget(req, 'help_text', 'Help', 170, 0)
    tde4.addSeparatorWidget(req, 'separator1')
    tde4.addFileWidget(req, 'file_browser', 'File Name...', '*')

    tde4.appendTextAreaWidgetString(req, 'help_text', HELP_TEXT)

    ret = tde4.postCustomRequester(req, WINDOW_TITLE, 800, 300, 'Ok', 'Cancel')
    if ret == 1:
        file_path = tde4.getWidgetValue(req, 'file_browser')
        if file_path is not None and os.path.isfile(file_path):
            image_width = tde4.getCameraImageWidth(c)
            image_height = tde4.getCameraImageHeight(c)
            file_info, mkr_data_list = read(
                file_path, image_width=image_width, image_height=image_height
            )

            start, end, step = tde4.getCameraSequenceAttr(c)
            start_frame = start

            create_markers(c, pg, start_frame, file_info, mkr_data_list)
else:
    tde4.postQuestionRequester(
        WINDOW_TITLE, 'There is no current Point Group or Camera.', 'Ok'
    )
