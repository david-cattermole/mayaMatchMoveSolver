# This CMake script is for building and organising the 'external' dependancies
# for Maya MatchMove Solver.
cmake_minimum_required(VERSION 2.8)
project(mayaMatchMoveSolver)

# 'levmar' package.
#
# Here we unpack 'levmar-2.6.tgz'.
# You can find the Tarball here:
# http://users.ics.forth.gr/~lourakis/levmar/levmar-2.6.tgz
#
# The MD5 hash should equal:
# 16bc34efa1617219f241eef06427f13f
# 
set(LEVMAR_DOWNLOAD_PATH "${CMAKE_SOURCE_DIR}/archives/levmar-2.6.tgz")
set(LEVMAR_EXTRACTED_DIR "${CMAKE_SOURCE_DIR}/working")
set(LEVMAR_EXTRACTED_FILE "${CMAKE_SOURCE_DIR}/working/levmar-2.6")

# Extract Lev-Mar
add_custom_command(
    OUTPUT ${LEVMAR_EXTRACTED_FILE}
    COMMAND ${CMAKE_COMMAND} -E remove_directory ${LEVMAR_EXTRACTED_FILE}
    COMMAND ${CMAKE_COMMAND} -E tar xvf ${LEVMAR_DOWNLOAD_PATH} -C ${LEVMAR_EXTRACTED_FILE}
    WORKING_DIRECTORY ${LEVMAR_EXTRACTED_DIR}
    DEPENDS ${LEVMAR_DOWNLOAD_PATH}
    )
add_custom_target(
    levmar_target ALL 
    DEPENDS ${LEVMAR_EXTRACTED_FILE}
    COMMENT "Unpacking Lev-Mar package..."
    )
