# Building on Microsoft Windows

Maya MatchMove Solver can be built on Microsoft Windows.

On Windows the only tested build method is with `levmar` only; ATLAS
and Intel MKL methods are untested.

# Download Archives

You must download the archive packages manually and move them into a
specific directory. Once these archives are available, the build
script below will automatically unpack the archives as needed.

- levmar
  - URL: `http://users.ics.forth.gr/~lourakis/levmar/levmar-2.6.tgz`
  - MD5 hash: `16bc34efa1617219f241eef06427f13f`
  - Archive name: `levmar-2.6.tgz`

The downloaded `levmar-2.6.tgz` archive must be saved into the directory:

```
<project root>\external\archives\
```

# Windows Command Prompt

All commands in this install guide are assumed to be run
inside a Windows Command Prompt, with Visual Studio environment
variables set.

For example, from the Start Menu on Microsoft Windows 10, go to
`Programs (list) > Microsoft Visual Studio 2012 > VS2012 x64 Cross Tools Command Prompt`.
This will open a Command Prompt for you to type commands below.

It is *important* you use the `x64` Command Prompt, *not*
`Developer`, `x86` or `ARM`.

# Edit the Build Scripts

The build script `build_with_levmar.bat` will assume a default `Maya
2017` install directory. You will need to edit the build script with
your custom Maya include and library directories.

For example you will need to set the following variables in the `.bat`
file:

| Variable           | Description                             | Example                                                  |
| ------------       | -----------                             | -----------                                              |
| MAYA_VERSION       | Maya version to build for.              | `2017`                                                   |
| MAYA_INCLUDE_PATH  | Location for Maya header (.h) files.    | `C:\Program Files\Autodesk\Maya2017\include`             |
| MAYA_LIB_PATH      | Location for Maya library (.lib) files. | `C:\Program Files\Autodesk\Maya2017\lib`                 |
| INSTALL_MODULE_DIR | Directory to install the Maya module.   | `C:\Users\YOUR_USER_NAME\My Documents\maya\2017\modules` |

For developers, you may change the variable `GENERATE_SOLUTION` to
"1". This will build a Visual Studio solution file, ready to make
changes and compile interactively inside Visual Studio.

# Build with levmar

Building with only `levmar` is the only supported and tested configuration
on Microsoft Windows.

To build on Windows, run these commands:
```cmd
> CD <project root>
> CMD /C build_with_levmar.bat
```

NOTE: Replace ``<project root>`` as required.

Following the steps above you should have the Maya plug-in compiled,
and installed into your
`C:\Users\UserName\My Documents\maya\MAYA_VERSION\modules` directory.

For the next steps, see
[BUILD.md]([[https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/BUILD.md]])
 for more details.

# CMake Build Script

For those needing or wanting to compile the ``mmSolver`` Maya plug-in
manually you can do it easily using the following commands.

Example CMake usage on Windows:
```cmd
> CD <project root>
> MKDIR build
> CD build
> cmake -G "NMake Makefiles" ^
        -DCMAKE_BUILD_TYPE=Release ^
        -DCMAKE_INSTALL_PREFIX="C:\Users\MyUser\My Documents\maya\2017\modules" ^
        -DMAYA_VERSION="2017" ^
        -DMAYA_INCLUDE_PATH="C:\Program Files\Autodesk\Maya2017\include" ^
        -DMAYA_LIB_PATH="C:\Program Files\Autodesk\Maya2017\lib" ^
        -DLEVMAR_INCLUDE_PATH="<project root>\external\include" ^
        -DLEVMAR_LIB_PATH="<project root>\external\lib" ^
        -DUSE_ATLAS=0 ^
        -DUSE_MKL=0 ^
        ..
> NMAKE /F Makefile all
> NMAKE /F Makefile install
> NMAKE /F Makefile package
```

| CMake Option         | Description                                 |
| -------------------- | ------------------------------------------- |
| CMAKE_BUILD_TYPE     | The type of build (`Release`, `Debug`, etc) |
| CMAKE_INSTALL_PREFIX | Location to install the Maya module.        |
| MAYA_VERSION         | Maya version to build for.                  |
| MAYA_INCLUDE_PATH    | Directory to the Maya header include files  |
| MAYA_LIB_PATH        | Directory to the Maya library files         |
| LEVMAR_INCLUDE_PATH  | Directory to levmar header includes         |
| LEVMAR_LIB_PATH      | Directory to levmar library                 |
| USE_ATLAS            | Use ATLAS libraries?                        |
| USE_MKL              | Use Intel MKL libraries?                    |
| ATLAS_LIB_PATH       | (Unsupported on Windows)                    |
| MKL_LIB_PATH         | (Unsupported on Windows)                    |

Setting ``USE_ATLAS`` and ``USE_MKL`` to ``1`` is an error, both
libraries provide the same functionality and both are not needed,
only one. If `ATLAS` and `Intel MKL` are not required you may set both
``USE_ATLAS`` and ``USE_MKL`` to ``0``.

You can read any of the build scripts to find out how they work.
The build scripts can be found in `<project root>/build_with_*.sh`
and `<project root>/external/*.sh`.

# Building Packages

For developers wanting to produce a pre-compiled archive "package",
simply add the following line, after `nmake /F Makefile install` in
the `build_with_levmar.bat` build script:

```cmd
nmake /F Makefile package
```

And re-run the `build_with_levmar.bat` script. This will re-compile
the project, then copy all scripts and plug-ins into a `.zip` file,
ready for distribution to users.
