# Maya MatchMoveSolver build script.
#
cmake_minimum_required(VERSION 2.8)

# Project configuration.
project(mayaMatchMoveSolver)
set(PROJECT_VERSION_MAJOR 0)
set(PROJECT_VERSION_MINOR 3)
set(PROJECT_VERSION_PATCH 0)
set(PROJECT_VERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}")
set(PROJECT_HOMEPAGE_URL "https://github.com/david-cattermole/mayaMatchMoveSolver")
set(PROJECT_DESCRIPTION "Bundle Adjustment solver for MatchMove tasks in Autodesk Maya.")
set(PROJECT_AUTHOR "David Cattermole and others (see AUTHORS.txt file)")
set(PROJECT_COPYRIGHT "2018, 2019, David Cattermole, Anil Reddy.")

# Add custom modules to the module path
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH}
        ${CMAKE_CURRENT_SOURCE_DIR}/cmake/modules)

# Maya SDK
set(MAYA_VERSION "2017" CACHE STRING "Maya version number")
set(MAYA_LOCATION "/usr/autodesk/maya${MAYA_VERSION}/" CACHE PATH "Maya install directory")
set(MAYA_INCLUDE_PATH "/usr/autodesk/maya${MAYA_VERSION}/include" CACHE PATH "Maya include directory")
set(MAYA_LIB_PATH "/usr/autodesk/maya${MAYA_VERSION}/lib" CACHE PATH "Maya library directory")

# Lev-Mar
# WARNING: 'Lev-Mar' is GPL licensed and must not be distributed in binary form to anyone.
set(USE_GPL_LEVMAR 0 CACHE BOOLEAN "Compile with the GPL-licensed Lev-Mar library?")
set(LEVMAR_ROOT "/usr/local" CACHE PATH "Levmar directory")
set(LEVMAR_INCLUDE_PATH "/usr/local/include" CACHE PATH "Levmar include directory")
set(LEVMAR_LIB_PATH "/usr/local/lib" CACHE PATH "Levmar library directory")

# CMinpack
set(USE_CMINPACK 1 CACHE BOOLEAN "Compile with the cminpack library?")
set(CMINPACK_ROOT "/usr/local" CACHE PATH "CMinpack directory")
set(CMINPACK_INCLUDE_PATH "/usr/local/include" CACHE PATH "cminpack include directory")
set(CMINPACK_LIB_PATH "/usr/local/lib" CACHE PATH "cminpack library directory")


# Extra (BLAS) Libraries
set(USE_BLAS OFF CACHE BOOLEAN "Should we use BLAS?")
set(BLAS_INCLUDE_PATH "/usr/include/blas" CACHE PATH "BLAS library directory")
set(BLAS_LIB_PATH "/usr/lib64/blas" CACHE PATH "BLAS library directory")
set(BLAS_LIB_NAMES
       ""
       CACHE STRING
       "BLAS libraries to link")


# Default Solver to use.
set(PREFERRED_SOLVER "cminpack_lm" CACHE STRING
        "Choices are cminpack_lm or levmar. Which solver is used by default?")

# Module paths
if (UNIX)
    set(MODULE_OS_NAME linux)
elseif(MSVC)
    set(MODULE_OS_NAME win64)
else()
    message(FATAL_ERROR "Only Linux and Windows are supported.")
endif()

# Module names
set(MODULE_NAME "${PROJECT_NAME}-${PROJECT_VERSION}")
set(MODULE_FULL_NAME "${MODULE_NAME}-maya${MAYA_VERSION}-${MODULE_OS_NAME}")
set(MODULE_BUILD_DIR "${CMAKE_BINARY_DIR}/${MODULE_FULL_NAME}")

# Set a default solver
set(DEFAULT_SOLVER ${PREFERRED_SOLVER})
if ((USE_CMINPACK EQUAL 1) AND (USE_GPL_LEVMAR EQUAL 0))
    if (NOT (DEFAULT_SOLVER STREQUAL "cminpack_lm"))
        message(WARNING 
          "Preferred solver cannot be used because it's not enabled. "
          "preferred=${PREFERRED_SOLVER} "
          "default=${DEFAULT_SOLVER} "
          "use_cminpack=${USE_CMINPACK} "
          "use_gpl_levmar=${USE_GPL_LEVMAR}"
          )
        set(DEFAULT_SOLVER "cminpack_lm")
    endif()
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
    endif()
