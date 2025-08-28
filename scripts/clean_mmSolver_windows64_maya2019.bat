@ECHO OFF
SETLOCAL
::
:: Copyright (C) 2025 David Cattermole.
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
:: Cleans the Maya MatchMove Solver build directories.

:: Build location - where to clean the project build files.
::
:: Defaults to %PROJECT_ROOT%\..\build_repro if not set.
IF "%BUILD_DIR_BASE%"=="" SET BUILD_DIR_BASE=%CD%\..

:: Maya version
SET MAYA_VERSION=2019

CALL "%~dp0internal\clean_mmSolver_windows64.bat"