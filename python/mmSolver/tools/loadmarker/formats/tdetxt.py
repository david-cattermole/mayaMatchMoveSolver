"""
The .txt format from the 3DEqualizer 2D Points exporter.

The position coordinate (0.0, 0.0) is the lower-left.
The position coordinate (width, height) is the upper-right.

This format is resolution dependant!

The file format looks like this::

    int     # Number of track points in the file
    string  # Name of point
    int     # Color of the point
    int     # Number of frames
    int float float  # Frame, X position, Y position

Simple file with 1 2D track and 1 frame of data::

    1
    My Point Name
    0
    1
    1 1920.0 1080.0

"""

import mmSolver.logger
import mmSolver.tools.loadmarker.interface as interface
import mmSolver.tools.loadmarker.formatmanager as fmtmgr

LOG = mmSolver.logger.get_logger()


class Loader3DETXT(interface.LoaderBase):

    name = '3DEqualizer Track Points (*.txt)'
    file_exts = ['.txt']
    args = [
        ('image_width', None),
        ('image_height', None),
    ]

    def parse(self, file_path, **kwargs):
        """
        Parse the file path as a 3DEqualizer .txt file.

        :param file_path: File path to parse.
        :type file_path: str

        :param kwargs: expected to contain 'image_width' and 'image_height'.

        :return: List of MarkerData.
        """
        # If the image width/height is not given we raise an error immediately.
        image_width = kwargs.get('image_width')
        image_height = kwargs.get('image_height')
        if isinstance(image_width, (int, float)):
            ValueError('image_width must be float or int.')
        if isinstance(image_height, (int, float)):
            ValueError('image_height must be float or int.')
        if image_width is None:
            image_width = 1.0
        if image_height is None:
            image_height = 1.0
        inv_image_width = 1.0 / image_width
        inv_image_height = 1.0 / image_height

        f = open(file_path, 'r')
        lines = f.readlines()
        f.close()
        if len(lines) == 0:
            raise OSError('No contents in the file: %s' % file_path)
        mkr_data_list = []

        line = lines[0]
        line = line.strip()
        num_points = int(line)
        if num_points < 1:
            raise interface.ParserError('No points exist.')

        idx = 1  # Skip the first line
        for i in xrange(num_points):
            line = lines[idx]
            mkr_name = line.strip()

            # Create marker
            mkr_data = interface.MarkerData()
            mkr_data.set_name(mkr_name)

            # Get point color
            idx += 1
            line = lines[idx]
            line = line.strip()
            mkr_color = int(line)
            mkr_data.set_color(mkr_color)

            idx += 1
            line = lines[idx]
            line = line.strip()
            num_frames = int(line)
            if num_frames <= 0:
                idx += 1
                msg = 'point has no data: %r'
                LOG.warning(msg, mkr_name)
                continue

            # Frame data parsing
            frames = []
            j = num_frames
            while j > 0:
                idx += 1
                line = lines[idx]
                line = line.strip()
                if len(line) == 0:
                    # Have we reached the end of the file?
                    break
                j = j - 1
                split = line.split()
                if len(split) != 3:
                    # We should not get here
                    msg = 'File invalid, there must be 3 numbers in line: %r'
                    raise interface.ParserError(msg % line)
                frame = int(split[0])
                mkr_u = float(split[1]) * inv_image_width
                mkr_v = float(split[2]) * inv_image_height
                mkr_weight = 1.0

                mkr_data.weight.set_value(frame, mkr_weight)
                mkr_data.x.set_value(frame, mkr_u)
                mkr_data.y.set_value(frame, mkr_v)
                frames.append(frame)

            # Fill in occluded point frames
            all_frames = list(range(min(frames), max(frames)+1))
            for frame in all_frames:
                mkr_enable = int(frame in frames)
                mkr_data.enable.set_value(frame, mkr_enable)
                if mkr_enable is False:
                    mkr_data.weight.set_value(frame, 0.0)

            mkr_data_list.append(mkr_data)
            idx += 1

        return mkr_data_list


# Register the File Format
mgr = fmtmgr.get_format_manager()
mgr.register_format(Loader3DETXT)
