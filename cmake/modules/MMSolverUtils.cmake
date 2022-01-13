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
  # Compile Flags.
  #
  # Release flags come from the Autodesk Maya build scripts (and
  # Visual Studio project files).
  if (MSVC)
    # For Visual Studio 11 2012
    set(CMAKE_CXX_FLAGS "")  # Zero out the C++ flags, we have complete control.
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /GS /Zc:wchar_t /Zi /fp:precise /Zc:forScope /GR /Gd /EHsc")

    add_definitions(/DOSWin_)
    add_definitions(/DWIN32)
    add_definitions(/D_WINDOWS)
    add_definitions(/D_USRDLL)
    add_definitions(/DNT_PLUGIN)
    add_definitions(/D_HAS_ITERATOR_DEBUGGING=0)
    add_definitions(/D_SECURE_SCL=0)
    add_definitions(/D_SECURE_SCL_THROWS=0)
    add_definitions(/D_SECURE_SCL_DEPRECATE=0)
    add_definitions(/D_CRT_SECURE_NO_DEPRECATE)
    add_definitions(/DTBB_USE_DEBUG=0)
    add_definitions(/D__TBB_LIB_NAME=tbb.lib)
    add_definitions(/D_WINDLL)
    add_definitions(/DBits64_)
    add_definitions(/DREQUIRE_IOSTREAM)
    add_definitions(/DNT_PLUGIN)

    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS} /D \"_DEBUG\"")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /MDd")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Gm /Od /RTC1")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Ob0 /GR /GL /Oi /Gy /Zi /EHsc")

    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS} /D \"NDEBUG\"")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /MD")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /Gy /Gm- /O2 /Ob1 /GF")

    # Ensure Google Logging does not use "ERROR" macro, because Windows
    # doesn't support it.
    add_compile_definitions(GLOG_NO_ABBREVIATED_SEVERITIES)

    add_definitions(/DGOOGLE_GLOG_DLL_DECL=)
    add_definitions(-DGFLAGS_DLL_DECL=)

    # Ceres running on Windows can trigger a MSVC warning:
    #
    # "Compiler Warning (level 3) C4996: Your code uses a function,
    # class member, variable, or typedef that's marked deprecated."
    #
    # To override this, we define "_CRT_NONSTDC_NO_DEPRECATE"
    #
    # https://docs.microsoft.com/en-us/previous-versions/ms235384(v=vs.100)
    add_compile_definitions(_CRT_NONSTDC_NO_DEPRECATE)

    # # Must add the plug-in entry/exit points otherwise
    # # the plug-in won't load.
    # set(CMAKE_SHARED_LINKER_FLAGS
    #   "${CMAKE_SHARED_LINKER_FLAGS} /export:initializePlugin /export:uninitializePlugin")

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
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DCC_GNU_ -DOSMac_ -DOSMacOSX_ -DOSMac_MachO_ -D_LANGUAGE_C_PLUS_PLUS -mmacosx-version-min=10.8")

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
    set(CMAKE_CXX_FLAGS "")  # Zero out the C++ flags, we have complete control.
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-multichar -Wno-comment -Wno-sign-compare")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -funsigned-char -pthread -fopenmp")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DBits64_ -DUNIX -D_BOOL -DLINUX -DFUNCPROTO -D_GNU_SOURCE -DLINUX_64 -DREQUIRE_IOSTREAM")
    # '-ftemplate-depth-27', rather than '25' is required to compile under GCC 4.8.5.
    # '-ftemplate-depth-35', rather than '25' is required to compile under GCC 5.5.x.
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-deprecated -Wno-reorder -ftemplate-depth-35 -fno-gnu-keywords")
    set(CMAKE_CXX_FLAGS_DEBUG "-O0 -g")
    set(CMAKE_CXX_FLAGS_RELEASE "-O3 -fPIC -fno-strict-aliasing -m64")
  endif ()
endfunction()


function(add_target_link_library_names target names)
    string(STRIP ${names} names_strip)
    string(REPLACE " " ";" names_list ${names_strip})
    foreach (name IN LISTS names_list)
        target_link_libraries(${target} ${name})
    endforeach ()
endfunction()


function(set_target_maya_plugin_compile_options target)
  # Must add the plug-in entry/exit points otherwise
  # the plug-in won't load.
  set_target_properties(${target} PROPERTIES
    LINK_FLAGS "/export:initializePlugin /export:uninitializePlugin")
endfunction()


function(set_target_as_maya_plugin_library target)
  # no 'lib' prefix to Maya plugin .so files
  set_target_properties(${target} PROPERTIES PREFIX "")

  # On Linux, the Maya Plug-In file extension is '.so'.
  # On MacOS, the Maya Plug-In file extension is '.bundle'.
  # On Windows, the Maya Plug-In file extension is '.mll', not '.dll'.
  set(maya_plugin_suffix ".so")
  if (APPLE)
    set(maya_plugin_suffix ".bundle")
  elseif (WIN32)
    set(maya_plugin_suffix ".mll")
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


# Install the Plug-In.
function(install_target_plugin_to_module target module_dir)
  set_target_as_maya_plugin_library(${target})

  if(CMAKE_SYSTEM_NAME STREQUAL Linux)
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
    RUNTIME DESTINATION "${MODULE_FULL_NAME}/plug-ins"
    LIBRARY DESTINATION "${MODULE_FULL_NAME}/plug-ins")
endfunction()


# Install shared (dynamic) library.
function(install_library lib_file lib_file_dll install_dir)
  # message(STATUS "INSTALL FILE: ${lib_file}")
  # message(STATUS "INSTALL DLL: ${lib_file_dll}")
  # message(STATUS "INSTALL DIR: ${install_dir}")
  if (WIN32)
    if (EXISTS ${lib_file_dll})
      install(FILES ${lib_file_dll}
        DESTINATION ${install_dir})
    else ()
      message(FATAL_ERROR "Cannot find .dll file to install: ${lib_file_dll}")
    endif ()
  elseif (UNIX)
    # Install both symlink and real library
    get_filename_component(absolute_lib_file ${lib_file} REALPATH)
    install(FILES ${lib_file} DESTINATION ${install_dir})
    install(FILES ${absolute_lib_file} DESTINATION ${install_dir})
  endif ()
endfunction()


# Install many shared (dynamic) libraries.
function(install_libraries lib_files lib_files_dll install_dir)
  # message(STATUS "INSTALL FILES: ${lib_files}")
  # message(STATUS "INSTALL DLLS: ${lib_files_dll}")
  # message(STATUS "INSTALL DIR: ${install_dir}")

  string(STRIP "${lib_files}" lib_files_strip)
  string(STRIP "${lib_files_dll}" lib_files_dll_strip)

  string(REPLACE " " ";" lib_files_list "${lib_files_strip}")
  string(REPLACE " " ";" lib_files_dll_list "${lib_files_dll_strip}")

  list(LENGTH lib_files_list len1)
  math(EXPR len2 "${len1} - 1")

  foreach(val RANGE ${len2})
    list(GET lib_files_list ${val} lib_file)
    list(GET lib_files_dll_list ${val} lib_file_dll)

    install_library(
      ${lib_file}
      ${lib_file_dll}
      ${install_dir})
  endforeach ()
endfunction()
