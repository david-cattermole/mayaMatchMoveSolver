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
:: Internal script to clean mmSolver build directories.
::
:: NOTE: Do not call this script directly! This file should be called by
:: the clean_mmSolver_windows64_mayaXXXX.bat files.
::
:: This script assumes MAYA_VERSION has been set by the calling script.

:: Validate that MAYA_VERSION is set
IF "%MAYA_VERSION%"=="" (
    ECHO ERROR: MAYA_VERSION environment variable is not set.
    ECHO This script should be called from a Maya version-specific wrapper script.
    exit /b 1
)

:: The root of this project.
SET PROJECT_ROOT=%CD%

:: Source centralised build configuration.
CALL "%PROJECT_ROOT%\scripts\internal\build_config_windows64.bat"

ECHO Cleaning mmSolver build directories for Maya %MAYA_VERSION%...
ECHO Build directory base: %BUILD_DIR_BASE%

:: Remove mmSolver-specific build directories.
SET CMAKE_DIR=%BUILD_MMSOLVER_CMAKE_DIR%
SET PYTHON_VENV_DIR=%BUILD_MMSOLVER_PYTHON_VENV_DIR%
SET RUST_DIR=%BUILD_MMSOLVER_RUST_DIR%
SET DOCS_DIR=%BUILD_DOCS_DIR_BASE%

IF EXIST "%CMAKE_DIR%" (
    ECHO Removing directory: %CMAKE_DIR%
    RMDIR /S /Q "%CMAKE_DIR%"
) ELSE (
    ECHO Directory does not exist, skipping: %CMAKE_DIR%
)

IF EXIST "%PYTHON_VENV_DIR%" (
    ECHO Removing directory: %PYTHON_VENV_DIR%
    RMDIR /S /Q "%PYTHON_VENV_DIR%"
) ELSE (
    ECHO Directory does not exist, skipping: %PYTHON_VENV_DIR%
)

IF EXIST "%RUST_DIR%" (
    ECHO Removing directory: %RUST_DIR%
    RMDIR /S /Q "%RUST_DIR%"
) ELSE (
    ECHO Directory does not exist, skipping: %RUST_DIR%
)

IF EXIST "%DOCS_DIR%" (
    ECHO Removing directory: %DOCS_DIR%
    RMDIR /S /Q "%DOCS_DIR%"
) ELSE (
    ECHO Directory does not exist, skipping: %DOCS_DIR%
)


ECHO mmSolver build cleanup completed for Maya %MAYA_VERSION%.

:: Successful return.
exit /b 0
