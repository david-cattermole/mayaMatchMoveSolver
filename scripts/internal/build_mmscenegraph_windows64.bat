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

:: What directory to build the project in?
SET BUILD_DIR_BASE=%PROJECT_ROOT%\..

:: What type of build? "Release" or "Debug"?
SET BUILD_TYPE=Release

SET RELEASE_FLAG=
SET BUILD_TYPE_DIR=debug
IF "%BUILD_TYPE%"=="Release" (
    SET RELEASE_FLAG=--release
    SET BUILD_TYPE_DIR=release
)

:: Where to find the mmSceneGraph Rust libraries and headers.
SET MMSCENEGRAPH_INSTALL_PATH=%BUILD_DIR_BASE%\build_mmscenegraph\install\maya%MAYA_VERSION%_windows64\
SET MMSCENEGRAPH_ROOT=%PROJECT_ROOT%\mmscenegraph
SET MMSCENEGRAPH_RUST_DIR=%MMSCENEGRAPH_ROOT%\rust
SET MMSCENEGRAPH_CPP_DIR=%MMSCENEGRAPH_ROOT%\cppbind
SET MMSCENEGRAPH_RUST_TARGET_DIR="%BUILD_DIR_BASE%\build_mmscenegraph\rust_windows64_maya%MAYA_VERSION%"
SET MMSCENEGRAPH_CPP_TARGET_DIR="%BUILD_DIR_BASE%\build_mmscenegraph\rust_windows64_maya%MAYA_VERSION%"
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
%RUST_CARGO_EXE% install cxxbridge-cmd --version 1.0.75
SET MMSCENEGRAPH_CXXBRIDGE_EXE="%USERPROFILE%\.cargo\bin\cxxbridge.exe"

ECHO Building C++ Bindings... (%MMSCENEGRAPH_CPP_DIR%)
CHDIR "%MMSCENEGRAPH_CPP_DIR%"
:: Assumes 'cxxbridge' (cxxbridge-cmd) is installed.
ECHO Generating C++ Headers...
cxxbridge --header --output "%MMSCENEGRAPH_CPP_DIR%\include\mmscenegraph\_cxx.h"
if errorlevel 1 goto failed_to_generate_cpp_header

%RUST_CARGO_EXE% build %RELEASE_FLAG% --target-dir "%MMSCENEGRAPH_CPP_TARGET_DIR%"
if errorlevel 1 goto failed_to_build_rust

:: MinGW is a common install for developers on Windows and
:: if installed and used it will cause build conflicts and
:: errors, so we disable it.
SET IGNORE_INCLUDE_DIRECTORIES=""
IF EXIST "C:\MinGW" (
    SET IGNORE_INCLUDE_DIRECTORIES="C:\MinGW\bin;C:\MinGW\include"
)

:: Optionally use "NMake Makefiles" as the build system generator.
SET CMAKE_GENERATOR=Ninja

:: Build project
SET BUILD_DIR_NAME=cmake_win64_maya%MAYA_VERSION%_%BUILD_TYPE%
SET BUILD_DIR=%BUILD_DIR_BASE%\build_mmscenegraph\%BUILD_DIR_NAME%
ECHO BUILD_DIR_BASE: %BUILD_DIR_BASE%
ECHO BUILD_DIR_NAME: %BUILD_DIR_NAME%
ECHO BUILD_DIR: %BUILD_DIR%
CHDIR "%BUILD_DIR_BASE%"
MKDIR "build_mmscenegraph"
CHDIR "%BUILD_DIR_BASE%\build_mmscenegraph\"
MKDIR "%BUILD_DIR_NAME%"
CHDIR "%BUILD_DIR%"

%CMAKE_EXE% -G %CMAKE_GENERATOR% ^
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
if errorlevel 1 goto failed_to_generate_cpp

%CMAKE_EXE% --build . --parallel
if errorlevel 1 goto failed_to_build_cpp

%CMAKE_EXE% --install .
if errorlevel 1 goto failed_to_install_cpp

:: Return back project root directory.
CHDIR "%PROJECT_ROOT%"
exit /b 0

:failed_to_generate_cpp_header
echo Failed to Generate C++ header files from Rust.
exit /b 1

:failed_to_build_rust
echo Failed to build Rust code.
exit /b 1

:failed_to_generate_cpp
echo Failed to generate C++ build files.
exit /b 1

:failed_to_build_cpp
echo Failed to build C++ code.
exit /b 1

:failed_to_install_cpp
echo Failed to install C++ artifacts.
exit /b 1
