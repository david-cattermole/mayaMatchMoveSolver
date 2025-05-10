# Copyright (C) 2020, 2024 David Cattermole.
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
                libexec/   # Maya 2025 on Linux changed the directory.
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
            libexec/  # Maya 2025 on Linux changed the directory.
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

# Find the Ceres "miniglog" include from looking up the Ceres include
# path.
function(find_ceres_miniglog_include_dir output_var)
  get_target_property(ceres_include_dirs ceres INTERFACE_INCLUDE_DIRECTORIES)
  # An example of "${ceres_include_dirs}" is:
  # /build_mmsolver/cmake_linux_maya2025_Release/ext/install/ceres/include
  #
  # ... where the "glog/logging.h" file can be found is:
  # /build_mmsolver/cmake_linux_maya2025_Release/ext/install/ceres/include/ceres/internal/miniglog/glog/logging.h
  #
  # ...and in this case the "${output_var}" value would be:
  # /build_mmsolver/cmake_linux_maya2025_Release/ext/install/ceres/include/ceres/internal/miniglog/

  # It's not great that we need to hard-code this sub-path rather than
  # using CMake's 'find_path', however the problem with using
  # 'find_path' is that find_path is run during the CMake build
  # generation phase *not* when actually compiling. This means
  # 'find_path' works fine but only if ceres is already built, which
  # cannot happen until the 'miniglog' include is found - so it's a
  # "chicken and egg" situation.
  set(${output_var} "${ceres_include_dirs}/ceres/internal/miniglog/" PARENT_SCOPE)
endfunction()
