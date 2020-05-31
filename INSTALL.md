# Download

The ***Maya MatchMove Solver*** is available for the following
platforms and can be downloaded from the
[Releases](https://github.com/david-cattermole/mayaMatchMoveSolver/releases)
page on the GitHub [project page](https://github.com/david-cattermole/mayaMatchMoveSolver).

| Operating System  | Maya Version(s)             |
| ----------------- | --------------------------- |
| Linux             | Maya 2016, 2017, 2018, 2019 |
| Windows           | Maya 2016, 2017, 2018, 2019 |
| Mac OS X          | *Not Currently Supported*   |

Download the archive format (`.zip` or `.tar.gz`) for your Maya
version and operating system.

For a simple installation, **do not** install from the
`Source code (zip)` or `Source code (tar.gz)` archives. These archives
are for developers only.

# Install Qt.py (in a Home Environment)

*Maya MatchMove Solver* uses the very popular
[Qt.py](https://github.com/mottosso/Qt.py) project for it's
[Qt Framework](https://www.qt.io/) user interfaces.
Starting with mmSolver v0.2.0, `Qt.py` is installed with mmSolver, and
users do not need to install `Qt.py`.

# Install Qt.py (in a Professional Environment)

Starting with mmSolver v0.2.0, `Qt.py` is installed with mmSolver
pre-build packages on GitHub.
If `Qt.py` is already installed in your professional environment
(studio pipeline), you will not need to install it again.

To remove `Qt.py` from the installation delete the folder named
`python_qt` in the module directory.

***Warning:*** If you are installing *Maya MatchMove Solver* in a studio
production environment, *Qt.py* may already be installed. Installing a
custom version of *Qt.py* in to your home directory may override your
pipeline provided file and may cause unexpected problems. It is
recommended to check with your studio's Pipeline team **before**
installing any custom software.

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

***Note:*** Please remove the `<module root>/python_qt` directory, if
`Qt.py` is already installed, see the above note
*Install Qt.py (in a Professional Environment)*.

# Project Configuration

By default, the tool should work without trouble, but some individuals
may want extra customisation.

To make customisations, edit the Maya Module file (ending with `.mod`)
using a text editor. The following environment variables are defined
which can control mmSolver's behaviour.

| Name                       | Description                                                                                            |
| -------------------------- | ------------------------------------------------------------------------------------------------------ |
| MMSOLVER_LOAD_AT_STARTUP   | Automatically load mmSolver plug-in at Maya start-up.                                                  |
| MMSOLVER_CREATE_SHELF      | Automatically create a Maya shelf at start-up.                                                         |
| MMSOLVER_CREATE_MENU       | Automatically create a Maya menu at start-up.                                                          |
| MMSOLVER_CREATE_HOTKEY_SET | Automatically create a Maya hotkey set at start-up.                                                    |
| MMSOLVER_HELP_SOURCE       | Prefer 'internet' or 'local' source of help? For users with internet restrictions set this to 'local'. |
| MMSOLVER_DEFAULT_SOLVER    | (Advanced) The default solver to use in mmSolver; 'cminpack_lm' or 'levmar'.                           |
| MMSOLVER_DEBUG             | (Advanced) Forces mmSolver to print out debug messages. Not for users, for use by developers only.     |
| MMSOLVER_LOCATION          | Do not change this variable!!!                                                                         |

# Install 3DEqualizer Files

To install the 3DEqualizer (3DE) tools for *mmSolver*, follow the steps below.

The 3DEqualizer tools are for integration into workflows using
3DEqualizer. These tools have been tested with *3DEqualizer4 Release 5*,
but may work with older versions.

There are currently three 3DEqualizer tools available:

| File Name                | Tool Name                       |
| ------------------------ | ------------------------------- |
| copy_track_mmsolver.py   | Copy 2D Tracks (MM Solver)      |
| export_track_mmsolver.py | Export 2D Tracks (MM Solver)... |
| paste_camera_mmsolver.py | Paste Camera (MM Solver)...     |

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
