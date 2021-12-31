# Expected inputs.
set(MMSCENEGRAPH_RUST_BUILD_DIR "/path/to/rust/build/directory/" CACHE PATH
  "The path to the compiled rust directory.")
set(MMSCENEGRAPH_RUST_INCLUDE_DIR "/path/to/rust/include/directory/" CACHE PATH
  "The path to the generated include.")

# C++ Source Code
set(lib_source_files
  ${CMAKE_CURRENT_SOURCE_DIR}/_cxxbridge.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/attrdatablock.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/flatscene.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/scenebake.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/scenegraph.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/evaluationobjects.cpp
  )

# Find the Rust Library
include(MMSceneGraphUtils)
set(rust_linktime_file "NOT-FOUND")
find_rust_library("mmscenegraph" ${MMSCENEGRAPH_RUST_BUILD_DIR} rust_linktime_file)
message(STATUS "Rust Linktime Library: ${rust_linktime_file}")

# Generate CXX Bridge files.
find_program(cxxbridge_exec cxxbridge REQUIRED PATHS $ENV{HOME}/.cargo/bin)
message(STATUS "Using cxxbridge: ${cxxbridge_exec}")
set(cxxbridge_in ${CMAKE_CURRENT_SOURCE_DIR}/cxxbridge.rs)
set(cxxbridge_source_out ${CMAKE_CURRENT_SOURCE_DIR}/_cxxbridge.cpp)
set(cxxbridge_header_out ${CMAKE_CURRENT_SOURCE_DIR}/../include/mmscenegraph/_cxxbridge.h)
set(cxxbridge_args "--cxx-impl-annotations" "MMSCENEGRAPH_API_EXPORT")
add_custom_command(
  OUTPUT ${cxxbridge_source_out} ${cxxbridge_header_out}
  COMMAND ${cxxbridge_exec} ${cxxbridge_in} ${cxxbridge_args} --header --output ${cxxbridge_header_out}
  COMMAND ${cxxbridge_exec} ${cxxbridge_in} ${cxxbridge_args} --output ${cxxbridge_source_out}
  COMMENT "Generating CXX Bridge: ${cxxbridge_header_out} ${cxxbridge_source_out}"
  DEPENDS ${cxxbridge_in})

set (CMAKE_CXX_STANDARD 11)

if (MSVC)
  set(depend_on_libraries
    ws2_32 userenv advapi32 shell32 msvcrt Bcrypt
    )
elseif (UNIX)
  set(depend_on_libraries
    pthread m dl
    )
endif ()

# Add 'mmscenegraph' library as a C++ wrapper around the Rust library.
add_library(${target_release_lib_name}
  SHARED
  ${lib_source_files})
target_link_libraries(${target_release_lib_name}
  ${RUST_LINKTIME_LIBRARY_FILE}
  ${depend_on_libraries}
  ${rust_linktime_file}
  )
target_include_directories(${target_release_lib_name}
  PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/../include
  PUBLIC ${RUST_INCLUDE_DIR}
  PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}
  )

include(MMSolverUtils)
install_target_to_module(${target_release_lib_name} "${MODULE_FULL_NAME}")
