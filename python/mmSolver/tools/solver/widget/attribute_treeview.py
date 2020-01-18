# Copyright (C) 2020 David Cattermole.
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
Object Browser widget.
"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt
import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger


LOG = mmSolver.logger.get_logger()


class AttributeTreeView(QtWidgets.QTreeView):

    def __init__(self, parent=None, *args, **kwargs):
        super(AttributeTreeView, self).__init__(parent, *args, **kwargs)
        return

    def contextMenuEvent(self, event):
        LOG.info('Attribute TreeView Context Menu Event: %r', event)
        menu = QtWidgets.QMenu(self)
        cutAct = QtWidgets.QAction('Attr Cut Action', self)
        copyAct = QtWidgets.QAction('Attr Copy Action', self)
        pasteAct = QtWidgets.QAction('Attr Paste Action', self)
        menu.addAction(cutAct)
        menu.addAction(copyAct)
        menu.addAction(pasteAct)
        menu.exec_(event.globalPos())
        return