else()
    message(FATAL_ERROR
      " Solver is not available! "
      "preferred=${PREFERRED_SOLVER} "
      "default=${DEFAULT_SOLVER} "
      "use_cminpack=${USE_CMINPACK} "
      "use_gpl_levmar=${USE_GPL_LEVMAR}"
    )
endif()

# Create Module Description file.
if (UNIX)
    configure_file(
            ${CMAKE_CURRENT_SOURCE_DIR}/modules/mayaMatchMoveSolver_linux.mod
            ${CMAKE_CURRENT_BINARY_DIR}/${MODULE_FULL_NAME}.mod
            @ONLY)
elseif(MSVC)
    configure_file(
            ${CMAKE_CURRENT_SOURCE_DIR}/modules/mayaMatchMoveSolver_windows.mod
            ${CMAKE_CURRENT_BINARY_DIR}/${MODULE_FULL_NAME}.mod
            @ONLY)
else()
    message(FATAL_ERROR "Only Linux and Windows are supported.")
endif()


# Create Python file with some build options baked in.
configure_file(
        ${CMAKE_CURRENT_SOURCE_DIR}/python/mmSolver/constant.py.in
        ${CMAKE_CURRENT_SOURCE_DIR}/python/mmSolver/constant.py
        @ONLY)

# Create Python file with some build options baked in.
configure_file(
        ${CMAKE_CURRENT_SOURCE_DIR}/include/buildConstant.h.in
        ${CMAKE_CURRENT_SOURCE_DIR}/include/buildConstant.h
        @ONLY)

# Create Python file for documentation sphinx build with some build
# options baked in.
configure_file(
        ${CMAKE_CURRENT_SOURCE_DIR}/docs/source/conf.py.in
        ${CMAKE_CURRENT_SOURCE_DIR}/docs/source/conf.py
        @ONLY)


# Source
set(SOURCE_FILES
        include/utilities/debugUtils.h
        include/nodeTypeIds.h
        include/mayaUtils.h
        include/mmSolver.h
        include/mmSolverFunc.h
        include/mmSolverLevMar.h
        include/mmSolverCMinpack.h
        include/Camera.h
        include/Marker.h
        include/Bundle.h
        include/Attr.h
        include/reprojection.h
        include/MMMarkerScaleNode.h
        include/MMReprojectionNode.h
        include/MMMarkerGroupTransformNode.h
        include/MMTestCameraMatrixCmd.h
        include/MMSolverCmd.h
        include/MMSolverTypeCmd.h
        include/MMReprojectionCmd.h
        src/mmSolver.cpp
        src/mmSolverFunc.cpp
        src/mmSolverLevMar.cpp
        src/mmSolverCMinpack.cpp
        src/Camera.cpp
        src/Marker.cpp
        src/Bundle.cpp
        src/Attr.cpp
        src/reprojection.cpp
        src/MMMarkerScaleNode.cpp
        src/MMReprojectionNode.cpp
        src/MMMarkerGroupTransformNode.cpp
        src/MMTestCameraMatrixCmd.cpp
        src/MMSolverCmd.cpp
        src/MMSolverTypeCmd.cpp
        src/MMReprojectionCmd.cpp
        src/pluginMain.cpp
)

# Find external packages
find_package(Maya REQUIRED)
find_package(LevMar)
find_package(CMinpack)

