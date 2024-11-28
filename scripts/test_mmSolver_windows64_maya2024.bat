@ECHO OFF
SETLOCAL
::
:: Copyright (C) 2024 David Cattermole.
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
:: Runs tests via the Maya Python Interpreter.
::
:: NOTE: This file is intended as a short-cut rather than having to
:: find and type the full path to 'mayapy.exe' on Windows. On Linux,
:: `mayapy` should be set for your environment (assuming you have an
:: environment managed).


:: The root of this project.
SET PROJECT_ROOT=%CD%
ECHO Project Root: %PROJECT_ROOT%

:: Path to Maya Python interpreter.
SET MAYA_EXE="%PROGRAMFILES%\Autodesk\Maya2024\bin\mayapy.exe"

:: Run tests.
%MAYA_EXE% %PROJECT_ROOT%\tests\runTests.py %*
if errorlevel 1 goto tests_failed

:: Successful return.
exit /b 0

:tests_failed
echo mmSolver tests failed!
exit /b 1
