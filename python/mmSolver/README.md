# Project Layout

The Python code layout is split into different sub-packages, and each
serves a purpose.

| Module            | Description                                                      |
|-------------------|------------------------------------------------------------------|
| mmSolver._api     | Internal API sub-modules                                         |
| mmSolver.api      | User facing API                                                  |
| mmSolver.constant | Build generated values                                           |
| mmSolver.logger   | [Logging](https://docs.python.org/3/library/logging.html) module |
| mmSolver.startup  | Functions to start mmSolver                                      |
| mmSolver.tools    | mmSolver Tools                                                   |
| mmSolver.ui       | Functions needing a desktop                                      |
| mmSolver.utils    | mmSolver helper functions                                        |
