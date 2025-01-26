# Download

The ***Maya MatchMove Solver*** is available for the following
platforms and can be downloaded from the
[Releases](https://github.com/david-cattermole/mayaMatchMoveSolver/releases)
page on the GitHub [project page](https://github.com/david-cattermole/mayaMatchMoveSolver).

| Operating System | Maya Version(s)                   |
|------------------|-----------------------------------|
| Linux            | Maya 2019, 2020, 2022, 2023, 2024 |
| Windows          | Maya 2019, 2020, 2022, 2023, 2024 |

Download the archive format (`.zip` or `.tar.gz`) for your Maya
version and operating system.

For a simple installation, **do not** install from the
`Source code (zip)` or `Source code (tar.gz)` archives. These archives
are for developers only.

*NOTE:* The pre-built binaries provided have been statically built
with special care for ABI compatibility and the recommended Linux
(CentOS), Windows, Maya API and VFX Platforms versions. If there are
any build or ABI issues, PRs are welcome or please file an
[issue](https://github.com/david-cattermole/mayaMatchMoveSolver/issues).

# Install Maya Module

***Maya MatchMove Solver*** can be installed by un-zipping the archive
(`.zip` or `.tar.gz`) file, and copying the contents into the
following directory on your computer:

On Windows:
```
C:\Users\<Your User Name>\My Documents\maya\<Maya Version>\modules
```

On Linux:
```
~/maya/<Maya Version>/modules
```

You may need to create the *modules* directory manually, as it is not
created default by Maya.

You should now have one file and one directory like this:
```
<maya user directory>\2017\modules\mayaMatchMoveSolver-0.1.0-maya2017-win64.mod (module file)
<maya user directory>\2017\modules\mayaMatchMoveSolver-0.1.0-maya2017-win64 (directory)
```

You can open Maya as normal and the tool will be recognised
automatically at start-up.  You will see a message in the Script
Editor `# root : MM Solver Startup... #`, and a new shelf will
automatically be created for you named *mmSolver*.

# Load mmSolver in Maya 2022

Loading custom plug-ins in Maya 2022+ has been changed to increase
security and avoid viruses, as a result mmSolver has needed to change
slightly. Previous versions of Maya should still work exactly as
before.

To load mmSolver in Maya 2022 you must run the following MEL command:
```
mmsolver_load
```

This will load the mmSolver plug-in, and allow you to automatically
load the mmSolver plug-in and will ensure it is loaded each time Maya
is started.

If you wish to unload mmSolver so it will not be loaded at Maya
start-up run the following MEL command:
```
mmsolver_unload
```

These commands added in mmSolver v0.3.16 were added to work-around the
Maya 2022+ Security preferences and ensure mmSolver will be loaded
when it's needed.

Additionally the Python module `mmSolver.startup` was added, and
allows pipelines to manually load mmSolver with the Python commands:
```
import mmSolver.startup
mmSolver.startup.mmsolver_startup()
```

Rather than using the `mmsolver_load` or `mmsolver_unload` commands,
optionally you can load the mmSolver plug-in via the menu `Windows >
Settings/Preferences > Plug-in Manager` window. This will also load
the mmSolver tools automatically when the plug-in is loaded. If you
wish to load mmSolver each time Maya is started you may enable
"autoload" via the Plug-in Manager to ensure the mmSolver tools,
shelves, menus and plug-in are always loaded.

# Project Configuration

By default, the tool should work without trouble, but some individuals
may want extra customisation.

To make customisations, edit the Maya Module file (ending with `.mod`)
using a text editor. The following environment variables are defined
which can control mmSolver's behaviour. The modified behaviour will be
for all users loading this module - if the module file is located on
the network for multiple users changes to this file will affect all
users.

| Name                       | Description                                                                                                           |
|----------------------------|-----------------------------------------------------------------------------------------------------------------------|
| MMSOLVER_LOAD_AT_STARTUP   | Automatically load mmSolver plug-in at Maya start-up (values of '0' or '1').                                          |
| MMSOLVER_CREATE_SHELF      | Automatically create a Maya shelf at start-up (values of '0' or '1').                                                 |
| MMSOLVER_CREATE_MENU       | Automatically create a Maya menu at start-up (values of '0' or '1').                                                  |
| MMSOLVER_CREATE_HOTKEY_SET | Automatically create a Maya hotkey set at start-up (values of '0' or '1').                                            |
| MMSOLVER_VIEWPORT_MESSAGES | Enable or disable warnings and errors printed to the viewport (values of '0' or '1').                                 |
| MMSOLVER_HELP_SOURCE       | Prefer 'internet' or 'local' source of help? For users with internet restrictions set this to 'local'.                |
| MMSOLVER_DEFAULT_SOLVER    | (Advanced) The default solver to use in mmSolver; 'cminpack_lmdif', 'cminpack_lmder', 'ceres_lmdif' or 'ceres_lmder'. |
| MMSOLVER_DEBUG             | (Advanced) Forces mmSolver to print out debug messages. Not for users, for use by developers only.                    |
| MMSOLVER_LOCATION          | Do not change this variable!!!                                                                                        |

# Install 3DEqualizer Files

To install the 3DEqualizer (3DE) tools for *mmSolver*, follow the steps below.

The 3DEqualizer tools are for integration into workflows using
3DEqualizer. These tools have been tested with *3DEqualizer4 Release 5*,
but may work with older versions.

There are currently three 3DEqualizer tools available:

| File Name                 | Tool Name                       |
| ------------------------- | ------------------------------- |
| copy_track_mmsolver.py    | Copy 2D Tracks (MM Solver)      |
| export_track_mmsolver.py  | Export 2D Tracks (MM Solver)... |
| import_tracks_mmsolver.py | Import 2D Tracks (MM Solver)... |
| paste_camera_mmsolver.py  | Paste Camera (MM Solver)...     |

## Script Database

For 3DEqualizer versions supporting the online
[Script Database](https://www.3dequalizer.com/?site=scriptdb), you may
install the latest tools via the menu '3DE4 > Python > ScriptDB Installer'.

See this [video tutorial](https://www.youtube.com/watch?v=gVr_Fo1xh0E)
for an example of installing scripts with ScriptDB.

## Home Directory

Alternatively, you may install scripts manually by copying the
3DEqualizer python scripts in the `3dequalizer` sub-directory into the
`~/.3dequalizer/py_scripts` directory.

On Linux:
```commandline
$ cd <module directory>
$ cp ./3dequalizer/* ~/.3dequalizer/py_scripts
```

On Windows:
```cmd
> CD <module directory>
> XCOPY 3dequalizer\* "%AppData%\.3dequalizer\py_scripts" /Y
```

# Install SynthEyes Files

To install the SynthEyes tools for *mmSolver*, copy the files inside
the `<module root>/syntheyes` directory, into the custom SynthEyes
script directory.

On Windows:
```cmd
> CD <module directory>
> XCOPY syntheyes\* "%AppData%\SynthEyes\scripts" /Y
```

For example, this path:
```
C:\Users\<Your User Name>\AppData\Roaming\SynthEyes\scripts
```

The tool can be accessed as a standard export script in the menu
`File > Export > Trackers (mmSolver)`. This tool will export all
Tracks in the scene as .uv file format, ready to be imported into
mmSolver.

# Install Blender Add-On

Starting with mmSolver v0.3.15 a Blender Add-On (.zip file) is
included in the 'blender' directory.

If you wish to use Blender's 2D tracking featurs along with mmSolver
please see the documentation for installation and usage tips:
https://david-cattermole.github.io/mayaMatchMoveSolver/tools_inputoutput.html#copy-2d-tracks-from-blender
