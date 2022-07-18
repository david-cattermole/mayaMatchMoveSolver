# Utilities Modules

The modules in this directory are utilities that can be used in Maya
or in a Standalone Python interpreter.

The modules must *never* use any modules outside of this sub-package
(modules in `mmSolver.utils` only). If modules outside
`mmSolver.utils` are used then a module dependency loop will be
created, which will result in Python functions erroring.

The modules will be maintained for backwards compatibility. We cannot
remove or rename functions in `mmSolver.utils`.
