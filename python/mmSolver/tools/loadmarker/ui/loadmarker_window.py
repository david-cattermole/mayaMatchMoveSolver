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
Window for the Load Marker tool.

Usage::

   import mmSolver.tools.loadmarker.ui.loadmarker_window as loadmarker_window
   loadmarker_window.main()

"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.helputils as helputils
import mmSolver.tools.loadmarker.constant as const
import mmSolver.tools.loadmarker.lib as lib
import mmSolver.tools.loadmarker.ui.loadmarker_layout as loadmarker_layout
import mmSolver.tools.loadmarker.lib.mayareadfile as mayareadfile


LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


class LoadMarkerWindow(BaseWindow):

    name = 'LoadMarkerWindow'

    def __init__(self, parent=None, name=None):
        super(LoadMarkerWindow, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(loadmarker_layout.LoadMarkerLayout)

        self.setWindowTitle(const.WINDOW_TITLE)

        # Standard Buttons
        self.baseHideStandardButtons()
        self.applyBtn.show()
        self.helpBtn.show()
        self.closeBtn.show()
        self.applyBtn.setText('Load')

        self.applyBtn.clicked.connect(self.apply)
        self.helpBtn.clicked.connect(self.help)

        # Hide irrelevant stuff
        self.baseHideMenuBar()
        self.baseHideProgressBar()

    def apply(self):
        cam = None
        try:
            self.progressBar.setValue(0)
            self.progressBar.show()

            file_path = self.subForm.getFilePath()
            camera_text = self.subForm.getCameraText()
            camera_data = self.subForm.getCameraData()
            width, height = self.subForm.getImageResolution()
            self.progressBar.setValue(20)

            mkr_data_list = mayareadfile.read(
                file_path,
                image_width=width,
                image_height=height
            )
            self.progressBar.setValue(70)

            if camera_text == const.NEW_CAMERA_VALUE:
                cam = lib.create_new_camera()
            else:
                cam = camera_data
            self.progressBar.setValue(90)

            mayareadfile.create_nodes(mkr_data_list, cam=cam)
        finally:
            self.progressBar.setValue(100)
            self.progressBar.hide()
            # Update the camera comboBox with the created camera, or
            # the last used camera.
            selected_cameras = [cam]
            self.subForm.updateCameraList(
                self.subForm.camera_comboBox,
                self.subForm.camera_model,
                selected_cameras)
        return

    def help(self):
        src = helputils.get_help_source()
        helputils.open_help_in_browser(page='tools.html#load-markers', help_source=src)
        return


def main(show=True, auto_raise=True, delete=False):
    """
    Open the Load Marker UI window.

    :param show: Show the UI.
    :type show: bool

    :param auto_raise: If the UI is open, raise it to the front?
    :type auto_raise: bool

    :param delete: Delete the existing UI and rebuild it? Helpful when
                   developing the UI in Maya script editor.
    :type delete: bool

    :returns: A new solver window, or None if the window cannot be
              opened.
    :rtype: SolverWindow or None.
    """
    win = LoadMarkerWindow.open_window(
        show=show,
        auto_raise=auto_raise,
        delete=delete
    )
    return win
