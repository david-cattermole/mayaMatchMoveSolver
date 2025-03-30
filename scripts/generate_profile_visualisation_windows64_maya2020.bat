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
:: Runs flamegraph generation via the Maya Python Interpreter.
::

:: The root of this project.
SET PROJECT_ROOT=%CD%
ECHO Project Root: %PROJECT_ROOT%

:: Path to Maya Python interpreter.
SET MAYA_EXE="%PROGRAMFILES%\Autodesk\Maya2020\bin\mayapy.exe"

:: Where are the profile files (.pstat)?
SET PROFILES_DIR="%PROJECT_ROOT%\tests\profile\"

rem :: Run generation to human readable.
rem call %PROJECT_ROOT%\scripts\internal\convert_pstats_to_human_readable.bat %MAYA_EXE% %PROFILES_DIR%
rem if errorlevel 1 goto generation_failed

:: Run generation to flamegraph.
call %PROJECT_ROOT%\scripts\internal\convert_pstats_to_flamegraph.bat %MAYA_EXE% %PROFILES_DIR%
if errorlevel 1 goto generation_failed


:: Successful return.
exit /b 0

:generation_failed
echo mmSolver flamegraph generation failed!
exit /b 1
