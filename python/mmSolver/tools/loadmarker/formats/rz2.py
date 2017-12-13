"""
Reads a Matchmover rz2 file.
"""

import re

import mmSolver.api as mmapi
import mmSolver.tools.loadmarker.interface as interface
import mmSolver.tools.loadmarker.formatmanager as fmtmgr


class LoaderRZ2(interface.LoaderBase):

    name = 'MatchMover TrackPoints (.rz2)'
    file_exts = ['.rz2']

    def parse(self, file_path):
        mkr_data_list = []

        f = open(file_path, 'r')
        text = f.read()
        f.close()

        idx = text.find('imageSequence')
        if idx == -1:
            return mkr_data_list

        start_idx = text.find('{', idx+1)
        if start_idx == -1:
            return mkr_data_list

        end_idx = text.find('}', start_idx+1)
        if end_idx == -1:
            return mkr_data_list

        imgseq = text[start_idx+1:end_idx]
        imgseq = imgseq.strip()
        splt = imgseq.split()
        x_res = int(splt[0])
        y_res = int(splt[1])
        
        # Get path
        imgseq_path = re.search(r'.*f\(\s\"(.*)\"\s\).*', imgseq)
        if imgseq_path is None:
            return mkr_data_list
        imgseq_path = imgseq_path.groups()

        # Get frame range
        range_regex = re.search(r'.*b\(\s(\d*)\s(\d*)\s(\d*)\s\)', imgseq)
        if range_regex is None:
            return mkr_data_list
        range_grps = range_regex.groups()

        # # TODO: Should we have a start_frame argument, which allows us to
        # specify the start_frame when loading into Maya?

        # Get start, end and by frame.
        # file_start_frame = int(range_grps[0])
        # file_end_frame = int(range_grps[1])
        # file_by_frame = int(range_grps[2])
        # if start_frame is None:
        #     start_frame = file_start_frame
        #     end_frame = file_end_frame
        #     by_frame = file_by_frame
        # else:
        #     # re-orient the frame range by the given start_frame.
        #     start_frame = start_frame
        #     end_frame = start_frame + (file_end_frame - file_start_frame)
        #     by_frame = file_by_frame

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
                x = float(splt[1]) / x_res
                y = float(splt[2]) / y_res
                enable_value = int(frame in frames)

                mkr_data.enable.set_value(frame, enable_value)
                mkr_data.x.set_value(frame, x)
                mkr_data.y.set_value(frame, y)

            mkr_data_list.append(mkr_data)

        return mkr_data_list


# Register the File Format
mgr = fmtmgr.get_format_manager()
mgr.register_format(LoaderRZ2)
