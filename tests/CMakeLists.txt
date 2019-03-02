# Define the tests for mmSolver.

find_package(Maya REQUIRED)

set(EXEC_SCRIPT ${CMAKE_SOURCE_DIR}/tests/runTests.py)

## API Tests
#set(suffix api)
#add_test(
#   NAME
#       test_python_${suffix}
#   COMMAND
#       ${MAYA_PYTHON_EXECUTABLE} ${EXEC_SCRIPT} ${CMAKE_SOURCE_DIR}/tests/test/test_${suffix}
#   WORKING_DIRECTORY
#       ${CMAKE_SOURCE_DIR}
#)

## Solver Tests
#set(suffix solver)
#add_test(
#       NAME
#       test_python_${suffix}
#       COMMAND
#       ${MAYA_PYTHON_EXECUTABLE} ${EXEC_SCRIPT} ${CMAKE_SOURCE_DIR}/tests/test/test_${suffix}
#       WORKING_DIRECTORY
#       ${CMAKE_SOURCE_DIR}
#)

## Tools Tests
#set(suffix tools)
#add_test(
#       NAME
#       test_python_${suffix}
#       COMMAND
#       ${MAYA_PYTHON_EXECUTABLE} ${EXEC_SCRIPT} ${CMAKE_SOURCE_DIR}/tests/test/test_${suffix}
#       WORKING_DIRECTORY
#       ${CMAKE_SOURCE_DIR}
#)

## Utilities Tests
#set(suffix utils)
#add_test(
#       NAME
#       test_python_${suffix}
#       COMMAND
#       ${MAYA_PYTHON_EXECUTABLE} ${EXEC_SCRIPT} ${CMAKE_SOURCE_DIR}/tests/test/test_${suffix}
#       WORKING_DIRECTORY
#       ${CMAKE_SOURCE_DIR}
#)

# API Tests
add_test(
        NAME
        test_python
        COMMAND
        ${MAYA_PYTHON_EXECUTABLE} ${EXEC_SCRIPT}
        WORKING_DIRECTORY
        ${CMAKE_SOURCE_DIR}
)
