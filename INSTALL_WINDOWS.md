# Building on Microsoft Windows

Maya MatchMove Solver can be built on Microsoft Windows.

On Windows the only tested build method is with `levmar` only; ATLAS
and Intel MKL are untested.

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

# Build with levmar

Building with only `levmar` is the only supported and tested configuration
on Microsoft Windows.

To build on Windows, run these commands:
```cmd
> CD <project root>
> notepad build_with_levmar.bat  :: Edit path to Maya include / library
> CMD /C build_with_levmar.bat
```

NOTE: `notepad` is only an example, you may use whatever text
editor you wish.

NOTE: Replace ``<project root>`` as required.

Following the steps above you should have a compiled Maya plug-in.

Next we must install the plug-in and corresponding files, see
[INSTALL.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/INSTALL.md)
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
        -DUSE_ATLAS=0 ^
        -DUSE_MKL=0 ^
        -DMAYA_INCLUDE_PATH="C:\Program Files\Autodesk\Maya2017\include" ^
        -DMAYA_LIB_PATH="C:\Program Files\Autodesk\Maya2017\lib" ^
        -DLEVMAR_LIB_PATH="<project root>\external\lib" ^
        -DLEVMAR_INCLUDE_PATH="<project root>\external\include" ^
        ..
> NMAKE /F Makefile all
```

| CMake Option         | Description                                 |
| -------------------- | ------------------------------------------- |
| CMAKE_BUILD_TYPE     | The type of build (`Release`, `Debug`, etc) |
| MAYA_INCLUDE_PATH    | Directory to the Maya header include files  |
| MAYA_LIB_PATH        | Directory to the Maya library files         |
| LEVMAR_LIB_PATH      | Directory to levmar library                 |
| LEVMAR_INCLUDE_PATH  | Directory to levmar header includes         |
| USE_ATLAS            | Use ATLAS libraries?                        |
| ATLAS_LIB_PATH       | Directory to ATLAS libraries                |
| USE_MKL              | Use Intel MKL libraries?                    |
| MKL_LIB_PATH         | Directory to Intel MKL libraries            |

Setting ``USE_ATLAS`` and ``USE_MKL`` to ``1`` is an error, both
libraries provide the same functionality and both are not needed,
only one. If `ATLAS` and `Intel MKL` are not required you may set both
``USE_ATLAS`` and ``USE_MKL`` to ``0``.

You can read any of the build scripts to find out how they work.
The build scripts can be found in `<project root>/build_with_*.sh`
and `<project root>/external/*.sh`.
