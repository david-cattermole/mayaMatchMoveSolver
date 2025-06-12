// This file is part of OpenMVG, an Open Multiple View Geometry C++ library.

// Copyright (c) 2015 Pierre MOULON.

// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

#ifndef OPENMVG_ROBUST_AC_KERNEL_ADAPTOR_RESECTION_HPP
#define OPENMVG_ROBUST_AC_KERNEL_ADAPTOR_RESECTION_HPP

#include "openMVG/cameras/Camera_Intrinsics.hpp"
#include "openMVG/cameras/Camera_Pinhole.hpp"
#include "openMVG/multiview/solver_resection_p3p_nordberg.cpp"
#include "openMVG/geometry/pose3.hpp"
#include "openMVG/robust_estimation/robust_estimator_ACRansac.hpp"
#include "openMVG/robust_estimation/robust_estimator_ACRansacKernelAdaptator.hpp"

#include <memory>
#include <utility>

namespace openMVG {

/// Pose/Resection Kernel adapter for the A contrario model estimator
/// with known camera intrinsics.
template <typename SolverArg, typename ModelArg = openMVG::Mat34>
class ACKernelAdaptorResection_Intrinsics {
public:
    using Solver = SolverArg;
    using Model = ModelArg;

    ACKernelAdaptorResection_Intrinsics(
        const openMVG::Mat &x2d,  // Undistorted 2d feature_point location
        const openMVG::Mat &x3d,  // 3D corresponding points
        const openMVG::cameras::IntrinsicBase *camera)
        : x2d_(x2d)
        , x3d_(x3d)
        , logalpha0_(log10(M_PI))
        , N1_(openMVG::Mat3::Identity())
        , camera_(camera) {
        N1_.diagonal().head(2) *= camera->imagePlane_toCameraPlaneError(1.0);
        assert(2 == x2d_.rows());
        assert(3 == x3d_.rows());
        assert(x2d_.cols() == x3d_.cols());
        bearing_vectors_ = camera->operator()(x2d_);
    }

    enum { MINIMUM_SAMPLES = Solver::MINIMUM_SAMPLES };
    enum { MAX_MODELS = Solver::MAX_MODELS };

    void Fit(const std::vector<uint32_t> &samples,
             std::vector<Model> *models) const {
        Solver::Solve(openMVG::ExtractColumns(bearing_vectors_,
                                              samples),  // bearing vectors
                      openMVG::ExtractColumns(x3d_, samples),  // 3D points
                      models);  // Found model hypothesis
    }

    void Errors(const Model &model, std::vector<double> &vec_errors) const {
        // Convert the found model into a Pose3
        const openMVG::Vec3 t = model.block(0, 3, 3, 1);
        const openMVG::geometry::Pose3 pose(
            model.block(0, 0, 3, 3), -model.block(0, 0, 3, 3).transpose() * t);

        vec_errors.resize(x2d_.cols());

        // We ignore distortion since we are using undistorted bearing
        // vector as input.
        const bool ignore_distortion = true;

        for (openMVG::Mat::Index sample = 0; sample < x2d_.cols(); ++sample) {
            vec_errors[sample] =
                (camera_->residual(pose(x3d_.col(sample)), x2d_.col(sample),
                                   ignore_distortion) *
                 N1_(0, 0))
                    .squaredNorm();
        }
    }

    size_t NumSamples() const { return x2d_.cols(); }

    void Unnormalize(Model *model) const {}

    double logalpha0() const { return logalpha0_; }
    double multError() const { return 1.0; }  // point to point error
    openMVG::Mat3 normalizer1() const { return openMVG::Mat3::Identity(); }
    openMVG::Mat3 normalizer2() const { return N1_; }
    double unormalizeError(double val) const { return sqrt(val) / N1_(0, 0); }

private:
    openMVG::Mat x2d_;
    openMVG::Mat bearing_vectors_;
    const openMVG::Mat &x3d_;
    openMVG::Mat3 N1_;
    double logalpha0_;  // Alpha0 is used to make the error adaptive
                        // to the image size
    const openMVG::cameras::IntrinsicBase
        *camera_;  // Intrinsic camera parameter
};

}  // namespace openMVG

#endif  // OPENMVG_ROBUST_AC_KERNEL_ADAPTOR_RESECTION_HPP
