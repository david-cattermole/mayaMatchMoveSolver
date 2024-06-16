# Copyright (C) 2020 David Cattermole.
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
# CMake utilities for mmSolver.
#


function(set_global_maya_plugin_compile_options)

  if(CMAKE_BUILD_TYPE EQUAL "Release")
    add_compile_definitions(NDEBUG)
  elseif (CMAKE_BUILD_TYPE EQUAL "Debug")
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
    #
    # NOTE: This changes the ABI.
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
    #
    # NOTE: This changes the ABI.
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

  elseif (APPLE)

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

  else ()
    # For Linux with GCC

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

    # Use the older C++11 ABI for std::string and std::list, to be
    # compatible with RHEL/CentOS 7, Maya and the VFX Platform.
    #
    # https://vfxplatform.com/#footnote-gcc6
    #
    # In VFX Platform CY2023, and the move to RHEL 8 or RHEL 9,
    # the new default is to use "_GLIBCXX_USE_CXX11_ABI=1".
    #
    # https://vfxplatform.com/#footnote-gcc9
    #
    # NOTE: This changes the ABI.
    if (VFX_PLATFORM VERSION_GREATER_EQUAL 2023)
      # Must be enabled for RHEL 8/9, Alma Linux and Rocky Linux 8/9.
      add_compile_definitions(_GLIBCXX_USE_CXX11_ABI=1)
    else ()
      add_compile_definitions(_GLIBCXX_USE_CXX11_ABI=0)
    endif()

    # Enable warnings.
    add_definitions(-Wall)
    add_definitions(-Wno-multichar)
    add_definitions(-Wno-comment)
    add_definitions(-Wno-sign-compare)
    add_definitions(-Wno-unused-parameter)
    add_definitions(-Wno-unused-parameter)
    add_definitions(-Wno-unused-variable)
    add_definitions(-Wno-unused-private-field)
    add_definitions(-Wno-deprecated)
    add_definitions(-Wno-reorder)

    # GCC Features
    add_definitions(-pthread)
    add_definitions(-fopenmp)
    add_definitions(-fvisibility=hidden)
    add_definitions(-funsigned-char)
    add_definitions(-fno-gnu-keywords)
    add_definitions(-fno-strict-aliasing)

    # '-ftemplate-depth-27' is required to compile under GCC 4.8.5.
    # '-ftemplate-depth-35' is required to compile under GCC 5.5.x.
    #
    # In GCC 6.3.x, with C++11 the default depth is set to 900, but
    # the C++11 standard says 1024 is the default.
    add_definitions(-ftemplate-depth-900)

    set(CMAKE_CXX_FLAGS_DEBUG "-O0")  # No optmizations.
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g")  # Include debug symbols

    # Enable AddressSanitizer.
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -fsanitize=address")

    # Nicer stack traces in error messages
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -fno-omit-frame-pointer")

    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3")  # Optimize for maximum performance.
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -m64")  # Set 64-bit machine.
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -march=skylake")   # Use AVX2 instructions

  endif ()
endfunction()


function(set_global_treat_warnings_as_errors)
  if(MSVC)
    add_compile_options(/WX)
  else()
    add_compile_options(-Werror)
  endif()
endfunction()


function(add_library_maya_plugin target source_files)
  if (APPLE)
    add_library(${target} MODULE "${source_files}")
  else ()
    add_library(${target} SHARED "${source_files}")
  endif ()
endfunction()


function(set_target_maya_plugin_compile_options target)
  # Must add the plug-in entry/exit points otherwise
  # the plug-in won't load.
  if (MSVC)
    set_target_properties(${target} PROPERTIES
      LINK_FLAGS "/export:initializePlugin /export:uninitializePlugin")
  endif()
endfunction()


function(set_target_as_maya_plugin_library target)
  # no 'lib' prefix to Maya plugin .so files
  set_target_properties(${target} PROPERTIES PREFIX "")

  # On Linux, the Maya Plug-In file extension is '.so'.
  # On MacOS, the Maya Plug-In file extension is '.bundle'.
  # On Windows, the Maya Plug-In file extension is '.mll', not '.dll'.
  set(maya_plugin_suffix "")
  if (APPLE)
    set(maya_plugin_suffix ".bundle")
  elseif (WIN32)
    set(maya_plugin_suffix ".mll")
  elseif (UNIX)
    set(maya_plugin_suffix ".so")
  else()
    message(FATAL_ERROR "Only Linux, MacOS and Windows are supported.")
  endif ()
  set_target_properties(${target} PROPERTIES SUFFIX ${maya_plugin_suffix})
endfunction()


# Output the target to the Module plug-ins directory.
function(install_target_to_module target module_dir)
  install(TARGETS ${target}
    RUNTIME DESTINATION "${module_dir}/lib"
    LIBRARY DESTINATION "${module_dir}/lib")
endfunction()


