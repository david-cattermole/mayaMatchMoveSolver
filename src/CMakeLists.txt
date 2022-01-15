# Copyright (C) 2019, 2020 David Cattermole.
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
# Building the C++ code for mmSolver.
#

# Explicitly enable features
set(CMAKE_MACOSX_RPATH 1)


# Default Solver to use.
set(PREFERRED_SOLVER "cminpack_lmder" CACHE STRING "Choices are cminpack_lm, cminpack_lmder or levmar. Which solver is used by default?")


# Set a default solver
set(DEFAULT_SOLVER ${PREFERRED_SOLVER})
if ((USE_GPL_LEVMAR EQUAL 1) AND (USE_CMINPACK EQUAL 1))
  # Support both levmar and cminpack.
elseif ((USE_CMINPACK EQUAL 1) AND (USE_GPL_LEVMAR EQUAL 0))
  if (NOT (DEFAULT_SOLVER MATCHES "cminpack_lm[a-zA-Z]+"))
    message(WARNING
      "Preferred solver cannot be used because it's not enabled. "
      "preferred=${PREFERRED_SOLVER} "
      "default=${DEFAULT_SOLVER} "
      "use_cminpack=${USE_CMINPACK} "
      "use_gpl_levmar=${USE_GPL_LEVMAR}"
      )
    set(DEFAULT_SOLVER "cminpack_lm")
  endif ()
elseif ((USE_GPL_LEVMAR EQUAL 1) AND (USE_CMINPACK EQUAL 0))
  if (NOT (DEFAULT_SOLVER STREQUAL "levmar"))
    message(WARNING
      "Preferred solver cannot be used because it's not enabled. "
      "preferred=${PREFERRED_SOLVER} "
      "default=${DEFAULT_SOLVER} "
      "use_cminpack=${USE_CMINPACK} "
      "use_gpl_levmar=${USE_GPL_LEVMAR}"
      )
    set(DEFAULT_SOLVER "levmar")
  endif ()
else ()
  message(FATAL_ERROR
    " Solver is not available! "
    "preferred=${PREFERRED_SOLVER} "
    "default=${DEFAULT_SOLVER} "
    "use_cminpack=${USE_CMINPACK} "
    "use_gpl_levmar=${USE_GPL_LEVMAR}"
    )
endif ()

# Source
set(SOURCE_FILES
  core/reprojection.cpp
  core/bundleAdjust_base.cpp
  core/bundleAdjust_relationships.cpp
  core/bundleAdjust_solveFunc.cpp
  core/bundleAdjust_levmar_bc_dif.cpp
  core/bundleAdjust_cminpack_base.cpp
  core/bundleAdjust_cminpack_lmdif.cpp
  core/bundleAdjust_cminpack_lmder.cpp
  core/calibrate/common.cpp
  core/calibrate/vanishingPoint.cpp
  core/mmcamera.cpp
  core/mmcoord.cpp
  core/mmdata.cpp
  core/mmmath.cpp
  Camera.cpp
  Marker.cpp
  Bundle.cpp
  Attr.cpp
  mayaUtils.cpp
  commonArgFlags.cpp
  MMCameraCalibrateNode.cpp
  MMLineIntersectNode.cpp
  MMSolverAffectsCmd.cpp
  MMMarkerScaleNode.cpp
  MMReprojectionNode.cpp
  MMMarkerGroupTransformNode.cpp
  MMTestCameraMatrixCmd.cpp
  MMSolverCmd.cpp
  MMSolverTypeCmd.cpp
  MMReprojectionCmd.cpp
  pluginMain.cpp
  )


# Find external packages
find_package(Maya REQUIRED)
# find_package(LevMar)
find_package(CMinpack)

# Treat warnings as errors.
if(MSVC)
  add_compile_options(/W4 /WX)
else()
  add_compile_options(-W -Wall -Werror -Wpedantic)
endif()

