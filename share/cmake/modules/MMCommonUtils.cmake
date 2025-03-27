# Copyright (C) 2020, 2021, 2023, 2024, 2025 David Cattermole.
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
# CMake common utilities for mmSolver.
#


function(mm_common_apple_clang_set_global_compile_options)
  # For MacOS with Clang (which is the supported compiler for Maya
  # 2018+)
  set(CMAKE_CXX_FLAGS "")  # Zero out the C++ flags, we have complete control.
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -arch x86_64")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x  -stdlib=libc++")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-multichar -Wno-comment -Wno-sign-compare")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-deprecated -Wno-reorder")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -ftemplate-depth-35 -fno-gnu-keywords")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -funsigned-char -fpascal-strings") #  -pthread
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DCC_GNU_")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DOSMac_")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DOSMacOSX_")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DOSMac_MachO_")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D_LANGUAGE_C_PLUS_PLUS")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -mmacosx-version-min=10.8")

  # Special MacOS linking stuff
  set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk")
  set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -headerpad_max_install_names")
  set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -framework System")
  set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -framework SystemConfiguration")
  set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -framework CoreServices")
  set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -framework Carbon")
  set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -framework Cocoa")
  set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -framework ApplicationServices")
  set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -framework IOKit")
  set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -bundle")

  set(CMAKE_CXX_FLAGS_DEBUG "-O0 -g")
  set(CMAKE_CXX_FLAGS_RELEASE "-O3 -fPIC -fno-strict-aliasing -m64")
endfunction()


function(mm_common_windows_msvc_set_global_compile_options)
  # For Visual Studio 11 2012
  set(CMAKE_CXX_FLAGS "")  # Zero out the C++ flags, we have complete control.
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /GS")          # Buffer Security Check
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /Zc:wchar_t")  # wchar_t Is Native Type
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /Zi")          # Separate .pdb debug info file.
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /fp:precise")  # Precise floating-point behavior
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /Zc:forScope") # Force Conformance in for Loop Scope
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /GR")          # Enable Run-Time Type Information
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /Gd")          # __cdecl Calling Convention
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /EHsc")        # Handle standard C++ Exceptions.
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /W4")          # Warning Levels 1-4 enabled.

  add_compile_definitions(OSWin_)
  add_compile_definitions(WIN32)
  add_compile_definitions(_WINDOWS)
  add_compile_definitions(_USRDLL)
  add_compile_definitions(NT_PLUGIN)
  add_compile_definitions(_HAS_ITERATOR_DEBUGGING=0)
  add_compile_definitions(_SECURE_SCL=0)
  add_compile_definitions(_SECURE_SCL_THROWS=0)
  add_compile_definitions(_SECURE_SCL_DEPRECATE=0)
  add_compile_definitions(_CRT_SECURE_NO_DEPRECATE)
  add_compile_definitions(_CRT_SECURE_NO_WARNINGS)
  add_compile_definitions(TBB_USE_DEBUG=0)
  add_compile_definitions(__TBB_LIB_NAME=tbb.lib)
  add_compile_definitions(_WINDLL)
  add_compile_definitions(Bits64_)
  add_compile_definitions(REQUIRE_IOSTREAM)
  add_compile_definitions(NT_PLUGIN)
  add_compile_definitions(USERDLL)

  # Use multithread-specific Run-Time Library.
  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS} /MD")

  add_compile_options("/arch:AVX2")

  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /Gy")  # Enable Function-Level Linking
  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /GF")  # Eliminate Duplicate Strings
  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /O2")  # Optimize for Maximize Speed
  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /Oi")  # Generate Intrinsic Functions
  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /GL")  # Whole program optimization
  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /arch:AVX2")  # Use AVX2 instructions

  # Link-time code generation.
  #
  # /LTGC and /GL work together and therefore are both enabled.
  set(CMAKE_EXE_LINKER_FLAGS_RELEASE "${CMAKE_EXE_LINKER_FLAGS_RELEASE} /LTCG")
  set(CMAKE_SHARED_LINKER_FLAGS_RELEASE "${CMAKE_SHARED_LINKER_FLAGS_RELEASE} /LTCG")
  set(CMAKE_MODULE_LINKER_FLAGS_RELEASE "${CMAKE_MODULE_LINKER_FLAGS_RELEASE} /LTCG")

  # Use debug-specific Run-Time Library.
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS} /MDd")

  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Od")    # Optimize for Debug.
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /RTC1")  # Run-time error checks
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Ob0")   # Disables inline expansions.
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /GR")    # Enable Run-Time Type Information
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /GL")    # Whole program optimization
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Oi")    # Generate Intrinsic Functions
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Gy")    # Enable Function-Level Linking
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Zi")    # Debug Information Format
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /EHsc")  # Handle standard C++ Exceptions.
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /analyze")  # Code analysis

  # Ensure Google Logging does not use "ERROR" macro, because Windows
  # doesn't support it.
  add_compile_definitions(GLOG_NO_ABBREVIATED_SEVERITIES)

  # Ceres running on Windows can trigger a MSVC warning:
  #
  # "Compiler Warning (level 3) C4996: Your code uses a function,
  # class member, variable, or typedef that's marked deprecated."
  #
  # To override this, we define "_CRT_NONSTDC_NO_DEPRECATE"
  #
  # https://docs.microsoft.com/en-us/previous-versions/ms235384(v=vs.100)
  add_compile_definitions(_CRT_NONSTDC_NO_DEPRECATE)
