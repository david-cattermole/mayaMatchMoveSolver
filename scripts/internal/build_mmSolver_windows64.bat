@ECHO OFF
SETLOCAL
::
:: Copyright (C) 2019, 2024 David Cattermole.
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
:: Build the mmSolver plug-in (unified build including Rust libraries).
::
:: NOTE: Do not call this script directly! This file should be called by
:: the build_mmSolver_windows64_mayaXXXX.bat files.
::
:: This file assumes the MAYA_VERSION and MAYA_LOCATION variables
:: have been set.

:: The root of this project.
SET PROJECT_ROOT=%CD%
ECHO Project Root: %PROJECT_ROOT%

:: Source centralised build configuration.
CALL "%PROJECT_ROOT%\scripts\internal\build_config_windows64.bat"

:: Directory configuration handled by centralised build_config_windows64.bat.
ECHO Build root directory base: %BUILD_DIR_BASE%
ECHO Build OpenColorIO directory base: %BUILD_OCIO_DIR_BASE%
ECHO Build mmSolver directory base: %BUILD_MMSOLVER_DIR_BASE%

:: Run the Python API and Solver tests inside Maya, after a
:: successfully build an install process.
SET RUN_TESTS=0

:: Where to install the module?
::
:: Note: In Windows 8 and 10, "My Documents" is no longer visible,
::       however files copying to "My Documents" automatically go
::       to the "Documents" directory.
::
:: The "$HOME/maya/2018/modules" directory is automatically searched
:: for Maya module (.mod) files. Therefore we can install directly.
::
:: SET INSTALL_MODULE_DIR="%PROJECT_ROOT%\modules"
SET INSTALL_MODULE_DIR="%USERPROFILE%\My Documents\maya\%MAYA_VERSION%\modules"

:: Build ZIP Package.
:: For developer use. Make ZIP packages ready to distribute to others.
SET BUILD_PACKAGE=1

:: Do not edit below, unless you know what you're doing.
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:: What type of build? "Release" or "Debug"?
SET BUILD_TYPE=Release
SET MMSOLVER_DEBUG=1

SET RELEASE_FLAG=
SET BUILD_TYPE_DIR=debug
IF "%BUILD_TYPE%"=="Release" (
    SET RELEASE_FLAG=--release
    SET BUILD_TYPE_DIR=release
)

:: Build options, to allow faster compilation times. (not to be used by
:: users wanting to build this project.)
SET MMSOLVER_BUILD_PLUGIN=1
SET MMSOLVER_BUILD_TOOLS=1
SET MMSOLVER_BUILD_PYTHON=1
SET MMSOLVER_BUILD_MEL=1
SET MMSOLVER_BUILD_3DEQUALIZER=1
SET MMSOLVER_BUILD_SYNTHEYES=1
SET MMSOLVER_BUILD_BLENDER=1
SET MMSOLVER_BUILD_QT_UI=1
SET MMSOLVER_BUILD_RENDERER=1
SET MMSOLVER_BUILD_DOCS=1
SET MMSOLVER_BUILD_ICONS=1
SET MMSOLVER_BUILD_CONFIG=1
SET MMSOLVER_BUILD_TESTS=0

:: Allows you to see the build command lines, to help debugging build
:: problems. Set to ON to enable, and OFF to disable.
SET MMSOLVER_BUILD_VERBOSE=OFF

:: Note: There is no need to deactivate the virtual environment because
:: this batch script is 'SETLOCAL' (see top of file) and therefore no
:: environment variables are leaked into the calling environment.
CALL %PROJECT_ROOT%\scripts\internal\python_venv_activate.bat

:: Where to find the mmsolverlibs Rust libraries and headers.
SET MMSOLVERLIBS_ROOT=%PROJECT_ROOT%\lib
SET MMSOLVERLIBS_RUST_ROOT=%MMSOLVERLIBS_ROOT%\mmsolverlibs
SET MMSOLVERLIBS_LIB_DIR=%BUILD_MMSOLVER_RUST_DIR%\%BUILD_TYPE_DIR%
SET MMSOLVERLIBS_RUST_DIR=%BUILD_MMSOLVER_RUST_DIR%\%BUILD_TYPE_DIR%

SET MMSOLVERLIBS_BUILD_TESTS=0