# Get the build operating system name, to be used when constructing
# build paths.
function(get_maya_module_os_name output_var)
  set(${output_var} unknown PARENT_SCOPE)
  if(CMAKE_SYSTEM_NAME STREQUAL Darwin)
    set(${output_var} mac PARENT_SCOPE)
  elseif(CMAKE_SYSTEM_NAME STREQUAL Linux)
    set(${output_var} linux PARENT_SCOPE)
  elseif(CMAKE_SYSTEM_NAME STREQUAL Windows)
    set(${output_var} win64 PARENT_SCOPE)
  else ()
    message(FATAL_ERROR "Only Linux, MacOS and Windows are supported.")
  endif ()
endfunction()


# Install the Plug-In.
function(install_target_plugin_to_module target module_dir)
  set_target_as_maya_plugin_library(${target})

  if(CMAKE_SYSTEM_NAME STREQUAL Linux)
    # This allows Linux to find the dynamic libraries at runtime.
    #
    # HACK: On Linux, LD_LIBRARY_PATH cannot be modified at runtime (on
    # Windows it can), therefore the .mod files *can* change
    # LD_LIBRARY_PATH, but the changes are not used by 'ld.so', which
    # resolves the library path. Therefore, to make sure the the libraries
    # in <module root>/lib are searched for libraries, we add a relative
    # directory 'RPATH' to the library which tells the library resolution
    # to search in the 'lib' directory inside the module root. Note: Linux
    # does not allow run-time changes for security reasons.

    # We must escape the '$' symbol to make sure it is passed to the
    # compiler.
    set_target_properties(${target} PROPERTIES
      BUILD_WITH_INSTALL_RPATH ON
      INSTALL_RPATH "\$ORIGIN/../lib"
      )
  endif ()

  # On Windows, the Plug-In is treated as a 'RUNTIME' type,
  # on Linux, it's a 'LIBRARY' type.
  set_target_properties(${target} PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${module_dir}"
    LIBRARY_OUTPUT_DIRECTORY "${module_dir}"
    ARCHIVE_OUTPUT_DIRECTORY "${module_dir}")

  install(TARGETS ${target}
    RUNTIME DESTINATION "${module_dir}/plug-ins"
    LIBRARY DESTINATION "${module_dir}/plug-ins")
endfunction()


