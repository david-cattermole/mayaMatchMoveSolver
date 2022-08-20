# Tool Modules

Each tool is separated into named modules, each has a specific purpose
and rules. For examples of tools, look at the existing tools for
inspiration and a skeleton to use.

A tool structure (with a UI) will look like this:

- toolname/
  - tool.py
  - lib.py
  - constant.py
  - ui/
    - toolname_window.py
    - toolname_layout.py
    - toolname_layout.ui

## tool sub-module

The `tool` module constains the user-facing functions `main()` and/or
`open_window()`.

`main()` is the main entry point of the tool. This is the function
that should be run when a user clicks the tool, as the first choice
(not an option box, or secondary mode).

`main()` should never take positional arguments (although keyword
arguments are fine but should not be needed often), or assume the user
will run the function directly.

The `main()` function should take the current state of the Maya UI and
act accordingly. For example, the user's currently selected node(s),
the currently active window and the user's configuration settings
(including per-scene configuration data).

The `open_window()` function is intended to open a graphical user
interface to provide the user the ability to interactively enter data
before manually running the tool.

## lib sub-module

The `lib` module should contain all functions that do the "main
purpose" of the tool. This module should *never* assume there is a
Maya UI available.

The `lib` module provides a way for other tools (including the current
one) to access functions that are re-usable. The functions in `lib`
are not intended to be used by users directly.

## constant sub-module

The `constant` module contains data that should never change. This
includes information like common (static) values used in the tool, or
default values for the tool.

The values in this module are values that may be quickly edited by the
programmer to quickly change the behavior or display of the tool.

The module can be used to store hard-coded look-up data, to avoid
complicating and bloating the main `tool` or `lib` modules.

If there is no significant static data for the tool, this module can
be skipped.

## ui sub-module

The `ui` module contains the graphical User Interface code. All code
in the `ui` module is allowed to assume the user has a display/screen
(ie, not a command-line only tool) will be available to the tool.

### ui.toolname_window sub-module

The `ui.toolname_window` module contains a window class used to
display a UI window to the user. The window should generally inherit
from the common base class
(`mmSolver.ui.base_maya_window.BaseMayaWindow`) to provide common
features that are available in all mmSolver UIs.

The `ui.toolname_window` module should construct the window, menus,
buttons and add widgets from the `ui.toolname_layout`.

### ui.toolname_layout sub-module

The `ui.toolname_layout` module provides individual widgets to the
`ui.toolname_window` module that are unique to the tool. For example
in a simple tool, a string value named "name" may be displayed to the
user as a Qt QLineEdit widget.

The `ui.toolname_layout` module may also import and use Python classes
automatically generated from `.ui` files. The `.ui` files can be
generated with Qt Designer - a graphical user interface for generating
graphical user interfaces.
