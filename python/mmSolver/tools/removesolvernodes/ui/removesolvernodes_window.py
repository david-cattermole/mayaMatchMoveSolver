"""
Window for the Remove Solver Nodes tool.

Usage::

   import mmSolver.tools.removesolvernodes.ui.removesolvernodes_window as removesolvernodes_window
   removesolvernodes_window.main()

"""
import datetime
import uuid

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.commonmenus as commonmenus
import mmSolver.ui.helputils as helputils
import mmSolver.utils.tools as tools_utils
import mmSolver.tools.removesolvernodes.constants as const
import mmSolver.tools.removesolvernodes.tool as tool
import mmSolver.tools.removesolvernodes.ui.removesolvernodes_layout as removesolvernodes_layout

LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


def _open_help():
    src = helputils.get_help_source()
    page = 'tools_generaltools.html#remove-solver-nodes'
    helputils.open_help_in_browser(page=page, help_source=src)
    return


class RemoveSolverNodesWindow(BaseWindow):
    name = 'RemoveSolverNodesWindow'

    def __init__(self, parent=None, name=None):
        super(RemoveSolverNodesWindow, self).__init__(parent,
                                               name=name)
        self.setupUi(self)
        self.addSubForm(removesolvernodes_layout.RemoveSolverNodesLayout)

        self.setWindowTitle(const.WINDOW_TITLE)
        self.setWindowFlags(QtCore.Qt.Tool)

        # Standard Buttons
        self.baseHideStandardButtons()
        self.applyBtn.show()
        self.closeBtn.show()
        self.applyBtn.setText('Clean')
        self.applyBtn.clicked.connect(self.clean)

        # Hide irrelevant stuff
        self.baseHideProgressBar()

        self.add_menus(self.menubar)
        self.menubar.show()

    def add_menus(self, menubar):
        edit_menu = QtWidgets.QMenu('Edit', menubar)
        commonmenus.create_edit_menu_items(
            edit_menu,
            save_settings_func=None,
            reset_settings_func=self.reset_options)
        menubar.addMenu(edit_menu)

        help_menu = QtWidgets.QMenu('Help', menubar)
        commonmenus.create_help_menu_items(
            help_menu,
            tool_help_func=_open_help)
        menubar.addMenu(help_menu)

    def reset_options(self):
        form = self.getSubForm()
        form.reset_options()
        return

    def clean(self):
        what_to_delete_dict = {
            'markers': self.subForm.markers_checkBox.isChecked(),
            'bundles': self.subForm.bundles_checkBox.isChecked(),
            'marker_groups': self.subForm.markerGroup_checkBox.isChecked(),
            'collections': self.subForm.collections_checkBox.isChecked(),
            'other_nodes': self.subForm.otherNodes_checkBox.isChecked()
            }
        all_list_to_delete, unknown_node_found = tool.filter_nodes(
                                                        what_to_delete_dict
                                                    )
        LOG.info(str(all_list_to_delete))
        LOG.warning(('unknown_node_found: ', unknown_node_found))
        if unknown_node_found:
            title = 'Confirmation'
            msg = 'Non-bundle nodes found parented under one or more bundle\n'\
                'nodes. It is suggested that you unparent and bake nodes \n'\
                'you want to keep.\n'\
                'Are you sure you want to delete them?'
            clicked_button = QtWidgets.QMessageBox.question(self, title, msg)
            if clicked_button == QtWidgets.QMessageBox.No:
                return
        undo_id = 'removesolvernodes: '
        undo_id += str(datetime.datetime.isoformat(datetime.datetime.now()))
        undo_id += ' '
        undo_id += str(uuid.uuid4())
        with tools_utils.tool_context(use_undo_chunk=True,
                                      undo_chunk_name=undo_id,
                                      restore_current_frame=True):
            tool.delete_nodes(all_list_to_delete)


def main(show=True, auto_raise=True, delete=False):
    """
    Open the Remove Solver Nodes UI.

    :param show: Show the UI.
    :type show: bool

    :param auto_raise: If the UI is open, raise it to the front?
    :type auto_raise: bool

    :param delete: Delete the existing UI and rebuild it? Helpful when
                   developing the UI in Maya script editor.
    :type delete: bool

    :returns: A new solver window, or None if the window cannot be
              opened.
    :rtype: RemoveSolverNodesWindow or None.
    """
    win = RemoveSolverNodesWindow.open_window(
        show=show,
        auto_raise=auto_raise,
        delete=delete
    )
    return win
