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

:: Clear the currently generated Python virtual environment before
:: running the build process (including Python commands).
::
:: The generation of a Python Virtual Environment slow to run and should
:: be reused if possible; therefore leave this off for normal usage.
SET FRESH_PYTHON_VIRTUAL_ENV=0

:: Activate script file name.
SET PYTHON_VIRTUAL_ENV_ACTIVATE_SCRIPT=%PYTHON_VIRTUAL_ENV_DIR_NAME%\Scripts\activate.bat

:: Delete any existing Python virtual environment, if it exists.
IF "%FRESH_PYTHON_VIRTUAL_ENV%"=="1" (
    MKDIR %PYTHON_VIRTUAL_ENV_DIR_NAME%
    CHDIR %PYTHON_VIRTUAL_ENV_DIR_NAME%
    DEL /S /Q *
    FOR /D %%G in ("*") DO RMDIR /S /Q "%%~nxG"
    CHDIR "%PROJECT_ROOT%"
)

:: Ensure Python Virtual Environment is setup.
IF NOT EXIST %PYTHON_VIRTUAL_ENV_ACTIVATE_SCRIPT% (
    ECHO Setting up Python Virtual Environment
    %PYTHON_EXE% -m venv %PYTHON_VIRTUAL_ENV_DIR_NAME%
)

:: Activate!
ECHO Activating Python Virtual Environment "%PYTHON_VIRTUAL_ENV_DIR_NAME%"
CALL %PYTHON_VIRTUAL_ENV_ACTIVATE_SCRIPT%

:: Install requirements
python -m pip install -r %PROJECT_ROOT%\requirements-dev.txt

:: Return back project root directory.
CHDIR "%PROJECT_ROOT%"
