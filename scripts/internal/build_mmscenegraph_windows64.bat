@ECHO OFF
::
:: Copyright (C) 2022 David Cattermole.
::
:: This file is part of mmSolver.
::
:: mmSolver is free software: you can redistribute it and/or modify it
:: under the terms of the GNU Lesser General Public License as
:: published by the Free Software Foundation, either version 3 of the
:: License, or (at your option) any later version.
::
:: mmSolver is distributed in the hope that it will be useful,
:: but WITHOUT ANY WARRANTY; without even the implied warranty of
:: MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
:: GNU Lesser General Public License for more details.
::
:: You should have received a copy of the GNU Lesser General Public License
:: along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
:: ---------------------------------------------------------------------
::
:: Build the mmscenegraph library.
::
:: NOTE: Do not call this script directly! This file should be called by
:: the build_mmSolver_windows64_mayaXXXX.bat files.
::
:: This file assumes the variables MAYA_VERSION and RUST_CARGO_EXE
:: have been set.

:: The root of this project.
SET PROJECT_ROOT=%CD%
ECHO Project Root: %PROJECT_ROOT%

:: What type of build? "Release" or "Debug"?
SET BUILD_TYPE=Release

SET RELEASE_FLAG=
SET BUILD_TYPE_DIR=debug
IF "%BUILD_TYPE%"=="Release" (
    SET RELEASE_FLAG=--release
    SET BUILD_TYPE_DIR=release
)

:: Where to find the mmSceneGraph Rust libraries and headers.
SET MMSCENEGRAPH_INSTALL_PATH=%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\mmscenegraph\
SET MMSCENEGRAPH_ROOT=%PROJECT_ROOT%\mmscenegraph
SET MMSCENEGRAPH_RUST_DIR=%MMSCENEGRAPH_ROOT%\rust
SET MMSCENEGRAPH_CPP_DIR=%MMSCENEGRAPH_ROOT%\cppbind
SET MMSCENEGRAPH_RUST_TARGET_DIR="%PROJECT_ROOT%\build_mmscenegraph_rust_windows64_maya%MAYA_VERSION%"
SET MMSCENEGRAPH_CPP_TARGET_DIR="%PROJECT_ROOT%\build_mmscenegraph_rust_windows64_maya%MAYA_VERSION%"
SET MMSCENEGRAPH_LIB_DIR="%MMSCENEGRAPH_CPP_TARGET_DIR%\%BUILD_TYPE_DIR%"
SET MMSCENEGRAPH_INCLUDE_DIR="%MMSCENEGRAPH_CPP_DIR%\include"

ECHO Building mmSceneGraph... (%MMSCENEGRAPH_ROOT%)

:: Install the needed 'cxxbridge.exe' command.
::
:: NOTE: When chaging this version number, make sure to update the
:: CXX version used in the C++ buildings, and all the build scripts
:: using this value:
:: './mmscenegraph/cppbind/Cargo.toml'
:: './scripts/internal/build_mmscenegraph_linux.bash'
%RUST_CARGO_EXE% install cxxbridge-cmd --version 1.0.62
SET MMSCENEGRAPH_CXXBRIDGE_EXE="%USERPROFILE%\.cargo\bin\cxxbridge.exe"

ECHO Building C++ Bindings... (%MMSCENEGRAPH_CPP_DIR%)
CHDIR "%MMSCENEGRAPH_CPP_DIR%"
:: Assumes 'cxxbridge' (cxxbridge-cmd) is installed.
ECHO Generating C++ Headers...
cxxbridge --header --output "%MMSCENEGRAPH_CPP_DIR%\include\mmscenegraph\_cxx.h"
%RUST_CARGO_EXE% build %RELEASE_FLAG% --target-dir "%MMSCENEGRAPH_CPP_TARGET_DIR%"

:: MinGW is a common install for developers on Windows and
:: if installed and used it will cause build conflicts and
:: errors, so we disable it.
SET IGNORE_INCLUDE_DIRECTORIES=""
IF EXIST "C:\MinGW" (
    SET IGNORE_INCLUDE_DIRECTORIES="C:\MinGW\bin;C:\MinGW\include"
)

:: Build project
CHDIR "%PROJECT_ROOT%"
SET BUILD_DIR_NAME=build_mmscenegraph_windows64_maya%MAYA_VERSION%_%BUILD_TYPE%
SET BUILD_DIR=%PROJECT_ROOT%\%BUILD_DIR_NAME%
ECHO BUILD_DIR_NAME: %BUILD_DIR_NAME%
ECHO BUILD_DIR: %BUILD_DIR%
MKDIR "%BUILD_DIR_NAME%"
CHDIR "%BUILD_DIR%"

%CMAKE_EXE% -G "NMake Makefiles" ^
    -DCMAKE_BUILD_TYPE=%BUILD_TYPE% ^
    -DCMAKE_INSTALL_PREFIX=%MMSCENEGRAPH_INSTALL_PATH% ^
    -DCMAKE_IGNORE_PATH=%IGNORE_INCLUDE_DIRECTORIES% ^
    -DCMAKE_CXX_STANDARD=%CXX_STANDARD% ^
    -DMMSCENEGRAPH_CXXBRIDGE_EXE=%MMSCENEGRAPH_BUILD_TESTS% ^
    -DMMSCENEGRAPH_BUILD_TESTS=%MMSCENEGRAPH_BUILD_TESTS% ^
    -DMMSCENEGRAPH_LIB_DIR=%MMSCENEGRAPH_LIB_DIR% ^
    -DMMSCENEGRAPH_INCLUDE_DIR=%MMSCENEGRAPH_INCLUDE_DIR% ^
    -DBUILD_SHARED_LIBS=OFF ^
    %MMSCENEGRAPH_ROOT%

%CMAKE_EXE% --build . --parallel 4
%CMAKE_EXE% --install .

:: Return back project root directory.
CHDIR "%PROJECT_ROOT%"
