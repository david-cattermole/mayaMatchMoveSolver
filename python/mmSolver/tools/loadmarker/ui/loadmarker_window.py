# Copyright (C) 2018, 2019, 2020, 2025 David Cattermole.
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

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.helputils as helputils
import mmSolver.ui.commonmenus as commonmenus
import mmSolver.utils.undo as undoutils
import mmSolver.utils.config as config_utils
import mmSolver.tools.loadmarker.constant as const
import mmSolver.tools.loadmarker.ui.loadmarker_layout as loadmarker_layout
import mmSolver.tools.loadmarker.lib.utils as lib
import mmSolver.tools.loadmarker.lib.mayareadfile as mayareadfile
import mmSolver.tools.solver.lib.collection as col_lib
import mmSolver.tools.userpreferences.constant as userprefs_const
import mmSolver.tools.userpreferences.lib as userprefs_lib


LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


def get_config():
    """Get the Load Marker config object or None."""
    file_name = const.CONFIG_FILE_NAME
    config_path = config_utils.get_home_dir_path(file_name)
    config = config_utils.Config(config_path)
    config.set_autoread(False)
    config.set_autowrite(False)
    return config


def _open_help():
    src = helputils.get_help_source()
    helputils.open_help_in_browser(
        page='tools_inputoutput.html#load-markers', help_source=src
    )
    return


def _load_nodes(
    load_mode,
    progress_bar,
    camera_text,
    camera_data,
    mkr_grp_text,
    mkr_grp_data,
    add_to_collection,
    collection_text,
    collection_data,
    mkr_data_list,
    load_bnd_pos,
    camera_field_of_view,
):
    new_mkr_list = None

    if load_mode == const.LOAD_MODE_NEW_VALUE:
        # Get Camera and MarkerGroup.
        if camera_text == const.NEW_CAMERA_VALUE:
            cam = lib.create_new_camera()
            mkr_grp = lib.create_new_marker_group(cam)
        else:
            cam = camera_data
            if mkr_grp_text == const.NEW_MARKER_GROUP_VALUE:
                mkr_grp = lib.create_new_marker_group(cam)
            else:
                mkr_grp = mkr_grp_data
        progress_bar.setValue(60)

        # Get Collection
        col = None
        if add_to_collection is True:
            if collection_text == const.NEW_COLLECTION_VALUE:
                col = col_lib.create_collection()
            else:
                col = collection_data
        progress_bar.setValue(70)

        new_mkr_list = mayareadfile.create_nodes(
            mkr_data_list,
            cam=cam,
            mkr_grp=mkr_grp,
            col=col,
            with_bundles=True,
            load_bundle_position=load_bnd_pos,
            camera_field_of_view=camera_field_of_view,
        )

    elif load_mode == const.LOAD_MODE_REPLACE_VALUE:
        progress_bar.setValue(60)
        mkr_list = lib.get_selected_markers()
        # NOTE: camera_field_of_view can only be from one
        # camera, because (we assume) only one MarkerData
        # file can be loaded at once.
        new_mkr_list = mayareadfile.update_nodes(
            mkr_list,
            mkr_data_list,
            load_bundle_position=load_bnd_pos,
            camera_field_of_view=camera_field_of_view,
        )
    else:
        raise ValueError('Load mode is not valid: %r' % load_mode)

    return new_mkr_list


