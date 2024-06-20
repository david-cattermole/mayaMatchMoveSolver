# Copyright (C) 2024 David Cattermole.
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
# CMake utilities for mmColorIO.
#

macro(mmcolorio_find_packages)
  message(STATUS "mmcolorio_find_packages")

  # OpenColorIO
  find_package(OpenColorIO REQUIRED)
  message(STATUS "OpenColorIO: Version: ${OpenColorIO_VERSION}")

  # OpenColorIO Dependencies
  find_package(pystring REQUIRED)
  message(STATUS "pystring: Found: ${pystring_FOUND}")
  message(STATUS "pystring: Version: ${pystring_VERSION}")
  message(STATUS "pystring: Libraries: ${pystring_LIBRARY}")
  message(STATUS "pystring: Include Dir: ${pystring_INCLUDE_DIR}")

  # This is the (all-lower-case) 'expat' library namespace, which is the
  # same as the 'EXPAT' library, except using ALL-UPPER-CASE name will
  # use the inbuilt CMake FindEXPAT.cmake module which is not what
  # OpenColorIO uses.
  find_package(expat REQUIRED)
  message(STATUS "expat: Found: ${expat_FOUND}")
  message(STATUS "expat: Version: ${expat_VERSION}")
  message(STATUS "expat: Libraries: ${expat_LIBRARY}")
  message(STATUS "expat: Include Dir: ${expat_INCLUDE_DIR}")

  find_package(yaml-cpp REQUIRED)
  message(STATUS "yaml-cpp: Found: ${yaml-cpp_FOUND}")
  message(STATUS "yaml-cpp: Version: ${yaml-cpp_VERSION}")
  message(STATUS "yaml-cpp: Libraries: ${yaml-cpp_LIBRARY}")
  message(STATUS "yaml-cpp: Include Dir: ${yaml-cpp_INCLUDE_DIR}")

  if(OpenColorIO_VERSION VERSION_GREATER_EQUAL "2.1.0")
    find_package(Imath REQUIRED)
    message(STATUS "Imath: Found: ${Imath_FOUND}")
    message(STATUS "Imath: Version: ${Imath_VERSION}")
    message(STATUS "Imath: Libraries: ${Imath_LIBRARY}")
    message(STATUS "Imath: Include Dir: ${Imath_INCLUDE_DIR}")
  else()
    find_package(Half REQUIRED)
    message(STATUS "Half: Found: ${Half_FOUND}")
    message(STATUS "Half: Version: ${Half_VERSION}")
    message(STATUS "Half: Libraries: ${Half_LIBRARY}")
    message(STATUS "Half: Include Dir: ${Half_INCLUDE_DIR}")
  endif()

  if(OpenColorIO_VERSION VERSION_GREATER_EQUAL "2.2.0")
    find_package(ZLIB REQUIRED)
    message(STATUS "ZLIB: Found: ${ZLIB_FOUND}")
    message(STATUS "ZLIB: Version: ${ZLIB_VERSION}")
    message(STATUS "ZLIB: Libraries: ${ZLIB_LIBRARIES}")
    message(STATUS "ZLIB: Include Dirs: ${ZLIB_INCLUDE_DIRS}")

    find_package(minizip-ng REQUIRED)
    message(STATUS "minizip-ng: Found: ${minizip-ng_FOUND}")
    message(STATUS "minizip-ng: Version: ${minizip-ng_VERSION}")
    message(STATUS "minizip-ng: Libraries: ${minizip-ng_LIBRARY}")
    message(STATUS "minizip-ng: Include Dir: ${minizip-ng_INCLUDE_DIR}")
  endif()

endmacro()


