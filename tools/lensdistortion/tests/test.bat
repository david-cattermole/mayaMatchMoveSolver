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

SET MAIN_BINARY="C:\Users\catte\Documents\maya\2022\modules\mayaMatchMoveSolver-0.4.6-maya2022-win64\bin\mmsolver-lensdistortion.exe"
SET LENS_FILE="c:\Users\catte\dev\mayaMatchMoveSolver_linux\lib\cppbind\mmlens\tests\test_file_3de_classic_3.nk"
SET OUTPUT_FILE_PATTERN="c:/Users/catte/Desktop/out."

SET NUM_THREADS=0
SET FRAME_START=0
SET FRAME_END=12

CALL %MAIN_BINARY% --num-threads %NUM_THREADS% --frame-range %FRAME_START% %FRAME_END% --lens %LENS_FILE% --output %OUTPUT_FILE_PATTERN%
if errorlevel 1 goto failed_to_run

:failed_to_run
echo Failed to run mmsolver-lensdistortion
exit /b 1
