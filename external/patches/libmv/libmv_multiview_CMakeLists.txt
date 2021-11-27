# define the source files
SET(MULTIVIEW_SRC affine.cc
                  affine_kernel.cc
                  autocalibration.cc
                  bundle.cc
                  conditioning.cc
                  essential_kernel.cc
                  euclidean.cc
                  euclidean_kernel.cc
                  euclidean_resection.cc
                  five_point.cc
                  focal_from_fundamental.cc
                  fundamental.cc
                  fundamental_kernel.cc
                  homography.cc
                  homography_kernel.cc
                  panography.cc
                  panography_kernel.cc
                  projection.cc
                  robust_affine.cc
                  robust_estimation.cc
                  robust_euclidean.cc
                  robust_euclidean_resection.cc
                  robust_fundamental.cc
                  robust_homography.cc
                  robust_resection.cc
                  robust_similarity.cc
                  similarity.cc
                  similarity_kernel.cc
                  sixpointnview.cc
                  structure.cc
                  triangulation.cc
                  twoviewtriangulation.cc)

# define the header files (make the headers appear in IDEs.)
FILE(GLOB MULTIVIEW_HDRS *.h)

ADD_LIBRARY(multiview ${MULTIVIEW_SRC} ${MULTIVIEW_HDRS})

TARGET_LINK_LIBRARIES(multiview glog numeric V3D ${CERES_LIBRARIES})

# make the name of debug libraries end in _d.
SET_TARGET_PROPERTIES(multiview PROPERTIES DEBUG_POSTFIX "_d")

# installation rules for the library
LIBMV_INSTALL_LIB(multiview)

IF (BUILD_TESTS)
  ADD_LIBRARY(multiview_test_data test_data_sets.cc)
  TARGET_LINK_LIBRARIES(multiview_test_data multiview)
  # make the name of debug libraries end in _d.
  SET_TARGET_PROPERTIES(multiview_test_data PROPERTIES DEBUG_POSTFIX "_d")
ENDIF (BUILD_TESTS)

MACRO (MULTIVIEW_TEST NAME)
  LIBMV_TEST(${NAME} "multiview_test_data;multiview;numeric;V3D")
ENDMACRO (MULTIVIEW_TEST)

MULTIVIEW_TEST(affine_kernel)
MULTIVIEW_TEST(affine_parameterization)
MULTIVIEW_TEST(affine)
MULTIVIEW_TEST(autocalibration)
MULTIVIEW_TEST(bundle)
MULTIVIEW_TEST(essential_kernel)
MULTIVIEW_TEST(euclidean_kernel)
MULTIVIEW_TEST(euclidean_parameterization)
MULTIVIEW_TEST(euclidean_resection_kernel)
MULTIVIEW_TEST(euclidean_resection)
MULTIVIEW_TEST(euclidean)
MULTIVIEW_TEST(five_point_kernel)
MULTIVIEW_TEST(five_point)
MULTIVIEW_TEST(focal_from_fundamental)
MULTIVIEW_TEST(fundamental_kernel)
MULTIVIEW_TEST(fundamental_parameterization)
MULTIVIEW_TEST(fundamental)
MULTIVIEW_TEST(homography_error)
MULTIVIEW_TEST(homography_kernel)
MULTIVIEW_TEST(homography_parameterization)
MULTIVIEW_TEST(homography)
MULTIVIEW_TEST(nviewtriangulation)
MULTIVIEW_TEST(panography)
MULTIVIEW_TEST(projection)
MULTIVIEW_TEST(resection_kernel)
MULTIVIEW_TEST(resection)
MULTIVIEW_TEST(robust_affine)
MULTIVIEW_TEST(robust_estimation)
MULTIVIEW_TEST(robust_euclidean_resection)
MULTIVIEW_TEST(robust_euclidean)
MULTIVIEW_TEST(robust_fundamental)
MULTIVIEW_TEST(robust_homography)
MULTIVIEW_TEST(robust_resection)
MULTIVIEW_TEST(robust_similarity)
MULTIVIEW_TEST(rotation_parameterization)
MULTIVIEW_TEST(similarity_kernel)
MULTIVIEW_TEST(similarity_parameterization)
MULTIVIEW_TEST(similarity)
MULTIVIEW_TEST(sixpointnview)
MULTIVIEW_TEST(triangulation)
MULTIVIEW_TEST(twoviewtriangulation)
