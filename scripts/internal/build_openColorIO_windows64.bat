@ECHO OFF
::
:: Copyright (C) 2022, 2023, 2024 David Cattermole.
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
:: Builds the OpenColorIO project.
::
:: By default the minimal build is performed that will give us the
:: library.  This is not a "full" build with all features, bindings and
:: programs.
::
:: A static library is also preferred, to avoid shipping shared/dynamic
:: libraries with mmSolver (which is a pain when dealing with a
:: third-party studio's environment - it's easiest to embed everything
:: and be done with it).
::
:: This script is assumed to be called with a number of variables
:: already set:
::
:: - MAYA_VERSION
:: - MAYA_LOCATION
:: - PYTHON_EXE
:: - CMAKE_EXE
:: - CXX_STANDARD
:: - OPENCOLORIO_TARBALL_NAME
:: - OPENCOLORIO_TARBALL_EXTRACTED_DIR_NAME
::
:: NOTE: Do not call this script directly! This file should be called by
:: the build_mmSolver_windows64_mayaXXXX.bat files.

:: The root of this project.
SET PROJECT_ROOT=%CD%
ECHO Project Root: %PROJECT_ROOT%

:: What directory to build the project in?
::
:: Note: BUILD_DIR_BASE should already be set by the calling script.
:: If not, use default location.
IF "%BUILD_DIR_BASE%"=="" SET BUILD_DIR_BASE=%PROJECT_ROOT%\..
ECHO Build directory base: %BUILD_DIR_BASE%

:: Install directory.
SET OPENCOLORIO_INSTALL_PATH=%BUILD_DIR_BASE%\build_opencolorio\install\maya%MAYA_VERSION%_windows64\

:: What type of build? "Release" or "Debug"?
SET BUILD_TYPE=Release

:: Allows you to see the build command lines, to help debugging build
:: problems. Set to ON to enable, and OFF to disable.
SET MMSOLVER_BUILD_VERBOSE=OFF

:: Make sure source code archive is downloaded and exists.
SET SOURCE_TARBALL=%PROJECT_ROOT%\external\archives\%OPENCOLORIO_TARBALL_NAME%
IF NOT EXIST %SOURCE_TARBALL% (
    ECHO %SOURCE_TARBALL% does not exist.
    ECHO Please download the tar.gz file from https://github.com/AcademySoftwareFoundation/OpenColorIO/releases
    EXIT /b 1
)

SET EXTRACT_OUT_DIR=%PROJECT_ROOT%\external\working\maya%MAYA_VERSION%_windows64
IF NOT EXIST %EXTRACT_OUT_DIR% (
   ECHO %EXTRACT_OUT_DIR% does not exist, creating it...
   MKDIR %EXTRACT_OUT_DIR%
)
SET SOURCE_ROOT=%EXTRACT_OUT_DIR%\%OPENCOLORIO_TARBALL_EXTRACTED_DIR_NAME%\
IF NOT EXIST %SOURCE_ROOT% (
   ECHO %SOURCE_ROOT% does not exist, extracting tarball...
   :: The 'tar' command is unlikely to be available on Windows, so we
   :: use CMake because we know it has 'tar'.
   %CMAKE_EXE% -E chdir %EXTRACT_OUT_DIR% tar xf %SOURCE_TARBALL%
)


ECHO Building opencolorio... (%SOURCE_ROOT%)

:: MinGW is a common install for developers on Windows and
:: if installed and used it will cause build conflicts and
:: errors, so we disable it.
SET IGNORE_INCLUDE_DIRECTORIES=""
IF EXIST "C:\MinGW" (
    SET IGNORE_INCLUDE_DIRECTORIES="C:\MinGW\bin;C:\MinGW\include"
)

:: Optionally use "NMake Makefiles" as the build system generator.
SET CMAKE_GENERATOR=Ninja

