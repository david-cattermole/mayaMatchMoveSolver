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
:: Wrapper script to build documentation with proper Python virtual environment.
::

:: Get the project root (one level up from docs directory).
SET PROJECT_ROOT=%~dp0..
CD /D "%PROJECT_ROOT%"

:: Activate the Python virtual environment for the specified Maya version.
CALL "%PROJECT_ROOT%\scripts\python_venv_activate_maya%MAYA_VERSION%.bat"
IF ERRORLEVEL 1 (
    ECHO ERROR: Failed to activate Python virtual environment!
    EXIT /B 1
)

:: Change back to docs directory.
CD /D "%PROJECT_ROOT%\docs"

:: Run the make command with environment variables.
make.bat html