endfunction()


# For Linux with GCC
function(mm_common_linux_gcc_set_cxx11_abi)

  if(NOT DEFINED MMSOLVER_VFX_PLATFORM)
    message(FATAL_ERROR "Please define the VFX_PLATFORM variable (eg. with '-DVFX_PLATFORM=2020').")
  endif()

  # Use the older C++11 ABI for std::string and std::list, to be
  # compatible with RHEL/CentOS 7, Maya and the VFX Platform.
  #
  # https://vfxplatform.com/#footnote-gcc6
  #
  # In VFX Platform CY2023, and the move to RHEL 8 or RHEL 9,
  # the new default is to use "_GLIBCXX_USE_CXX11_ABI=1".
  #
  # https://vfxplatform.com/#footnote-gcc9
  if (MMSOLVER_VFX_PLATFORM VERSION_GREATER_EQUAL 2023)
    # Must be enabled for RHEL 8/9, Alma Linux and Rocky Linux 8/9.
    add_compile_definitions(_GLIBCXX_USE_CXX11_ABI=1)
  else ()
    add_compile_definitions(_GLIBCXX_USE_CXX11_ABI=0)
  endif()

endfunction()


# For Linux with GCC
function(mm_common_linux_gcc_set_global_compile_options)

  # Definitions
  add_compile_definitions(Bits64_)
  add_compile_definitions(UNIX)
  add_compile_definitions(_BOOL)
  add_compile_definitions(LINUX)
  add_compile_definitions(linux)
  add_compile_definitions(__linux__)
  add_compile_definitions(OSLinux_)
  add_compile_definitions(FUNCPROTO)
  add_compile_definitions(_GNU_SOURCE)
  add_compile_definitions(LINUX_64)
  add_compile_definitions(REQUIRE_IOSTREAM)

  # Enable warnings.
  add_compile_options(-Wall)
  add_compile_options(-Wno-multichar)
  add_compile_options(-Wno-comment)
  add_compile_options(-Wno-sign-compare)
  add_compile_options(-Wno-unused-parameter)
  add_compile_options(-Wno-unused-parameter)
  add_compile_options(-Wno-unused-variable)
  add_compile_options(-Wno-unused-private-field)
  add_compile_options(-Wno-deprecated)
  add_compile_options(-Wno-reorder)

  # GCC Features
  add_compile_options(-pthread)
  add_compile_options(-fopenmp)
  add_compile_options(-fvisibility=hidden)
  add_compile_options(-funsigned-char)
  add_compile_options(-fno-gnu-keywords)
  add_compile_options(-fno-strict-aliasing)

  mm_common_linux_gcc_set_cxx11_abi()

  # How how many levels of 'depth' can templates use until the depth
  # is too high?
  #
  # If this value is too high compile times will be too slow.
  #
  # '-ftemplate-depth-27' is required to compile under GCC 4.8.5.
  # '-ftemplate-depth-35' is required to compile under GCC 5.5.x.
  #
  # In GCC 6.3.x, with C++11 the default depth is set to 900, but
  # the C++11 standard says 1024 is the default.
  add_compile_options(-ftemplate-depth-900)

  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -O0")  # No optmizations.
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g")  # Include debug symbols

  # Enable AddressSanitizer.
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -fsanitize=address")

  # Nicer stack traces in error messages
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -fno-omit-frame-pointer")

  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3")  # Optimize for maximum performance.
  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -m64")  # Set 64-bit machine.
  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -march=skylake")   # Use AVX2 instructions
