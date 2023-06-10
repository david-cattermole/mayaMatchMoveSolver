@ECHO OFF
SETLOCAL
::
:: Copyright (C) 2019 David Cattermole.
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
SET MAYA_VERSION=2024
SET MAYA_LOCATION="C:\Program Files\Autodesk\Maya2024"

:: Executable names/paths used for build process.
SET PYTHON_EXE=python
SET CMAKE_EXE=cmake
SET RUST_CARGO_EXE=cargo

:: C++ Standard to use.
SET CXX_STANDARD=14

:: Setup Compiler environment. Change for your install path as needed.
CALL "C:\Program Files (x86)\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" amd64

:: These scripts assume 'RUST_CARGO_EXE' has been set to the Rust
:: 'cargo' executable.
CALL scripts\internal\build_rust_library_windows64.bat mmscenegraph
if errorlevel 1 goto failed_to_build_mmscenegraph

CALL scripts\internal\build_mmSolver_windows64.bat
if errorlevel 1 goto failed_to_build_mmsolver
exit /b 0

:failed_to_build_mmscenegraph
echo Failed to build MM Scene Graph.
exit /b 1

:failed_to_build_mmsolver
echo Failed to build MM Solver.
exit /b 1