"""
Window for the Load Marker tool.

Usage::

   import mmSolver.tools.loadmarker.ui.loadmarker_window as loadmarker_window
   loadmarker_window.main()

"""

import sys

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.helputils as helputils
import mmSolver.tools.loadmarker.constant as const
import mmSolver.tools.loadmarker.lib as lib
import mmSolver.tools.loadmarker.ui.loadmarker_layout as loadmarker_layout
import mmSolver.tools.loadmarker.mayareadfile as mayareadfile


LOG = mmSolver.logger.get_logger()
UI = None


baseModule, BaseWindow = uiutils.getBaseWindow()


class LoadMarkerWindow(BaseWindow):
    def __init__(self, parent=None, name=None):
        super(LoadMarkerWindow, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(loadmarker_layout.LoadMarkerLayout)

        self.setWindowTitle('Load Markers - mmSolver')

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
        helputils.open_help_in_browser(page='tools.html#load-markers')
        return


def main(show=True, widthHeight=(800, 400)):
    global UI

    valid = uiutils.isValidQtObject(UI)
    if UI is not None and valid is True:
        UI.close()

    name = 'LoadMarkerWindow'
    app, parent = uiutils.getParent()
    UI = LoadMarkerWindow(parent=parent, name=name)
    if not UI:
        return UI
    if show:
        UI.show()

    if ((isinstance(widthHeight, (tuple, list)) is True)
         and (len(widthHeight) == 2)):
        pos = UI.pos()
        UI.setGeometry(pos.x(), pos.y(), widthHeight[0], widthHeight[1])

    # Enter Qt application main loop
    if app is not None:
        sys.exit(app.exec_())
    return UI
