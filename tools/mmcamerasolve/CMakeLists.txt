# Copyright (C) 2026 David Cattermole.
#
# This file is part of mmSolver.
#
# mmSolver is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# mmSolver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
# ---------------------------------------------------------------------
#
# Install the mmcamerasolve executable, which is pre-built by Cargo
# (Rust build system) and installed into the module's bin directory.
#

if (MMSOLVER_BUILD_TOOLS)
  # The binary is produced by 'cargo build' in the same target
  # directory used for mmsolverlibs_rust.
  set(mmcamerasolve_src_name "mmcamerasolve${CMAKE_EXECUTABLE_SUFFIX}")
  set(mmcamerasolve_src_path "${mmsolverlibs_rust_DIR}/${mmcamerasolve_src_name}")

  # Needed for building on Windows... Normalise to forward slashes so
  # that CMake's install() does not interpret backslash sequences
  # (e.g. \U, \b) as escape characters when the path is embedded in
  # the generated cmake_install.cmake.
  file(TO_CMAKE_PATH "${mmcamerasolve_src_path}" mmcamerasolve_src_path)

  # The installed name follows the same convention as other tools.
  set(mmcamerasolve_install_name "mmsolver-camerasolve${CMAKE_EXECUTABLE_SUFFIX}")

  # Install the pre-built Rust binary directly from the Rust build
  # directory, renaming it at install time. The Rust binary is always
  # built by 'cargo build' before cmake runs, so the source file is
  # guaranteed to exist at install time.
  install(PROGRAMS "${mmcamerasolve_src_path}"
    DESTINATION "${MODULE_FULL_NAME}/bin"
    RENAME "${mmcamerasolve_install_name}")

  # Install CHOLMOD shared libraries so the binary and the Maya plugin
  # can find them at runtime.
  #
  # On Linux the libraries go into <module>/lib/ which is on the rpath
  # of both the binary (set via RUSTFLAGS at cargo build time) and the
  # Maya plugin (set via INSTALL_RPATH "$ORIGIN/../lib" in
  # MMSolverUtils.cmake).
  #
  # On Windows the DLLs go into <module>/bin/ alongside the executable
  # so that Windows DLL search finds them automatically.
  if (DEFINED CHOLMOD_LIB_DIR AND IS_DIRECTORY "${CHOLMOD_LIB_DIR}")
    set(_cholmod_libs
      cholmod
      amd
      camd
      colamd
      ccolamd
      suitesparseconfig
      openblas)

    if (UNIX AND NOT APPLE)
      # Install all versioned .so files (e.g. libcholmod.so,
      # libcholmod.so.5, libcholmod.so.5.3.0) so the dynamic linker
      # can resolve the SONAME embedded in the binary.
      foreach(_lib IN LISTS _cholmod_libs)
        file(GLOB _so_files "${CHOLMOD_LIB_DIR}/lib${_lib}.so*")
        if (_so_files)
          install(FILES ${_so_files}
            DESTINATION "${MODULE_FULL_NAME}/lib")
        endif ()
        unset(_so_files)
      endforeach ()
    endif ()

    if (WIN32 AND DEFINED CHOLMOD_BIN_DIR AND IS_DIRECTORY "${CHOLMOD_BIN_DIR}")
      foreach(_lib IN LISTS _cholmod_libs)
        find_file(_cholmod_dll_${_lib}
          NAMES "${_lib}.dll"
          PATHS "${CHOLMOD_BIN_DIR}"
          NO_DEFAULT_PATH)
        if (_cholmod_dll_${_lib})
          install(FILES "${_cholmod_dll_${_lib}}"
            DESTINATION "${MODULE_FULL_NAME}/bin")
        endif ()
        unset(_cholmod_dll_${_lib} CACHE)
      endforeach ()
    endif ()
  endif ()
endif ()
