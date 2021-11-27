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
set(PREFERRED_SOLVER "cminpack_lmder"
  CACHE STRING
  "Choices are cminpack_lm, cminpack_lmder or ceres. Which solver is used by default?")


# Set a default solver
set(DEFAULT_SOLVER ${PREFERRED_SOLVER})

# Source
set(SOURCE_FILES
  core/reprojection.cpp
  core/bundleAdjust_base.cpp
  core/bundleAdjust_relationships.cpp
  core/bundleAdjust_solveFunc.cpp
  core/bundleAdjust_cminpack_base.cpp
  core/bundleAdjust_cminpack_lmdif.cpp
  core/bundleAdjust_cminpack_lmder.cpp
  Camera.cpp
  Marker.cpp
  Bundle.cpp
  Attr.cpp
  commonArgFlags.cpp
  MMSolverAffectsCmd.cpp
  MMMarkerScaleNode.cpp
  MMReprojectionNode.cpp
  MMMarkerGroupTransformNode.cpp
  MMTestCameraMatrixCmd.cpp
  MMSolverCmd.cpp
  MMSolverTypeCmd.cpp
  MMReprojectionCmd.cpp
  MMCameraSolveCmd.cpp
  pluginMain.cpp
)


# Find external packages
find_package(Maya REQUIRED)
find_package(CMinpack REQUIRED)
find_package(Gflags REQUIRED)
find_package(Glog REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(Ceres REQUIRED)
find_package(Libmv REQUIRED)

message(STATUS "CMINPACK: ${CMINPACK_FOUND}"
  " Root=${CMINPACK_ROOT}"
  " Include=${CMINPACK_INCLUDE_DIRS}"
  " Library=${CMINPACK_LIBRARIES}")

message(STATUS "GFLAGS: ${GFLAGS_FOUND}"
  " Include=${GFLAGS_INCLUDE_DIRS}"
  " Library=${GFLAGS_LIBRARIES}")

message(STATUS "GLOG: ${GLOG_FOUND}"
  " Include=${GLOG_INCLUDE_DIRS}"
  " Library=${GLOG_LIBRARIES}")



message(STATUS "EIGEN3: ${EIGEN3_FOUND}"
  " Root=${Eigen3_DIR}"
  " Include=${EIGEN3_INCLUDE_DIRS}")


message(STATUS "CERES: ${CERES_FOUND}"
  " Root=${CERES_ROOT}"
  " Include=${CERES_INCLUDE_DIRS}"
  " Library=${CERES_LIBRARIES}")

message(STATUS "LIBMV: ${LIBMV_FOUND}"
  " Root=${LIBMV_ROOT}"
  " Include=${LIBMV_INCLUDE_DIRS}"
  " Library=${LIBMV_LIBRARIES}")

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
  PRIVATE ${MAYA_INCLUDE_DIRS}
  PRIVATE ${GFLAGS_INCLUDE_DIRS}
  PRIVATE ${GLOG_INCLUDE_DIRS}
  PRIVATE ${CMINPACK_INCLUDE_DIRS}
  PRIVATE ${EIGEN3_INCLUDE_DIRS}
  PRIVATE ${CERES_INCLUDE_DIRS}
  PRIVATE ${LIBMV_INCLUDE_DIRS}
  )
target_link_libraries(mmSolver
  PUBLIC
  ${MAYA_OpenMaya_LIBRARY}
  ${MAYA_OpenMayaAnim_LIBRARY}
  ${MAYA_Foundation_LIBRARY}
  )
target_link_libraries(mmSolver
  PRIVATE
  ${GFLAGS_LIBRARIES}
  ${GLOG_LIBRARIES}
  ${CMINPACK_LIBRARIES}
  ${CERES_LIBRARIES}
  ${LIBMV_LIBRARIES}
)
target_compile_definitions(mmSolver PRIVATE USE_SOLVER_CMINPACK)
target_compile_definitions(mmSolver PRIVATE USE_SOLVER_CERES)
target_compile_definitions(mmSolver PRIVATE USE_SOLVER_LIBMV)

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
if (CMINPACK_FOUND)
  install_library(
    ${CMINPACK_LIBRARY}
    ${CMINPACK_LIBRARY_DLL}
    "${MODULE_FULL_NAME}/lib/")
endif ()

