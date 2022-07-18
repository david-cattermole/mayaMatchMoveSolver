# Tool Modules

Each tool is separated into named modules, each has a specific purpose
and rules. For examples of tools, look at the existing tools for
inspiration and a skeleton to use.

A tool structure (with a UI) will look like this:

- toolname/
  - lib.py
  - tool.py
  - constant.py
  - ui/
    - toolname_layout.py
    - toolname_layout.ui
    - toolname_window.py

## lib sub-module

The `lib` module should contain all functions that do the "main
purpose" of the tool. This module should *never* assume there is a
Maya UI available.

The `lib` module provides a way for other tools (including the current
one) to access functions that are re-usable. The functions in `lib`
are not intended to be used by users directly.

## tool sub-module

The `tool` module constains the user-facing functions

Functions `main()` and `open_window()`.

## constant sub-module

The `constant` module

## ui sub-module

The `ui` module

### ui.toolname_layout sub-module

The `toolname_layout` module

### ui.toolname_window sub-module

The `toolname_window` module
