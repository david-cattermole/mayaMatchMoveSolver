@ECHO OFF
SETLOCAL
:: Builds the cminpack shared library.

:: The root of this project.
SET THIS_DIR=%~dp0
SET ROOT=%THIS_DIR%..\external\
ECHO Package Root: %ROOT%
CHDIR %ROOT%

SET INSTALL_DIR="%ROOT%\install\cminpack"

:: Extract LevMar
python "%THIS_DIR%get_cminpack.py" "%ROOT%\archives" "%ROOT%\working" "%ROOT%\patches"

:: Build plugin
MKDIR build
CHDIR build
DEL /S /Q *
FOR /D %%G in ("*") DO RMDIR /S /Q "%%~nxG"

cmake -G "NMake Makefiles" ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DCMAKE_INSTALL_PREFIX=%INSTALL_DIR% ^
    -DBUILD_SHARED_LIBS=ON ^
    -DBUILD_EXAMPLES=OFF ^
    -DUSE_FPIC=ON ^
    -DUSE_BLAS=0 ^
    ../working/cminpack-1.3.6

nmake /F Makefile clean
nmake /F Makefile all
nmake /F Makefile install

:: Return back project root directory.
CHDIR "%ROOT%"
