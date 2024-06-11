# Copyright (C) 2024 David Cattermole
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
The main component of the user interface for the image cache
window.
"""

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.tools.imagecache.ui.ui_imagecache_layout as ui_imagecache_layout


LOG = mmSolver.logger.get_logger()


class ImageCacheLayout(QtWidgets.QWidget, ui_imagecache_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(ImageCacheLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Populate the UI with data
        self.populateUi()

    def reset_options(self):
        self.populateUi()

    def populateUi(self):
        """
        Update the UI for the first time the class is created.
        """
        return
