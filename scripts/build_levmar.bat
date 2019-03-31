@ECHO OFF
SETLOCAL
:: Build LevMar library without any dependencies.

:: The root of this project.
SET THIS_DIR=%~dp0
SET ROOT=%THIS_DIR%..\external\
ECHO Package Root: %ROOT%
CHDIR %ROOT%

SET INSTALL_DIR="%ROOT%\install\levmar"

:: Extract LevMar
python "%THIS_DIR%get_levmar.py" "%ROOT%\archives" "%ROOT%\working" "%ROOT%\patches"

:: Build Library
MKDIR build
CHDIR build
DEL /S /Q *
FOR /D %%G in ("*") DO RMDIR /S /Q "%%~nxG"
cmake -G "NMake Makefiles" ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DCMAKE_INSTALL_PREFIX=%INSTALL_DIR% ^
    -DBUILD_SHARED_LIBS=ON ^
    -DHAVE_LAPACK=0 ^
    -DNEED_F2C=0 ^
    -DBUILD_DEMO=0 ^
    -DLM_SNGL_PREC=0 ^
    ../working/levmar-2.6

nmake /F Makefile clean
nmake /F Makefile all

:: The CMake script with levmar does not not define an install process.
:: So we copy the files manually
MKDIR "%ROOT%\install\levmar\lib"
MKDIR "%ROOT%\install\levmar\include"
COPY /Y "%ROOT%\build\levmar.lib" "%ROOT%\install\levmar\lib\"
COPY /Y "%ROOT%\build\levmar.dll" "%ROOT%\install\levmar\lib\"
COPY /Y "%ROOT%\working\levmar-2.6\levmar.h" "%ROOT%\install\levmar\include\"

:: Return back project root directory.
CHDIR "%ROOT%"
