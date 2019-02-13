"""
Window for the Channel Sensitivity tool.

Usage::

   import mmSolver.tools.channelsensitivity.ui.channelsensitivity_window as channelsensitivity_window
   channelsensitivity_window.main()

"""

import sys

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.helputils as helputils
import mmSolver.tools.channelsensitivity.ui.channelsensitivity_layout\
    as channelsensitivity_layout


LOG = mmSolver.logger.get_logger()
MM_SOLVER_CHAN_SENSE_UI = None
baseModule, BaseWindow = uiutils.getBaseWindow()


class ChannelSensitivityWindow(BaseWindow):
    def __init__(self, parent=None, name=None):
        super(ChannelSensitivityWindow, self).__init__(parent,
                                                       name=name)
        self.setupUi(self)
        self.addSubForm(channelsensitivity_layout.ChannelSensitivityLayout)

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


def main(show=True, widthHeight=(400, 100)):
    global MM_SOLVER_CHAN_SENSE_UI

    valid = uiutils.isValidQtObject(MM_SOLVER_CHAN_SENSE_UI)
    if MM_SOLVER_CHAN_SENSE_UI is not None and valid is True:
        MM_SOLVER_CHAN_SENSE_UI.close()

    name = 'ChannelSensitivityWindow'
    app, parent = uiutils.getParent()
    MM_SOLVER_CHAN_SENSE_UI = ChannelSensitivityWindow(parent=parent,
                                                       name=name)
    if not MM_SOLVER_CHAN_SENSE_UI:
        return MM_SOLVER_CHAN_SENSE_UI
    if show:
        MM_SOLVER_CHAN_SENSE_UI.show()

    if ((isinstance(widthHeight, (tuple, list)) is True)
         and (len(widthHeight) == 2)):
        pos = MM_SOLVER_CHAN_SENSE_UI.pos()
        MM_SOLVER_CHAN_SENSE_UI.setGeometry(pos.x(),
                                            pos.y(),
                                            widthHeight[0],
                                            widthHeight[1])

    # Enter Qt application main loop
    if app is not None:
        sys.exit(app.exec_())
    return MM_SOLVER_CHAN_SENSE_UI