macro(mmcolorio_target_link_packages target)
  message(STATUS "mmcolorio_target_link_packages: ${target}")

  find_package(yaml-cpp REQUIRED)
  get_target_property(yaml_cpp_LOCATION_RELEASE
    yaml-cpp
    IMPORTED_LOCATION_RELEASE)
  message(STATUS
    "yaml_cpp_LOCATION_RELEASE: ${yaml_cpp_LOCATION_RELEASE}")

  find_package(expat REQUIRED)
  find_package(pystring REQUIRED)
  target_link_libraries(${target}
    PRIVATE ${expat_LIBRARY}
    PRIVATE ${pystring_LIBRARY}
    PRIVATE ${yaml_cpp_LOCATION_RELEASE}
  )

  find_package(OpenColorIO REQUIRED)
  find_package(ZLIB REQUIRED)
  find_package(minizip-ng REQUIRED)
  if(OpenColorIO_VERSION VERSION_GREATER_EQUAL "2.2.0")
    target_link_libraries(${target}
      PRIVATE ZLIB::ZLIB
      PRIVATE ${minizip-ng_LIBRARY}
    )
  endif()

  # The 'half' 16-bit float data type is used from Imath by default in
  # OCIO 2.2+, but OpenEXR/IlmBase is used before that.
  #
  # The reason is that OpenEXR used to be the sole location for the
  # 'half' data type (because it was supported as part of OpenEXR),
  # but since many libraries wanted the 'half' data type without all
  # of OpenEXR, it was refactored out of OpenEXR.
  if(OpenColorIO_VERSION VERSION_GREATER_EQUAL "2.2.0")
    find_package(Imath REQUIRED)
    target_link_libraries(${target}
      PRIVATE Imath::Imath
    )
  else()
    find_package(Half REQUIRED)
    target_link_libraries(${target}
      PRIVATE ${Half_LIBRARY}
    )
  endif()

  if (WIN32)
    find_package(OpenColorIO REQUIRED)
    get_target_property(OpenColorIO_IMPLIB_RELEASE
      OpenColorIO::OpenColorIO
      IMPORTED_IMPLIB_RELEASE)
    message(STATUS
      "OpenColorIO_IMPLIB_RELEASE: ${OpenColorIO_IMPLIB_RELEASE}")

    get_target_property(OpenColorIO_LOCATION_RELEASE
      OpenColorIO::OpenColorIO
      IMPORTED_LOCATION_RELEASE)
    message(STATUS
      "OpenColorIO_LOCATION_RELEASE: ${OpenColorIO_LOCATION_RELEASE}")

    get_filename_component(
      OpenColorIO_IMPLIB_RELEASE_ABS
      ${OpenColorIO_IMPLIB_RELEASE}
      REALPATH)

    target_link_libraries(${target}
      PRIVATE ${OpenColorIO_IMPLIB_RELEASE_ABS}
    )
  elseif (UNIX)
    get_target_property(OpenColorIO_LOCATION_RELEASE
      OpenColorIO::OpenColorIO
      IMPORTED_LOCATION_RELEASE)
    message(STATUS
      "OpenColorIO_LOCATION_RELEASE: ${OpenColorIO_LOCATION_RELEASE}")

    target_link_libraries(${target}
      PRIVATE ${OpenColorIO_LOCATION_RELEASE}
    )
  endif ()

endmacro()


macro(mmcolorio_target_include_packages target)
  message(STATUS "mmcolorio_target_include_packages: ${target}")

  message(STATUS "OpenColorIO: Version: ${OpenColorIO_VERSION}")

  if(OpenColorIO_VERSION VERSION_GREATER_EQUAL "2.1.0")
    get_target_property(OpenColorIO_INCLUDE_DIR
      OpenColorIO::OpenColorIO
      INTERFACE_INCLUDE_DIRECTORIES)
  else()
    get_target_property(OpenColorIO_INCLUDE_DIR
      OpenColorIO::OpenColorIOHeaders
      INTERFACE_INCLUDE_DIRECTORIES)
  endif()

  message(STATUS
    "OpenColorIO_INCLUDE_DIR: ${OpenColorIO_INCLUDE_DIR}")

  target_include_directories(${target}
    PRIVATE ${OpenColorIO_INCLUDE_DIR}
    PRIVATE ${pystring_INCLUDE_DIR}
    PRIVATE ${expat_INCLUDE_DIR}
    PRIVATE ${yaml-cpp_INCLUDE_DIR}
  )

  if(OpenColorIO_VERSION VERSION_GREATER_EQUAL "2.1.0")
    target_include_directories(${target}
      PRIVATE ${Imath_INCLUDE_DIR}
    )
  else()
    target_include_directories(${target}
      PRIVATE ${Half_INCLUDE_DIR}
    )
  endif()

  if(OpenColorIO_VERSION VERSION_GREATER_EQUAL "2.2.0")
    target_include_directories(${target}
      PRIVATE ${ZLIB_INCLUDE_DIRS}
      PRIVATE ${minizip-ng_INCLUDE_DIR}
    )
  endif()

endmacro()
