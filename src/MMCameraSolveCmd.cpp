/*
 * Copyright (C) 2021 David Cattermole.
 *
 * This file is part of mmSolver.
 *
 * mmSolver is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * mmSolver is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
 * ====================================================================
 *
 * Command for running mmCameraSolve.
 */

// Internal
#include <MMCameraSolveCmd.h>
#include <mayaUtils.h>

// STL
#include <vector>
#include <cmath>
#include <cassert>
#include <list>
#include <string>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <iterator>
#include <map>

// Utils
#include <utilities/debugUtils.h>


// Ceres Solver
#pragma warning( push )
// Compiler Warning (level 1) C4251: needs to have dll-interface to be used by clients of class.
#pragma warning( disable : 4251 )
#include <ceres/ceres.h>
#pragma warning( pop )

// LibMV
#pragma warning( push )
// Compiler Warning (level 3) C4267: conversion from 'size_t' to 'object', possible loss of data.
#pragma warning( disable : 4267 )
// Compiler Warning (level 4) C4127: conditional expression is constant
#pragma warning( disable : 4127 )
#include <libmv/base/vector.h>
#include <libmv/base/vector_utils.h>
#include <libmv/base/scoped_ptr.h>
#include <libmv/camera/pinhole_camera.h>
#include <libmv/correspondence/export_matches_txt.h>
#include <libmv/correspondence/feature.h>
#include <libmv/correspondence/feature_matching.h>
#include <libmv/correspondence/nRobustViewMatching.h>
#include <libmv/correspondence/import_matches_txt.h>
#include <libmv/correspondence/tracker.h>
#include <libmv/detector/detector_factory.h>
#include <libmv/descriptor/descriptor_factory.h>
#include <libmv/image/image.h>
#include <libmv/image/image_converter.h>
#include <libmv/image/image_drawing.h>
#include <libmv/image/image_io.h>
#include <libmv/logging/logging.h>
#include <libmv/numeric/numeric.h>
#include <libmv/reconstruction/euclidean_reconstruction.h>
#include <libmv/reconstruction/export_blender.h>
#include <libmv/reconstruction/export_ply.h>
#include <libmv/tools/tool.h>
#pragma warning( pop )

// Maya
#include <maya/MSyntax.h>
#include <maya/MArgList.h>
#include <maya/MArgDatabase.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>
#include <maya/MMatrix.h>
#include <maya/MMatrixArray.h>
#include <maya/MDagPath.h>
#include <maya/MFnDependencyNode.h>

// GFlags test.
DEFINE_bool(big_menu, true, "Include 'advanced' options in the menu listing");
DEFINE_string(languages, "english,french,german",
              "comma-separated list of languages to offer in the 'lang' menu");


MMCameraSolveCmd::~MMCameraSolveCmd() {}

void *MMCameraSolveCmd::creator() {
    return new MMCameraSolveCmd();
}

MString MMCameraSolveCmd::cmdName() {
    return MString("mmCameraSolve");
}

/*
 * Tell Maya we have a syntax function.
 */
bool MMCameraSolveCmd::hasSyntax() const {
    return true;
}

bool MMCameraSolveCmd::isUndoable() const {
    return false;
}

/*
 * Add flags to the command syntax
 */
MSyntax MMCameraSolveCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    unsigned int minNumObjects = 0;
    syntax.setObjectType(MSyntax::kSelectionList, minNumObjects);

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMCameraSolveCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    return status;
}

void get_file_path_extension(const std::string &file,
                             std::string *path_name,
                             std::string *ext) {
    size_t dot_pos =  file.rfind (".");
    if (dot_pos != std::string::npos) {
        *path_name = file.substr(0, dot_pos);
        *ext = file.substr(dot_pos + 1, file.length() - dot_pos - 1);
    } else {
        *path_name = file;
        *ext = "";
    }
}

struct CostFunctor {
   template <typename T>
   bool operator()(const T* const x, T* residual) const {
     residual[0] = 10.0 - x[0];
     return true;
   }
};

// Data generated using the following octave code.
//   randn('seed', 23497);
//   m = 0.3;
//   c = 0.1;
//   x=[0:0.075:5];
//   y = exp(m * x + c);
//   noise = randn(size(x)) * 0.2;
//   y_observed = y + noise;
//   data = [x', y_observed'];
const int kNumObservations = 67;

