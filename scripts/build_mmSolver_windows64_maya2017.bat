@ECHO OFF
SETLOCAL
:: Builds the Maya MatchMove Solver project.

:: Maya directories
::
:: If you're not using Maya 2017 or have a non-standard install location,
:: set these variables here.
::
:: Note: Do not enclose the MAYA_VERSION in quotes, it will
::       lead to tears.
SET MAYA_VERSION=2017
SET MAYA_LOCATION="C:\Program Files\Autodesk\Maya2017"

:: Clear all build information before re-compiling.
:: Turn this off when wanting to make small changes and recompile.
SET FRESH_BUILD=1

:: Run the Python API and Solver tests inside Maya, after a
:: successfully build an install process.
SET RUN_TESTS=0

:: Use CMinpack?
:: CMinpack is the recommended solving library.
SET WITH_CMINPACK=1

:: WARNING: Would you like to use GPL-licensed code? If so you will
:: not be able to distribute
SET WITH_GPL_CODE=0

:: Where to install the module?
::
:: Note: In Windows 8 and 10, "My Documents" is no longer visible,
::       however files copying to "My Documents" automatically go
::       to the "Documents" directory.
::
:: The "$HOME/maya/2017/modules" directory is automatically searched
:: for Maya module (.mod) files. Therefore we can install directly.
::
:: SET INSTALL_MODULE_DIR="%PROJECT_ROOT%\modules"
SET INSTALL_MODULE_DIR="%USERPROFILE%\My Documents\maya\%MAYA_VERSION%\modules"


:: Do not edit below, unless you know what you're doing.
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


:: To Generate a Visual Studio 'Solution' file, change the '0' to a '1'.
SET GENERATE_SOLUTION=0

:: The root of this project.
SET PROJECT_ROOT=%CD%
ECHO Project Root: %PROJECT_ROOT%

:: Build plugin
MKDIR build
CHDIR build
IF "%FRESH_BUILD%"=="1" (
    DEL /S /Q *
    FOR /D %%G in ("*") DO RMDIR /S /Q "%%~nxG"
)

IF "%GENERATE_SOLUTION%"=="1" (

REM For Maya 2018 (which uses Visual Studio 2015)
REM cmake -G "Visual Studio 14 2015 Win64" -T "v140"

REM To Generate a Visual Studio 'Solution' file
    cmake -G "Visual Studio 11 2012 Win64" -T "v110" ^
        -DMAYA_VERSION=%MAYA_VERSION% ^
        -DUSE_GPL_LEVMAR=%WITH_GPL_CODE% ^
        -DUSE_CMINPACK=%WITH_CMINPACK% ^
        -DCMINPACK_ROOT="%PROJECT_ROOT%\external\install\cminpack" ^
        -DLEVMAR_ROOT="%PROJECT_ROOT%\external\install\levmar" ^
        -DMAYA_LOCATION=%MAYA_LOCATION% ^
        -DMAYA_VERSION=%MAYA_VERSION% ^
        ..

) ELSE (

    cmake -G "NMake Makefiles" ^
        -DCMAKE_BUILD_TYPE=Release ^
        -DCMAKE_INSTALL_PREFIX=%INSTALL_MODULE_DIR% ^
        -DUSE_GPL_LEVMAR=%WITH_GPL_CODE% ^
        -DUSE_CMINPACK=%WITH_CMINPACK% ^
        -DCMINPACK_ROOT="%PROJECT_ROOT%\external\install\cminpack" ^
        -DLEVMAR_ROOT="%PROJECT_ROOT%\external\install\levmar" ^
        -DMAYA_LOCATION=%MAYA_LOCATION% ^
        -DMAYA_VERSION=%MAYA_VERSION% ^
        ..

    nmake /F Makefile clean
    nmake /F Makefile all

REM Comment this line out to stop the automatic install into the home directory.
    nmake /F Makefile install

REM Run tests
    IF "%RUN_TESTS%"=="1" (
        nmake /F Makefile test
    )

REM Create a .zip package.
IF "%BUILD_PACKAGE%"=="1" (
       nmake /F Makefile package
   )

)

:: Return back project root directory.
CHDIR "%PROJECT_ROOT%"
