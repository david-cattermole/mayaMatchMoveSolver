@ECHO OFF
::
:: Copyright (C) 2022, 2023, 2024 David Cattermole.
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
:: Build the mmSolverLibs library.
::
:: NOTE: Do not call this script directly! This file should be called by
:: the build_mmSolver_windows64_mayaXXXX.bat files.
::
:: This file assumes the variables MAYA_VERSION and RUST_CARGO_EXE
:: have been set.

:: The root of this project.
SET PROJECT_ROOT=%CD%
ECHO Project Root: %PROJECT_ROOT%

:: What directory to build the project in?
SET BUILD_DIR_BASE=%PROJECT_ROOT%\..

:: What type of build? "Release" or "Debug"?
SET BUILD_TYPE=Release

SET RELEASE_FLAG=
SET BUILD_TYPE_DIR=debug
IF "%BUILD_TYPE%"=="Release" (
    SET RELEASE_FLAG=--release
    SET BUILD_TYPE_DIR=release
)

:: Allows you to see the build command lines, to help debugging build
:: problems. Set to ON to enable, and OFF to disable.
SET MMSOLVER_BUILD_VERBOSE=OFF

:: Where to find the mmsolverlibs Rust libraries and headers.
SET MMSOLVERLIBS_INSTALL_PATH=%BUILD_DIR_BASE%\build_mmsolverlibs\install\maya%MAYA_VERSION%_windows64\
SET MMSOLVERLIBS_ROOT=%PROJECT_ROOT%\lib
SET MMSOLVERLIBS_RUST_ROOT=%MMSOLVERLIBS_ROOT%\mmsolverlibs
SET MMSOLVERLIBS_CPP_TARGET_DIR=%BUILD_DIR_BASE%\build_mmsolverlibs\rust_windows64_maya%MAYA_VERSION%
SET MMSOLVERLIBS_LIB_DIR=%MMSOLVERLIBS_CPP_TARGET_DIR%\%BUILD_TYPE_DIR%
SET MMSOLVERLIBS_INCLUDE_DIR=%MMSOLVERLIBS_ROOT%\include

SET MMSOLVERLIBS_BUILD_TESTS=1

:: Paths for dependencies.
SET EXTERNAL_BUILD_DIR=%BUILD_DIR_BASE%\build_opencolorio\cmake_win64_maya%MAYA_VERSION%_%BUILD_TYPE%\ext\dist
SET OPENCOLORIO_INSTALL_DIR=%BUILD_DIR_BASE%\build_opencolorio\install\maya%MAYA_VERSION%_windows64\
SET OPENCOLORIO_CMAKE_CONFIG_DIR=%OPENCOLORIO_INSTALL_DIR%\lib\cmake\OpenColorIO\
SET OPENCOLORIO_CMAKE_FIND_MODULES_DIR=%PROJECT_ROOT%\external\working\maya%MAYA_VERSION%_windows64\%OPENCOLORIO_TARBALL_EXTRACTED_DIR_NAME%\share\cmake\modules
:: Convert back-slashes to forward-slashes.
:: https://stackoverflow.com/questions/23542453/change-backslash-to-forward-slash-in-windows-batch-file
SET "OPENCOLORIO_CMAKE_FIND_MODULES_DIR=%OPENCOLORIO_CMAKE_FIND_MODULES_DIR:\=/%"

SET expat_DIR=%EXTERNAL_BUILD_DIR%\%EXPAT_RELATIVE_CMAKE_DIR%
SET expat_INCLUDE_DIR=%EXTERNAL_BUILD_DIR%\include\
SET expat_LIBRARY=%EXTERNAL_BUILD_DIR%\%EXPAT_RELATIVE_LIB_PATH%

SET pystring_INCLUDE_DIR=%EXTERNAL_BUILD_DIR%\include
SET pystring_LIBRARY=%EXTERNAL_BUILD_DIR%\%PYSTRING_RELATIVE_LIB_PATH%

SET yaml_DIR=%EXTERNAL_BUILD_DIR%\%YAML_RELATIVE_CMAKE_DIR%
SET yaml_LIBRARY=%EXTERNAL_BUILD_DIR%\%YAML_RELATIVE_LIB_PATH%
SET yaml_INCLUDE_DIR=%EXTERNAL_BUILD_DIR%\include\

SET Imath_DIR=%EXTERNAL_BUILD_DIR%\lib\cmake\Imath

SET ZLIB_INCLUDE_DIR=%EXTERNAL_BUILD_DIR%\include\
SET ZLIB_LIBRARY=%EXTERNAL_BUILD_DIR%\%ZLIB_RELATIVE_LIB_PATH%

SET minizip_DIR=%EXTERNAL_BUILD_DIR%\%MINIZIP_RELATIVE_CMAKE_DIR%

ECHO Building mmsolverlibs... (%MMSOLVERLIBS_ROOT%)

:: Check if 'cxxbridge.exe' is installed or not, and then install it if
:: not.
::
:: https://stackoverflow.com/questions/4781772/how-to-test-if-an-executable-exists-in-the-path-from-a-windows-batch-file
where /q cxxbridge
IF ERRORLEVEL 1 (
   :: Install the needed 'cxxbridge.exe' command.
   ::
   :: NOTE: When changing this version number, make sure to update the
   :: CXX version used in the C++ buildings, and all the build scripts
   :: using this value:
   :: './Cargo.toml'
   :: './scripts/internal/build_mmSolverLibs_windows64.bat'
   :: './scripts/internal/build_mmSolverLibs_linux.bash'
   %RUST_CARGO_EXE% install cxxbridge-cmd --version 1.0.129
)
SET MMSOLVERLIBS_CXXBRIDGE_EXE="%USERPROFILE%\.cargo\bin\cxxbridge.exe"
:: Convert back-slashes to forward-slashes.
:: https://stackoverflow.com/questions/23542453/change-backslash-to-forward-slash-in-windows-batch-file
SET "MMSOLVERLIBS_CXXBRIDGE_EXE=%MMSOLVERLIBS_CXXBRIDGE_EXE:\=/%"

