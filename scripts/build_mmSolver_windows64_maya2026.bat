@ECHO OFF
SETLOCAL
::
:: Copyright (C) 2019, 2024 David Cattermole.
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
:: Builds the Maya MatchMove Solver project.

:: Maya directories
::
:: Note: Do not enclose the MAYA_VERSION in quotes, it will
::       lead to tears.
SET MAYA_VERSION=2026
SET MAYA_LOCATION="%PROGRAMFILES%\Autodesk\Maya2026"

:: Source centralized build configuration.
CALL "%CD%\scripts\internal\build_config_windows64.bat"

:: Executable names/paths used for build process.
SET PYTHON_EXE=python
SET CMAKE_EXE=cmake
SET RUST_CARGO_EXE=cargo

:: OpenColorIO specific options.
::
:: https://github.com/AcademySoftwareFoundation/OpenColorIO/releases/tag/v2.2.1
:: https://github.com/AcademySoftwareFoundation/OpenColorIO/archive/refs/tags/v2.2.1.tar.gz
SET OPENCOLORIO_TARBALL_NAME=OpenColorIO-2.2.1.tar.gz
SET OPENCOLORIO_TARBALL_EXTRACTED_DIR_NAME=OpenColorIO-2.2.1
SET EXPAT_RELATIVE_CMAKE_DIR=lib\cmake\expat-2.4.1\
SET EXPAT_RELATIVE_LIB_PATH=lib\expatMD.lib
SET ZLIB_RELATIVE_LIB_PATH=lib\zlibstatic.lib
SET MINIZIP_RELATIVE_CMAKE_DIR=lib\cmake\minizip-ng
:: yaml-cpp 0.7.0
SET YAML_RELATIVE_CMAKE_DIR=share\cmake\yaml-cpp\
SET YAML_RELATIVE_LIB_PATH=lib\yaml-cpp.lib
SET PYSTRING_RELATIVE_LIB_PATH=lib\pystring.lib

:: Which version of the VFX platform are we "using"? (Maya doesn't
:: currently conform to the VFX Platform.)
SET VFX_PLATFORM=2025

:: C++ Standard to use.
SET CXX_STANDARD=14

:: Setup Compiler environment. Change for your install path as needed.
CALL "%PROGRAMFILES%\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" amd64

CALL scripts\internal\build_opencolorio_windows64.bat
if errorlevel 1 goto failed_to_build_opencolorio

:: This script assumes 'RUST_CARGO_EXE' has been set to the Rust
:: 'cargo' executable.
CALL scripts\internal\build_mmSolver_windows64.bat
if errorlevel 1 goto failed_to_build_mmsolver

:: Successful return.
exit /b 0

:failed_to_build_opencolorio
echo Failed to build OpenColorIO dependency.
exit /b 1

:failed_to_build_mmsolver
echo Failed to build MM Solver.
exit /b 1
