# Static build information.
set(target_test_exe_name "mmscenegraph_tests")

set(test_source_files
  ${CMAKE_CURRENT_SOURCE_DIR}/main.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_a.cpp
  # ${CMAKE_CURRENT_SOURCE_DIR}/test_b.cpp
  # ${CMAKE_CURRENT_SOURCE_DIR}/test_c.cpp
  )

# Add test executable using the C++ bindings.
add_executable(${target_test_exe_name} ${test_source_files})
target_link_libraries(${target_test_exe_name} ${target_release_lib_name})
target_include_directories(${target_test_exe_name}
  PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/../include
  )
target_include_directories(${target_test_exe_name}
  PUBLIC ${RUST_INCLUDE_DIR}
  )

# Install
install_target_to_module(${target_test_exe_name} "${MODULE_FULL_NAME}")
