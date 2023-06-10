@ECHO OFF
SETLOCAL
::
:: Copyright (C) 2022 David Cattermole.
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
:: Runs 'clang-format' for the project.
::
:: The Bash/Linux version of this script can exclude files with names
:: "cxx", but this is not implmented in the Windows script.

SET PROJECT_ROOT=%CD%

clang-format --dry-run --style=file --Werror ^
       "%PROJECT_ROOT%\src\mmSolver\calibrate\*.cpp" ^
       "%PROJECT_ROOT%\src\mmSolver\calibrate\*.h" ^
       "%PROJECT_ROOT%\src\mmSolver\adjust\*.cpp" ^
       "%PROJECT_ROOT%\src\mmSolver\adjust\*.h" ^
       "%PROJECT_ROOT%\src\mmSolver\cmd\*.h" ^
       "%PROJECT_ROOT%\src\mmSolver\cmd\*.cpp" ^
       "%PROJECT_ROOT%\src\mmSolver\core\*.cpp" ^
       "%PROJECT_ROOT%\src\mmSolver\core\*.h" ^
       "%PROJECT_ROOT%\src\mmSolver\mayahelper\*.cpp" ^
       "%PROJECT_ROOT%\src\mmSolver\mayahelper\*.h" ^
       "%PROJECT_ROOT%\src\mmSolver\node\*.cpp" ^
       "%PROJECT_ROOT%\src\mmSolver\node\*.h" ^
       "%PROJECT_ROOT%\src\mmSolver\render\*.cpp" ^
       "%PROJECT_ROOT%\src\mmSolver\render\*.h" ^
       "%PROJECT_ROOT%\src\mmSolver\render\data\*.cpp" ^
       "%PROJECT_ROOT%\src\mmSolver\render\data\*.h" ^
       "%PROJECT_ROOT%\src\mmSolver\render\ops\*.cpp" ^
       "%PROJECT_ROOT%\src\mmSolver\render\ops\*.h" ^
       "%PROJECT_ROOT%\src\mmSolver\render\passes\*.cpp" ^
       "%PROJECT_ROOT%\src\mmSolver\render\passes\*.h" ^
       "%PROJECT_ROOT%\src\mmSolver\render\shader\*.cpp" ^
       "%PROJECT_ROOT%\src\mmSolver\render\shader\*.h" ^
       "%PROJECT_ROOT%\src\mmSolver\sfm\*.cpp" ^
       "%PROJECT_ROOT%\src\mmSolver\sfm\*.h" ^
       "%PROJECT_ROOT%\src\mmSolver\shape\*.cpp" ^
       "%PROJECT_ROOT%\src\mmSolver\shape\*.h" ^
       "%PROJECT_ROOT%\src\mmSolver\utilities\*.cpp" ^
       "%PROJECT_ROOT%\src\mmSolver\utilities\*.h" ^
       "%PROJECT_ROOT%\src\mmSolver\pluginMain.cpp" ^
       "%PROJECT_ROOT%\include\mmSolver\*.cpp" ^
       "%PROJECT_ROOT%\include\mmSolver\*.h" ^
       "%PROJECT_ROOT%\lib\cppbind\mmcore\include\mmcore\*.cpp" ^
       "%PROJECT_ROOT%\lib\cppbind\mmcore\include\mmcore\*.h" ^
       "%PROJECT_ROOT%\lib\cppbind\mmcore\src\*.cpp" ^
       "%PROJECT_ROOT%\lib\cppbind\mmcore\src\*.h" ^
       "%PROJECT_ROOT%\lib\cppbind\mmcore\tests\*.cpp" ^
       "%PROJECT_ROOT%\lib\cppbind\mmcore\tests\*.h" ^
       "%PROJECT_ROOT%\lib\cppbind\mmlens\include\mmlens\*.cpp" ^
       "%PROJECT_ROOT%\lib\cppbind\mmlens\include\mmlens\*.h" ^
       "%PROJECT_ROOT%\lib\cppbind\mmlens\src\*.cpp" ^
       "%PROJECT_ROOT%\lib\cppbind\mmlens\src\*.h" ^
       "%PROJECT_ROOT%\lib\cppbind\mmlens\tests\*.cpp" ^
       "%PROJECT_ROOT%\lib\cppbind\mmlens\tests\*.h" ^
       "%PROJECT_ROOT%\lib\cppbind\mmimage\include\mmimage\*.cpp" ^
       "%PROJECT_ROOT%\lib\cppbind\mmimage\include\mmimage\*.h" ^
       "%PROJECT_ROOT%\lib\cppbind\mmimage\src\*.cpp" ^
       "%PROJECT_ROOT%\lib\cppbind\mmimage\src\*.h" ^
       "%PROJECT_ROOT%\lib\cppbind\mmimage\tests\*.cpp" ^
       "%PROJECT_ROOT%\lib\cppbind\mmimage\tests\*.h" ^
       "%PROJECT_ROOT%\lib\cppbind\mmscenegraph\include\mmscenegraph\*.cpp" ^
       "%PROJECT_ROOT%\lib\cppbind\mmscenegraph\include\mmscenegraph\*.h" ^
       "%PROJECT_ROOT%\lib\cppbind\mmscenegraph\src\*.cpp" ^
       "%PROJECT_ROOT%\lib\cppbind\mmscenegraph\src\*.h" ^
       "%PROJECT_ROOT%\lib\cppbind\mmscenegraph\tests\*.cpp" ^
       "%PROJECT_ROOT%\lib\cppbind\mmscenegraph\tests\*.h"