:: Paths for dependencies.
SET EXTERNAL_OCIO_BUILD_DIR=%BUILD_OCIO_CMAKE_DIR%\ext\dist
SET OCIO_CMAKE_CONFIG_DIR=%BUILD_OCIO_INSTALL_DIR%\lib\cmake\OpenColorIO\
SET OCIO_CMAKE_FIND_MODULES_DIR=%BUILD_OCIO_SOURCE_DIR%\%OPENCOLORIO_TARBALL_EXTRACTED_DIR_NAME%\share\cmake\modules
:: Convert back-slashes to forward-slashes.
:: https://stackoverflow.com/questions/23542453/change-backslash-to-forward-slash-in-windows-batch-file
SET "OCIO_CMAKE_FIND_MODULES_DIR=%OCIO_CMAKE_FIND_MODULES_DIR:\=/%"

SET expat_DIR=%EXTERNAL_OCIO_BUILD_DIR%\%EXPAT_RELATIVE_CMAKE_DIR%
SET expat_INCLUDE_DIR=%EXTERNAL_OCIO_BUILD_DIR%\include\
SET expat_LIBRARY=%EXTERNAL_OCIO_BUILD_DIR%\%EXPAT_RELATIVE_LIB_PATH%

SET pystring_INCLUDE_DIR=%EXTERNAL_OCIO_BUILD_DIR%\include
SET pystring_LIBRARY=%EXTERNAL_OCIO_BUILD_DIR%\%PYSTRING_RELATIVE_LIB_PATH%

SET yaml_DIR=%EXTERNAL_OCIO_BUILD_DIR%\%YAML_RELATIVE_CMAKE_DIR%
SET yaml_LIBRARY=%EXTERNAL_OCIO_BUILD_DIR%\%YAML_RELATIVE_LIB_PATH%
SET yaml_INCLUDE_DIR=%EXTERNAL_OCIO_BUILD_DIR%\include\

SET Imath_DIR=%EXTERNAL_OCIO_BUILD_DIR%\lib\cmake\Imath

SET ZLIB_INCLUDE_DIR=%EXTERNAL_OCIO_BUILD_DIR%\include\
SET ZLIB_LIBRARY=%EXTERNAL_OCIO_BUILD_DIR%\%ZLIB_RELATIVE_LIB_PATH%

SET minizip_DIR=%EXTERNAL_OCIO_BUILD_DIR%\%MINIZIP_RELATIVE_CMAKE_DIR%

:: Check if 'cxxbridge.exe' is installed or not, and then install it if
:: not.
::
:: https://stackoverflow.com/questions/4781772/how-to-test-if-an-executable-exists-in-the-path-from-a-windows-batch-file
where /Q cxxbridge
IF %ERRORLEVEL% EQU 1 (
   :: Install the needed 'cxxbridge.exe' command.
   ::
   :: NOTE: When changing this version number, make sure to update the
   :: CXX version used in the C++ buildings, and all the build scripts
   :: using this value:
   :: './Cargo.toml'
   :: './scripts/internal/build_mmSolver_windows64.bat'
   :: './scripts/internal/build_mmSolver_linux.bash'
   :: './scripts/internal/build_mmSolverLibs_windows64.bat'
   :: './scripts/internal/build_mmSolverLibs_linux.bash'
   %RUST_CARGO_EXE% install cxxbridge-cmd --version 1.0.155
)
SET MMSOLVERLIBS_CXXBRIDGE_EXE="%USERPROFILE%\.cargo\bin\cxxbridge.exe"
:: Convert back-slashes to forward-slashes.
:: https://stackoverflow.com/questions/23542453/change-backslash-to-forward-slash-in-windows-batch-file
SET "MMSOLVERLIBS_CXXBRIDGE_EXE=%MMSOLVERLIBS_CXXBRIDGE_EXE:\=/%"

:: Build mmSolverLibs Rust code first
ECHO Building mmsolverlibs Rust libraries... (%MMSOLVERLIBS_ROOT%)
CHDIR "%MMSOLVERLIBS_RUST_ROOT%"
%RUST_CARGO_EXE% build %RELEASE_FLAG% --target-dir "%BUILD_MMSOLVER_RUST_DIR%"
if errorlevel 1 goto failed_to_build_rust

:: MinGW is a common install for developers on Windows and
:: if installed and used it will cause build conflicts and
:: errors, so we disable it.
SET IGNORE_INCLUDE_DIRECTORIES=""
IF EXIST "C:\MinGW" (
    SET IGNORE_INCLUDE_DIRECTORIES="C:\MinGW\bin;C:\MinGW\include"
)