# Compile Flags.
#
# Release flags come from the Autodesk Maya build scripts (and
# Visual Studio project files).
if (MSVC)
  # For Visual Studio 11 2012
  set(CMAKE_CXX_FLAGS "")  # Zero out the C++ flags, we have complete control.
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /GS /Zc:wchar_t /Zi /fp:precise /Zc:forScope /GR /Gd /EHsc")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D \"OSWin_\" /D \"WIN32\" /D \"_WINDOWS\" /D \"_USRDLL\" /D \"NT_PLUGIN\"")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D \"_HAS_ITERATOR_DEBUGGING=0\" /D \"_SECURE_SCL=0\" /D \"_SECURE_SCL_THROWS=0\"")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D \"_SECURE_SCL_DEPRECATE=0\" /D \"_CRT_SECURE_NO_DEPRECATE\" /D \"TBB_USE_DEBUG=0\"")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D \"__TBB_LIB_NAME=tbb.lib\" /D \"Bits64_\" /D \"_WINDLL\"")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D \"NT_PLUGIN\" /D \"REQUIRE_IOSTREAM\"")

  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS} /D \"_DEBUG\"")
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /MDd /Gm /Od /RTC1")
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Ob0 /GR /GL /Oi /Gy /Zi /EHsc")

  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS} /D \"NDEBUG\"")
  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /Gy /Gm- /O2 /Ob1 /GF")

  # Must add the plug-in entry/exit points otherwise
  # the plug-in won't load.
  set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} /export:initializePlugin /export:uninitializePlugin")
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


include(MMSolverUtils)


# 'mmSolver' maya plugin library
if (APPLE)
  add_library(mmSolver MODULE ${SOURCE_FILES})
else ()
  add_library(mmSolver SHARED ${SOURCE_FILES})
endif ()
target_include_directories(mmSolver
  PRIVATE ../include
  PRIVATE .
  PUBLIC ${MAYA_INCLUDE_DIRS}
  )
target_link_libraries(mmSolver
  PUBLIC
  ${MAYA_OpenMaya_LIBRARY}
  ${MAYA_OpenMayaAnim_LIBRARY}
  ${MAYA_Foundation_LIBRARY}
  )

# if (USE_GPL_LEVMAR)
#   message(WARNING
#     "'levmar' library is licensed under GNU GPL and therefore this library "
#     "must not be distributed in binary form.")
#   target_include_directories(mmSolver PUBLIC ${LEVMAR_INCLUDE_DIRS})
#   target_link_libraries(mmSolver PUBLIC ${LEVMAR_LIBRARIES})
#   target_compile_definitions(mmSolver PRIVATE USE_SOLVER_LEVMAR)

#   if(CMAKE_SYSTEM_NAME STREQUAL Darwin)
#     # To locate Levmar from the mmSolver dynamic library we
#     # must change the "install name" to a path relative to the
#     # loaded bundle.
#     #
#     # Run:
#     # $ install_name_tool -change liblevmar.dylib @loader_path/../lib/liblevmar.dylib mmSolver.bundle
#     #
#     # NOTE: If ${LEVMAR_LIBRARIES} has more than one library,
#     #  this command will fail.
#     #
#     add_custom_command(TARGET mmSolver
#       POST_BUILD COMMAND
#       ${CMAKE_INSTALL_NAME_TOOL} -change ${LEVMAR_LIBRARIES} @loader_path/../lib/${LEVMAR_LIBRARIES}
#       $<TARGET_FILE:mmSolver>
#       )
#   endif()
# endif ()

if (USE_CMINPACK)
  target_include_directories(mmSolver PUBLIC ${CMINPACK_INCLUDE_DIRS})
  target_link_libraries(mmSolver PUBLIC ${CMINPACK_LIBRARIES})
  target_compile_definitions(mmSolver PRIVATE USE_SOLVER_CMINPACK)

  if(CMAKE_SYSTEM_NAME STREQUAL Darwin)
    # To locate CMinpack from the mmSolver dynamic library we
    # must change the "install name" to a path relative to the
    # loaded bundle.
    #
    # Run:
    # $ install_name_tool -change libcminpack.1.dylib @loader_path/../lib/libcminpack.1.dylib mmSolver.bundle
    #
    # NOTE: If ${CMINPACK_LIBRARIES} has more than one library,
    #  this command will fail.
    #
    get_filename_component(CMINPACK_LIBRARY_NAME ${CMINPACK_LIBRARIES} NAME)
    add_custom_command(TARGET mmSolver
      POST_BUILD COMMAND
      ${CMAKE_INSTALL_NAME_TOOL} -change ${CMINPACK_LIBRARY_NAME} @loader_path/../lib/${CMINPACK_LIBRARY_NAME}
      $<TARGET_FILE:mmSolver>
      )
  endif()
