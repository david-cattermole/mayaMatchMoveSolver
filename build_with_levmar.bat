@echo off
SETLOCAL
:: Builds the Maya plug-in with levmar.

:: To Generate a Visual Studio 'Solution' file, change the '0' to a '1'.
SET /A GENERATE_SOLUTION=0

:: Maya directories
::
:: If you're not using Maya 2017 or have a non-standard install location,
:: set these variables here.
SET MAYA_INCLUDE_PATH="C:\Program Files\Autodesk\Maya2017\include"
SET MAYA_LIB_PATH="C:\Program Files\Autodesk\Maya2017\lib"

:: The root of this project.
SET PROJECT_ROOT=%CD%
ECHO Project Root: %PROJECT_ROOT%

:: Remove existing libraries and include headers.
DEL /S /Q %PROJECT_ROOT%\external\lib\*.dll
DEL /S /Q %PROJECT_ROOT%\external\lib\*.lib
DEL /S /Q %PROJECT_ROOT%\external\include\*.h

:: Build the external dependencies
CMD /C %PROJECT_ROOT%\external\build_levmar_with_nodeps.bat

:: Build plugin
MKDIR build
CHDIR build
DEL /S /Q *
RMDIR /Q *
IF %GENERATE_SOLUTION%==1 (
    :: To Generate a Visual Studio 'Solution' file
    cmake -G "Visual Studio 11 2012 Win64" -T "v110" ^
        -DUSE_ATLAS=0 ^
        -DUSE_MKL=0 ^
        -DMAYA_INCLUDE_PATH=%MAYA_INCLUDE_PATH% ^
        -DMAYA_LIB_PATH=%MAYA_LIB_PATH% ^
        -DLEVMAR_LIB_PATH=%PROJECT_ROOT%\external\lib\ ^
        -DLEVMAR_INCLUDE_PATH=%PROJECT_ROOT%\external\include\ ^
        ..
)  else (
    cmake -G "NMake Makefiles" ^
        -DCMAKE_BUILD_TYPE=Release ^
        -DUSE_ATLAS=0 ^
        -DUSE_MKL=0 ^
        -DMAYA_INCLUDE_PATH=%MAYA_INCLUDE_PATH% ^
        -DMAYA_LIB_PATH=%MAYA_LIB_PATH% ^
        -DLEVMAR_LIB_PATH=%PROJECT_ROOT%\external\lib ^
        -DLEVMAR_INCLUDE_PATH=%PROJECT_ROOT%\external\include ^
        ..
    nmake /f Makefile clean
    nmake /f Makefile all
)

:: Return back project root directory.
CHDIR %PROJECT_ROOT%
