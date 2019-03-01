# This CMake script is for building and organising the 'external' dependancies
# for Maya MatchMove Solver.
cmake_minimum_required(VERSION 2.8)
find_package(Python2 COMPONENTS Interpreter REQUIRED)

set(ARCHIVES_DIR "${CMAKE_SOURCE_DIR}/archives")
set(WORKING_DIR "${CMAKE_SOURCE_DIR}/working")
set(PATCHES_DIR "${CMAKE_SOURCE_DIR}/patches")

set(CMINPACK_DOWNLOAD_FILE "${ARCHIVES_DIR}/cminpack-1.3.6.tar.gz")
set(CMINPACK_EXTRACTED_FILE "${WORKING_DIR}/cminpack-1.3.6")

set(LEVMAR_DOWNLOAD_FILE "${ARCHIVES_DIR}/levmar-2.6.tgz")
set(LEVMAR_EXTRACTED_FILE "${WORKING_DIR}/levmar-2.6")


# Extract CMinpack
set(PY_SCRIPT "${CMAKE_SOURCE_DIR}/../scripts/get_cminpack.py")
add_custom_command(
    OUTPUT ${CMINPACK_EXTRACTED_FILE}
    COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMINPACK_EXTRACTED_FILE}
    COMMAND python ${PY_SCRIPT} ${ARCHIVES_DIR} ${WORKING_DIR} ${PATCHES_DIR}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    DEPENDS ${CMINPACK_DOWNLOAD_FILE}
    )
add_custom_target(
    cminpack_package ALL
    DEPENDS ${CMINPACK_EXTRACTED_FILE}
    COMMENT "Unpacking CMinpack package..."
    )


# Extract Levmar
set(PY_SCRIPT "${CMAKE_SOURCE_DIR}/../scripts/get_levmar.py")
add_custom_command(
        OUTPUT ${LEVMAR_EXTRACTED_FILE}
        COMMAND ${CMAKE_COMMAND} -E remove_directory ${LEVMAR_EXTRACTED_FILE}
        COMMAND python ${PY_SCRIPT} ${ARCHIVES_DIR} ${WORKING_DIR} ${PATCHES_DIR}
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        DEPENDS ${LEVMAR_DOWNLOAD_FILE}
)
add_custom_target(
        levmar_package ALL
        DEPENDS ${LEVMAR_EXTRACTED_FILE}
        COMMENT "Unpacking LevMar package..."
)


