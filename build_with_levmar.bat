@ECHO OFF
SETLOCAL
:: Builds the Maya plug-in with levmar.

:: To Generate a Visual Studio 'Solution' file, change the '0' to a '1'.
SET GENERATE_SOLUTION=0

:: Maya directories
::
:: If you're not using Maya 2017 or have a non-standard install location,
:: set these variables here.
::
:: Note: Do not enclose the MAYA_VERSION in quotes, it will
::       lead to tears.
SET MAYA_VERSION=2017
SET MAYA_INCLUDE_PATH="C:\Program Files\Autodesk\Maya2017\include"
SET MAYA_LIB_PATH="C:\Program Files\Autodesk\Maya2017\lib"

:: The root of this project.
SET PROJECT_ROOT=%CD%
ECHO Project Root: %PROJECT_ROOT%

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

:: Remove existing libraries and include headers.
DEL /S /Q "%PROJECT_ROOT%\external\lib\*.dll"
DEL /S /Q "%PROJECT_ROOT%\external\lib\*.lib"
DEL /S /Q "%PROJECT_ROOT%\external\include\*.h"

:: Build the external dependencies
CMD /C "%PROJECT_ROOT%\external\build_levmar_with_nodeps.bat"

:: Build plugin
MKDIR build
CHDIR build
DEL /S /Q *
FOR /D %%G in ("*") DO RMDIR /S /Q "%%~nxG"

IF "%GENERATE_SOLUTION%"=="1" (

REM For Maya 2018 (which uses Visual Studio 2015)
REM cmake -G "Visual Studio 14 2015 Win64" -T "v140"

REM To Generate a Visual Studio 'Solution' file
    cmake -G "Visual Studio 11 2012 Win64" -T "v110" ^
        -DUSE_ATLAS=0 ^
        -DUSE_MKL=0 ^
        -DMAYA_VERSION=%MAYA_VERSION% ^
        -DMAYA_INCLUDE_PATH=%MAYA_INCLUDE_PATH% ^
        -DMAYA_LIB_PATH=%MAYA_LIB_PATH% ^
        -DLEVMAR_LIB_PATH="%PROJECT_ROOT%\external\lib\" ^
        -DLEVMAR_INCLUDE_PATH="%PROJECT_ROOT%\external\include\" ^
        ..

) ELSE (

    cmake -G "NMake Makefiles" ^
        -DCMAKE_BUILD_TYPE=Release ^
        -DCMAKE_INSTALL_PREFIX=%INSTALL_MODULE_DIR% ^
        -DUSE_ATLAS=0 ^
        -DUSE_MKL=0 ^
        -DMAYA_VERSION=%MAYA_VERSION% ^
        -DMAYA_INCLUDE_PATH=%MAYA_INCLUDE_PATH% ^
        -DMAYA_LIB_PATH=%MAYA_LIB_PATH% ^
        -DLEVMAR_LIB_PATH="%PROJECT_ROOT%\external\lib" ^
        -DLEVMAR_INCLUDE_PATH="%PROJECT_ROOT%\external\include" ^
        ..

    nmake /F Makefile clean
    nmake /F Makefile all
    nmake /F Makefile install

REM Uncomment to create a .zip package.
REM   nmake /F Makefile package

)

:: Return back project root directory.
CHDIR "%PROJECT_ROOT%"
