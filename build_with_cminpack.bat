@ECHO OFF
SETLOCAL
:: Builds the Maya plug-in with cminpack.

:: To Generate a Visual Studio 'Solution' file, change the '0' to a '1'.
SET GENERATE_SOLUTION=0

:: WARNING: Would you like to use GPL-licensed code? If so you will
:: not be able to distribute
SET WITH_GPL_CODE=0

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
IF "%WITH_GPL_CODE%"=="1" (
    CMD /C "%PROJECT_ROOT%\external\build_levmar_with_nodeps.bat"
)

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
        -DUSE_GPL_LEVMAR=%WITH_GPL_CODE% ^
        -DUSE_CMINPACK=1 ^
        -DUSE_BLAS=0 ^
        -DUSE_F2C=0 ^
        -DUSE_LAPACK=0 ^
        -DUSE_ATLAS=0 ^
        -DUSE_MKL=0 ^
        -DMAYA_VERSION=%MAYA_VERSION% ^
        -DMAYA_INCLUDE_PATH=%MAYA_INCLUDE_PATH% ^
        -DMAYA_LIB_PATH=%MAYA_LIB_PATH% ^
        -DLEVMAR_LIB_PATH="%PROJECT_ROOT%\external\lib" ^
        -DLEVMAR_INCLUDE_PATH="%PROJECT_ROOT%\external\include" ^
        -DCMINPACK_LIB_PATH="C:\Users\catte\dev\cminpack-1.3.6_msvc11\cminpack-1.3.6\x64\Release" ^
        -DCMINPACK_INCLUDE_PATH="C:\Users\catte\dev\cminpack-1.3.6_msvc11\cminpack-1.3.6" ^
        -DCMINPACK_LIB_NAMES="cminpack_dll" ^
        -DBLAS_LIB_PATH="%PROJECT_ROOT%\external\lib" ^
        -DBLAS_INCLUDE_PATH="%PROJECT_ROOT%\external\include" ^
        -DF2C_LIB_PATH="C:\Users\catte\dev\libf2c-1.0\bin\x64\Release" ^
        -DF2C_INCLUDE_PATH="C:\Users\catte\dev\libf2c-1.0\bin\x64\Release" ^
        -DLAPACK_LIB_PATH="%PROJECT_ROOT%\external\lib" ^
        -DLAPACK_INCLUDE_PATH="%PROJECT_ROOT%\external\include" ^
        -DATLAS_LIB_PATH="%PROJECT_ROOT%\external\lib" ^
        -DATLAS_INCLUDE_PATH="%PROJECT_ROOT%\external\include" ^
        -DMKL_LIB_PATH="%PROJECT_ROOT%\external\lib" ^
        -DMKL_INCLUDE_PATH="%PROJECT_ROOT%\external\include" ^
        ..

    nmake /F Makefile clean
    nmake /F Makefile all

REM Comment this line out to stop the automatic install into the home directory.
    nmake /F Makefile install

REM Uncomment to create a .zip package.
REM   nmake /F Makefile package

)

:: Return back project root directory.
CHDIR "%PROJECT_ROOT%"
