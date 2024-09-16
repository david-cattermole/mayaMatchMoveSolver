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
:: Activates (and sets up) the Python development environment.
::
:: Warning: This file expects the variables "PYTHON_VIRTUAL_ENV_DIR_NAME"
:: and "PYTHON_EXE" to be defined in the calling environment, if this is
:: not done, undefined behaviour will happen (likely an error).

:: The root of this project.
SET PROJECT_ROOT=%CD%

:: What directory to build the environment in?
SET BASE_DIR=%PROJECT_ROOT%\..

:: Clear the currently generated Python virtual environment before
:: running the build process (including Python commands).
::
:: The generation of a Python Virtual Environment slow to run and should
:: be reused if possible; therefore leave this off for normal usage.
SET FRESH_PYTHON_VIRTUAL_ENV=0

:: Full directory path to environment.
SET PYTHON_VIRTUAL_ENV_DIR=%BASE_DIR%\%PYTHON_VIRTUAL_ENV_DIR_NAME%

:: Activate script file name.
SET PYTHON_VIRTUAL_ENV_ACTIVATE_SCRIPT=%PYTHON_VIRTUAL_ENV_DIR%\Scripts\activate.bat

:: Delete any existing Python virtual environment, if it exists.
IF "%FRESH_PYTHON_VIRTUAL_ENV%"=="1" (
    CHDIR %BASE_DIR%
    MKDIR %PYTHON_VIRTUAL_ENV_DIR_NAME%
    CHDIR %PYTHON_VIRTUAL_ENV_DIR%
    DEL /S /Q *
    FOR /D %%G in ("*") DO RMDIR /S /Q "%%~nxG"
)

:: Ensure Python Virtual Environment is setup.
SET REQUIRE_PACKAGE_INSTALL=0
IF NOT EXIST %PYTHON_VIRTUAL_ENV_ACTIVATE_SCRIPT% (
    ECHO Setting up Python Virtual Environment "%PYTHON_VIRTUAL_ENV_DIR_NAME%"
    %PYTHON_EXE% --version
    %PYTHON_EXE% -m venv %PYTHON_VIRTUAL_ENV_DIR%
    SET REQUIRE_PACKAGE_INSTALL=1
)

:: Activate!
ECHO Activating Python Virtual Environment "%PYTHON_VIRTUAL_ENV_DIR_NAME%"
CALL %PYTHON_VIRTUAL_ENV_ACTIVATE_SCRIPT%

:: Install requirements
SET MAYA_VERSION_REQUIRE_FILE=%PROJECT_ROOT%\share\python_requirements\requirements-maya%MAYA_VERSION%.txt
IF "%REQUIRE_PACKAGE_INSTALL%"=="1" (
    %PYTHON_EXE% --version
    :: TODO: Why is the PIP upgrade disabled on Windows? On Linux it's very important.
    :: %PYTHON_EXE% -m pip install --upgrade pip
    %PYTHON_EXE% -m pip install -r %MAYA_VERSION_REQUIRE_FILE%
)

:: Return back project root directory.
CHDIR "%PROJECT_ROOT%"