CHDIR "%MMSOLVERLIBS_RUST_ROOT%"
%RUST_CARGO_EXE% build %RELEASE_FLAG% --target-dir "%MMSOLVERLIBS_CPP_TARGET_DIR%"
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
SET LDPK_URL="%PROJECT_ROOT%\external\archives\ldpk-2.8.tar"
:: Convert back-slashes to forward-slashes.
:: https://stackoverflow.com/questions/23542453/change-backslash-to-forward-slash-in-windows-batch-file
SET "LDPK_URL=%LDPK_URL:\=/%"

:: Optionally use "NMake Makefiles" as the build system generator.
SET CMAKE_GENERATOR=Ninja

:: Force the compilier to be MSVC's cl.exe, so that if other
:: compiliers are installed, CMake doesn't get confused and try to use
:: it (such as clang).
SET CMAKE_C_COMPILER=cl
SET CMAKE_CXX_COMPILER=cl

:: Build project
SET BUILD_DIR_NAME=cmake_win64_maya%MAYA_VERSION%_%BUILD_TYPE%
SET BUILD_DIR=%BUILD_DIR_BASE%\build_mmsolverlibs\%BUILD_DIR_NAME%
ECHO BUILD_DIR_BASE: %BUILD_DIR_BASE%
ECHO BUILD_DIR_NAME: %BUILD_DIR_NAME%
ECHO BUILD_DIR: %BUILD_DIR%
CHDIR "%BUILD_DIR_BASE%"
MKDIR "build_mmsolverlibs"
CHDIR "%BUILD_DIR_BASE%\build_mmsolverlibs\"
MKDIR "%BUILD_DIR_NAME%"
CHDIR "%BUILD_DIR%"

%CMAKE_EXE% -G %CMAKE_GENERATOR% ^
    -DBUILD_SHARED_LIBS=OFF ^
    -DCMAKE_BUILD_TYPE=%BUILD_TYPE% ^
    -DCMAKE_INSTALL_PREFIX=%MMSOLVERLIBS_INSTALL_PATH% ^
    -DCMAKE_IGNORE_PATH=%IGNORE_INCLUDE_DIRECTORIES% ^
    -DCMAKE_CXX_STANDARD=%CXX_STANDARD% ^
    -DCMAKE_C_COMPILER=%CMAKE_C_COMPILER% ^
    -DCMAKE_CXX_COMPILER=%CMAKE_CXX_COMPILER% ^
    -DCMAKE_MODULE_PATH=%OPENCOLORIO_CMAKE_FIND_MODULES_DIR% ^
    -DCMAKE_VERBOSE_MAKEFILE=%MMSOLVER_BUILD_VERBOSE% ^
    -DMMSOLVER_VFX_PLATFORM=%VFX_PLATFORM% ^
    -DMMSOLVERLIBS_CXXBRIDGE_EXE=%MMSOLVERLIBS_CXXBRIDGE_EXE% ^
    -DMMSOLVERLIBS_BUILD_TESTS=%MMSOLVERLIBS_BUILD_TESTS% ^
    -DMMSOLVERLIBS_LIB_DIR=%MMSOLVERLIBS_LIB_DIR% ^
    -Dldpk_URL=%LDPK_URL% ^
    -DOpenColorIO_DIR=%OPENCOLORIO_CMAKE_CONFIG_DIR% ^
    -DOCIO_INSTALL_EXT_PACKAGES=NONE ^
    -Dexpat_DIR=%expat_DIR% ^
    -Dexpat_LIBRARY=%expat_LIBRARY% ^
    -Dexpat_INCLUDE_DIR=%expat_INCLUDE_DIR% ^
    -Dexpat_USE_STATIC_LIBS=TRUE ^
    -Dpystring_LIBRARY=%pystring_LIBRARY% ^
    -Dpystring_INCLUDE_DIR=%pystring_INCLUDE_DIR% ^
    -Dyaml-cpp_DIR=%yaml_DIR% ^
    -Dyaml-cpp_LIBRARY=%yaml_LIBRARY% ^
    -Dyaml-cpp_INCLUDE_DIR=%yaml_INCLUDE_DIR% ^
    -DImath_DIR=%Imath_DIR% ^
    -DZLIB_LIBRARY=%ZLIB_LIBRARY% ^
    -DZLIB_INCLUDE_DIR=%ZLIB_INCLUDE_DIR% ^
    -DZLIB_STATIC_LIBRARY=ON ^
    -Dminizip-ng_DIR=%minizip_DIR% ^
    %MMSOLVERLIBS_ROOT%
if errorlevel 1 goto failed_to_generate_cpp

%CMAKE_EXE% --build . --parallel
if errorlevel 1 goto failed_to_build_cpp

%CMAKE_EXE% --install .
if errorlevel 1 goto failed_to_install_cpp

:: Return back project root directory.
CHDIR "%PROJECT_ROOT%"
exit /b 0

:failed_to_generate_cpp_header
echo Failed to Generate C++ header files from Rust.
exit /b 1

:failed_to_build_rust
echo Failed to build Rust code.
exit /b 1

:failed_to_generate_cpp
echo Failed to generate C++ build files.
exit /b 1

:failed_to_build_cpp
echo Failed to build C++ code.
exit /b 1

:failed_to_install_cpp
echo Failed to install C++ artifacts.
exit /b 1
