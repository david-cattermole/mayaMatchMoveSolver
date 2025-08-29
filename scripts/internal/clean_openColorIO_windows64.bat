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
:: Internal script to clean OpenColorIO build directories.
::
:: NOTE: Do not call this script directly! This file should be called by
:: the clean_openColorIO_windows64_mayaXXXX.bat files.
::
:: This script assumes MAYA_VERSION has been set by the calling script.

:: Validate that MAYA_VERSION is set.
IF "%MAYA_VERSION%"=="" (
    ECHO ERROR: MAYA_VERSION environment variable is not set.
    ECHO This script should be called from a Maya version-specific wrapper script.
    EXIT /b 1
)

:: The root of this project.
SET PROJECT_ROOT=%CD%

:: Source centralised build configuration.
CALL "%PROJECT_ROOT%\scripts\internal\build_config_windows64.bat"

ECHO Cleaning OpenColorIO build directories for Maya %MAYA_VERSION%...
ECHO Build directory base: %BUILD_DIR_BASE%

:: Remove OpenColorIO-specific build directories for this Maya version.
SET BUILD_DIRS[0]=%BUILD_OCIO_CMAKE_WIN64_DIR%
SET BUILD_DIRS[1]=%BUILD_OCIO_INSTALL_WIN64_DIR%
SET BUILD_DIRS[2]=%BUILD_OCIO_SOURCE_WIN64_DIR%

:: TODO: Check this loop. It's probably easier to just do this
:: sequentially for each directory, there are only 3.
FOR /L %%i IN (0,1,2) DO (
    CALL SET "dir=%%BUILD_DIRS[%%i]%%"
    CALL ECHO Checking directory: %%dir%%
    IF EXIST "%%dir%%" (
        ECHO Removing directory: %%dir%%
        RMDIR /S /Q "%%dir%%"
    ) ELSE (
        ECHO Directory does not exist ^(skipping^): %%dir%%
    )
)

ECHO OpenColorIO build cleanup completed for Maya %MAYA_VERSION%.
