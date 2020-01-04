Configuration
=============

``mmSolver`` can be customised using configuration files.  The default
configuration of ``mmSolver`` is stored in the installation directory
'config' sub-directory, but each file may be overridden by adding a file into the home directory.

For Linux: ``${HOME}/.mmSolver``

For Windows: ``%APPDATA%/mmSolver``

When a new configuration file with the exact file name as a default
config file is found, it replaces the original. Configuration files
do not accumulate values.

For documenatation of the config utility module, see `mmSolver.utils.config`.