// clang-format off
const double data[] = {
  0.000000e+00, 1.133898e+00,
  7.500000e-02, 1.334902e+00,
  1.500000e-01, 1.213546e+00,
  2.250000e-01, 1.252016e+00,
  3.000000e-01, 1.392265e+00,
  3.750000e-01, 1.314458e+00,
  4.500000e-01, 1.472541e+00,
  5.250000e-01, 1.536218e+00,
  6.000000e-01, 1.355679e+00,
  6.750000e-01, 1.463566e+00,
  7.500000e-01, 1.490201e+00,
  8.250000e-01, 1.658699e+00,
  9.000000e-01, 1.067574e+00,
  9.750000e-01, 1.464629e+00,
  1.050000e+00, 1.402653e+00,
  1.125000e+00, 1.713141e+00,
  1.200000e+00, 1.527021e+00,
  1.275000e+00, 1.702632e+00,
  1.350000e+00, 1.423899e+00,
  1.425000e+00, 1.543078e+00,
  1.500000e+00, 1.664015e+00,
  1.575000e+00, 1.732484e+00,
  1.650000e+00, 1.543296e+00,
  1.725000e+00, 1.959523e+00,
  1.800000e+00, 1.685132e+00,
  1.875000e+00, 1.951791e+00,
  1.950000e+00, 2.095346e+00,
  2.025000e+00, 2.361460e+00,
  2.100000e+00, 2.169119e+00,
  2.175000e+00, 2.061745e+00,
  2.250000e+00, 2.178641e+00,
  2.325000e+00, 2.104346e+00,
  2.400000e+00, 2.584470e+00,
  2.475000e+00, 1.914158e+00,
  2.550000e+00, 2.368375e+00,
  2.625000e+00, 2.686125e+00,
  2.700000e+00, 2.712395e+00,
  2.775000e+00, 2.499511e+00,
  2.850000e+00, 2.558897e+00,
  2.925000e+00, 2.309154e+00,
  3.000000e+00, 2.869503e+00,
  3.075000e+00, 3.116645e+00,
  3.150000e+00, 3.094907e+00,
  3.225000e+00, 2.471759e+00,
  3.300000e+00, 3.017131e+00,
  3.375000e+00, 3.232381e+00,
  3.450000e+00, 2.944596e+00,
  3.525000e+00, 3.385343e+00,
  3.600000e+00, 3.199826e+00,
  3.675000e+00, 3.423039e+00,
  3.750000e+00, 3.621552e+00,
  3.825000e+00, 3.559255e+00,
  3.900000e+00, 3.530713e+00,
  3.975000e+00, 3.561766e+00,
  4.050000e+00, 3.544574e+00,
  4.125000e+00, 3.867945e+00,
  4.200000e+00, 4.049776e+00,
  4.275000e+00, 3.885601e+00,
  4.350000e+00, 4.110505e+00,
  4.425000e+00, 4.345320e+00,
  4.500000e+00, 4.161241e+00,
  4.575000e+00, 4.363407e+00,
  4.650000e+00, 4.161576e+00,
  4.725000e+00, 4.619728e+00,
  4.800000e+00, 4.737410e+00,
  4.875000e+00, 4.727863e+00,
  4.950000e+00, 4.669206e+00,
};
// clang-format on

struct ExponentialResidual {
  ExponentialResidual(double x, double y) : x_(x), y_(y) {}
  template <typename T>
  bool operator()(const T* const m, const T* const c, T* residual) const {
    residual[0] = y_ - exp(m[0] * x_ + c[0]);
    return true;
  }
 private:
  const double x_;
  const double y_;
};

