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
SET BUILD_MMSCENEGRAPH=1
SET BUILD_PYTHON=1
SET BUILD_MEL=1
SET BUILD_3DEQUALIZER=1
SET BUILD_SYNTHEYES=1
SET BUILD_BLENDER=1
SET BUILD_QT_UI=1
SET BUILD_DOCS=1
SET BUILD_ICONS=1
SET BUILD_CONFIG=1
SET BUILD_TESTS=1

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
SET CERES_ROOT="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\libmv"
SET CERES_INCLUDE_DIR="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\libmv\include\third_party\ceres\include"
SET CERES_LIB_PATH="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\libmv\lib"
SET LIBMV_ROOT="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\libmv"
SET EIGEN3_INCLUDE_DIR="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\eigen\include\eigen3"
SET GLOG_ROOT="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\libmv"
SET GLOG_INCLUDE_DIR="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\libmv\include\third_party\glog\src"
SET GLOG_LIB_PATH="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\libmv\lib"
SET GFLAGS_ROOT="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\libmv"
SET GFLAGS_INCLUDE_DIR="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\libmv\include\third_party\gflags"
SET GFLAGS_LIB_PATH="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\libmv\lib"
SET OPENMVG_ROOT="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\openMVG"
SET OPENMVG_INCLUDE_DIR="%OPENMVG_ROOT%\include"
SET OPENMVG_LIB_PATH="%OPENMVG_ROOT%\lib"
SET DLFCN_ROOT="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\dlfcn"
SET DLFCN_INCLUDE_DIR="%DLFCN_ROOT%\include"
SET DLFCN_LIB_PATH="%DLFCN_ROOT%\lib"
SET LDPK_ROOT="%PROJECT_ROOT%\external\install\maya%MAYA_VERSION%_windows64\ldpk"
SET LDPK_INCLUDE_DIR="%LDPK_ROOT%\include"
SET LDPK_LIB_PATH="%LDPK_ROOT%\lib"

:: Where to find the mmSceneGraph Rust libraries and headers.
SET MMSCENEGRAPH_RUST_DIR=%PROJECT_ROOT%\src\mmscenegraph\rust
SET MMSCENEGRAPH_CPP_DIR=%PROJECT_ROOT%\src\mmscenegraph\cppbind
SET MMSCENEGRAPH_RUST_BUILD_DIR="%MMSCENEGRAPH_CPP_DIR%\target\release"
SET MMSCENEGRAPH_INCLUDE_DIR="%MMSCENEGRAPH_CPP_DIR%\include"

:: MinGW is a common install for developers on Windows and
:: if installed and used it will cause build conflicts and
:: errors, so we disable it.
SET IGNORE_INCLUDE_DIRECTORIES=""
IF EXIST "C:\MinGW" (
    SET IGNORE_INCLUDE_DIRECTORIES="C:\MinGW\bin;C:\MinGW\include"
)

IF "%BUILD_MMSCENEGRAPH%"=="1" (
   ECHO Building mmSceneGraph...

   :: Install the needed 'cxxbridge.exe' command.
   ::
   :: NOTE: When chaging this version number, make sure to update the
   :: CXX version used in the C++ buildings, and all the build scripts
   :: using this value:
   :: './src/mmscenegraph/cppbind/Cargo.toml'
   :: './scripts/internal/build_mmSolver_linux.bash'
   cargo install cxxbridge-cmd --version 1.0.62

   ECHO Building Rust crate... (%MMSCENEGRAPH_RUST_DIR%)
   CHDIR "%MMSCENEGRAPH_RUST_DIR%"
   cargo build --release

   ECHO Building C++ Bindings... (%MMSCENEGRAPH_CPP_DIR%)
   CHDIR "%MMSCENEGRAPH_CPP_DIR%"
   :: Assumes 'cxxbridge' (cxxbridge-cmd) is installed.
   ECHO Generating C++ Headers...
   cxxbridge --header --output "%MMSCENEGRAPH_CPP_DIR%\include\mmscenegraph\_cxx.h"
   cargo build --release

   CHDIR "%PROJECT_ROOT%"
)

:: Build project
SET BUILD_DIR_NAME=build_windows64_maya%MAYA_VERSION%_%BUILD_TYPE%
SET BUILD_DIR=%PROJECT_ROOT%\%BUILD_DIR_NAME%
ECHO BUILD_DIR_NAME: %BUILD_DIR_NAME%
ECHO BUILD_DIR: %BUILD_DIR%
MKDIR "%BUILD_DIR_NAME%"
CHDIR "%BUILD_DIR%"

:: To Generate a Visual Studio 'Solution' file, for Maya 2018 (which
:: uses Visual Studio 2015), replace the cmake -G line with the following line:
::
:: cmake -G "Visual Studio 14 2015 Win64" -T "v140"

cmake -G "NMake Makefiles" ^
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
    -DLIBMV_ROOT=%LIBMV_ROOT% ^
    -DCMINPACK_ROOT=%CMINPACK_ROOT% ^
    -DCERES_ROOT=%CERES_ROOT% ^
    -DCERES_LIB_PATH=%CERES_LIB_PATH% ^
    -DCERES_INCLUDE_DIR=%CERES_INCLUDE_DIR% ^
    -DEIGEN3_INCLUDE_DIR=%EIGEN3_INCLUDE_DIR% ^
    -DGLOG_ROOT=%GLOG_ROOT% ^
    -DGLOG_INCLUDE_DIR=%GLOG_INCLUDE_DIR% ^
    -DGFLAGS_ROOT=%GFLAGS_ROOT% ^
    -DGFLAGS_INCLUDE_DIR=%GFLAGS_INCLUDE_DIR% ^
    -DOPENMVG_ROOT=%OPENMVG_ROOT% ^
    -DOPENMVG_INCLUDE_DIR=%OPENMVG_INCLUDE_DIR% ^
    -DOPENMVG_LIB_PATH=%OPENMVG_LIB_PATH% ^
    -DLDPK_ROOT=%LDPK_ROOT% ^
    -DLDPK_INCLUDE_DIR=%LDPK_INCLUDE_DIR% ^
    -DLDPK_LIB_PATH=%LDPK_LIB_PATH% ^
    -DDLFCN_ROOT=%DLFCN_ROOT% ^
    -DDLFCN_INCLUDE_DIR=%DLFCN_INCLUDE_DIR% ^
    -DDLFCN_LIB_PATH=%DLFCN_LIB_PATH% ^
    -DMAYA_LOCATION=%MAYA_LOCATION% ^
    -DMAYA_VERSION=%MAYA_VERSION% ^
    -DMMSCENEGRAPH_RUST_BUILD_DIR=%MMSCENEGRAPH_RUST_BUILD_DIR% ^
    -DMMSCENEGRAPH_INCLUDE_DIR=%MMSCENEGRAPH_INCLUDE_DIR% ^
    ..

cmake --build . --parallel 8

:: Comment this line out to stop the automatic install into the home directory.
cmake --install .

:: Run tests
IF "%RUN_TESTS%"=="1" (
    cmake --build . --target test
)

:: Create a .zip package.
IF "%BUILD_PACKAGE%"=="1" (
    cmake --build . --target package
)

:: Return back project root directory.
CHDIR "%PROJECT_ROOT%"
