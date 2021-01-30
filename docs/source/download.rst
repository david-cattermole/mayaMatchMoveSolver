.. _download-heading:

Download
========

Download the latest release **mmSolver v0.3.12**:

.. list-table:: Downloads
   :widths: auto
   :header-rows: 1

   * - Operating System
     - Maya Version
     - Link

   * - Linux
     - Maya 2016
     - `link <https://github.com/david-cattermole/mayaMatchMoveSolver/releases/download/v0.3.12/mayaMatchMoveSolver-0.3.12-maya2016-linux.tar.gz>`_

   * - Linux
     - Maya 2017
     - `link <https://github.com/david-cattermole/mayaMatchMoveSolver/releases/download/v0.3.12/mayaMatchMoveSolver-0.3.12-maya2017-linux.tar.gz>`_

   * - Linux
     - Maya 2018
     - `link <https://github.com/david-cattermole/mayaMatchMoveSolver/releases/download/v0.3.12/mayaMatchMoveSolver-0.3.12-maya2018-linux.tar.gz>`_

   * - Linux
     - Maya 2019
     - `link <https://github.com/david-cattermole/mayaMatchMoveSolver/releases/download/v0.3.12/mayaMatchMoveSolver-0.3.12-maya2019-linux.tar.gz>`_

   * - Windows
     - Maya 2016
     - `link <https://github.com/david-cattermole/mayaMatchMoveSolver/releases/download/v0.3.12/mayaMatchMoveSolver-0.3.12-maya2016-win64.zip>`_

   * - Windows
     - Maya 2017
     - `link <https://github.com/david-cattermole/mayaMatchMoveSolver/releases/download/v0.3.12/mayaMatchMoveSolver-0.3.12-maya2017-win64.zip>`_

   * - Windows
     - Maya 2018
     - `link <https://github.com/david-cattermole/mayaMatchMoveSolver/releases/download/v0.3.12/mayaMatchMoveSolver-0.3.12-maya2018-win64.zip>`_

   * - Windows
     - Maya 2019
     - `link <https://github.com/david-cattermole/mayaMatchMoveSolver/releases/download/v0.3.12/mayaMatchMoveSolver-0.3.12-maya2019-win64.zip>`_

   * - MacOS
     - Maya 2018
     - `link <https://github.com/david-cattermole/mayaMatchMoveSolver/releases/download/v0.3.12/mayaMatchMoveSolver-0.3.12-maya2018-mac.tar.gz>`_

   * - MacOS
     - Maya 2019
     - `link <https://github.com/david-cattermole/mayaMatchMoveSolver/releases/download/v0.3.12/mayaMatchMoveSolver-0.3.12-maya2019-mac.tar.gz>`_

Older versions and full release notes can be found on the GitHub releases_ page.

Installation
============

To install **mmSolver** on your personal computer,
follow the install instructions below.

Alternatively to install in a large company environment needing
configuration options make sure to follow the
`INSTALL.md <https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/INSTALL.md>`_
file.

Install Maya Module
-------------------

**mmSolver** can be installed by un-zipping the archive
(`.zip` or `.tar.gz`) file, and copying the contents into the
following directory on your computer:

On Windows::

   C:\Users\<Your User Name>\My Documents\maya\<Maya Version>\modules

On Linux::

   ~/maya/<Maya Version>/modules

You may need to create the 'modules' directory manually, as it is not
created default by Maya.

You should now have one file and one directory like this::

   <maya user directory>/2017/modules/mayaMatchMoveSolver-0.1.0-maya2017-win64.mod (module file)
   <maya user directory>/2017/modules/mayaMatchMoveSolver-0.1.0-maya2017-win64 (directory)

You can open Maya as normal and the tool will be recognised
automatically at start-up.  You will see a message in the Script
Editor '# root : MM Solver Startup... #', a new shelf and menu will
automatically be created for you named 'mmSolver'.

Install 3DEqualizer Files
-------------------------

To install the 3DEqualizer (3DE) tools for **mmSolver**, follow the steps below.

The 3DEqualizer tools are for integration into workflows using 3DEqualizer.

.. list-table:: 3DEqualizer Tools
   :widths: auto
   :header-rows: 1

   * - File Name
     - Tool Name

   * - copy_track_mmsolver.py
     - Copy 2D Tracks (MM Solver)

   * - export_track_mmsolver.py
     - Export 2D Tracks (MM Solver)...

   * - paste_camera_mmsolver.py
     - Paste Camera (MM Solver)...

Script Database
---------------

For 3DEqualizer versions supporting the online
`Script Database <https://www.3dequalizer.com/?site=scriptdb>`_, you may
install the latest tools via the menu '3DE4 > Python > ScriptDB Installer'.

See this `video tutorial <https://www.youtube.com/watch?v=gVr_Fo1xh0E>`_
for an example of installing scripts with ScriptDB.

Home Directory
--------------

Alternatively, you may install scripts manually by copying the
3DEqualizer python scripts in the `3dequalizer` sub-directory into the
`~/.3dequalizer/py_scripts` directory.

On Linux::

   $ cd <module directory>
   $ cp ./3dequalizer/* ~/.3dequalizer/py_scripts

On Windows::

   > CD <module directory>
   > XCOPY 3dequalizer\* "%AppData%\.3dequalizer\py_scripts" /Y

Install SynthEyes Files
-----------------------

To install the SynthEyes tools for **mmSolver**, copy the files inside
the `<module root>/syntheyes` directory, into the custom SynthEyes
script directory.

On Windows::

   > CD <module directory>
   > XCOPY syntheyes\* "%AppData%\SynthEyes\scripts" /Y

For example, this path::

   C:\Users\<Your User Name>\AppData\Roaming\SynthEyes\scripts

The tool can be accessed as a standard export script in the menu
`File > Export > Trackers (mmSolver)`. This tool will export all
Tracks in the scene as .uv file format, ready to be imported into
mmSolver.

.. _releases:
   https://github.com/david-cattermole/mayaMatchMoveSolver/releases
