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
:: Build the mmSolver plug-in.
::
:: NOTE: Do not call this script directly! This file should be called by
:: the build_mmSolver_windows64_mayaXXXX.bat files.
::
:: This file assumes the MAYA_VERSION and MAYA_LOCATION variables
:: have been set.

:: Run the Python API and Solver tests inside Maya, after a
:: successfully build an install process.
SET RUN_TESTS=0

:: Where to install the module?
::
:: Note: In Windows 8 and 10, "My Documents" is no longer visible,
::       however files copying to "My Documents" automatically go
::       to the "Documents" directory.
::
:: The "$HOME/maya/2018/modules" directory is automatically searched
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
SET BUILD_3DEQUALIZER=1
SET BUILD_SYNTHEYES=1
SET BUILD_BLENDER=1
SET BUILD_QT_UI=1
SET BUILD_DOCS=1
SET BUILD_ICONS=1
SET BUILD_CONFIG=1
SET BUILD_TESTS=0

:: The root of this project.
SET PROJECT_ROOT=%CD%
ECHO Project Root: %PROJECT_ROOT%

SET PYTHON_VIRTUAL_ENV_DIR_NAME=python_venv_windows64_maya%MAYA_VERSION%

:: Note: There is no need to deactivate the virtual environment because
:: this batch script is 'SETLOCAL' (see top of file) and therefore no
:: environment variables are leaked into the calling environment.
CALL %PROJECT_ROOT%\scripts\internal\python_venv_activate.bat

:: Paths for dependencies.
::
:: By default these paths will work if the "build_thirdparty.bat"
:: scripts have been run before this script.
SET CMINPACK_ROOT="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\cminpack"
SET CERES_ROOT="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\ceres"
SET CERES_DIR="%CERES_ROOT%\CMake"
SET CERES_INCLUDE_DIR="%CERES_ROOT%\include"
SET CERES_LIB_PATH="%CERES_ROOT%\lib"
SET Eigen3_DIR="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\eigen\share\eigen3\cmake"
SET EIGEN3_INCLUDE_DIR="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\eigen\include\eigen3"
SET OPENMVG_ROOT="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\openMVG"
SET OPENMVG_DIR="%OPENMVG_ROOT%\share\openMVG\cmake"
SET OPENMVG_INCLUDE_DIR="%OPENMVG_ROOT%\include"
SET OPENMVG_LIB_PATH="%OPENMVG_ROOT%\lib"
SET DLFCN_ROOT="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\dlfcn"
SET DLFCN_INCLUDE_DIR="%DLFCN_ROOT%\include"
SET DLFCN_LIB_PATH="%DLFCN_ROOT%\lib"
SET LDPK_ROOT="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\ldpk"
SET LDPK_INCLUDE_DIR="%LDPK_ROOT%\include"
SET LDPK_LIB_PATH="%LDPK_ROOT%\lib"
SET MMSCENEGRAPH_INSTALL_DIR="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\mmscenegraph"
SET MMSCENEGRAPH_CMAKE_CONFIG_DIR="%MMSCENEGRAPH_INSTALL_DIR%\lib\cmake\mmscenegraph"

:: MinGW is a common install for developers on Windows and
:: if installed and used it will cause build conflicts and
:: errors, so we disable it.
SET IGNORE_INCLUDE_DIRECTORIES=""
IF EXIST "C:\MinGW" (
    SET IGNORE_INCLUDE_DIRECTORIES="C:\MinGW\bin;C:\MinGW\include"
)

:: Optionally use "NMake Makefiles" as the build system generator.
SET CMAKE_GENERATOR=Ninja

:: Build project
SET BUILD_DIR_NAME=build_mmSolver_windows64_maya%MAYA_VERSION%_%BUILD_TYPE%
SET BUILD_DIR=%PROJECT_ROOT%\%BUILD_DIR_NAME%
ECHO BUILD_DIR_NAME: %BUILD_DIR_NAME%
ECHO BUILD_DIR: %BUILD_DIR%
MKDIR "%BUILD_DIR_NAME%"
CHDIR "%BUILD_DIR%"

%CMAKE_EXE% -G %CMAKE_GENERATOR% ^
    -DCMAKE_BUILD_TYPE=%BUILD_TYPE% ^
    -DCMAKE_INSTALL_PREFIX=%INSTALL_MODULE_DIR% ^
    -DCMAKE_IGNORE_PATH=%IGNORE_INCLUDE_DIRECTORIES% ^
    -DBUILD_PLUGIN=%BUILD_PLUGIN% ^
    -DBUILD_PYTHON=%BUILD_PYTHON% ^
    -DBUILD_MEL=%BUILD_MEL% ^
    -DBUILD_3DEQUALIZER=%BUILD_3DEQUALIZER% ^
    -DBUILD_SYNTHEYES=%BUILD_SYNTHEYES% ^
    -DBUILD_BLENDER=%BUILD_BLENDER% ^
    -DBUILD_QT_UI=%BUILD_QT_UI% ^
    -DBUILD_DOCS=%BUILD_DOCS% ^
    -DBUILD_ICONS=%BUILD_ICONS% ^
    -DBUILD_CONFIG=%BUILD_CONFIG% ^
    -DBUILD_TESTS=%BUILD_TESTS% ^
    -DCMINPACK_ROOT=%CMINPACK_ROOT% ^
    -DCeres_DIR=%CERES_DIR% ^
    -DEigen3_DIR=%Eigen3_DIR% ^
    -DEIGEN3_INCLUDE_DIR=%EIGEN3_INCLUDE_DIR% ^
    -DOpenMVG_DIR=%OPENMVG_DIR% ^
    -DLDPK_ROOT=%LDPK_ROOT% ^
    -DLDPK_INCLUDE_DIR=%LDPK_INCLUDE_DIR% ^
    -DLDPK_LIB_PATH=%LDPK_LIB_PATH% ^
    -DDLFCN_ROOT=%DLFCN_ROOT% ^
    -DDLFCN_INCLUDE_DIR=%DLFCN_INCLUDE_DIR% ^
    -DDLFCN_LIB_PATH=%DLFCN_LIB_PATH% ^
    -DMAYA_LOCATION=%MAYA_LOCATION% ^
    -DMAYA_VERSION=%MAYA_VERSION% ^
    -Dmmscenegraph_DIR=%MMSCENEGRAPH_CMAKE_CONFIG_DIR% ^
    ..
if errorlevel 1 goto failed_to_generate

%CMAKE_EXE% --build . --parallel 4
if errorlevel 1 goto failed_to_build

:: Comment this line out to stop the automatic install into the home directory.
%CMAKE_EXE% --install .
if errorlevel 1 goto failed_to_install

:: Run tests
IF "%RUN_TESTS%"=="1" (
    %CMAKE_EXE% --build . --target test
)

:: Create a .zip package.
IF "%BUILD_PACKAGE%"=="1" (
    %CMAKE_EXE% --build . --target package
    if errorlevel 1 goto failed_to_build_zip
)

:: Return back project root directory.
CHDIR "%PROJECT_ROOT%"
exit /b 0

:failed_to_generate
echo Failed to generate build files.
exit /b 1

:failed_to_build
echo Failed to build.
exit /b 1

:failed_to_install
echo Failed to install.
exit /b 1

:failed_to_build_zip
echo Failed to build the ZIP package file.
exit /b 1
