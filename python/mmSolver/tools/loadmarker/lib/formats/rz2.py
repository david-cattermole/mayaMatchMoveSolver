# Copyright (C) 2018 David Cattermole.
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
Reads a Matchmover rz2 file.
"""

import os
import re

import mmSolver.tools.loadmarker.lib.interface as interface
import mmSolver.tools.loadmarker.lib.formatmanager as fmtmgr


class LoaderRZ2(interface.LoaderBase):

    name = 'MatchMover TrackPoints (*.rz2)'
    file_exts = ['.rz2']
    args = []

    def parse(self, file_path, **kwargs):
        if not isinstance(file_path, basestring):
            raise TypeError('file_path is not a string: %r' % file_path)
        if not os.path.isfile(file_path):
            raise OSError('File path does not exist: %s' % file_path)

        mkr_data_list = []
        f = open(file_path, 'r')
        text = f.read()
        f.close()

        idx = text.find('imageSequence')
        if idx == -1:
            msg = "Could not get 'imageSequence' index from: %r"
            raise interface.ParserError(msg % text)

        start_idx = text.find('{', idx+1)
        if start_idx == -1:
            msg = 'Could not get the starting index from: %r'
            raise interface.ParserError(msg % text)

        end_idx = text.find('}', start_idx+1)
        if end_idx == -1:
            msg = 'Could not get the ending index from: %r'
            raise interface.ParserError(msg % text)

        imgseq = text[start_idx+1:end_idx]
        imgseq = imgseq.strip()
        splt = imgseq.split()
        x_res = int(splt[0])
        y_res = int(splt[1])
        
        # Get path
        imgseq_path = re.search(r'.*f\(\s\"(.*)\"\s\).*', imgseq)
        if imgseq_path is None:
            msg = 'Could not get the image sequence path from: %r'
            raise interface.ParserError(msg % imgseq)
        imgseq_path = imgseq_path.groups()

        # Get frame range
        range_regex = re.search(r'.*b\(\s(\d*)\s(\d*)\s(\d*)\s\)', imgseq)
        if range_regex is None:
            msg = 'Could not get the frame range from: %r'
            raise interface.ParserError(msg % imgseq)
        range_grps = range_regex.groups()
        start_frame = int(range_grps[0])
        end_frame = int(range_grps[1])
        by_frame = int(range_grps[2])
        frames = xrange(start_frame, end_frame, by_frame)

        idx = end_idx
        while True:
            idx = text.find('pointTrack', idx+1)
            if idx == -1:
                break
            start_idx = text.find('{', idx+1)
            if start_idx == -1:
                break
            end_idx = text.find('}', start_idx+1)
            if end_idx == -1:
                break

            # Get point track name
            point_track_header = text[idx:start_idx]
            track_regex = re.search(r'pointTrack\s*\"(.*)\".*', point_track_header)
            if track_regex is None:
                continue
            track_grps = track_regex.groups()
            if len(track_grps) == 0:
                continue
            mkr_name = track_grps[0]

            # create marker
            mkr_data = interface.MarkerData()
            mkr_data.set_name(mkr_name)
            mkr_data.weight.set_value(start_frame, 1.0)
            for frame in frames:
                mkr_data.enable.set_value(frame, 0)

            point_track = text[start_idx + 1:end_idx]
            for line in point_track.splitlines():
                splt = line.split()
                if len(splt) == 0:
                    continue
                frame = int(splt[0])
                # NOTE: In MatchMover, top-left is (0,0), but we want
                # bottom-left to be (0,0).
                x = float(splt[1]) / x_res
                y = ((float(splt[2]) / y_res) * -1) + 1.0
                enable_value = int(frame in frames)

                mkr_data.enable.set_value(frame, enable_value)
                mkr_data.x.set_value(frame, x)
                mkr_data.y.set_value(frame, y)

            mkr_data_list.append(mkr_data)

        return mkr_data_list


# Register the File Format
mgr = fmtmgr.get_format_manager()
mgr.register_format(LoaderRZ2)
