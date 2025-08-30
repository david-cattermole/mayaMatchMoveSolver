@ECHO OFF
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
:: Centralised build directory configuration for Windows builds.
::
:: This file defines all build directory names, paths, and patterns used
:: across the mmSolver build system. By centralising these definitions,
:: we ensure consistency and make it easier to maintain the build system.
::
:: NOTE: This file should be called by build scripts after MAYA_VERSION
:: has been set, as many paths depend on the Maya version.

:: Validate that MAYA_VERSION is set.
IF "%MAYA_VERSION%"=="" (
    ECHO WARNING: MAYA_VERSION not set when calling build_config_windows64.bat
    ECHO Some build directory paths may be incomplete.
)

:: Base build directory configuration.
::
:: Can be overridden by setting BUILD_DIR_BASE environment variable.
IF "%BUILD_DIR_BASE%"=="" SET BUILD_DIR_BASE=%CD%\..

:: Build directory names.
SET BUILD_MMSOLVER_DIR_NAME=build_mmsolver
SET BUILD_OCIO_DIR_NAME=build_opencolorio
SET BUILD_MMSOLVERLIBS_DIR_NAME=build_mmsolverlibs

:: Build directory base paths.
SET BUILD_MMSOLVER_DIR_BASE=%BUILD_DIR_BASE%\%BUILD_MMSOLVER_DIR_NAME%
SET BUILD_OCIO_DIR_BASE=%BUILD_DIR_BASE%\%BUILD_OCIO_DIR_NAME%
SET BUILD_MMSOLVERLIBS_DIR_BASE=%BUILD_DIR_BASE%\%BUILD_MMSOLVERLIBS_DIR_NAME%

:: Set default BUILD_TYPE if not already set.
IF "%BUILD_TYPE%"=="" SET BUILD_TYPE=Release

:: Build directory patterns.
SET BUILD_CMAKE_DIR_PATTERN=cmake_win64_maya%MAYA_VERSION%_%BUILD_TYPE%
SET BUILD_RUST_DIR_PATTERN=rust_windows64_maya%MAYA_VERSION%
SET BUILD_PYTHON_VENV_DIR_PATTERN=python_venv_windows64_maya%MAYA_VERSION%
SET BUILD_DOCS_DIR_PATTERN=docs_windows64_maya%MAYA_VERSION%

:: OCIO-specific patterns.
SET OCIO_INSTALL_DIR_PATTERN=install\maya%MAYA_VERSION%_windows64
SET OCIO_SOURCE_DIR_PATTERN=source\maya%MAYA_VERSION%_windows64

:: Derived paths.
SET BUILD_MMSOLVER_CMAKE_DIR=%BUILD_MMSOLVER_DIR_BASE%\%BUILD_CMAKE_DIR_PATTERN%
SET BUILD_MMSOLVER_RUST_DIR=%BUILD_MMSOLVER_DIR_BASE%\%BUILD_RUST_DIR_PATTERN%
SET BUILD_MMSOLVER_PYTHON_VENV_DIR=%BUILD_MMSOLVER_DIR_BASE%\%BUILD_PYTHON_VENV_DIR_PATTERN%
SET BUILD_DOCS_DIR_BASE=%BUILD_MMSOLVER_DIR_BASE%\%BUILD_DOCS_DIR_PATTERN%\

SET BUILD_OCIO_CMAKE_DIR=%BUILD_OCIO_DIR_BASE%\%BUILD_CMAKE_DIR_PATTERN%
SET BUILD_OCIO_INSTALL_DIR=%BUILD_OCIO_DIR_BASE%\%OCIO_INSTALL_DIR_PATTERN%\
SET BUILD_OCIO_SOURCE_DIR=%BUILD_OCIO_DIR_BASE%\%OCIO_SOURCE_DIR_PATTERN%

:: For backwards compatibility with existing scripts.
SET MMSOLVERLIBS_CPP_TARGET_DIR=%BUILD_MMSOLVER_RUST_DIR%
SET PYTHON_VIRTUAL_ENV_DIR_NAME=%BUILD_PYTHON_VENV_DIR_PATTERN%

:: Debug output when VERBOSE is set to 1.
IF "%VERBOSE%"=="1" (
    ECHO Build Config Windows:
    ECHO   BUILD_DIR_BASE: %BUILD_DIR_BASE%
    ECHO   BUILD_MMSOLVER_DIR_BASE: %BUILD_MMSOLVER_DIR_BASE%
    ECHO   BUILD_OCIO_DIR_BASE: %BUILD_OCIO_DIR_BASE%
    ECHO   BUILD_MMSOLVER_CMAKE_DIR: %BUILD_MMSOLVER_CMAKE_DIR%
    ECHO   BUILD_MMSOLVER_RUST_DIR: %BUILD_MMSOLVER_RUST_DIR%
    ECHO   BUILD_MMSOLVER_PYTHON_VENV_DIR: %BUILD_MMSOLVER_PYTHON_VENV_DIR%
    ECHO   BUILD_DOCS_DIR_BASE: %BUILD_DOCS_DIR_BASE%
)

:: Successful return.
exit /b 0
