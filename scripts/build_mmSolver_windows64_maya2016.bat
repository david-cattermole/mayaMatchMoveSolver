@ECHO OFF
SETLOCAL
::
:: Copyright (C) 2019 David Cattermole.
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
:: If you're not using Maya 2016 or have a non-standard install location,
:: set these variables here.
::
:: Note: Do not enclose the MAYA_VERSION in quotes, it will
::       lead to tears.
SET MAYA_VERSION=2016
SET MAYA_LOCATION="C:\Program Files\Autodesk\Maya2016"

:: Clear all build information before re-compiling.
:: Turn this off when wanting to make small changes and recompile.
SET FRESH_BUILD=1

:: Run the Python API and Solver tests inside Maya, after a
:: successfully build an install process.
SET RUN_TESTS=0

:: Use CMinpack?
:: CMinpack is the recommended solving library.
SET WITH_CMINPACK=1

:: WARNING: Would you like to use GPL-licensed code? If so you will
:: not be able to distribute
SET WITH_GPL_CODE=0

:: Where to install the module?
::
:: Note: In Windows 8 and 10, "My Documents" is no longer visible,
::       however files copying to "My Documents" automatically go
::       to the "Documents" directory.
::
:: The "$HOME/maya/2016/modules" directory is automatically searched
:: for Maya module (.mod) files. Therefore we can install directly.
::
:: SET INSTALL_MODULE_DIR="%PROJECT_ROOT%\modules"
SET INSTALL_MODULE_DIR="%USERPROFILE%\My Documents\maya\%MAYA_VERSION%\modules"

:: Build ZIP Package.
:: For developer use. Make ZIP packages ready to distribute to others.
SET BUILD_PACKAGE=1


:: Do not edit below, unless you know what you're doing.
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:: What type of build? "Release" or "Debug"?
SET BUILD_TYPE=Release

:: Build options, to allow faster compilation times. (not to be used by
:: users wanting to build this project.)
SET BUILD_PLUGIN=1
SET BUILD_PYTHON=1
SET BUILD_MEL=1
SET BUILD_QT_UI=1
SET BUILD_DOCS=1
SET BUILD_ICONS=1
SET BUILD_CONFIG=1
SET BUILD_TESTS=1

:: To Generate a Visual Studio 'Solution' file, change the '0' to a '1'.
SET GENERATE_SOLUTION=0

:: The root of this project.
SET PROJECT_ROOT=%CD%
ECHO Project Root: %PROJECT_ROOT%

:: Build plugin
MKDIR build_windows64_maya%MAYA_VERSION%_%BUILD_TYPE%
CHDIR build_windows64_maya%MAYA_VERSION%_%BUILD_TYPE%
IF "%FRESH_BUILD%"=="1" (
    DEL /S /Q *
    FOR /D %%G in ("*") DO RMDIR /S /Q "%%~nxG"
)

IF "%GENERATE_SOLUTION%"=="1" (

REM For Maya 2018 (which uses Visual Studio 2015)
REM cmake -G "Visual Studio 14 2015 Win64" -T "v140"

REM To Generate a Visual Studio 'Solution' file
    cmake -G "Visual Studio 11 2012 Win64" -T "v110" ^
        -DMAYA_VERSION=%MAYA_VERSION% ^
        -DUSE_GPL_LEVMAR=%WITH_GPL_CODE% ^
        -DUSE_CMINPACK=%WITH_CMINPACK% ^
        -DCMINPACK_ROOT="%PROJECT_ROOT%\external\install\cminpack" ^
        -DLEVMAR_ROOT="%PROJECT_ROOT%\external\install\levmar" ^
        -DMAYA_LOCATION=%MAYA_LOCATION% ^
        -DMAYA_VERSION=%MAYA_VERSION% ^
        ..

) ELSE (

    cmake -G Ninja ^
        -DCMAKE_BUILD_TYPE=%BUILD_TYPE% ^
        -DCMAKE_INSTALL_PREFIX=%INSTALL_MODULE_DIR% ^
        -DBUILD_PLUGIN=%BUILD_PLUGIN% ^
        -DBUILD_PYTHON=%BUILD_PYTHON% ^
        -DBUILD_MEL=%BUILD_MEL% ^
        -DBUILD_QT_UI=%BUILD_QT_UI% ^
        -DBUILD_DOCS=%BUILD_DOCS% ^
        -DBUILD_ICONS=%BUILD_ICONS% ^
        -DBUILD_CONFIG=%BUILD_CONFIG% ^
        -DBUILD_TESTS=%BUILD_TESTS% ^
        -DUSE_GPL_LEVMAR=%WITH_GPL_CODE% ^
        -DUSE_CMINPACK=%WITH_CMINPACK% ^
        -DCMINPACK_ROOT="%PROJECT_ROOT%\external\install\cminpack" ^
        -DLEVMAR_ROOT="%PROJECT_ROOT%\external\install\levmar" ^
        -DMAYA_LOCATION=%MAYA_LOCATION% ^
        -DMAYA_VERSION=%MAYA_VERSION% ^
        ..

    cmake --build . --parallel 4

REM Comment this line out to stop the automatic install into the home directory.
    cmake --install .

REM Run tests
    IF "%RUN_TESTS%"=="1" (
        cmake --build . --target test
    )

REM Create a .zip package.
IF "%BUILD_PACKAGE%"=="1" (
       cmake --build . --target package
   )

)

:: Return back project root directory.
CHDIR "%PROJECT_ROOT%"