MStatus MMCameraSolveCmd::doIt(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    // Command Outputs
    MDoubleArray outResult;

    // Test the GLOG library.
    INFO("Camera Solve Command - This is a log message!\n");

    // Ceres Solver - Example #1
    //
    // https://ceres-solver.googlesource.com/ceres-solver/+/master/examples/helloworld.cc
    {
        // The variable to solve for with its initial value.
        double initial_x = 5.0;
        double x = initial_x;

        // Build the problem.
        ceres::Problem problem;

        // Set up the only cost function (also known as residual). This uses
        // auto-differentiation to obtain the derivative (jacobian).
        ceres::CostFunction* cost_function =
            new ceres::AutoDiffCostFunction<CostFunctor, 1, 1>(new CostFunctor);
        problem.AddResidualBlock(cost_function, nullptr, &x);

        // Run the solver!
        ceres::Solver::Options options;
        options.linear_solver_type = ceres::DENSE_QR;
        options.minimizer_progress_to_stdout = true;
        ceres::Solver::Summary summary;
        ceres::Solve(options, &problem, &summary);

        INFO(summary.BriefReport());
        INFO("x : " << initial_x << " -> " << x)
    }

    // Ceres Solver - Example #2 - Curve Fitting
    //
    // https://ceres-solver.googlesource.com/ceres-solver/+/master/examples/curve_fitting.cc
    {
        double m = 0.0;
        double c = 0.0;

        ceres::Problem problem;
        for (int i = 0; i < kNumObservations; ++i) {
            problem.AddResidualBlock(
                new ceres::AutoDiffCostFunction<ExponentialResidual, 1, 1, 1>(
                    new ExponentialResidual(data[2 * i], data[2 * i + 1])),
                NULL,
                &m,
                &c);
        }

        ceres::Solver::Options options;
        options.max_num_iterations = 25;
        options.linear_solver_type = ceres::DENSE_QR;
        options.minimizer_progress_to_stdout = true;

        ceres::Solver::Summary summary;
        Solve(options, &problem, &summary);
        INFO(summary.BriefReport());
        INFO("Initial m: " << 0.0 << " c: " << 0.0);
        INFO("Final   m: " << m << " c: " << c);
    }

    // LibMV - Example #1
    {
        auto focal = 500.0;
        libmv::Vec2 principal_point(0.0, 0.0);
        libmv::Vec2f pixel(0.0, 0.0);
        libmv::Vec2u img_size(1920.0, 1080.0);

        auto cam = libmv::PinholeCamera(focal, principal_point);
        auto img_width = cam.image_width();
        cam.set_image_size(img_size);
        auto img_width2 = cam.image_width();
        auto ray = cam.Ray(pixel);

        auto focal_x = cam.focal_x();
        auto focal_y = cam.focal_y();
        INFO("img_width = " << img_width);
        INFO("img_width2 = " << img_width2);
        INFO("ray = " << ray);
        INFO("focal_x = " << focal_x);
        INFO("focal_y = " << focal_y);
    }

    // LibMV - Example #2 - Reconstruct Video
    //
    // Estimate the camera trajectory using matches.
    {
        // Input values
        std::string input_file_path = "matches.txt";
        std::string output_file_path = "reconstruction.py";
        int image_width = 1920;
        int image_height = 1080;
        double focal_length = 50.0;
        double principal_point_u0 = 0.0;
        double principal_point_v0 = 0.0;

        // Imports matches
        libmv::tracker::FeaturesGraph fg;
        FeatureSet *fs = fg.CreateNewFeatureSet();

        INFO("Loading Matches file...");
        libmv::ImportMatchesFromTxt(input_file_path, &fg.matches_, fs);
        INFO("Loading Matches file...[DONE].");

        // Estimates the camera trajectory and 3D structure of the scene
        int w = image_width;
        int h = image_height;
        if (principal_point_u0 > 0) {
            w = static_cast<int>(2.0 * (principal_point_u0 + 0.5));
        }
        if (principal_point_v0 > 0) {
            h = static_cast<int>(2.0 * (principal_point_v0 + 0.5));
        }

        INFO("Euclidean Reconstruction From Video...");
        std::list<libmv::Reconstruction *> reconstructions;
        EuclideanReconstructionFromVideo(
            fg.matches_,
            w, h,
            focal_length,
            &reconstructions);
        INFO("Euclidean Reconstruction From Video...[DONE]");

        // Exports the reconstructions
        INFO("Exporting Reconstructions...");
        std::string file_path_name;
        std::string file_ext;
        get_file_path_extension(output_file_path, &file_path_name, &file_ext);
        std::transform(file_ext.begin(), file_ext.end(), file_ext.begin(), ::tolower);

         int i = 0;
         std::list<libmv::Reconstruction *>::iterator iter = reconstructions.begin();
         if (file_ext == "ply") {
             for (; iter != reconstructions.end(); ++iter) {
                 std::stringstream s;
                 if (reconstructions.size() > 1)
                     s << file_path_name << "-" << i << ".ply";
                 else
                     s << output_file_path;
                 libmv::ExportToPLY(**iter, s.str());
             }
         } else  if (file_ext == "py") {
             for (; iter != reconstructions.end(); ++iter) {
                 std::stringstream s;
                 if (reconstructions.size() > 1)
                     s << file_path_name << "-" << i << ".py";
                 else
                     s << output_file_path;
                 libmv::ExportToBlenderScript(**iter, s.str());
             }
         }
        INFO("Exporting Reconstructions...[DONE]");

        // Cleaning
        INFO("Cleaning.");
        iter = reconstructions.begin();
        for (; iter != reconstructions.end(); ++iter) {
            (*iter)->ClearCamerasMap();
            (*iter)->ClearStructuresMap();
            delete *iter;
        }
        reconstructions.clear();
        // Delete the features graph
        fg.DeleteAndClear();
    }

    // Read all the flag arguments.
    status = parseArgs(args);
    if (status == MStatus::kFailure) {
        return status;
    }

    MMCameraSolveCmd::setResult(outResult);
    return status;
}