endif ()

# On Linux the 'm' library is required.
if(CMAKE_SYSTEM_NAME STREQUAL Linux)
  target_link_libraries(mmSolver PUBLIC m)
endif ()

# no 'lib' prefix to Maya plugin .so files
set_target_properties(mmSolver PROPERTIES PREFIX "")

# On Linux, the Maya Plug-In file extension is '.so'.
# On MacOS, the Maya Plug-In file extension is '.bundle'.
# On Windows, the Maya Plug-In file extension is '.mll', not '.dll'.
set(MAYA_PLUGIN_SUFFIX ".so")
if (APPLE)
  set(MAYA_PLUGIN_SUFFIX ".bundle")
elseif (WIN32)
  set(MAYA_PLUGIN_SUFFIX ".mll")
else()
  message(FATAL_ERROR "Only Linux, MacOS and Windows are supported.")
endif ()
set_target_properties(mmSolver PROPERTIES SUFFIX ${MAYA_PLUGIN_SUFFIX})

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
  set_target_properties(mmSolver PROPERTIES
    BUILD_WITH_INSTALL_RPATH ON
    INSTALL_RPATH "\$ORIGIN/../lib"
    )
endif ()

# Output to the Module plug-ins directory.
#
# On Windows, the Plug-In is treated as a 'RUNTIME' type,
# on Linux, it's a 'LIBRARY' type.
set_target_properties(mmSolver PROPERTIES
  RUNTIME_OUTPUT_DIRECTORY "${MODULE_FULL_NAME}"
  LIBRARY_OUTPUT_DIRECTORY "${MODULE_FULL_NAME}"
  ARCHIVE_OUTPUT_DIRECTORY "${MODULE_FULL_NAME}")

# Install the Plug-In.
install(TARGETS mmSolver
  RUNTIME DESTINATION "${MODULE_FULL_NAME}/plug-ins"
  LIBRARY DESTINATION "${MODULE_FULL_NAME}/plug-ins")


# Install dynamic libraries; cminpack
if (USE_CMINPACK AND CMINPACK_FOUND)
  if (WIN32)
    if (EXISTS ${CMINPACK_LIBRARY_DLL})
      install(FILES ${CMINPACK_LIBRARY_DLL}
        DESTINATION "${MODULE_FULL_NAME}/lib/")
    else ()
      install(FILES ${CMINPACK_LIBRARY}
        DESTINATION "${MODULE_FULL_NAME}/lib/")
    endif ()
  elseif (UNIX)
    # Install both symlink and real library
    get_filename_component(ABS_CMINPACK_LIBRARY ${CMINPACK_LIBRARY} REALPATH)
    install(FILES ${CMINPACK_LIBRARY}
      DESTINATION "${MODULE_FULL_NAME}/lib/")
    install(FILES ${ABS_CMINPACK_LIBRARY}
      DESTINATION "${MODULE_FULL_NAME}/lib/")
  endif ()
endif ()

# # Install dynamic libraries; levmar
# if (USE_GPL_LEVMAR AND LEVMAR_FOUND)
#   if (WIN32)
#     if (EXISTS ${LEVMAR_LIBRARY_DLL})
#       install(FILES ${LEVMAR_LIBRARY_DLL}
#         DESTINATION "${MODULE_FULL_NAME}/lib/")
#     else ()
#       install(FILES ${LEVMAR_LIBRARY}
#         DESTINATION "${MODULE_FULL_NAME}/lib/")
#     endif ()
#   elseif (UNIX)
#     # Install both symlink and real library
#     get_filename_component(ABS_LEVMAR_LIBRARY ${LEVMAR_LIBRARY} REALPATH)
#     install(FILES ${LEVMAR_LIBRARY}
#       DESTINATION "${MODULE_FULL_NAME}/lib/")
#     install(FILES ${ABS_LEVMAR_LIBRARY}
#       DESTINATION "${MODULE_FULL_NAME}/lib/")
#   endif ()
# endif ()
