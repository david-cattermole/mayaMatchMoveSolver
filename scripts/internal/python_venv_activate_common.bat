@ECHO OFF
SETLOCAL EnableDelayedExpansion
::
:: Copyright (C) 2021, 2024, 2025 David Cattermole.
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
:: Common Python virtual environment activation script for Windows.
::
:: This script expects MAYA_VERSION to be set before calling.
:: It reads configuration from scripts\config\maya_settings.py

:: Validate that MAYA_VERSION is set.
IF "%MAYA_VERSION%"=="" (
    echo ERROR: MAYA_VERSION must be set before calling this script
    exit /b 1
)

SET PROJECT_ROOT=%CD%

:: Use Python to get configuration settings.
SET PYTHON_CONFIG_SCRIPT=%PROJECT_ROOT%\scripts\config\maya_settings.py

IF NOT EXIST "%PYTHON_CONFIG_SCRIPT%" (
    echo ERROR: Configuration file not found: %PYTHON_CONFIG_SCRIPT%
    exit /b 1
)

:: Get settings using Python configuration.
FOR /F "usebackq tokens=1,2 delims==" %%A IN (`python -c "import sys; import os; sys.path.insert(0, os.path.join('%PROJECT_ROOT%', 'scripts', 'config')); from maya_settings import MayaConfig; config = MayaConfig('windows'); print('PYTHON_EXE=' + config.get_python_exe('%MAYA_VERSION%')); print('PYTHON_VIRTUAL_ENV_DIR_NAME=' + config.get_python_venv_dir_name('%MAYA_VERSION%'))"`) DO (
    IF "%%A"=="PYTHON_EXE" SET "PYTHON_EXE=%%B"
    IF "%%A"=="PYTHON_VIRTUAL_ENV_DIR_NAME" SET "PYTHON_VIRTUAL_ENV_DIR_NAME=%%B"
)

:: Validate required settings.
IF "%PYTHON_EXE%"=="" (
    echo ERROR: PYTHON_EXE not found for Maya version %MAYA_VERSION%
    exit /b 1
)

IF "%PYTHON_VIRTUAL_ENV_DIR_NAME%"=="" (
    echo ERROR: PYTHON_VIRTUAL_ENV_DIR_NAME not found for Maya version %MAYA_VERSION%
    exit /b 1
)

:: Print configuration for debugging.
echo Maya Version: %MAYA_VERSION%
echo Python Executable: %PYTHON_EXE%
echo Virtual Environment: %PYTHON_VIRTUAL_ENV_DIR_NAME%

:: Call the existing internal script.
CALL %PROJECT_ROOT%\scripts\internal\python_venv_activate.bat
