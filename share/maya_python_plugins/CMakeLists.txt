# Install Maya Python Plug-ins.
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/"
        DESTINATION "${MODULE_FULL_NAME}/plug-ins"
        FILES_MATCHING PATTERN "*.py")