endfunction()

function(mm_common_set_global_compile_options mmsolver_debug)

  if (mmsolver_debug)
    add_compile_definitions(MMSOLVER_DEBUG)
  endif ()

  if (CMAKE_BUILD_TYPE EQUAL "Debug")
    add_compile_definitions(_DEBUG)
  endif ()

  # Compile Flags.
  #
  # TODO: Make this function take a target and set the compile
  # arguments per-target.
  #
  # Release flags come from the Autodesk Maya build scripts (and
  # Visual Studio project files).
  if (MSVC)
    mm_common_windows_msvc_set_global_compile_options()
  elseif (APPLE)
    mm_common_apple_clang_set_global_compile_options()
  else ()
    mm_common_linux_gcc_set_global_compile_options()
  endif ()
endfunction()


function(mm_common_set_global_treat_warnings_as_errors)
  if(MSVC)
    add_compile_options(/WX)
  else()
    add_compile_options(-Werror)
  endif()
endfunction()


macro(mm_common_set_relative_library_rpath target relative_path)
  # HACK: We must change the RPATH variable for the library so that a
  # binary can find the shared object, even if it's not in the
  # $LD_LIBRARY_PATH.
  if (UNIX)
    # We must escape the '$' symbol to make sure it is passed to the
    # compiler.
    set_target_properties(${target} PROPERTIES
      BUILD_WITH_INSTALL_RPATH ON
      INSTALL_RPATH "\$ORIGIN/${relative_path}"
    )
  endif ()
endmacro()


macro(mm_common_set_rpath_to_cwd target)
  # HACK: We must change the RPATH variable for the library so that a
  # binary can find the shared object, even if it's not in the
  # $LD_LIBRARY_PATH.
  if (UNIX)
    # We must escape the '$' symbol to make sure it is passed to the
    # compiler.
    set_target_properties(${target} PROPERTIES
      BUILD_WITH_INSTALL_RPATH ON
      INSTALL_RPATH "\$ORIGIN/."
    )
  endif ()
endmacro()


function(mm_common_add_target_link_library_names target names)
  string(STRIP ${names} names_strip)
  string(REPLACE " " ";" names_list ${names_strip})
  foreach (name IN LISTS names_list)
    target_link_libraries(${target} ${name})
  endforeach ()
endfunction()


macro(mm_common_install_target_library target_name target_release_lib_name)
  include(GNUInstallDirs)
  install(TARGETS ${target_release_lib_name}
    EXPORT ${target_name}Targets
  )
endmacro()


function(mm_common_add_install_target target_name cmake_config_template_file)
  include(GNUInstallDirs)

  # Generate CMake Targets file.
  install(EXPORT ${target_name}Targets
    FILE ${target_name}Targets.cmake
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/${target_name}"
    NAMESPACE ${target_name}::
  )

  # Generate and install a CMake target config files.
  include(CMakePackageConfigHelpers)
  configure_package_config_file(${cmake_config_template_file}
    "${CMAKE_CURRENT_BINARY_DIR}/${target_name}Config.cmake"
    INSTALL_DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/${target_name}"
  )
  write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/${target_name}ConfigVersion.cmake"
    VERSION ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
    COMPATIBILITY AnyNewerVersion
  )
  install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/${target_name}Config.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/${target_name}ConfigVersion.cmake"
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/${target_name}")
  export(EXPORT ${target_name}Targets
    FILE "${CMAKE_INSTALL_LIBDIR}/${target_name}Targets.cmake"
  )
endfunction()


# Copy the compile_commands.json file to the root of the project, for
# use with clang-tidy.
#
# clang-tidy will look for a 'compile_commands.json' in the parent
# directory recursively from the source file it is parsing. This
# allows clang-tidy to find the exact flags used to compile the source
# file.
#
# https://stackoverflow.com/questions/57464766/copy-compile-commands-json-to-project-root-folder
function(mm_common_setup_clang_tidy_compile_commands binary_dir source_dir)
  if (CMAKE_EXPORT_COMPILE_COMMANDS)
    add_custom_target(
      copy-compile-commands ALL
      ${CMAKE_COMMAND} -E copy_if_different
      ${binary_dir}/compile_commands.json
      ${source_dir}
    )
  endif()
endfunction()
