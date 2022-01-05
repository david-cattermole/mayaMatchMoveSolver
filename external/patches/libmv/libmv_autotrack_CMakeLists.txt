SET(AUTOTRACK_SRC
    autotrack.cc
    tracks.cc
    predict_tracks.cc
    )

# Define the header files so that they appear in IDEs.
FILE(GLOB AUTOTRACK_HDRS *.h)

ADD_LIBRARY(autotrack ${AUTOTRACK_SRC} ${AUTOTRACK_HDRS})

TARGET_LINK_LIBRARIES(autotrack V3D multiview image tracking)

# Make the name of debug libraries end in _d.
SET_TARGET_PROPERTIES(autotrack PROPERTIES DEBUG_POSTFIX "_d")

LIBMV_INSTALL_LIB(autotrack)

MACRO (AUTOTRACK_TEST NAME)
  LIBMV_TEST(${NAME} "autotrack")
ENDMACRO (AUTOTRACK_TEST)

AUTOTRACK_TEST(tracks)
AUTOTRACK_TEST(predict_tracks)