:: A local copy of LDPK to reduce the amount of downloads to the
:: 3DEqualizer website (LDPK doesn't have a git repo to clone from).
SET LDPK_URL="%PROJECT_ROOT%\external\archives\ldpk-2.12.0.tar"
:: Convert back-slashes to forward-slashes.
:: https://stackoverflow.com/questions/23542453/change-backslash-to-forward-slash-in-windows-batch-file
SET "LDPK_URL=%LDPK_URL:\=/%"

:: Get the git branch name, commit long and short hashes.
::
:: NOTE: Assumes the current working directory is the project root.
SET GIT_BRANCH=""
SET GIT_COMMIT_HASH_LONG=""
SET GIT_COMMIT_HASH_SHORT=""
where /Q git
IF %ERRORLEVEL% EQU 0 (
    ECHO 'git' executable found, finding git info.
    FOR /F %%I IN ('git rev-parse --abbrev-ref HEAD') DO SET "GIT_BRANCH=%%I"
    FOR /F %%I IN ('git rev-parse --verify HEAD') DO SET "GIT_COMMIT_HASH_LONG=%%I"
    FOR /F %%I IN ('git rev-parse --verify --short HEAD') DO SET "GIT_COMMIT_HASH_SHORT=%%I"
)
ECHO GIT_BRANCH: %GIT_BRANCH%
ECHO GIT_COMMIT_HASH_LONG: %GIT_COMMIT_HASH_LONG%
ECHO GIT_COMMIT_HASH_SHORT: %GIT_COMMIT_HASH_SHORT%

:: Get Current date/time in UTC timezone using PowerShell.
for /F "delims=" %%I in ('powershell -Command "(Get-Date).ToUniversalTime().ToString('yyyy-MM-dd HH:mm:ss')"') do set "BUILD_DATE_TIME=%%I UTC"
ECHO BUILD_DATE_TIME: %BUILD_DATE_TIME%

:: Optionally use "NMake Makefiles" as the build system generator.
SET CMAKE_GENERATOR=Ninja

:: Force the compilier to be MSVC's cl.exe, so that if other
:: compiliers are installed, CMake doesn't get confused and try to use
:: it (such as clang).
SET CMAKE_C_COMPILER=cl
SET CMAKE_CXX_COMPILER=cl

:: Build mmSolver project.
SET BUILD_DIR=%BUILD_MMSOLVER_CMAKE_DIR%
ECHO BUILD_DIR_BASE: %BUILD_DIR_BASE%
ECHO BUILD_DIR: %BUILD_DIR%
CHDIR "%BUILD_DIR_BASE%"
MKDIR "%BUILD_MMSOLVER_DIR_NAME%"
MKDIR "%BUILD_DIR%"
CHDIR "%BUILD_DIR%"

%CMAKE_EXE% -G %CMAKE_GENERATOR% ^
    -DCMAKE_BUILD_TYPE=%BUILD_TYPE% ^
    -DCMAKE_INSTALL_PREFIX=%INSTALL_MODULE_DIR% ^
    -DCMAKE_IGNORE_PATH=%IGNORE_INCLUDE_DIRECTORIES% ^
    -DCMAKE_CXX_STANDARD=%CXX_STANDARD% ^
    -DCMAKE_C_COMPILER=%CMAKE_C_COMPILER% ^
    -DCMAKE_CXX_COMPILER=%CMAKE_CXX_COMPILER% ^
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ^
    -DCMAKE_MODULE_PATH=%OCIO_CMAKE_FIND_MODULES_DIR% ^
    -DCMAKE_VERBOSE_MAKEFILE=%MMSOLVER_BUILD_VERBOSE% ^
    -DBUILD_DATE_TIME="%BUILD_DATE_TIME%" ^
    -DGIT_BRANCH=%GIT_BRANCH% ^
    -DGIT_COMMIT_HASH_LONG=%GIT_COMMIT_HASH_LONG% ^
    -DGIT_COMMIT_HASH_SHORT=%GIT_COMMIT_HASH_SHORT% ^
    -DMMSOLVER_VFX_PLATFORM=%VFX_PLATFORM% ^
    -DMMSOLVER_DEBUG=%MMSOLVER_DEBUG% ^
    -DMMSOLVER_BUILD_PLUGIN=%MMSOLVER_BUILD_PLUGIN% ^
    -DMMSOLVER_BUILD_TOOLS=%MMSOLVER_BUILD_TOOLS% ^
    -DMMSOLVER_BUILD_PYTHON=%MMSOLVER_BUILD_PYTHON% ^
    -DMMSOLVER_BUILD_MEL=%MMSOLVER_BUILD_MEL% ^
    -DMMSOLVER_BUILD_3DEQUALIZER=%MMSOLVER_BUILD_3DEQUALIZER% ^
    -DMMSOLVER_BUILD_SYNTHEYES=%MMSOLVER_BUILD_SYNTHEYES% ^
    -DMMSOLVER_BUILD_BLENDER=%MMSOLVER_BUILD_BLENDER% ^
    -DMMSOLVER_BUILD_QT_UI=%MMSOLVER_BUILD_QT_UI% ^
    -DMMSOLVER_BUILD_RENDERER=%MMSOLVER_BUILD_RENDERER% ^
    -DMMSOLVER_BUILD_DOCS=%MMSOLVER_BUILD_DOCS% ^
    -DMMSOLVER_BUILD_ICONS=%MMSOLVER_BUILD_ICONS% ^
    -DMMSOLVER_BUILD_CONFIG=%MMSOLVER_BUILD_CONFIG% ^
    -DMMSOLVER_BUILD_TESTS=%MMSOLVER_BUILD_TESTS% ^
    -DBUILD_DOCS_DIR_BASE=%BUILD_DOCS_DIR_BASE% ^
    -DMAYA_LOCATION=%MAYA_LOCATION% ^
    -DMAYA_VERSION=%MAYA_VERSION% ^
    -DMMSOLVERLIBS_CXXBRIDGE_EXE=%MMSOLVERLIBS_CXXBRIDGE_EXE% ^
    -DMMSOLVERLIBS_BUILD_TESTS=%MMSOLVERLIBS_BUILD_TESTS% ^
    -DMMSOLVER_DOWNLOAD_DEPENDENCIES=ON ^
    -Dmmsolverlibs_rust_DIR=%MMSOLVERLIBS_RUST_DIR% ^
    -Dldpk_URL=%LDPK_URL% ^
    -DOpenColorIO_DIR=%OCIO_CMAKE_CONFIG_DIR% ^
    -DOCIO_INSTALL_EXT_PACKAGES=NONE ^
    -DopenMVG_USE_AVX=0 ^
    -DopenMVG_USE_AVX2=0 ^
    -DZLIB_LIBRARY=%ZLIB_LIBRARY% ^
    -DZLIB_INCLUDE_DIR=%ZLIB_INCLUDE_DIR% ^
    -DZLIB_STATIC_LIBRARY=ON ^
    -Dexpat_DIR=%expat_DIR% ^
    -Dexpat_LIBRARY=%expat_LIBRARY% ^
    -Dexpat_INCLUDE_DIR=%expat_INCLUDE_DIR% ^
    -Dexpat_USE_STATIC_LIBS=TRUE ^
    -DImath_DIR=%Imath_DIR% ^
    -Dminizip-ng_DIR=%minizip_DIR% ^
    -Dpystring_LIBRARY=%pystring_LIBRARY% ^
    -Dpystring_INCLUDE_DIR=%pystring_INCLUDE_DIR% ^
    -Dyaml-cpp_DIR=%yaml_DIR% ^
    -Dyaml-cpp_LIBRARY=%yaml_LIBRARY% ^
    -Dyaml-cpp_INCLUDE_DIR=%yaml_INCLUDE_DIR% ^
    %PROJECT_ROOT%
if errorlevel 1 goto failed_to_generate

%CMAKE_EXE% --build . --parallel
if errorlevel 1 goto failed_to_build

:: Comment this line out to stop the automatic install into the home directory.
%CMAKE_EXE% --install .
if errorlevel 1 goto failed_to_install

:: Run tests
IF "%RUN_TESTS%"=="1" (
    %CMAKE_EXE% --build . --target test
)

:: Create a .zip package.
IF "%BUILD_PACKAGE%"=="1" (
    %CMAKE_EXE% --build . --target package
    if errorlevel 1 goto failed_to_build_zip
)

:: Return back project root directory.
CHDIR "%PROJECT_ROOT%"
exit /b 0

:failed_to_build_rust
echo Failed to build Rust code for mmSolverLibs.
exit /b 1

:failed_to_generate
echo Failed to generate build files for mmSolver component.
exit /b 1

:failed_to_build
echo Failed to build mmSolver component.
exit /b 1

:failed_to_install
echo Failed to install mmSolver component.
exit /b 1

:failed_to_build_zip
echo Failed to build the ZIP package file for mmSolver component.
exit /b 1
