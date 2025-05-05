# OpenMVG - Multiple View library

OpenMVG provides multi-view camera reconstruction and camera solving
features and is required for building mmSolver. OpenMVG uses Ceres and
Eigen internally, and Eigen is needed by downstream libraries because
it is used across the OpenMVG ABI.

This directory contains a copy of a sub-set of frames from the OpenMVG
project, plus CMake build scripts that have been written for
mmSolver.

The goal of this copying was to fix difficult crashing caused by the
build scripts in OpenMVG that are resolved when compiling together
with mmSolver.

Another goal was to reduce the number of third-party dependencies.
Therefore only a select number of features of OpenMVG have been used.

## Source Repository

This project was copied from the following location:

Page: https://github.com/openMVG/openMVG
Documentation: https://openmvg.readthedocs.io/en/latest/
Git URL: https://github.com/openMVG/openMVG.git
Git Tag: v2.1
Git Commit: 01193a245ee3c36458e650b1cf4402caad8983ef

## Copied Files

The following files have been copied. Some files were edited where
needed to remove unneeded dependencies (see below for details).

```
openMVG/AUTHORS
openMVG/COPYRIGHT.md
openMVG/LICENSE
openMVG/README.md
openMVG/src/openMVG/cameras/cameras.hpp
openMVG/src/openMVG/cameras/Camera_Common.hpp
openMVG/src/openMVG/cameras/Camera_Intrinsics.hpp
openMVG/src/openMVG/cameras/Camera_Pinhole.hpp
openMVG/src/openMVG/cameras/Camera_Pinhole_Brown.hpp
openMVG/src/openMVG/cameras/Camera_Pinhole_Fisheye.hpp
openMVG/src/openMVG/cameras/Camera_Pinhole_Radial.hpp
openMVG/src/openMVG/cameras/Camera_Spherical.hpp
openMVG/src/openMVG/cameras/PinholeCamera.hpp
openMVG/src/openMVG/features/feature.cpp
openMVG/src/openMVG/features/feature.hpp
openMVG/src/openMVG/geometry/pose3.hpp
openMVG/src/openMVG/geometry/rigid_transformation3D_srt.cpp
openMVG/src/openMVG/geometry/rigid_transformation3D_srt.hpp
openMVG/src/openMVG/geometry/Similarity3.cpp
openMVG/src/openMVG/geometry/Similarity3.hpp
openMVG/src/openMVG/geometry/Similarity3_Kernel.cpp
openMVG/src/openMVG/geometry/Similarity3_Kernel.hpp
openMVG/src/openMVG/multiview/conditioning.cpp
openMVG/src/openMVG/multiview/conditioning.hpp
openMVG/src/openMVG/multiview/essential.cpp
openMVG/src/openMVG/multiview/essential.hpp
openMVG/src/openMVG/multiview/motion_from_essential.cpp
openMVG/src/openMVG/multiview/motion_from_essential.hpp
openMVG/src/openMVG/multiview/projection.cpp
openMVG/src/openMVG/multiview/projection.hpp
openMVG/src/openMVG/multiview/solver_affine.cpp
openMVG/src/openMVG/multiview/solver_affine.hpp
openMVG/src/openMVG/multiview/solver_essential_eight_point.cpp
openMVG/src/openMVG/multiview/solver_essential_eight_point.hpp
openMVG/src/openMVG/multiview/solver_essential_five_point.cpp
openMVG/src/openMVG/multiview/solver_essential_five_point.hpp
openMVG/src/openMVG/multiview/solver_essential_kernel.cpp
openMVG/src/openMVG/multiview/solver_essential_kernel.hpp
openMVG/src/openMVG/multiview/solver_essential_three_point.cpp
openMVG/src/openMVG/multiview/solver_essential_three_point.hpp
openMVG/src/openMVG/multiview/solver_fundamental_kernel.cpp
openMVG/src/openMVG/multiview/solver_fundamental_kernel.hpp
openMVG/src/openMVG/multiview/solver_homography_kernel.cpp
openMVG/src/openMVG/multiview/solver_homography_kernel.hpp
openMVG/src/openMVG/multiview/solver_resection.hpp
openMVG/src/openMVG/multiview/solver_resection_kernel.cpp
openMVG/src/openMVG/multiview/solver_resection_kernel.hpp
openMVG/src/openMVG/multiview/solver_resection_metrics.hpp
openMVG/src/openMVG/multiview/solver_resection_p3p.hpp
openMVG/src/openMVG/multiview/solver_resection_p3p_nordberg.cpp
openMVG/src/openMVG/multiview/solver_resection_p3p_nordberg.hpp
openMVG/src/openMVG/multiview/solver_translation_knownRotation_kernel.hpp
openMVG/src/openMVG/multiview/triangulation.cpp
openMVG/src/openMVG/multiview/triangulation.hpp
openMVG/src/openMVG/multiview/triangulation_method.hpp
openMVG/src/openMVG/multiview/triangulation_nview.cpp
openMVG/src/openMVG/multiview/triangulation_nview.hpp
openMVG/src/openMVG/multiview/two_view_kernel.hpp
openMVG/src/openMVG/numeric/accumulator_trait.hpp
openMVG/src/openMVG/numeric/eigen_alias_definition.hpp
openMVG/src/openMVG/numeric/extract_columns.hpp
openMVG/src/openMVG/numeric/l1_solver_admm.hpp
openMVG/src/openMVG/numeric/lm.hpp
openMVG/src/openMVG/numeric/nullspace.cpp
openMVG/src/openMVG/numeric/nullspace.hpp
openMVG/src/openMVG/numeric/numeric.cpp
openMVG/src/openMVG/numeric/numeric.h
openMVG/src/openMVG/numeric/poly.h
openMVG/src/openMVG/robust_estimation/rand_sampling.hpp
openMVG/src/openMVG/robust_estimation/robust_estimator_ACRansac.hpp
openMVG/src/openMVG/robust_estimation/robust_estimator_ACRansacKernelAdaptator.hpp
openMVG/src/openMVG/robust_estimation/robust_estimator_LMeds.hpp
openMVG/src/openMVG/robust_estimation/robust_ransac_tools.hpp
openMVG/src/openMVG/sfm/pipelines/sfm_robust_model_estimation.cpp
openMVG/src/openMVG/sfm/pipelines/sfm_robust_model_estimation.hpp
openMVG/src/openMVG/sfm/sfm.hpp
openMVG/src/openMVG/sfm/sfm_data.hpp
openMVG/src/openMVG/sfm/sfm_data_BA.hpp
openMVG/src/openMVG/sfm/sfm_data_BA_ceres.cpp
openMVG/src/openMVG/sfm/sfm_data_BA_ceres.hpp
openMVG/src/openMVG/sfm/sfm_data_BA_ceres_camera_functor.hpp
openMVG/src/openMVG/sfm/sfm_data_transform.cpp
openMVG/src/openMVG/sfm/sfm_data_transform.hpp
openMVG/src/openMVG/sfm/sfm_data_triangulation.cpp
openMVG/src/openMVG/sfm/sfm_data_triangulation.hpp
openMVG/src/openMVG/sfm/sfm_data_utils.cpp
openMVG/src/openMVG/sfm/sfm_data_utils.hpp
openMVG/src/openMVG/sfm/sfm_filters.hpp
openMVG/src/openMVG/sfm/sfm_landmark.hpp
openMVG/src/openMVG/sfm/sfm_view.hpp
openMVG/src/openMVG/sfm/sfm_view_io.hpp
openMVG/src/openMVG/sfm/sfm_view_priors.hpp
openMVG/src/openMVG/stl/hash.hpp
openMVG/src/openMVG/system/logger.hpp
openMVG/src/openMVG/system/loggerprogress.hpp
openMVG/src/openMVG/system/progressinterface.hpp
openMVG/src/openMVG/types.hpp
openMVG/src/openMVG/version.hpp
openMVG/src/third_party/histogram/histogram.hpp
```

## solver_resection_kernel.cpp

The "solver_resection_kernel.cpp" file has been edited comment out P3P
algorithms in "solver_resection_p3p_ke.hpp" and
"solver_resection_p3p_kneip.hpp" and
"solver_resection_up2p_kukelova.hpp".

The edited file is here:
openMVG/src/openMVG/multiview/solver_resection_kernel.cpp

## SfM_Localizer.cpp

The "SfM_Localizer.cpp" file has been copied and edited to use the
internal class "ACKernelAdaptorResection_Intrinsics", and has been
saved as the file "robust_estimator_ACKernelAdaptorResection.hpp".

Old location:
openMVG/src/openMVG/sfm/pipelines/localization/SfM_Localizer.cpp

New location:
openMVG/src/openMVG/robust_estimation/robust_estimator_ACKernelAdaptorResection.hpp