# Compile Flags.
#
# Release flags come from the Autodesk Maya build scripts (and
# Visual Studio project files).
if (MSVC)
    # For Visual Studio 11 2012
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /GS /W3 /Zc:wchar_t /Zi /fp:precise /WX- /Zc:forScope /GR /Gd /EHsc")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D \"OSWin_\" /D \"WIN32\" /D \"_WINDOWS\" /D \"_USRDLL\" /D \"NT_PLUGIN\"")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D \"_HAS_ITERATOR_DEBUGGING=0\" /D \"_SECURE_SCL=0\" /D \"_SECURE_SCL_THROWS=0\"")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D \"_SECURE_SCL_DEPRECATE=0\" /D \"_CRT_SECURE_NO_DEPRECATE\" /D \"TBB_USE_DEBUG=0\"")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D \"__TBB_LIB_NAME=tbb.lib\" /D \"Bits64_\" /D \"_WINDLL\"")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D \"NT_PLUGIN\" /D \"REQUIRE_IOSTREAM\"")

    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS} /D \"_DEBUG\"")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Gm /Od /RTC1")

    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS} /D \"NDEBUG\"")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /Gy /Gm- /O2 /Ob1 /GF")

    # Must add the plug-in entry/exit points otherwise
    # the plug-in won't load.
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} /export:initializePlugin /export:uninitializePlugin")
else()
    # For Linux with GCC
    set(CMAKE_CXX_FLAGS_DEBUG "-std=c++0x -O0 -g -Wall")
    set(CMAKE_CXX_FLAGS_RELEASE "-std=c++0x -O3 -fPIC -fno-strict-aliasing -m64")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -DBits64_ -DUNIX -D_BOOL -DLINUX -DFUNCPROTO -D_GNU_SOURCE -DLINUX_64 -DREQUIRE_IOSTREAM")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -Wall -Wno-multichar -Wno-comment -Wno-sign-compare -funsigned-char -pthread -fopenmp")
    # '-ftemplate-depth-27', rather than '25' is required to compile under GCC 4.8.5.
    # '-ftemplate-depth-35', rather than '25' is required to compile under GCC 5.5.x.
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -Wno-deprecated -Wno-reorder -ftemplate-depth-35 -fno-gnu-keywords")
endif()

function (add_target_link_library_names target names)
    string(STRIP ${names} names_strip)
    string(REPLACE " " ";" names_list ${names_strip})
    foreach(name IN LISTS names_list)
        target_link_libraries(${target} ${name})
    endforeach()
endfunction()

# 'mmSolver' maya plugin library
add_library(mmSolver SHARED ${SOURCE_FILES})
target_include_directories(mmSolver
        PRIVATE include
        PUBLIC ${MAYA_INCLUDE_DIRS}
)
target_link_libraries(mmSolver
        ${MAYA_OpenMaya_LIBRARY}
        ${MAYA_OpenMayaAnim_LIBRARY}
        ${MAYA_Foundation_LIBRARY}
)

if (USE_GPL_LEVMAR)
    message(WARNING
            "'levmar' library is licensed under GNU GPL and therefore this library "
            "must not be distributed in binary form.")
    target_include_directories(mmSolver PUBLIC ${LEVMAR_INCLUDE_DIRS})
    target_link_libraries(mmSolver ${LEVMAR_LIBRARIES})
    add_definitions(-DUSE_SOLVER_LEVMAR)
endif()


if (USE_CMINPACK)
    target_include_directories(mmSolver PUBLIC ${CMINPACK_INCLUDE_DIRS})
    target_link_libraries(mmSolver ${CMINPACK_LIBRARIES})
    add_definitions(-DUSE_SOLVER_CMINPACK)
endif()

# On Linux the 'm' library is required.
if (UNIX)
    target_link_libraries(mmSolver m)
endif()

# no 'lib' prefix to Maya plugin .so files
set_target_properties(mmSolver PROPERTIES PREFIX "")

# On MacOS, the Maya Plug-In file extension is '.bundle'.
# On Windows, the Maya Plug-In file extension is '.mll', not '.dll'.
if(APPLE)
    set(MAYA_PLUGIN_SUFFIX ".bundle")
elseif (WIN32)
    set_target_properties(mmSolver PROPERTIES SUFFIX ".mll")
endif()

