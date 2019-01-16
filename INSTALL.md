# Install Module

Maya MatchMove Solver ('mmSolver' for short) can be installed by
un-zipping the module (`.zip` or `.tar.gz`) file into the
following directory on your computer:

On Windows:
```
C:/Users/<Your User Name>/My Documents/maya/2017/modules
```

On Linux:
```
~/maya/2017/modules
```

# Install 3DEqualizer Files

To install the 3DEqualizer (3DE) tools for `mmSolver`, follow the steps below.
The 3DEqualizer tools are for integration into workflows using 3DEqualizer.
These tools have been tested with `3DEqualizer4 Release 5`.

There are currently two 3DEqualizer tools available:

| File Name                | Tool Name                                      |
| ------------------------ | ---------------------------------------------- |
| copy_track_mmsolver.py   | Copy 2D Tracks (MM Solver)                     |
| export_track_mmsolver.py | Export 2D Tracks (MM Solver)...                |

## Script Database

For 3DEqualizer versions supporting the online 
[Script Database](https://www.3dequalizer.com/?site=scriptdb), you may 
install the latest tools via the menu '3DE4 > Python > ScriptDB Installer'.

See this [video tutorial](https://www.youtube.com/watch?v=gVr_Fo1xh0E) for 
an example of installing scripts with ScriptDB. 

## Home Directory

Alternatively, you may install scripts manually by copying the 3DEqualizer python 
scripts in `<project root>/3dequalizer/scriptdb` into the `~/.3dequalizer/py_scripts` directory.

On Linux:
```commandline
$ cd <project root>
$ cp ./3dequalizer/scriptdb/* ~/.3dequalizer/py_scripts
```

On Windows:
```cmd
> CD <project root>
> XCOPY 3dequalizer/scriptdb/* "%AppData%/.3dequalizer/py_scripts" /Y
```
