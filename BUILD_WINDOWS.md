# Building on Microsoft Windows

Maya MatchMove Solver can be built on Microsoft Windows. We have provided a
Windows Batch build script and CMake script which are configurable and readable.

To use the pre-made build scripts, you can use the following commands
to build the entire project and dependencies:

On Windows:
```cmd
> CD <project root>
> scripts\build_mmSolver_windows64_mayaXXXX.bat
```

Note: Replace XXXX, with the Maya version to build for.

The sections below explain the process in more detail.

# Windows Command Prompt

All commands in this install guide are assumed to be run
inside a Windows Command Prompt, with Visual Studio environment
variables set.

For example, from the Start Menu on Microsoft Windows 10, go to
`Programs (list) > Microsoft Visual Studio 2012 > VS2012 x64 Cross Tools Command Prompt`.
This will open a Command Prompt for you to type commands below.

It is *important* you use the `x64` Command Prompt, *not*
`Developer`, `x86` or `ARM`.

# Building Dependencies

mmSolver has a few dependencies, and are listed in
[BUILD.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/BUILD.md#dependencies).

The third-party dependencies are downloaded and built for
mmSolver automatically using the standard build script
`<project root>/scripts/build_mmSolver_windows64_mayaXXXX.bat`
(see below).

Using the CMake configuration, you can override the third-party
dependencies Git repositories URLs as needed - use `cmake-gui` to see
and configure the CMake variables.

# Build mmSolver

Run these commands, on Windows:
```cmd
> CD <project root>
> scripts\build_mmSolver_windows64_mayaXXXX.bat

# Run tests (optional, but encouraged)
> CD <project root>
> "C:\Program Files\Autodesk\MayaVERSION\bin\mayapy.exe" tests\runTests.py > tests.log
```

Note: Replace XXXX, with the Maya version to build for.

Following the steps above you will have the Maya plug-in compiled, and
installed into your `%USERPROFILE%\maya\MAYA_VERSION\modules` directory.

# Customizing Build Location

By default, mmSolver will build in the directory `%PROJECT_ROOT%\..`
(a subfolder in the parent directory of your project root). You can
override this location by setting the `BUILD_DIR_BASE` environment
variable before running the build script:

```cmd
:: Set a custom build directory
> SET BUILD_DIR_BASE=D:\custom\build\path
> scripts\build_mmSolver_windows64_maya2024.bat
```

Setting a custom build directory can be useful when:

- You want to keep build files on a different disk drive.
- You're building multiple versions and want separate build
  directories.
- You have limited space in the default location.

# Run Test Suite

If you use the build script, you can automatically run the test suite
after compiling and installing. Make sure to turn on the variable
`RUN_TESTS` in the `.bash` or `.bat` scripts.

After all parts of the `mmSolver` are installed and can be found by
Maya, try running the test suite to confirm everything is working as
expected.

On Windows:
```cmd
> CD <project root>
> "C:\Program Files\Autodesk\MayaVERSION\bin\mayapy.exe" tests\runTests.py > tests.log
```

Make sure you use the same Maya version 'mayapy' for testing as you
have build for.

**Note:** On Windows, 'cmd.exe' is very slow printing text to the console,
therefore redirecting to a log file ('> file.log' below) will improve
performance of the test suite greatly.

For more information about testing, see the Testing section in
[DEVELOPER.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/DEVELOPER.md).

# Build Release Packages from Scratch

If you wish to build a (.zip) package for users to download, there
are a number of steps to ensure are run correctly in specific
environments. The commands below are one-liner commands to set up
everything from scratch and build, then package.

The directories below are hard-coded for the author's computer, you
may need to change the paths for your environment.

Run in the Git Bash terminal for Windows:
```commandline
# Maya 2016
$ mkdir -p ~/dev/mayaMatchMoveSolver_maya2016Deploy_windows64 ; cd ~/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2016Deploy_windows64
$ cd ~/dev/mayaMatchMoveSolver_maya2016Deploy_windows64/; git fetch --all; git checkout -f develop; git reset --hard HEAD ; git pull; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ;

# Maya 2017
$ mkdir -p ~/dev/mayaMatchMoveSolver_maya2017Deploy_windows64 ; cd ~/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2017Deploy_windows64
$ cd ~/dev/mayaMatchMoveSolver_maya2017Deploy_windows64/; git fetch --all; git checkout -f develop; git reset --hard HEAD ; git pull; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ;

# Maya 2018
$ mkdir -p ~/dev/mayaMatchMoveSolver_maya2018Deploy_windows64 ; cd ~/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2018Deploy_windows64
$ cd ~/dev/mayaMatchMoveSolver_maya2018Deploy_windows64/; git fetch --all; git checkout -f develop; git reset --hard HEAD ; git pull; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ;

# Maya 2019
$ mkdir -p ~/dev/mayaMatchMoveSolver_maya2019Deploy_windows64 ; cd ~/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2019Deploy_windows64
$ cd ~/dev/mayaMatchMoveSolver_maya2019Deploy_windows64/; git fetch --all; git checkout -f develop; git reset --hard HEAD ; git pull ; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ;

# Maya 2020
$ mkdir -p ~/dev/mayaMatchMoveSolver_maya2020Deploy_windows64 ; cd ~/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2020Deploy_windows64
$ cd ~/dev/mayaMatchMoveSolver_maya2020Deploy_windows64/; git fetch --all; git checkout -f develop; git reset --hard HEAD ; git pull ; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ;

# Maya 2022
$ mkdir -p ~/dev/mayaMatchMoveSolver_maya2022Deploy_windows64 ; cd ~/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2022Deploy_windows64
$ cd ~/dev/mayaMatchMoveSolver_maya2022Deploy_windows64/; git fetch --all; git checkout -f develop; git reset --hard HEAD ; git pull ; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ;

# Maya 2023
$ mkdir -p ~/dev/mayaMatchMoveSolver_maya2023Deploy_windows64 ; cd ~/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2023Deploy_windows64
$ cd ~/dev/mayaMatchMoveSolver_maya2023Deploy_windows64/; git fetch --all; git checkout -f develop; git reset --hard HEAD ; git pull ; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ;

# Maya 2024
$ mkdir -p ~/dev/mayaMatchMoveSolver_maya2024Deploy_windows64 ; cd ~/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2024Deploy_windows64
$ cd ~/dev/mayaMatchMoveSolver_maya2024Deploy_windows64/; git fetch --all; git checkout -f develop; git reset --hard HEAD ; git pull ; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ;
```

Run in the Windows Command Prompt:
```cmd
REM Maya 2016 - Visual Studio 2012
> cd %userprofile%\dev\mayaMatchMoveSolver_maya2016Deploy_windows64 && scripts\build_mmSolver_windows64_maya2016.bat

REM Maya 2017 - Visual Studio 2012
> cd %userprofile%\dev\mayaMatchMoveSolver_maya2017Deploy_windows64 && scripts\build_mmSolver_windows64_maya2017.bat

REM Maya 2018 - Visual Studio 2015:
> cd %userprofile%\dev\mayaMatchMoveSolver_maya2018Deploy_windows64 && scripts\build_mmSolver_windows64_maya2018.bat

REM Maya 2019 - Visual Studio 2015:
> cd %userprofile%\dev\mayaMatchMoveSolver_maya2019Deploy_windows64 && scripts\build_mmSolver_windows64_maya2019.bat

REM Maya 2020 - Visual Studio 2017:
> cd %userprofile%\dev\mayaMatchMoveSolver_maya2020Deploy_windows64 && scripts\build_mmSolver_windows64_maya2020.bat

REM Maya 2022 - Visual Studio 2019:
> cd %userprofile%\dev\mayaMatchMoveSolver_maya2022Deploy_windows64 && scripts\build_mmSolver_windows64_maya2022.bat

REM Maya 2023 - Visual Studio 2019:
> cd %userprofile%\dev\mayaMatchMoveSolver_maya2023Deploy_windows64 && scripts\build_mmSolver_windows64_maya2023.bat

REM Maya 2024 - Visual Studio 2022:
> cd %userprofile%\dev\mayaMatchMoveSolver_maya2024Deploy_windows64 && scripts\build_mmSolver_windows64_maya2024.bat
```

NOTE: Starting in mmSolver v0.4.0, the Visual Studio compiler version
required for each Maya version will be automatically invoked. The path
for Visual Studio is assumed to be the default installation path, if
you use a different install path for Visual Studio, you may need to
edit the (.bat) build script.

Package files can then be uploaded from the
"%userprofile%\dev\mayaMatchMoveSolver_maya*Deploy_windows64\packages"
folder.
