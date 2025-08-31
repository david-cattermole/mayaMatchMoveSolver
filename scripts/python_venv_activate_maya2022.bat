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
:: Activates the Python development environment for Maya 2022.

:: Set Maya version for the venv activation script.
SET MAYA_VERSION=2022

:: Set required variables for python_venv_activate.bat
SET PYTHON_EXE=python
SET PYTHON_VIRTUAL_ENV_DIR_NAME=python_venv_windows64_maya2022

:: Call the internal venv activation script directly.
CALL scripts\internal\python_venv_activate.bat
