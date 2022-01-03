SET(TRACKING_SRC
    klt_region_tracker.cc
    pyramid_region_tracker.cc
    retrack_region_tracker.cc
    trklt_region_tracker.cc
    brute_region_tracker.cc
    esm_region_tracker.cc
    hybrid_region_tracker.cc
    lmicklt_region_tracker.cc
    klt.cc
    track_region.cc)

# Define the header files so that they appear in IDEs.
FILE(GLOB TRACKING_HDRS *.h)

ADD_LIBRARY(tracking ${TRACKING_SRC} ${TRACKING_HDRS})

TARGET_LINK_LIBRARIES(tracking base image multiview glog)

# Make the name of debug libraries end in _d.
SET_TARGET_PROPERTIES(tracking PROPERTIES DEBUG_POSTFIX "_d")

LIBMV_INSTALL_LIB(tracking)

LIBMV_TEST(brute_region_tracker "tracking;image;numeric")
LIBMV_TEST(klt_region_tracker "tracking;image;numeric")
LIBMV_TEST(pyramid_region_tracker "tracking;image;numeric")
