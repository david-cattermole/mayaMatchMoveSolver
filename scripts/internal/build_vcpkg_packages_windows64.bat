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
:: Installs OpenBLAS and SuiteSparse (CHOLMOD) using vcpkg.
::
:: OpenBLAS is built single-threaded as a shared DLL.
:: SuiteSparse CHOLMOD is built without GPL components and without CUDA.
::
:: This script is assumed to be called with a number of variables
:: already set:
::
:: - MAYA_VERSION
:: - CMAKE_EXE
::
:: NOTE: Do not call this script directly! This file should be called by
:: the build_mmSolver_windows64_mayaXXXX.bat files.

:: The root of this project.
SET PROJECT_ROOT=%CD%
ECHO Project Root: %PROJECT_ROOT%

:: Source centralised build configuration.
CALL "%PROJECT_ROOT%\scripts\internal\build_config_windows64.bat"

:: Directory configuration handled by centralised build_config_windows64.bat.
ECHO Build vcpkg directory base: %BUILD_VCPKG_DIR_BASE%
ECHO vcpkg install path: %BUILD_VCPKG_INSTALL_DIR%

:: Set up vcpkg directory.
SET VCPKG_DIR=%BUILD_VCPKG_DIR_BASE%\vcpkg
IF NOT EXIST "%VCPKG_DIR%" (
    ECHO Cloning vcpkg...
    MKDIR "%BUILD_VCPKG_DIR_BASE%"
    git clone https://github.com/microsoft/vcpkg.git "%VCPKG_DIR%"
)

:: Bootstrap vcpkg if needed.
IF NOT EXIST "%VCPKG_DIR%\vcpkg.exe" (
    ECHO Bootstrapping vcpkg...
    CALL "%VCPKG_DIR%\bootstrap-vcpkg.bat" -disableMetrics
    IF errorlevel 1 GOTO failed_to_bootstrap_vcpkg
)

SET VCPKG_EXE=%VCPKG_DIR%\vcpkg.exe

:: Use the x64-windows triplet which builds shared DLLs with dynamic CRT
:: (matching Maya's CRT linkage).
SET VCPKG_TRIPLET=x64-windows

:: Install OpenBLAS (single-threaded, shared DLL).
::
:: The default OpenBLAS port in vcpkg builds without the 'threads'
:: feature, which gives us single-threaded code. The x64-windows triplet
:: builds shared DLLs.
ECHO Installing OpenBLAS via vcpkg...
%VCPKG_EXE% install openblas:%VCPKG_TRIPLET% ^
    --x-install-root="%BUILD_VCPKG_INSTALL_DIR%"
IF errorlevel 1 GOTO failed_to_install_openblas

:: Install SuiteSparse CHOLMOD (no GPL, no CUDA, shared DLL).
::
:: By installing suitesparse-cholmod without the 'gpl' feature on
:: the top-level suitesparse port, we get only LGPL-licensed
:: components. CUDA is also off by default.
ECHO Installing SuiteSparse CHOLMOD via vcpkg...
%VCPKG_EXE% install suitesparse-cholmod:%VCPKG_TRIPLET% ^
    --x-install-root="%BUILD_VCPKG_INSTALL_DIR%"
IF errorlevel 1 GOTO failed_to_install_suitesparse

ECHO vcpkg packages installed successfully.
ECHO Install root: %BUILD_VCPKG_INSTALL_DIR%

:: Return back project root directory.
CHDIR "%PROJECT_ROOT%"
EXIT /b 0

:failed_to_bootstrap_vcpkg
ECHO Failed to bootstrap vcpkg.
EXIT /b 1

:failed_to_install_openblas
ECHO Failed to install OpenBLAS via vcpkg.
EXIT /b 1

:failed_to_install_suitesparse
ECHO Failed to install SuiteSparse CHOLMOD via vcpkg.
EXIT /b 1