# HACK: On Linux, LD_LIBRARY_PATH cannot be modified at runtime (on
# Windows it can), therefore the .mod files *can* change
# LD_LIBRARY_PATH, but the changes are not used by 'ld.so', which
# resolves the library path. Therefore, to make sure the the libraries
# in <module root>/lib are searched for libraries, we add a relative
# directory 'RPATH' to the library which tells the library resolution
# to search in the 'lib' directory inside the module root. Note: Linux
# does not allow run-time changes for security reasons.
if(UNIX)
    # We must escape the '$' symbol to make sure it is passed to the
    # compiler.
    set_target_properties(mmSolver PROPERTIES
         BUILD_WITH_INSTALL_RPATH ON
         INSTALL_RPATH "\$ORIGIN/../lib"
    )
endif()

# Output to the Module plug-ins directory.
#
# On Windows, the Plug-In is treated as a 'RUNTIME' type,
# on Linux, it's a 'LIBRARY' type.
set_target_properties(mmSolver PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${MODULE_FULL_NAME}"
        LIBRARY_OUTPUT_DIRECTORY "${MODULE_FULL_NAME}"
        ARCHIVE_OUTPUT_DIRECTORY "${MODULE_FULL_NAME}")

# Install the Module Description file.
install(FILES
        ${CMAKE_CURRENT_BINARY_DIR}/${MODULE_FULL_NAME}.mod
        DESTINATION "./")

# Install the Plug-In.
install(TARGETS mmSolver
        RUNTIME DESTINATION "${MODULE_FULL_NAME}/plug-ins"
        LIBRARY DESTINATION "${MODULE_FULL_NAME}/plug-ins")

# Install dynamic libraries
if(USE_CMINPACK AND CMINPACK_FOUND)
    if(WIN32)
        if(EXISTS ${CMINPACK_LIBRARY_DLL})
            install(FILES ${CMINPACK_LIBRARY_DLL}
                    DESTINATION "${MODULE_FULL_NAME}/lib/")
        else()
            install(FILES ${CMINPACK_LIBRARY}
                    DESTINATION "${MODULE_FULL_NAME}/lib/")
        endif()
    elseif(UNIX)
        # Install both symlink and real library
        get_filename_component(ABS_CMINPACK_LIBRARY ${CMINPACK_LIBRARY} REALPATH)
        install(FILES ${CMINPACK_LIBRARY}
                DESTINATION "${MODULE_FULL_NAME}/lib/")
        install(FILES ${ABS_CMINPACK_LIBRARY}
                DESTINATION "${MODULE_FULL_NAME}/lib/")
    endif()
endif()

if(USE_GPL_LEVMAR AND LEVMAR_FOUND)
    if(WIN32)
        if(EXISTS ${LEVMAR_LIBRARY_DLL})
            install(FILES ${LEVMAR_LIBRARY_DLL}
                    DESTINATION "${MODULE_FULL_NAME}/lib/")
        else()
            install(FILES ${LEVMAR_LIBRARY}
                    DESTINATION "${MODULE_FULL_NAME}/lib/")
        endif()
    elseif(UNIX)
        # Install both symlink and real library
        get_filename_component(ABS_LEVMAR_LIBRARY ${LEVMAR_LIBRARY} REALPATH)
        install(FILES ${LEVMAR_LIBRARY}
                DESTINATION "${MODULE_FULL_NAME}/lib/")
        install(FILES ${ABS_LEVMAR_LIBRARY}
                DESTINATION "${MODULE_FULL_NAME}/lib/")
    endif()
endif()

# Install Qt.py, if exists.
set(QTPY_FILE "${CMAKE_SOURCE_DIR}/external/install/qtpy/Qt.py")
if(EXISTS ${QTPY_FILE})
    install(FILES ${QTPY_FILE}
            DESTINATION "${MODULE_FULL_NAME}/python_qtpy/")
endif()

# Install Python API and tools
install(DIRECTORY "python/"
        DESTINATION "${MODULE_FULL_NAME}/python"
        FILES_MATCHING PATTERN "*.py")