# Install executables.
function(install_target_executable_to_module target module_dir)
  set_target_properties(${target} PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${module_dir}")

  install(TARGETS ${target}
    RUNTIME DESTINATION "${module_dir}/bin")
endfunction()


# Install shared (dynamic) library.
function(install_shared_library lib_file lib_file_dll install_dir)
  # message(STATUS "install_shared_library install file: ${lib_file}")
  # message(STATUS "install_shared_library install dll : ${lib_file_dll}")
  # message(STATUS "install_shared_library install dir : ${install_dir}")
  if (WIN32)
    if (EXISTS ${lib_file_dll})
      install(FILES ${lib_file_dll}
        DESTINATION ${install_dir})
    else ()
      message(FATAL_ERROR "Cannot find .dll file to install: ${lib_file_dll}")
    endif ()
  elseif (UNIX)
    string(FIND ${lib_file} ".so" find_so)
    if(${find_so} GREATER_EQUAL 0)
      # message(STATUS "install_shared_library lib_file     : ${lib_file}")

      # Install only the real library, with the original name.
      get_filename_component(abs_lib_file ${lib_file} REALPATH)
      get_filename_component(lib_file_name ${lib_file} NAME)
      # message(STATUS "install_shared_library abs_lib_file : ${abs_lib_file}")
      # message(STATUS "install_shared_library lib_file_name: ${lib_file_name}")
      install(FILES ${abs_lib_file}
        DESTINATION ${install_dir}
        RENAME ${lib_file_name}
      )

      # # Copies all files similar to ${lib_file} to the install
      # # directory.
      # file(GLOB lib_files
      #   LIST_DIRECTORIES 0
      #   "${lib_file}*")
      # install(FILES ${lib_files} DESTINATION ${install_dir})
    endif ()
  endif ()
endfunction()


function(install_shared_library_with_name lib_file lib_file_dll lib_name install_dir)
  # message(STATUS "install_shared_library install file: ${lib_file}")
  # message(STATUS "install_shared_library install dll : ${lib_file_dll}")
  # message(STATUS "install_shared_library install name: ${lib_name}")
  # message(STATUS "install_shared_library install dir : ${install_dir}")
  if (WIN32)
    if (EXISTS ${lib_file_dll})
      install(FILES ${lib_file_dll}
        DESTINATION ${install_dir})
    else ()
      message(FATAL_ERROR "Cannot find .dll file to install: ${lib_file_dll}")
    endif ()
  elseif (UNIX)
    string(FIND ${lib_file} ".so" find_so)
    if(${find_so} GREATER_EQUAL 0)
      # message(STATUS "install_shared_library lib_file     : ${lib_file}")

      # Install only the real library, with the original name.
      get_filename_component(abs_lib_file ${lib_file} REALPATH)
      get_filename_component(lib_file_name ${lib_file} NAME)
      # message(STATUS "install_shared_library abs_lib_file : ${abs_lib_file}")

      install(FILES ${abs_lib_file}
        DESTINATION ${install_dir}
        RENAME ${lib_name}
      )
    endif ()
  endif ()
endfunction()


# Install many shared (dynamic) libraries.
function(install_shared_libraries lib_files lib_files_dll install_dir)
  # message(STATUS "INSTALL FILES: ${lib_files}")
  # message(STATUS "INSTALL DLLS : ${lib_files_dll}")
  # message(STATUS "INSTALL DIR  : ${install_dir}")

  string(STRIP "${lib_files}" lib_files_strip)
  string(STRIP "${lib_files_dll}" lib_files_dll_strip)

  string(REPLACE " " ";" lib_files_list "${lib_files_strip}")
  string(REPLACE " " ";" lib_files_dll_list "${lib_files_dll_strip}")

  list(LENGTH lib_files_list len1)
  math(EXPR len2 "${len1} - 1")

  foreach(val RANGE ${len2})
    list(GET lib_files_list ${val} lib_file)
    list(GET lib_files_dll_list ${val} lib_file_dll)

    install_shared_library(
      ${lib_file}
      ${lib_file_dll}
      ${install_dir})
  endforeach ()
endfunction()


# Compile a .ui file into a .py file using 'mayapy' command.
function(compile_qt_ui_to_python_file
         name
         input_file
         output_file)
    if(MAYA_VERSION GREATER_EQUAL 2022)
        find_package(Maya REQUIRED)
        # Maya 2022 and above. Use Maya provided 'uic' executable to
        # compile .ui files into .py files. Earlier versions of Maya
        # can only compile to C++ code with 'uic'.
        find_program(MAYA_QT_UIC_EXECUTABLE
                uic
            HINTS
                "${MAYA_LOCATION}"
                "$ENV{MAYA_LOCATION}"
                "${MAYA_BASE_DIR}"
            PATH_SUFFIXES
                MacOS/
                bin/
            DOC
                "Maya provided Qt 'uic' executable path"
                )

        get_filename_component(output_directory ${output_file} DIRECTORY)

        # Runs 'uic -g python <ui_file> -o <output_python_file>'
        add_custom_command(
                OUTPUT
                    ${output_file}
                    # file_never_exist.txt  # force re-run.
                COMMAND ${CMAKE_COMMAND} -E make_directory ${output_directory}
                COMMAND ${MAYA_QT_UIC_EXECUTABLE} -g python ${input_file} -o ${output_file}
                WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
                DEPENDS ${input_file}
        )
        add_custom_target(
                compile_ui_${name} ALL
                DEPENDS ${output_file}
                COMMENT "Compiling Qt UI file (${input_file})..."
        )
    else ()
        # Use the Maya Python environment to compile the .ui files
        # into .py files.
        set(EXEC_SCRIPT ${CMAKE_SOURCE_DIR}/scripts/internal/compileUI.py)
        add_custom_command(
                OUTPUT
                    ${output_file}
                    # file_never_exist.txt  # force re-run.
                COMMAND ${MAYA_PYTHON_EXECUTABLE} ${EXEC_SCRIPT} ${input_file}
                WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
                DEPENDS ${input_file}
        )
        add_custom_target(
                compile_ui_${name} ALL
                DEPENDS ${output_file}
                COMMENT "Compiling Qt UI file (${input_file})..."
        )
    endif ()
    if (BUILD_PLUGIN)
        add_dependencies(mmSolver compile_ui_${name})
    endif ()
endfunction()


function(compile_qt_resources_qrc_to_rcc_file
         name
         input_file
         output_file)
    find_package(Maya REQUIRED)
    # This section sets a hard location to the rcc
    # executable file to prevent any errors of
    # likes of 'rcc command not found'
    find_program(MAYA_RCC_EXECUTABLE
            rcc
        HINTS
            "${MAYA_LOCATION}"
            "$ENV{MAYA_LOCATION}"
            "${MAYA_BASE_DIR}"
        PATH_SUFFIXES
            MacOS
            bin3/  # Use Python 3.x location, in Maya 2022.
            bin/
        DOC
            "Maya's Qt resource compiler (rcc) executable path"
    )

    # message(STATUS "Qt Resources file: ${output_file}")
    add_custom_command(
            OUTPUT ${output_file}
            COMMAND ${MAYA_RCC_EXECUTABLE} -binary ${input_file} -o ${output_file}
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
            DEPENDS ${input_file}
    )
    add_custom_target(
            compile_rcc_${name} ALL
            DEPENDS ${output_file}
            COMMENT "Building Icons (with Qt Resource Compiler) (${input_file})..."
    )
endfunction()
