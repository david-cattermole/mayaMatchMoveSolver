@ECHO OFF
SETLOCAL
::
:: Copyright (C) 2023 David Cattermole.
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
:: Tests the Lens Distortion tool.

:: The root of this project.
SET PROJECT_ROOT=%CD%
ECHO Project Root: %PROJECT_ROOT%

SET MAYA_VERSION=2020
SET MMSOLVER_VERSION=0.5.0.beta3
SET INSTALL_MODULE_DIR=%USERPROFILE%\Documents\maya\%MAYA_VERSION%\modules

SET MAIN_BINARY=%INSTALL_MODULE_DIR%\mayaMatchMoveSolver-%MMSOLVER_VERSION%-maya%MAYA_VERSION%-win64\bin\mmsolver-lensdistortion.exe

SET LENS_FILE=%PROJECT_ROOT%\lib\cppbind\mmlens\tests\test_file_3de_classic_1.nk
REM SET LENS_FILE=%PROJECT_ROOT%\lib\cppbind\mmlens\tests\test_file_3de_radial_std_deg4_1.nk
REM SET LENS_FILE=%PROJECT_ROOT%\lib\cppbind\mmlens\tests\test_file_3de_anamorphic_std_deg4_1.nk
REM SET LENS_FILE=%PROJECT_ROOT%\lib\cppbind\mmlens\tests\test_file_3de_anamorphic_std_deg4_rescaled_1.nk

SET OUTPUT_FILE_PATTERN=%PROJECT_ROOT%\tools\lensdistortion\tests\test_output/out
ECHO main binary: %MAIN_BINARY%
ECHO lens file: %LENS_FILE%
ECHO output file pattern: %OUTPUT_FILE_PATTERN%

SET NUM_THREADS=0
SET FRAME_START=0
SET FRAME_END=12

CALL %MAIN_BINARY% --verbose --num-threads %NUM_THREADS% --frame-range %FRAME_START% %FRAME_END% --lens %LENS_FILE% --output %OUTPUT_FILE_PATTERN%
if errorlevel 1 goto failed_to_run

:failed_to_run
echo Failed to run mmsolver-lensdistortion
exit /b 1