class LoadMarkerWindow(BaseWindow):

    name = 'LoadMarkerWindow'

    def __init__(self, parent=None, name=None):
        super(LoadMarkerWindow, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(loadmarker_layout.LoadMarkerLayout)

        self.setWindowTitle(const.WINDOW_TITLE)
        self.setWindowFlags(QtCore.Qt.Tool)

        # Standard Buttons
        self.baseHideStandardButtons()
        self.applyBtn.show()
        self.closeBtn.show()
        self.applyBtn.setText('Load')
        self.applyBtn.clicked.connect(self.apply)

        # Hide irrelevant stuff
        self.baseHideProgressBar()

        self.add_menus(self.menubar)
        self.menubar.show()

    def add_menus(self, menubar):
        help_menu = QtWidgets.QMenu('Help', menubar)
        commonmenus.create_help_menu_items(help_menu, tool_help_func=_open_help)
        menubar.addMenu(help_menu)

    def apply(self):
        cam = None
        mkr_grp = None
        col = None

        file_path = self.subForm.getFilePath()
        load_mode = self.subForm.getLoadModeText()
        rename_markers = self.subForm.getRenameMarkers()
        rename_markers_name = self.subForm.getRenameMarkersName()
        camera_text = self.subForm.getCameraText()
        camera_data = self.subForm.getCameraData()
        mkr_grp_text = self.subForm.getMarkerGroupText()
        mkr_grp_data = self.subForm.getMarkerGroupData()
        add_to_collection = self.subForm.getAddToCollectionValue()
        collection_text = self.subForm.getCollectionText()
        collection_data = self.subForm.getCollectionData()
        load_bnd_pos = self.subForm.getLoadBundlePositions()
        undist_mode = self.subForm.getDistortionModeText()
        use_overscan = self.subForm.getUseOverscanValue()
        undistorted = undist_mode == const.UNDISTORTION_MODE_VALUE
        width, height = self.subForm.getImageResolution()

        # Otherwise when we try to rename markers, the tool will get
        # errors.
        if rename_markers is True:
            if len(rename_markers_name) == 0:
                LOG.error(
                    'Please type a Rename Markers name, or disable Rename Markers.'
                )
                return
            elif rename_markers_name[0].isdigit():
                LOG.error(
                    'Rename Markers name cannot %r start with a number! '
                    'Please start with a letter or underscore.',
                    rename_markers_name,
                )
                return

        camera_field_of_view = None
        if use_overscan is True:
            camera_field_of_view = self.subForm.getCameraFieldOfViewValue()

        # Temporarily disable adding new Markers to the Active
        # Collection.
        config = userprefs_lib.get_config()
        key = userprefs_const.REG_EVNT_ADD_NEW_MKR_TO_KEY
        old_value = userprefs_lib.get_value(config, key)
        temp_value = userprefs_const.REG_EVNT_ADD_NEW_MKR_TO_NONE_VALUE
        userprefs_lib.set_value(config, key, temp_value)

        try:
            self.progressBar.setValue(0)
            self.progressBar.show()

            with undoutils.undo_chunk_context():
                _, mkr_data_list = mayareadfile.read(
                    file_path,
                    image_width=width,
                    image_height=height,
                    undistorted=undistorted,
                )
                self.progressBar.setValue(50)

                new_mkr_list = _load_nodes(
                    load_mode,
                    self.progressBar,
                    camera_text,
                    camera_data,
                    mkr_grp_text,
                    mkr_grp_data,
                    add_to_collection,
                    collection_text,
                    collection_data,
                    mkr_data_list,
                    load_bnd_pos,
                    camera_field_of_view,
                )

                self.progressBar.setValue(90)
                if rename_markers is True:
                    changed_mkr_nodes = lib.rename_markers_and_bundles(
                        new_mkr_list, rename_markers_name
                    )
                    lib.set_selected_nodes(changed_mkr_nodes)

                self.progressBar.setValue(99)
                lib.trigger_maya_to_refresh()
        finally:
            self.progressBar.setValue(100)
            self.progressBar.hide()

            # Restore original config value.
            lib.deferred_revert_of_config_value(config, key, old_value)

            # Update the camera comboBox with the created camera, or
            # the last used camera.
            all_camera_nodes = lib.get_cameras()
            selected_cameras = [cam]
            active_camera = cam
            self.subForm.updateCameraList(
                self.subForm.camera_comboBox,
                self.subForm.camera_model,
                all_camera_nodes,
                selected_cameras,
                active_camera,
            )
            active_camera = cam
            active_mkr_grp = mkr_grp
            mkr_grp_nodes = lib.get_marker_groups(active_camera)
            self.subForm.updateMarkerGroupList(
                self.subForm.markerGroup_comboBox,
                self.subForm.markerGroup_model,
                active_mkr_grp,
                mkr_grp_nodes,
            )

            # Update the list of Collections, and pick the last used
            # Collection.
            active_col = col
            col_list = col_lib.get_collections()
            self.subForm.updateCollectionList(
                self.subForm.collection_comboBox,
                self.subForm.collection_model,
                active_col,
                col_list,
            )

            # Update config file with latest values.
            config = get_config()
            if config is not None:
                config.set_value("data/use_overscan", use_overscan)
                config.set_value("data/load_bundle_position", load_bnd_pos)
                config.set_value("data/distortion_mode", undist_mode)
                config.set_value("data/load_mode", load_mode)
                config.set_value('data/rename_markers', rename_markers)
                config.set_value('data/rename_markers_name', rename_markers_name)
                config.write()

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

    :returns: A new loadMarker window, or None if the window cannot be
              opened.
    :rtype: LoadMarkerWindow or None.
    """
    win = LoadMarkerWindow.open_window(show=show, auto_raise=auto_raise, delete=delete)
    return win
