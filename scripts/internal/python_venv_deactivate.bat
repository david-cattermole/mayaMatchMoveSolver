@ECHO OFF
::
:: Copyright (C) 2021 David Cattermole.
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
:: Deactivates the Python development environment for mmSolver.
::
:: Warning: This file expects the variable "PYTHON_VIRTUAL_ENV_DIR_NAME"
:: to be defined in the calling environment, if this is not done,
:: undefined behaviour will happen (likely an error).

SET PROJECT_ROOT=%CD%

:: Deactivate script.
SET PYTHON_VIRTUAL_ENV_DEACTIVATE_SCRIPT=%PYTHON_VIRTUAL_ENV_DIR_NAME%\Scripts\deactivate.bat

:: Deactivate Python virtual environment.
CALL %PYTHON_VIRTUAL_ENV_DEACTIVATE_SCRIPT%

:: Return back project root directory.
CHDIR "%PROJECT_ROOT%"