@ECHO OFF
SETLOCAL
:: Downloads and installs Qt.py file.

:: The root of this project.
SET THIS_DIR=%~dp0
SET ROOT=%THIS_DIR%..\external\
ECHO Package Root: %ROOT%
CHDIR %ROOT%

SET INSTALL_DIR="%ROOT%\install\qtpy"

:: Extract Qt.py
python "%THIS_DIR%get_qtpy.py" "%ROOT%\archives" "%ROOT%\working" "%ROOT%\patches"

:: Copy file to install
MKDIR "%INSTALL_DIR%"
COPY /Y /V "%ROOT%\working\Qt.py-1.1.0\Qt.py" "%INSTALL_DIR%\Qt.py"

:: Return back project root directory.
CHDIR "%ROOT%"