:: Force the compilier to be MSVC's cl.exe, so that if other
:: compiliers are installed, CMake doesn't get confused and try to use
:: it (such as clang).
SET CMAKE_C_COMPILER=cl
SET CMAKE_CXX_COMPILER=cl

:: Build OpenColorIO project
SET BUILD_DIR_NAME=cmake_win64_maya%MAYA_VERSION%_%BUILD_TYPE%
SET BUILD_DIR=%BUILD_DIR_BASE%\build_opencolorio\%BUILD_DIR_NAME%
ECHO BUILD_DIR_BASE: %BUILD_DIR_BASE%
ECHO BUILD_DIR_NAME: %BUILD_DIR_NAME%
ECHO BUILD_DIR: %BUILD_DIR%
CHDIR "%BUILD_DIR_BASE%"
MKDIR "build_opencolorio"
CHDIR "%BUILD_DIR_BASE%\build_opencolorio\"
MKDIR "%BUILD_DIR_NAME%"
CHDIR "%BUILD_DIR%"

:: Renaming the library name and C++ namespace, is so that software
:: looking for the "regular" OpenColorIO will not conflict with the
:: mmSolver library.
SET MMSOLVER_OCIO_LIBNAME_SUFFIX="_mmSolver"
SET MMSOLVER_OCIO_NAMESPACE="OpenColorIO_mmSolver"

%CMAKE_EXE% -G %CMAKE_GENERATOR% ^
    -DBUILD_SHARED_LIBS=ON ^
    -DCMAKE_BUILD_TYPE=%BUILD_TYPE% ^
    -DCMAKE_INSTALL_PREFIX=%OPENCOLORIO_INSTALL_PATH% ^
    -DCMAKE_IGNORE_PATH=%IGNORE_INCLUDE_DIRECTORIES% ^
    -DCMAKE_C_COMPILER=%CMAKE_C_COMPILER% ^
    -DCMAKE_CXX_COMPILER=%CMAKE_CXX_COMPILER% ^
    -DCMAKE_CXX_STANDARD=%CXX_STANDARD% ^
    -DCMAKE_VERBOSE_MAKEFILE=%MMSOLVER_BUILD_VERBOSE% ^
    -DOCIO_INSTALL_EXT_PACKAGES=ALL ^
    -DOCIO_BUILD_APPS=OFF ^
    -DOCIO_USE_OIIO_FOR_APPS=OFF ^
    -DOCIO_BUILD_TESTS=OFF ^
    -DOCIO_BUILD_GPU_TESTS=OFF ^
    -DOCIO_BUILD_DOCS=OFF ^
    -DOCIO_BUILD_FROZEN_DOCS=OFF ^
    -DOCIO_BUILD_PYTHON=OFF ^
    -DOCIO_BUILD_OPENFX=OFF ^
    -DOCIO_USE_SSE=ON ^
    -DOCIO_LIBNAME_SUFFIX=%MMSOLVER_OCIO_LIBNAME_SUFFIX% ^
    -DOCIO_NAMESPACE=%MMSOLVER_OCIO_NAMESPACE% ^
    %SOURCE_ROOT%
IF errorlevel 1 GOTO failed_to_generate_cpp

%CMAKE_EXE% --build . --parallel
IF errorlevel 1 GOTO failed_to_build_cpp

%CMAKE_EXE% --install .
IF errorlevel 1 GOTO failed_to_install_cpp

:: Return back project root directory.
CHDIR "%PROJECT_ROOT%"
EXIT /b 0

:failed_to_generate_cpp_header
ECHO Failed to Generate C++ header files from Rust.
EXIT /b 1

:failed_to_build_rust
ECHO Failed to build Rust code.
EXIT /b 1

:failed_to_generate_cpp
ECHO Failed to generate C++ build files.
EXIT /b 1

:failed_to_build_cpp
ECHO Failed to build C++ code.
EXIT /b 1

:failed_to_install_cpp
ECHO Failed to install C++ artifacts.
EXIT /b 1
