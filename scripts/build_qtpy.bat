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
:: Downloads and installs Qt.py file.

:: The root of this project.
SET THIS_DIR=%~dp0
SET ROOT=%THIS_DIR%..\external\
ECHO Package Root: %ROOT%
CHDIR %ROOT%

SET INSTALL_DIR="%ROOT%\install\qtpy"

:: Extract Qt.py
python "%THIS_DIR%get_qtpy.py" "%ROOT%\archives" "%ROOT%\working" "%ROOT%\patches"

:: Copy file to install
MKDIR "%INSTALL_DIR%"
COPY /Y /V "%ROOT%\working\Qt.py-1.1.0\Qt.py" "%INSTALL_DIR%\Qt.py"

:: Return back project root directory.
CHDIR "%ROOT%"
