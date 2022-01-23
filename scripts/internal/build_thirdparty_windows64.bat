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
:: Builds the libmv libraries.

:: The root of this project.
SET THIS_DIR=%~dp0
SET ROOT=%THIS_DIR%..\external\
ECHO Package Root: %ROOT%
CHDIR %ROOT%

SET INSTALL_DIR="%ROOT%\install\maya%MAYA_VERSION%_windows64"
SET SOURCE_DIR="%ROOT%"
SET CXX_STANDARD=11

:: NOTE: The working directory is placed in the root 'C' drive, to
:: minimise the file path length, as we may get up to 250 characters
:: long, which is a limitation of Windows.
::
:: SET WORKING_DIR="%ROOT%\working\maya%MAYA_VERSION%_windows64"
SET WORKING_DIR="C:\build_mmSolver_maya%MAYA_VERSION%_windows64"

:: Build plugin
CHDIR %WORKING_DIR%
MKDIR build
CHDIR build
DEL /S /Q *
FOR /D %%G in ("*") DO RMDIR /S /Q "%%~nxG"

%CMAKE_EXE% -G "NMake Makefiles" ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DCMAKE_CXX_STANDARD=%CXX_STANDARD% ^
    -DTHIRDPARTY_BASE_INSTALL_DIR=%INSTALL_DIR% ^
    -DTHIRDPARTY_BASE_WORKING_DIR=%WORKING_DIR% ^
    %SOURCE_DIR%

%CMAKE_EXE% --build . --parallel 4
%CMAKE_EXE% --install .

:: Return back project root directory.
CHDIR "%ROOT%"
