@ECHO OFF
SETLOCAL

REM Makefile equivalent for Windows - mmSolver build and test shortcuts
REM
REM Usage:
REM   make build_2024                    - Build for Maya 2024
REM   make test_2024                     - Test for Maya 2024
REM   make test_2024 path/to/test.py     - Test specific file for Maya 2024
REM

if "%1" == "" goto help
if "%1" == "help" goto help

REM Build targets
if "%1" == "build_2018" goto build_2018
if "%1" == "build_2019" goto build_2019
if "%1" == "build_2020" goto build_2020
if "%1" == "build_2022" goto build_2022
if "%1" == "build_2023" goto build_2023
if "%1" == "build_2024" goto build_2024
if "%1" == "build_2025" goto build_2025
if "%1" == "build_2026" goto build_2026

REM Test targets
if "%1" == "test_2018" goto test_2018
if "%1" == "test_2019" goto test_2019
if "%1" == "test_2020" goto test_2020
if "%1" == "test_2022" goto test_2022
if "%1" == "test_2023" goto test_2023
if "%1" == "test_2024" goto test_2024
if "%1" == "test_2025" goto test_2025
if "%1" == "test_2026" goto test_2026

echo Unknown target: %1
goto help

:help
echo mmSolver Build and Test Shortcuts
echo.
echo Build targets:
echo   build_2018    Build for Maya 2018
echo   build_2019    Build for Maya 2019
echo   build_2020    Build for Maya 2020
echo   build_2022    Build for Maya 2022
echo   build_2023    Build for Maya 2023
echo   build_2024    Build for Maya 2024
echo   build_2025    Build for Maya 2025
echo   build_2026    Build for Maya 2026
echo.
echo Test targets:
echo   test_2018     Test for Maya 2018
echo   test_2019     Test for Maya 2019
echo   test_2020     Test for Maya 2020
echo   test_2022     Test for Maya 2022
echo   test_2023     Test for Maya 2023
echo   test_2024     Test for Maya 2024
echo   test_2025     Test for Maya 2025
echo   test_2026     Test for Maya 2026
echo.
echo Examples:
echo   make build_2024
echo   make test_2024
echo   make test_2024 tests\test\test_api\test_solve_robotArm.py
goto end

REM Build targets
:build_2018
call scripts\build_mmSolver_windows64_maya2018.bat
goto end

:build_2019
call scripts\build_mmSolver_windows64_maya2019.bat
goto end

:build_2020
call scripts\build_mmSolver_windows64_maya2020.bat
goto end

:build_2022
call scripts\build_mmSolver_windows64_maya2022.bat
goto end

:build_2023
call scripts\build_mmSolver_windows64_maya2023.bat
goto end

:build_2024
call scripts\build_mmSolver_windows64_maya2024.bat
goto end

:build_2025
call scripts\build_mmSolver_windows64_maya2025.bat
goto end

:build_2026
call scripts\build_mmSolver_windows64_maya2026.bat
goto end

REM Test targets - pass remaining arguments using %*
:test_2018
shift
call scripts\test_mmSolver_windows64_maya2018.bat %*
goto end

:test_2019
shift
call scripts\test_mmSolver_windows64_maya2019.bat %*
goto end

:test_2020
shift
call scripts\test_mmSolver_windows64_maya2020.bat %*
goto end

:test_2022
shift
call scripts\test_mmSolver_windows64_maya2022.bat %*
goto end

:test_2023
shift
call scripts\test_mmSolver_windows64_maya2023.bat %*
goto end

:test_2024
shift
call scripts\test_mmSolver_windows64_maya2024.bat %*
goto end

:test_2025
shift
call scripts\test_mmSolver_windows64_maya2025.bat %*
goto end

:test_2026
shift
call scripts\test_mmSolver_windows64_maya2026.bat %*
goto end

:end
