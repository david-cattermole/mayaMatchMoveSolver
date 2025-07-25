# Copyright (C) 2021 David Cattermole
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
Window for the Reparent tool.

Usage::

   import mmSolver.tools.reparent2.ui.reparent2_window as window
   window.main()

"""

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.commonmenus as commonmenus
import mmSolver.ui.helputils as helputils
import mmSolver.utils.transform as tfm_utils
import mmSolver.tools.reparent2.constant as const
import mmSolver.tools.reparent2.tool as tool
import mmSolver.tools.reparent2.ui.reparent2_layout as layout


LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


def _open_help():
    src = helputils.get_help_source()
    page = 'tools_generaltools.html#reparent-ui'
    helputils.open_help_in_browser(page=page, help_source=src)
    return


class Reparent2Window(BaseWindow):
    name = 'Reparent2Window'

    def __init__(self, parent=None, name=None):
        super(Reparent2Window, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(layout.Reparent2Layout)

        self.setWindowTitle(const.WINDOW_TITLE)
        self.setWindowType(qtpyutils.WINDOW_TYPE_DIALOG)

        # Standard Buttons
        self.baseHideStandardButtons()
        self.applyBtn.show()
        self.closeBtn.show()
        self.applyBtn.clicked.connect(self.apply)

        # Hide irrelevant stuff
        self.baseHideProgressBar()

        self.add_menus(self.menubar)
        self.menubar.show()

    def add_menus(self, menubar):
        edit_menu = QtWidgets.QMenu('Edit', menubar)
        commonmenus.create_edit_menu_items(
            edit_menu, reset_settings_func=self.reset_options
        )
        menubar.addMenu(edit_menu)

        help_menu = QtWidgets.QMenu('Help', menubar)
        commonmenus.create_help_menu_items(help_menu, tool_help_func=_open_help)
        menubar.addMenu(help_menu)

    def apply(self):
        form = self.getSubForm()
        children_nodes = form.getChildrenNodes()
        parent_node = form.getParentNode()
        LOG.debug('children_nodes: %r', children_nodes)
        LOG.debug('parent_node: %r', parent_node)

        # Store transform nodes (to be restored after tool is run).
        children_tfm_nodes = [tfm_utils.TransformNode(node=n) for n in children_nodes]
        if parent_node is not None:
            parent_tfm_node = tfm_utils.TransformNode(node=parent_node)

        # Ensure we have enough nodes.
        msg = ''
        if parent_node is None:
            msg = 'Not enough nodes, choose at least 1 node.'
        else:
            msg = 'Not enough children nodes, ' 'choose at least 1 child node.'
        if len(children_nodes) == 0:
            LOG.error(msg)
            return
        tool.reparent(children_nodes, parent_node)

        # Update children and parent nodes after reparent
        # process. Updates the UI.
        children_nodes = [tn.get_node() for tn in children_tfm_nodes]
        form.setChildrenNodes(children_nodes)
        if parent_node is None:
            form.setParentNode([])
        else:
            form.setParentNode([parent_tfm_node.get_node()])
        return

    def reset_options(self):
        form = self.getSubForm()
        form.reset_options()
        return


def main(show=True, auto_raise=True, delete=False):
    """
    Open the Smooth Keyframes UI window.

    :param show: Show the UI.
    :type show: bool

    :param auto_raise: If the UI is open, raise it to the front?
    :type auto_raise: bool

    :param delete: Delete the existing UI and rebuild it? Helpful when
                   developing the UI in Maya script editor.
    :type delete: bool

    :returns: A new reparent2 window, or None if the window cannot be
              opened.
    :rtype: Reparent2Window or None.
    """
    win = Reparent2Window.open_window(show=show, auto_raise=auto_raise, delete=delete)
    return win
