@ECHO OFF
SETLOCAL enabledelayedexpansion
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
:: Converts Python pstat files to a human readable text file.
::
:: > convert_pstats_to_human_readable.bat "C:\Program Files\Autodesk\Maya2020\bin\mayapy.exe" C:\path\to\profile\files
::

:: Check if both arguments were provided
if "%~1"=="" (
    echo Error: Missing arguments.
    echo Usage: %~nx0 path\to\mayapy.exe path\to\directory
    exit /b 1
)

if "%~2"=="" (
    echo Error: Missing directory argument.
    echo Usage: %~nx0 path\to\mayapy.exe path\to\directory
    exit /b 1
)

:: Set the path to Maya Python executable from the first argument
SET MAYA_EXE="%~1"

:: Set the path to the pstat reader script
SET CONVERTER_SCRIPT=%PROJECT_ROOT%\scripts\internal\convertPythonProfileToHumanReadable.py

:: Get the directory from the second argument
SET TARGET_DIR=%~2

echo Using Maya Python: !MAYA_EXE!
echo Processing all .pstat files in: !TARGET_DIR!
echo.

:: Check if the directory exists
if not exist "!TARGET_DIR!" (
    echo Error: Directory not found - !TARGET_DIR!
    exit /b 1
)

:: Check if Maya executable exists
if not exist !MAYA_EXE! (
    echo Error: Maya Python executable not found - !MAYA_EXE!
    exit /b 1
)

:: Count how many files we'll process
set /a COUNT=0
for %%F in ("!TARGET_DIR!\*.pstat") do set /a COUNT+=1

echo Found !COUNT! .pstat files to process.
echo.

if !COUNT! EQU 0 (
    echo No .pstat files found in the specified directory.
    exit /b 0
)

:: Process each .pstat file
set /a CURRENT=0
for %%F in ("!TARGET_DIR!\*.pstat") do (
    set /a CURRENT+=1
    set PSTAT_FILE=%%F
    set OUTPUT_FILE=%%~dpnF.human_readable_stats.txt

    echo [!CURRENT!/!COUNT!] Processing: %%~nxF
    echo   Generating stats file...
    
    !MAYA_EXE! %CONVERTER_SCRIPT% "!PSTAT_FILE!" --sort cumulative --limit 30 --output "!OUTPUT_FILE!" --callers --callees

    if exist "!OUTPUT_FILE!" (
        echo   Created: %%~nF_stats.txt
    ) else (
        echo   Error: Failed to create stats file.
    )
    echo.
)

echo Processing complete. Generated !CURRENT! stats files.
echo.

endlocal
