@ECHO OFF
SETLOCAL
::
:: Copyright (C) 2019, 2022 David Cattermole.
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
SET MAYA_VERSION=2022
SET MAYA_LOCATION="C:\Program Files\Autodesk\Maya2022"

:: Python executable - edit this to point to an explicit python executable file.
SET PYTHON_EXE=python
SET CMAKE_EXE=cmake

scripts\internal\build_thirdparty_windows64.bat