# Install Maya MEL and Python scripts.
install(DIRECTORY "mel/"
        DESTINATION "${MODULE_FULL_NAME}/scripts"
        FILES_MATCHING PATTERN "*.mel")
install(DIRECTORY "mel/"
        DESTINATION "${MODULE_FULL_NAME}/scripts"
        FILES_MATCHING PATTERN "*.py")
install(DIRECTORY "mel/AETemplates/"
        DESTINATION "${MODULE_FULL_NAME}/scripts/AETemplates"
        FILES_MATCHING PATTERN "*.mel")

# Install 3DEqualizer scripts.
install(DIRECTORY "3dequalizer/scriptdb/"
        DESTINATION "${MODULE_FULL_NAME}/3dequalizer"
        FILES_MATCHING PATTERN "*.py")

# Install SynthEyes scripts.
install(DIRECTORY "syntheyes/"
        DESTINATION "${MODULE_FULL_NAME}/syntheyes"
        FILES_MATCHING PATTERN "*.szl")

# Install Config.
install(DIRECTORY "config/"
        DESTINATION "${MODULE_FULL_NAME}/config"
        FILES_MATCHING PATTERN "*.json")

# Install Icons.
install(DIRECTORY "icons/"
        DESTINATION "${MODULE_FULL_NAME}/icons"
        FILES_MATCHING PATTERN "*.png"
        PATTERN "icons/edit" EXCLUDE
        PATTERN "icons/library" EXCLUDE)
install(DIRECTORY "icons/"
        DESTINATION "${MODULE_FULL_NAME}/icons"
        FILES_MATCHING PATTERN "*.svg"
        PATTERN "icons/edit" EXCLUDE
        PATTERN "icons/library" EXCLUDE)

# Install Documentation
install(DIRECTORY "docs/build/html/"
        DESTINATION "${MODULE_FULL_NAME}/docs/html")

# Install misc files
install(FILES
        ${CMAKE_CURRENT_SOURCE_DIR}/LICENSE
        ${CMAKE_CURRENT_SOURCE_DIR}/INSTALL.md
        ${CMAKE_CURRENT_SOURCE_DIR}/README.md
        DESTINATION "${MODULE_FULL_NAME}/")

# Package Configuration.
set(CPACK_PACKAGE_NAME "${PROJECT_NAME}")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "${PROJECT_DESCRIPTION}")
set(CPACK_PACKAGE_VENDOR "${PROJECT_AUTHOR}")
set(CPACK_PACKAGE_CONTACT "cattermole91@gmail.com")
set(CPACK_PACKAGE_DESCRIPTION_FILE "${CMAKE_CURRENT_SOURCE_DIR}/README.md")
set(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/LICENSE")
set(CPACK_PACKAGE_VERSION_MAJOR "${PROJECT_VERSION_MAJOR}")
set(CPACK_PACKAGE_VERSION_MINOR "${PROJECT_VERSION_MINOR}")
set(CPACK_PACKAGE_VERSION_PATCH "${PROJECT_VERSION_PATCH}")
set(CPACK_PACKAGE_FILE_NAME "${MODULE_FULL_NAME}")
set(CPACK_INCLUDE_TOPLEVEL_DIRECTORY 1)
# Put the packages into the source directory, so that when we run
# another build, it's not removed as part of the clean up.
SET(CPACK_OUTPUT_FILE_PREFIX "../packages")
if (WIN32 AND NOT UNIX)
    # .zip file for Windows.
    set(CPACK_GENERATOR "ZIP")
elseif (UNIX AND NOT WIN32)
    # .tar.gz for Linux.
    set(CPACK_GENERATOR "TGZ")
endif()

# TODO: Set up proper 'source' package file inclusion rules.
# # set(CPACK_SOURCE_GENERATOR "TGZ")
# # set(CPACK_SOURCE_PACKAGE_FILE_NAME "${MODULE_NAME}-Source")

# Use CPack (part of CMake) to generate the packages...
# If 'CPack' is not included, the 'packages' target will not be generated.
include(CPack)

add_subdirectory(python)
add_subdirectory(docs)

enable_testing()
add_subdirectory(tests)
