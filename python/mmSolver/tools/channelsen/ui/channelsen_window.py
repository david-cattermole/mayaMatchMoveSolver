"""
Window for the Channel Sensitivity tool.

Usage::

   import mmSolver.tools.channelsen.ui.channelsen_window as channelsen_window
   channelsen_window.main()

"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.helputils as helputils
import mmSolver.tools.channelsen.ui.channelsen_layout as channelsen_layout


LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


class ChannelSenWindow(BaseWindow):

    name = 'ChannelSenWindow'

    def __init__(self, parent=None, name=None):
        super(ChannelSenWindow, self).__init__(parent,
                                               name=name)
        self.setupUi(self)
        self.addSubForm(channelsen_layout.ChannelSenLayout)

        self.setWindowTitle('Channel Box Sensitivity')

        # Standard Buttons
        self.baseHideStandardButtons()
        self.helpBtn.show()
        self.closeBtn.show()

        self.helpBtn.clicked.connect(self.help)

        # Hide irrelevant stuff
        self.baseHideMenuBar()
        self.baseHideProgressBar()

    def help(self):
        src = helputils.get_help_source()
        page = 'tools.html#channel-sensitivity'
        helputils.open_help_in_browser(page=page, help_source=src)
        return


def main(show=True, auto_raise=True, delete=False):
    """
    Open the Channel Sensitivity UI window.

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
    win = ChannelSenWindow.open_window(
        show=show,
        auto_raise=auto_raise,
        delete=delete
    )
    return win
