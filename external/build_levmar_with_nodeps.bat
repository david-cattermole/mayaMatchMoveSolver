@echo off
SETLOCAL
:: Build LevMar library without any dependencies.

SET PROJECT_ROOT=%CD%

:: Clean up
RMDIR /S /Q "%PROJECT_ROOT%\external\working\levmar-2.6"

:: Extract - Use CMake to un-zip 'levmar-2.6.tgz'.
:: 'levmar-2.6.tgz' is expected to be downloaded already.
MKDIR "%PROJECT_ROOT%\external\working\"
RMDIR /S /Q "%PROJECT_ROOT%\external\build\"
MKDIR "%PROJECT_ROOT%\external\build\"
CHDIR "%PROJECT_ROOT%\external\build\"
cmake -G "NMake Makefiles" ..
nmake

:: 'Patch' with edited files.
COPY "%PROJECT_ROOT%\external\patches\levmar-2.6_nodeps_win64_Makefile.vc" "%PROJECT_ROOT%\external\working\levmar-2.6\Makefile.vc"
COPY "%PROJECT_ROOT%\external\patches\levmar-2.6_nodeps_win64_levmar.h" "%PROJECT_ROOT%\external\working\levmar-2.6\levmar.h"
COPY "%PROJECT_ROOT%\external\patches\levmar-2.6_nodeps_win64_levmar.h.in" "%PROJECT_ROOT%\external\working\levmar-2.6\levmar.h.in"

:: Build
CHDIR "%PROJECT_ROOT%\external\working\levmar-2.6\"
nmake /f Makefile.vc all
:: Run test
lmdemo.exe

:: Copy compiled contents
COPY /Y "%PROJECT_ROOT%\external\working\levmar-2.6\levmar.lib" "%PROJECT_ROOT%\external\lib\"
COPY /Y "%PROJECT_ROOT%\external\working\levmar-2.6\levmar.h" "%PROJECT_ROOT%\external\include\"

:: Go back to orignal root
CHDIR "%PROJECT_ROOT%"
